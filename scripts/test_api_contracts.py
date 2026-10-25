"""Regression checks for generated cross-client contracts (no formatter needed)."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "api_contracts", Path(__file__).with_name("generate-api-contracts.py")
)
contracts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contracts)


class ContractGenerationTest(unittest.TestCase):
    def test_export_download_grant_is_never_a_query_parameter(self):
        self.assertEqual([], contracts.queries["/me/data-exports/{id}/download"])


    def collect_fixture(self, name, source):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        file = Path(folder.name) / f"{name}.java"
        file.write_text(source)
        contracts.files[name] = file
        contracts.models.pop(name, None)
        contracts.field_rules.pop(name, None)
        contracts.collect(name)
        return contracts.render_contracts(
            {name: contracts.models[name]}, [], {}
        )

    def test_required_fields_and_explicit_null_clearing_are_distinct(self):
        generated = self.collect_fixture("RequiredFixture", """
public class RequiredFixture {
    @NotNull
    @Schema(allowableValues = {"1", "2"})
    private Long id;
    @NotBlank(message = "必填") private String title;
    @NotEmpty private List<String> ids;
    private Long parentId;
    @Valid private List<@NotNull String> optionalItems;
    @NotNull private Integer count = 1;
    @NotNull(groups = Update.class) private String updateOnly;
}
""")
        for declaration in (
            "id: string;", "title: string;", "ids: Array<string>;",
            "parentId?: string | null;", "optionalItems?: Array<string> | null;",
            "count?: number;", "updateOnly?: string | null;",
        ):
            self.assertIn(declaration, generated)

    def test_record_component_constraints_survive_annotation_removal(self):
        generated = self.collect_fixture("RecordFixture", """
public record RecordFixture(
    @NotBlank(message = "标题,不能为空") String title,
    @NotNull Long id,
    List<@NotNull String> optionalItems
) {}
""")
        self.assertIn("title: string;", generated)
        self.assertIn("id: string;", generated)
        self.assertIn("optionalItems?: Array<string> | null;", generated)

    def test_inherited_request_constraints_and_query_fields(self):
        self.collect_fixture("ParentFixture", """
public class ParentFixture {
    @NotNull private Long id;
    private Integer page;
    private Integer pageSize;
}
""")
        generated = self.collect_fixture("ChildFixture", """
public class ChildFixture extends ParentFixture {
    private String keyword;
}
""")
        self.assertIn("id: string;", generated)
        self.assertEqual(
            ["id", "page", "pageSize", "keyword"], contracts.names("ChildFixture")
        )

    def test_real_required_update_and_nested_create_requests(self):
        self.assertEqual(
            {"required": True, "nullable": False},
            contracts.field_rules["GoalUpdateReq"]["id"],
        )
        self.assertTrue(contracts.field_rules["HomePinReq"]["isPinned"]["required"])
        self.assertFalse(contracts.field_rules["ThoughtSaveReq"]["events"]["required"])
        self.assertTrue(contracts.field_rules["ThoughtSaveEventReq"]["content"]["required"])

    def test_validated_batch_request_is_not_dropped_from_allowlist(self):
        match = contracts.request_body_type(
            '@PathVariable Long id, @RequestBody @NotEmpty List<@Valid TaskSortReq> requests'
        )
        self.assertEqual(("List<", "TaskSortReq"), match.groups())
        match = contracts.request_body_type(
            '@RequestBody(required = false) @Valid GoalUpdateReq request'
        )
        self.assertEqual((None, "GoalUpdateReq"), match.groups())
        for path in ("/tasks/reSort", "/taskDetails/reSort", "/taskColumn/reSort"):
            self.assertTrue(any(route["path"] == path and route["list"] for route in contracts.routes))

    def test_clients_only_generate_canonical_pagination_names(self):
        for path in (
            "/tasks", "/movie/page", "/read-record/page", "/message/page",
            "/message/admin/list", "/system/bank-card-covers/page",
            "/github/recent-commits",
        ):
            fields = contracts.queries[path]
            self.assertTrue({"page", "pageSize"}.issubset(fields), path)
            self.assertTrue({"current", "size", "get", "perPage"}.isdisjoint(fields), path)
        self.assertEqual(["cursor", "pageSize"], contracts.queries["/weread/recent"])


if __name__ == "__main__":
    unittest.main()
