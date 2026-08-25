from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "recommended-integrations.json"
CATALOG_DOC = ROOT / "references" / "recommended-integrations.md"
CATALOG_DOC_ZH = ROOT / "references" / "recommended-integrations_zh.md"
LIST_SCRIPT = ROOT / "scripts" / "list_recommended_integrations.py"

ALLOWED_LICENSES = {
    "Apache-2.0",
    "FSL-1.1-Apache-2.0",
    "LGPL-2.1",
    "MIT",
    "MIT-0",
    "Sonar-Source-Available-1.0",
}
ALLOWED_LICENSE_KINDS = {"open-source", "source-available"}
ALLOWED_TIERS = {"baseline", "scenario", "production-risk"}
ALLOWED_IMPACTS = {
    "local-read",
    "local-write",
    "external-read",
    "external-write",
    "credentials-required",
    "production-read",
    "production-write",
}
REQUIRED_FIELDS = {
    "id",
    "name",
    "type",
    "tier",
    "maintainer",
    "repository_url",
    "source_url",
    "license_id",
    "license_kind",
    "license_url",
    "recommend_when",
    "avoid_when",
    "impacts",
    "tags",
    "status",
}
REQUIRED_COMPONENT_FIELDS = {
    "id",
    "name",
    "source_url",
    "tier",
    "recommend_when",
    "avoid_when",
    "impacts",
    "tags",
}


class RecommendedIntegrationsTests(unittest.TestCase):
    def load_catalog(self) -> dict:
        return json.loads(CATALOG.read_text(encoding="utf-8"))

    def all_items(self, catalog: dict) -> list[dict]:
        return catalog["skill_projects"] + catalog["mcp_servers"]

    def run_list(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LIST_SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_catalog_separates_workflow_skills_from_tool_servers(self) -> None:
        catalog = self.load_catalog()

        self.assertEqual(4, catalog["catalog_version"])
        self.assertFalse(catalog["policy"]["auto_install"])
        self.assertFalse(catalog["policy"]["auto_enable"])
        self.assertEqual("project", catalog["policy"]["default_install_scope"])
        self.assertFalse(catalog["policy"]["install_all"])
        self.assertEqual(".agents/skills", catalog["policy"]["default_skill_directory"])
        self.assertEqual(".codex/config.toml", catalog["policy"]["default_mcp_config"])
        self.assertEqual(
            ["open-source", "source-available"],
            catalog["policy"]["accepted_license_kinds"],
        )
        self.assertEqual(["skill_projects", "mcp_servers"], catalog["display_order"])
        self.assertTrue(catalog["skill_projects"])
        self.assertTrue(catalog["mcp_servers"])
        self.assertTrue(
            all(item["type"] == "skill-project" for item in catalog["skill_projects"])
        )
        self.assertTrue(
            all(item["type"] == "mcp-server" for item in catalog["mcp_servers"])
        )

    def test_each_repository_is_a_single_top_level_recommendation(self) -> None:
        catalog = self.load_catalog()
        repository_urls = [item["repository_url"] for item in self.all_items(catalog)]

        self.assertEqual(len(repository_urls), len(set(repository_urls)))
        self.assertEqual(
            1,
            sum(url == "https://github.com/obra/superpowers" for url in repository_urls),
        )
        self.assertEqual(
            1,
            sum(
                url == "https://github.com/TerminalSkills/skills"
                for url in repository_urls
            ),
        )

    def test_every_recommendation_is_traceable_and_has_explicit_license_terms(self) -> None:
        catalog = self.load_catalog()

        for item in self.all_items(catalog):
            with self.subTest(item=item.get("id")):
                self.assertTrue(REQUIRED_FIELDS.issubset(item))
                self.assertEqual("verified", item["status"])
                self.assertIn(item["license_id"], ALLOWED_LICENSES)
                self.assertIn(item["license_kind"], ALLOWED_LICENSE_KINDS)
                self.assertIn(item["tier"], ALLOWED_TIERS)
                self.assertTrue(set(item["impacts"]).issubset(ALLOWED_IMPACTS))
                self.assertTrue(item["repository_url"].startswith("https://github.com/"))
                self.assertTrue(item["source_url"].startswith(item["repository_url"]))
                self.assertTrue(item["license_url"].startswith(item["repository_url"]))
                self.assertTrue(item["maintainer"].strip())
                self.assertTrue(item["recommend_when"])
                self.assertTrue(item["avoid_when"])

        for project in catalog["skill_projects"]:
            with self.subTest(project=project["id"]):
                self.assertTrue(project["recommended_skills"])
                for skill in project["recommended_skills"]:
                    self.assertTrue(REQUIRED_COMPONENT_FIELDS.issubset(skill))
                    self.assertIn(skill["tier"], ALLOWED_TIERS)
                    self.assertTrue(set(skill["impacts"]).issubset(ALLOWED_IMPACTS))
                    self.assertTrue(skill["source_url"].startswith(project["repository_url"]))

    def test_known_integrations_are_classified_correctly(self) -> None:
        catalog = self.load_catalog()
        skill_ids = {item["id"] for item in catalog["skill_projects"]}
        mcp_ids = {item["id"] for item in catalog["mcp_servers"]}

        self.assertIn("superpowers", skill_ids)
        self.assertIn("terminal-skills", skill_ids)
        self.assertIn("ui-ux-pro-max", skill_ids)
        self.assertIn("openspec", skill_ids)
        self.assertIn("vercel-agent-skills", skill_ids)
        self.assertIn("cloudflare-skills", skill_ids)
        self.assertIn("awesome-copilot", skill_ids)
        self.assertIn("agent-skill-eval", skill_ids)
        self.assertIn("sentry-agent-skills", skill_ids)
        self.assertIn("microsoft-skills", skill_ids)
        self.assertIn("aws-agent-toolkit", skill_ids)
        self.assertIn("playwright-mcp", mcp_ids)
        self.assertIn("github-mcp-server", mcp_ids)
        self.assertIn("codegraph", mcp_ids)
        self.assertIn("semgrep-mcp", mcp_ids)
        self.assertIn("context7", mcp_ids)
        self.assertIn("grafana-mcp", mcp_ids)
        self.assertIn("sonarqube-mcp", mcp_ids)
        self.assertIn("sentry-mcp", mcp_ids)
        self.assertIn("dbhub", mcp_ids)
        self.assertNotIn("playwright-mcp", skill_ids)

        superpowers = next(
            item for item in catalog["skill_projects"] if item["id"] == "superpowers"
        )
        superpower_ids = {item["id"] for item in superpowers["recommended_skills"]}
        self.assertTrue(
            {
                "verification-before-completion",
                "systematic-debugging",
                "test-driven-development",
                "writing-plans",
                "executing-plans",
                "receiving-code-review",
                "using-git-worktrees",
                "finishing-a-development-branch",
            }.issubset(superpower_ids)
        )

        codegraph = next(item for item in catalog["mcp_servers"] if item["id"] == "codegraph")
        self.assertEqual("scenario", codegraph["tier"])
        self.assertEqual("https://github.com/colbymchenry/codegraph", codegraph["repository_url"])
        self.assertEqual("MIT", codegraph["license_id"])
        self.assertIn("local-write", codegraph["impacts"])
        self.assertTrue(codegraph["operational_notes"])

        sonarqube = next(
            item for item in catalog["mcp_servers"] if item["id"] == "sonarqube-mcp"
        )
        sentry = next(
            item for item in catalog["mcp_servers"] if item["id"] == "sentry-mcp"
        )
        dbhub = next(
            item for item in catalog["mcp_servers"] if item["id"] == "dbhub"
        )
        self.assertEqual("source-available", sonarqube["license_kind"])
        self.assertEqual("source-available", sentry["license_kind"])
        self.assertTrue(
            any("database-level read-only" in note for note in dbhub["operational_notes"])
        )

    def test_list_script_filters_without_installing_or_enabling_anything(self) -> None:
        result = self.run_list(
            "--type", "skill-project", "--tier", "baseline", "--format", "json"
        )
        payload = json.loads(result.stdout)

        self.assertTrue(payload["items"])
        self.assertTrue(
            all(item["type"] == "skill-project" for item in payload["items"])
        )
        self.assertTrue(
            all(
                any(skill["tier"] == "baseline" for skill in item["recommended_skills"])
                for item in payload["items"]
            )
        )
        self.assertFalse(payload["policy"]["auto_install"])
        self.assertFalse(payload["policy"]["auto_enable"])

        tagged = json.loads(self.run_list("--tag", "react", "--format", "json").stdout)
        self.assertTrue(tagged["items"])
        self.assertTrue(
            all(
                "react" in item["tags"]
                or any(
                    "react" in skill["tags"] for skill in item.get("recommended_skills", [])
                )
                for item in tagged["items"]
            )
        )

        risky = self.run_list(
            "--type", "skill-project", "--tier", "production-risk"
        )
        self.assertIn("scenario, production-risk", risky.stdout)

        source_available = self.run_list("--tag", "sonarqube")
        self.assertIn("Sonar-Source-Available-1.0", source_available.stdout)
        self.assertIn("source-available", source_available.stdout)

        licensed = json.loads(
            self.run_list(
                "--license-kind", "source-available", "--format", "json"
            ).stdout
        )
        self.assertEqual(2, licensed["count"])
        self.assertTrue(
            all(item["license_kind"] == "source-available" for item in licensed["items"])
        )

    def test_project_docs_explain_opt_in_recommendations_and_type_boundary(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README_zh.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        skill_zh = (ROOT / "SKILL_zh.md").read_text(encoding="utf-8")

        # English is the default: the operative docs state the policy in English.
        for text in [readme, skill]:
            self.assertIn("references/recommended-integrations.json", text)
            self.assertIn("Skill", text)
            self.assertIn("MCP Server", text)
            self.assertIn("never installed or enabled automatically", text)
            self.assertIn("project-level", text)

        # The linked Chinese translations state the same policy in Chinese.
        for text in [readme_zh, skill_zh]:
            self.assertIn("references/recommended-integrations.json", text)
            self.assertIn("不自动安装", text)
            self.assertIn("项目级", text)

        self.assertIn("scripts/list_recommended_integrations.py", readme)
        self.assertIn("scripts/install_project_integration.py", readme)
        self.assertIn(".agents/skills", readme)
        self.assertIn(".codex/config.toml", readme)
        self.assertIn("one recommendation per source repository", readme)
        self.assertIn("一个源码仓库只保留一条推荐", readme_zh)
        self.assertNotIn("--type skill --", readme)
        self.assertNotIn("--type skill --", readme_zh)

    def test_human_catalog_links_every_source_and_license_in_both_languages(self) -> None:
        catalog = self.load_catalog()
        documents = [
            CATALOG_DOC.read_text(encoding="utf-8"),
            CATALOG_DOC_ZH.read_text(encoding="utf-8"),
        ]

        for item in self.all_items(catalog):
            with self.subTest(item=item["id"]):
                for document in documents:
                    self.assertIn(item["repository_url"], document)
                    self.assertIn(item["license_id"], document)
                    self.assertIn(item["license_url"], document)

    def test_human_catalog_english_is_the_default_with_a_chinese_translation(self) -> None:
        document = CATALOG_DOC.read_text(encoding="utf-8")
        document_zh = CATALOG_DOC_ZH.read_text(encoding="utf-8")

        self.assertIn("Skill projects", document)
        self.assertIn("One recommendation per source repository", document)
        self.assertIn("Source-Available", document)
        self.assertIn("never installed or enabled automatically", document)
        self.assertIn("project-level", document)
        self.assertNotIn("未进入清单", document)
        self.assertNotIn("filesystem", document)
        self.assertNotIn("Trivy", document)

        self.assertIn("Skill 项目与 MCP Server", document_zh)
        self.assertIn("一个源码仓库只保留一条推荐", document_zh)
        self.assertIn("Source-Available", document_zh)
        self.assertIn("不自动安装", document_zh)
        self.assertIn("默认安装到项目级", document_zh)
        self.assertNotIn("未进入清单", document_zh)
        self.assertNotIn("filesystem", document_zh)
        self.assertNotIn("Trivy", document_zh)


if __name__ == "__main__":
    unittest.main()
