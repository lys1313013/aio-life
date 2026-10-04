#!/usr/bin/env python3
"""Generate Web/mobile request contracts from the backend's explicit API models.

Run from any directory. --check detects drift without writing. Only declared
request fields and actual GET filters are copied; dynamic third-party/MCP data
remains dynamic. Requires the frontend's installed Prettier and ESLint for stable output.
"""
import argparse
import subprocess

from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'aio-life-server/src/main/java'
def mask(s):
 return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:re.sub(r'[^\n]',' ',m[0]),s,flags=re.S)
def close(s,start,left,right):
 n=0
 for i in range(start,len(s)):
  if s[i]==left:n+=1
  elif s[i]==right:
   n-=1
   if n==0:return i
 raise ValueError(start)
def methods(s):
 ms=mask(s);out=[]
 for m in re.finditer(r'public\s+(ApiResponse<[\w.<>, ?]+>|SseEmitter|void)\s+(\w+)\s*\(',ms):
  end=close(ms,m.end()-1,'(',')');bs=ms.find('{',end);be=close(ms,bs,'{','}')
  previous=ms.rfind('}',0,m.start())
  ann=s[previous+1:m.start()]; mappings=list(re.finditer(r'@(Get|Post|Put|Delete|Patch)Mapping(?:\(([^\n]*)\))?',ann))
  if not mappings:continue
  ma=mappings[-1];path=re.search(r'"([^"]*)"',ma[2] or '')
  out.append(dict(start=m.start(),paramsStart=m.end(),paramsEnd=end,bodyStart=bs,bodyEnd=be,name=m[2],ret=m[1],params=s[m.end():end],body=s[bs+1:be],verb=ma[1].upper(),path=path[1] if path else ''))
 return out
def split_params(s):
 masked=mask(s);out=[];start=0;depth=0
 for i,ch in enumerate(masked):
  if ch in '(<[{':depth+=1
  elif ch in ')>]}':depth-=1
  elif ch==',' and depth==0:out.append(s[start:i]);start=i+1
 out.append(s[start:]);return out
base=SRC/'top/aiolife'
files={f.stem:f for f in sorted(base.rglob('*.java'))}
models={}
virtual={}
for filename,file in list(files.items()):
 text=file.read_text();masked=mask(text)
 for m in re.finditer(r"public (?:static )?(?:final )?(?:class|record) (\w+)",text):
  start=masked.find("{",m.end());end=close(masked,start,"{","}")
  name=filename+"_"+m[1]
  virtual[name]=(text[m.start():end+1].replace(m[1],name,1) if "record" in m[0] else "public class "+name+" "+text[start:end+1])
  files[name]=file
virtual["ToolCallRequest"]="public record ToolCallRequest(String name, Map<String, Object> arguments) {}"
files["ToolCallRequest"]=base/"mcp/api/McpController.java"
def collect(name):
 if name in models:return
 if name not in files:return
 p=files[name];s=virtual.get(name,p.read_text());masked=mask(s);data={}
 models[name]=data
 parent=re.search(r'public class \w+ extends (\w+)',s)
 if parent:collect(parent[1]);data.update(models.get(parent[1],{}))
 # Remove annotations while preserving source positions, including type-use annotations inside List<>.
 stripped=list(s)
 for annotation in re.finditer(r'@[\w.]+',masked):
  end=annotation.end(); pos=end
  while pos<len(masked) and masked[pos].isspace():pos+=1
  if pos<len(masked) and masked[pos]=='(':end=close(masked,pos,'(',')')+1
  stripped[annotation.start():end]=' '*(end-annotation.start())
 plain=''.join(stripped)
 for m in re.finditer(r'(?:\b(?:private|protected|public)\s+)?((?:java\.[\w.]+|[A-Z][\w.]*|boolean|int)(?:<[\w<>., ?]+>)?)\s+(\w+)\s*(?:=[^;]+)?;',plain):
  before=masked[:m.start()]
  if before.count('{')-before.count('}')!=1:continue
  typ,field=m.groups()
  if field in ['parentIdSpecified','ratingProvided','avatarFileIdSpecified','providerIdProvided']:continue
  typ=re.sub(r'\s+',' ',typ).replace('< ','<').replace(' >','>')
  data[field]=typ
  nested=re.sub(r'(?:java.util.)?List<([^>]+)>',r'\1',typ)
  if name+'_'+nested in virtual:
   typ=typ.replace(nested,name+'_'+nested);nested=name+'_'+nested;data[field]=typ
  if nested in files and ('/req/' in str(files[nested]) or '/query/' in str(files[nested])):collect(nested)
 record=re.search(r'public record '+re.escape(name)+r'\s*\(',plain)
 if record:
  end=close(mask(plain),record.end()-1,'(',')')
  for component in split_params(plain[record.end():end]):
   match=re.search(r'([\w<>., ?]+)\s+(\w+)\s*$',component.strip())
   if match:data[match[2]]=match[1]

routes=[]
for p in sorted(base.rglob('*Controller.java')):
 s=p.read_text();pr=re.search(r'@RequestMapping\("([^"]*)"\)',s);prefix=pr[1] if pr else ''
 for m in methods(s):
  q=re.search(r'@RequestBody\s+(List<)?([\w.]+)>?\s+\w+',m['params'])
  if q:
   arr,name=q.groups();name=re.sub(r'^top\.aiolife\.[\w.]+\.pojo\.req\.', '', name).replace('.', '_')
   # Imported nested request records can be referenced by their short Java name.
   # Resolve only types declared in this controller or its explicit imports;
   # never guess from unrelated same-named models elsewhere in the repository.
   if name not in files:
    candidates = {p.stem + '_' + name} & files.keys()
    for imported, wildcard in re.findall(r'import\s+(?:static\s+)?(\w+(?:\.\w+)*)(\.\*)?\s*;', s):
     parts = imported.split('.')
     candidate = parts[-1] + '_' + name if wildcard else '_'.join(parts[-2:])
     if (wildcard or parts[-1] == name) and candidate in virtual:
      candidates.add(candidate)
    if len(candidates) == 1:name = next(iter(candidates))
    elif len(candidates) > 1:raise ValueError(f'Ambiguous request model {name}: {p}')
   if name not in files:raise ValueError(f'Unknown request model {name}: {m["verb"]} {prefix+m["path"]}')
   collect(name);routes.append(dict(verb=m['verb'],path=prefix+m['path'],model=name,list=bool(arr)))
# InputSchema for MCP arguments, raw third-party predictions and menu metadata remain intentionally dynamic.
# These endpoint payloads are already explicit DTOs; their nested data is not arbitrary persistence data.
def ts_type(t):
 if t in models:return t
 if t.startswith(('List<','java.util.List<')):return 'Array<'+ts_type(t[t.index('<')+1:-1])+'>'
 if t.startswith(('Map<','java.util.Map<')):return 'Record<string, unknown>'
 if t in ('String','LocalDate','LocalDateTime','Instant'):return 'string'
 if t=='Long':return 'string'
 if t=='BigDecimal':return 'number | string'
 if t in ('Integer','int','Double','Float'):return 'number'
 if t in ('Boolean','boolean'):return 'boolean'
 if t=='ProgressStatusEnum':return "'not_started' | 'in_progress' | 'completed' | 'on_hold'"
 return 'unknown'
queries={}
def names(name):
 if name not in files:return []
 s=files[name].read_text()
 return [n for n in re.findall(r'\bprivate\s+[\w<>., ?]+\s+(\w+)\s*(?:=[^;]+)?;',s) if n!='condition']
for p in sorted(base.rglob('*Controller.java')):
 s=p.read_text();pr=re.search(r'@RequestMapping\("([^"]*)"\)',s);prefix=pr[1] if pr else ''
 for m in methods(s):
  if m['verb']!='GET':continue
  keys=[]
  for param in split_params(m['params']):
   if '@PathVariable' in param:continue
   q=re.search(r'CommonQuery<([\w.]+)>',param)
   if q:keys+=['page','pageSize']+names(q[1].split('.')[-1]);continue
   typed=re.search(r'(?:\b|\.)(\w+Query)\s+\w+\s*$',param)
   if typed:keys+=names(typed[1]);continue
   primitive=re.search(r'\b(?:(?:String|int|Integer|Long|long|Boolean|boolean)|(?:List|Set)<\s*(?:String|Integer|Long|Boolean)\s*>)\s+(\w+)\s*$',param)
   if primitive:
    alias=re.search(r'@RequestParam\((?:value\s*=\s*)?"([^"]+)"',param)
    keys.append(alias[1] if alias else primitive[1])
  queries[prefix+m['path']]=sorted(set(keys))
request_helpers='''
function samePath(pattern: string, path: string): boolean {
  const expected = pattern.split('/');
  const actual = path.split('?')[0]?.split('/') ?? [];
  return expected.length === actual.length && expected.every((part, index) =>
    part.startsWith('{') ? actual[index] !== '' : part === actual[index]);
}

/** GET 只发送接口支持的筛选与分页条件。 */
export function pickQuery(path: string, value: Record<string, unknown>): Record<string, unknown> {
  const entries = Object.entries(queryFields);
  const entry = entries.find(([pattern]) => pattern === path.split('?')[0])
    ?? entries.find(([pattern]) => samePath(pattern, path));
  if (!entry) return value;
  const result: Record<string, unknown> = {};
  for (const [key, item] of Object.entries(value)) {
    if (entry[1].includes(key) && item !== undefined && item !== null) result[key] = item;
  }
  return result;
}

/** 移动端存在动态业务路由，在请求边界按对应 DTO 选择字段。 */
export function minimalRequestPayload(path: string, method: string, value: unknown): unknown {
  if (value === null || value === undefined) return value;
  if (method === 'GET') return pickQuery(path, value as Record<string, unknown>);
  const route = requestModels.find((entry) => entry.method === method && entry.path === path.split('?')[0])
    ?? requestModels.find((entry) => entry.method === method && samePath(entry.path, path));
  if (!route) return value;
  return route.list ? pickPayloadList(route.model, value as unknown[]) : pickPayload(route.model, value);
}
'''

def render_contracts(models, routes, queries):
 lines=['/** 自动生成：运行 scripts/generate-api-contracts.py；ID 为字符串，显式 null 保留清空语义。 */']
 for name,fields in sorted(models.items()):
  lines.append(f'export interface {name} {{')
  for key,t in fields.items():lines.append(f'  {key}?: {ts_type(t)} | null;')
  lines.append('}\n')
 lines.append('export interface ApiRequests {')
 for name in sorted(models):lines.append(f'  {name}: {name};')
 lines.extend(['}\n','const fields: Record<string, Record<string, string | null>> = {'])
 for name,keys in sorted(models.items()):
  lines.append(f'  {name}: {{')
  for key,t in keys.items():
   nested=t[t.index('<')+1:-1] if t.startswith(('List<','java.util.List<')) else t
   lines.append(f'    {key}: {json.dumps(nested) if nested in models else "null"},')
  lines.append('  },')
 lines.extend(['};\n', '''/** 在发送点选择允许的字段，防止列表记录、审计字段和客户端派生字段被整对象回传。 */
export function pickPayload<K extends keyof ApiRequests>(name: K, value: unknown): ApiRequests[K] {
  const input = (value ?? {}) as Record<string, unknown>;
  const result: Record<string, unknown> = {};
  for (const [key, nested] of Object.entries(fields[name] ?? {})) {
    if (!Object.hasOwn(input, key) || input[key] === undefined) continue;
    const item = input[key];
    result[key] = nested && item !== null
      ? (Array.isArray(item)
        ? item.map((entry) => pickPayload(nested as K, entry))
        : pickPayload(nested as K, item))
      : item;
  }
  return result as ApiRequests[K];
}

export function pickPayloadList<K extends keyof ApiRequests>(name: K, values: unknown[]): ApiRequests[K][] {
  return values.map((value) => pickPayload(name, value));
}
'''])
 code='\n'.join(lines)
 extra='\nconst queryFields: Record<string, string[]> = '+json.dumps(queries,ensure_ascii=False,indent=2)+';\n'
 extra+='\nconst requestModels: Array<{ method: string; path: string; model: keyof ApiRequests; list: boolean }> = [\n'+''.join('  '+json.dumps(dict(method=r['verb'],path=r['path'],model=r['model'],list=r['list']))+',\n' for r in routes)+'];\n'
 return code+extra+request_helpers

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
formatter = ROOT / 'aio-life-front/node_modules/.bin/prettier'
if not formatter.exists():
 raise SystemExit('Install frontend dependencies before generating contracts (pnpm install).')
changed = []
for dest in [ROOT/'aio-life-front/apps/web-antd/src/api/payload.ts', ROOT/'aio-life-mobile/src/services/api-payload.ts']:
 # Web no longer exposes LLM chat or model settings. Keep its generated contracts
 # aligned with that scope without changing the backend or the mobile contract.
 is_web = dest.is_relative_to(ROOT/'aio-life-front')
 client_models = {name: fields for name, fields in models.items()
                  if not is_web or not files[name].is_relative_to(base/'llm')}
 client_routes = [route for route in routes if route['model'] in client_models]
 client_queries = {path: fields for path, fields in queries.items()
                   if not is_web or not path.startswith('/llm/')}
 source = render_contracts(client_models, client_routes, client_queries)
 output = subprocess.run([str(formatter), '--parser', 'typescript'], input=source, cwd=ROOT / 'aio-life-front', text=True, check=True, capture_output=True).stdout
 # Use the same formatting rules as checked-in API code without mutating files.
 lint = subprocess.run([str(ROOT/'aio-life-front/node_modules/.bin/eslint'), '--stdin', '--stdin-filename', 'apps/web-antd/src/api/payload.ts', '--fix-dry-run', '--format', 'json'], input=output, cwd=ROOT/'aio-life-front', text=True, check=True, capture_output=True)
 output = json.loads(lint.stdout)[0].get('output', output)
 if not dest.exists() or dest.read_text() != output:
  changed.append(str(dest.relative_to(ROOT)))
  if not args.check: dest.write_text(output)
print(f'{len(models)} request models, {len(routes)} body routes, {len(queries)} GET routes')
if args.check and changed:
 raise SystemExit('Contract drift: ' + ', '.join(changed))
print('Contracts match backend.' if args.check else 'Contracts generated.')
