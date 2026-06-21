import re
import os

# Fix dashboard
dash_path = "aio-life-front/apps/mobile-uniapp/src/pages/finance/dashboard/index.vue"
with open(dash_path, "r") as f:
    content = f.read()

content = content.replace(
    "if (map.has(m)) map.get(m)!.expense = item.amount || 0;\n          tExp += (item.amount || 0);",
    "const monthTotal = item.detail ? item.detail.reduce((sum: number, d: any) => sum + (d.amt || 0), 0) : (item.amount || 0);\n          if (map.has(m)) map.get(m)!.expense = monthTotal;\n          tExp += monthTotal;"
)

content = content.replace(
    "if (map.has(m)) map.get(m)!.income = item.amount || 0;\n          tInc += (item.amount || 0);",
    "const monthTotal = item.detail ? item.detail.reduce((sum: number, d: any) => sum + (d.amt || 0), 0) : (item.amount || 0);\n          if (map.has(m)) map.get(m)!.income = monthTotal;\n          tInc += monthTotal;"
)

with open(dash_path, "w") as f:
    f.write(content)

# Fix expense
exp_path = "aio-life-front/apps/mobile-uniapp/src/pages/finance/expense/index.vue"
with open(exp_path, "r") as f:
    content = f.read()

content = content.replace(
    "sum + (item.amount || 0)",
    "sum + (item.amt || item.transactionAmt || item.amount || 0)"
)
content = content.replace(
    "item.category ? item.category.substring(0,1) : '支'",
    "(item.counterparty || item.expDesc || item.category || '支').substring(0,1)"
)
content = content.replace(
    "item.category || '未分类'",
    "item.counterparty || item.expDesc || item.category || '未分类'"
)
content = content.replace(
    "{{ item.date }}",
    "{{ item.expTime || item.date }}"
)
content = content.replace(
    "item.amount.toFixed(2)",
    "(item.amt || item.transactionAmt || item.amount || 0).toFixed(2)"
)

with open(exp_path, "w") as f:
    f.write(content)

# Fix income
inc_path = "aio-life-front/apps/mobile-uniapp/src/pages/finance/income/index.vue"
with open(inc_path, "r") as f:
    content = f.read()

content = content.replace(
    "sum + (item.amount || 0)",
    "sum + (item.amt || item.amount || 0)"
)
content = content.replace(
    "item.category ? item.category.substring(0,1) : '收'",
    "(item.remark || item.category || '收').substring(0,1)"
)
content = content.replace(
    "item.category || '未分类'",
    "item.remark || item.category || '未分类'"
)
content = content.replace(
    "{{ item.date }}",
    "{{ item.incDate || item.date }}"
)
content = content.replace(
    "item.amount.toFixed(2)",
    "(item.amt || item.amount || 0).toFixed(2)"
)

with open(inc_path, "w") as f:
    f.write(content)

print("Done")