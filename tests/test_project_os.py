from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "scripts" / "init_project_os.py"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_project_os.py"
SELF_CHECK_SCRIPT = ROOT / "scripts" / "self_check.py"

CORE_FILES = {
    "AGENTS.md",
    ".codex/skills/project-memory/SKILL.md",
    "docs/ai/project.json",
    "docs/ai/routes.json",
    "docs/ai/memory.json",
    "docs/ai/logs/2026-08-25.md",
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectOsTests(unittest.TestCase):
    def run_script(
        self,
        script: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def init(self, target: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            INIT_SCRIPT,
            "--target",
            str(target),
            "--date",
            "2026-08-25",
            *args,
        )

    def test_initializes_only_the_core_project_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "customer-portal"
            result = self.init(target)

            self.assertIn("initialized", result.stdout.lower())
            for relative in CORE_FILES:
                self.assertTrue((target / relative).is_file(), relative)

            project = json.loads((target / "docs/ai/project.json").read_text(encoding="utf-8"))
            routes = json.loads((target / "docs/ai/routes.json").read_text(encoding="utf-8"))
            memory = json.loads((target / "docs/ai/memory.json").read_text(encoding="utf-8"))
            self.assertEqual("customer-portal", project["project"]["name"])
            self.assertEqual(1, project["schema_version"])
            self.assertEqual(1, routes["schema_version"])
            self.assertEqual(1, memory["schema_version"])
            self.assertIn("develop", routes["routes"])
            self.assertEqual([], memory["tool_failures"])

            generated = {
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file() and path.name != ".gitignore"
            }
            self.assertEqual(CORE_FILES, generated)

    def test_dry_run_is_non_mutating_and_uses_portable_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "preview"
            result = self.init(target, "--dry-run")

            self.assertIn("DRY RUN", result.stdout)
            self.assertIn("docs/ai/project.json", result.stdout)
            self.assertNotIn("docs\\ai\\project.json", result.stdout)
            self.assertFalse(target.exists())

    def test_existing_files_are_preserved_unless_force_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            project = target / "docs/ai/project.json"
            project.parent.mkdir(parents=True)
            project.write_text('{"keep": true}\n', encoding="utf-8")

            first = self.init(target)
            self.assertIn("skipped", first.stdout.lower())
            self.assertEqual({"keep": True}, json.loads(project.read_text(encoding="utf-8")))

            forced = self.init(target, "--force")
            self.assertIn("overwritten", forced.stdout.lower())
            self.assertIn("project", json.loads(project.read_text(encoding="utf-8")))

    def test_gitignore_update_is_idempotent_and_preserves_user_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            gitignore = target / ".gitignore"
            gitignore.write_text("dist/\n", encoding="utf-8")

            self.init(target)
            first = gitignore.read_text(encoding="utf-8")
            self.init(target)
            second = gitignore.read_text(encoding="utf-8")

            self.assertEqual(first, second)
            self.assertTrue(first.startswith("dist/\n"))
            self.assertIn("# AI Project OS: local-only files", first)
            self.assertIn(".codex/local/", first)
            self.assertIn("!.env.example", first)

    def test_initializer_rejects_sensitive_template_assets(self) -> None:
        module = load_module(INIT_SCRIPT, "init_project_os")
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / "bad.md"
            asset.write_text("api_key = sk-proj-abcdefghijklmnopqrstuvwxyz", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "sensitive"):
                module.assert_safe_asset(asset)

    def test_template_rendering_escapes_project_names_for_json(self) -> None:
        module = load_module(INIT_SCRIPT, "init_project_os_render")

        rendered = module.render_text(
            '{"name": "{{project_name}}"}',
            date="2026-08-25",
            project_name='quoted"project',
        )

        self.assertEqual('quoted"project', json.loads(rendered)["name"])

    def test_initializer_rejects_a_date_that_could_escape_the_log_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = self.run_script(
                INIT_SCRIPT,
                "--target",
                str(target),
                "--date",
                "../../outside",
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertFalse(target.exists())

    def test_validator_accepts_generated_project_and_reports_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "validated"
            self.init(target)

            result = self.run_script(
                VALIDATE_SCRIPT,
                "--target",
                str(target),
                "--format",
                "json",
            )
            payload = json.loads(result.stdout)

            self.assertEqual("pass", payload["status"])
            self.assertEqual(0, payload["summary"]["errors"])
            self.assertGreater(payload["summary"]["warnings"], 0)
            self.assertTrue(any(item["code"] == "project-placeholder" for item in payload["findings"]))

            strict = self.run_script(
                VALIDATE_SCRIPT,
                "--target",
                str(target),
                "--strict",
                check=False,
            )
            self.assertNotEqual(0, strict.returncode)

    def test_validator_detects_missing_invalid_and_unsafe_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init(target)

            (target / "docs/ai/routes.json").unlink()
            missing = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            missing_payload = json.loads(missing.stdout)
            self.assertEqual("fail", missing_payload["status"])
            self.assertTrue(any(item["code"] == "required-file-missing" for item in missing_payload["findings"]))

            (target / "docs/ai/routes.json").write_text("{not json", encoding="utf-8")
            invalid = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            invalid_payload = json.loads(invalid.stdout)
            self.assertTrue(any(item["code"] == "json-invalid" for item in invalid_payload["findings"]))

            (target / "docs/ai/routes.json").write_text(
                json.dumps({"schema_version": 1, "routes": {}}, ensure_ascii=False),
                encoding="utf-8",
            )
            (target / "docs/ai/memory.json").write_text(
                '{"schema_version": 1, "token": "sk-proj-abcdefghijklmnopqrstuvwxyz"}',
                encoding="utf-8",
            )
            unsafe = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            unsafe_payload = json.loads(unsafe.stdout)
            self.assertTrue(any(item["code"] == "possible-secret" for item in unsafe_payload["findings"]))

    def test_validator_rejects_route_targets_outside_the_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init(target)
            route_path = target / "docs/ai/routes.json"
            routes = json.loads(route_path.read_text(encoding="utf-8"))
            routes["routes"]["develop"]["read"] = ["../../outside.md"]
            route_path.write_text(json.dumps(routes), encoding="utf-8")

            result = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            payload = json.loads(result.stdout)
            self.assertTrue(any(item["code"] == "route-target-unsafe" for item in payload["findings"]))

    def test_validator_applies_route_safety_to_the_default_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init(target)
            route_path = target / "docs/ai/routes.json"
            routes = json.loads(route_path.read_text(encoding="utf-8"))
            routes["default"]["read"] = ["../outside.md"]
            route_path.write_text(json.dumps(routes), encoding="utf-8")

            result = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            payload = json.loads(result.stdout)
            self.assertTrue(any(item["code"] == "route-target-unsafe" for item in payload["findings"]))

    def test_validator_requires_the_core_product_delivery_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init(target)
            route_path = target / "docs/ai/routes.json"
            routes = json.loads(route_path.read_text(encoding="utf-8"))
            routes["routes"]["develop"].pop("gates")
            route_path.write_text(json.dumps(routes), encoding="utf-8")

            result = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            payload = json.loads(result.stdout)

            self.assertEqual("fail", payload["status"])
            self.assertTrue(any(item["code"] == "route-gates-missing" for item in payload["findings"]))

    def test_skill_entry_is_concise_and_routes_to_project_memory(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(skill.splitlines()), 140)
        self.assertIn("name: ai-project-os", skill)
        self.assertIn("docs/ai/routes.json", skill)
        self.assertIn("docs/ai/project.json", skill)
        self.assertIn("docs/ai/memory.json", skill)
        self.assertNotIn("Java 工程规范", skill)
        self.assertNotIn("前端工程规范", skill)
        self.assertNotIn("九个阶段", skill)

    def test_openai_metadata_uses_the_supported_interface_contract(self) -> None:
        metadata = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")

        self.assertTrue(metadata.startswith("interface:\n"))
        self.assertIn('  display_name: "AI Project OS"', metadata)
        self.assertIn('  short_description: "', metadata)
        self.assertIn('$ai-project-os', metadata)

    def test_generated_project_has_a_concise_product_work_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init(target)
            agreement = (target / "AGENTS.md").read_text(encoding="utf-8")

            for principle in [
                "user-visible outcome",
                "smallest complete scope",
                "only when relevant",
                "blocker, required risk, or later improvement",
                "plain language",
                "implementation, engineering verification, and product acceptance",
            ]:
                self.assertIn(principle, agreement)
            self.assertLessEqual(len(agreement.splitlines()), 50)

    def test_development_routes_encode_outcome_scope_risk_and_acceptance_gates(self) -> None:
        routes = json.loads(
            (ROOT / "assets/project-os/docs/ai/routes.json").read_text(encoding="utf-8")
        )["routes"]

        self.assertEqual(
            [
                "define_user_outcome",
                "define_minimum_complete_scope",
                "check_relevant_product_risks",
                "define_acceptance_evidence",
            ],
            routes["develop"]["gates"],
        )
        self.assertEqual(
            ["engineering_verification", "user_flow_acceptance"],
            routes["verify"]["gates"],
        )

    def test_portable_skill_does_not_hardcode_personal_git_preferences(self) -> None:
        portable_text = "\n".join(
            [
                (ROOT / "SKILL.md").read_text(encoding="utf-8"),
                (ROOT / "assets/project-os/AGENTS.md").read_text(encoding="utf-8"),
            ]
        ).lower()

        self.assertNotIn("git push", portable_text)
        self.assertNotIn("commit message", portable_text)

    def test_self_check_exercises_the_complete_package(self) -> None:
        result = self.run_script(SELF_CHECK_SCRIPT)
        self.assertIn("SELF CHECK PASSED", result.stdout)


if __name__ == "__main__":
    unittest.main()
