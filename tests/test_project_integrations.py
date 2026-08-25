from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "scripts" / "init_project_os.py"
INSTALL_SCRIPT = ROOT / "scripts" / "install_project_integration.py"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_project_os.py"


class ProjectIntegrationTests(unittest.TestCase):
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

    def initialize(self, target: Path) -> None:
        self.run_script(
            INIT_SCRIPT,
            "--target",
            str(target),
            "--date",
            "2026-08-25",
        )

    def test_selected_skill_is_installed_and_locked_at_project_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            source = root / "systematic-debugging"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: systematic-debugging\ndescription: Debug systematically.\n---\n",
                encoding="utf-8",
            )
            (source / "reference.md").write_text("evidence first\n", encoding="utf-8")
            self.initialize(target)

            result = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(source),
            )

            installed = target / ".agents/skills/systematic-debugging"
            self.assertIn("project", result.stdout.lower())
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "reference.md").is_file())
            manifest = json.loads(
                (target / "docs/ai/capabilities.json").read_text(encoding="utf-8")
            )
            lock = json.loads(
                (target / "docs/ai/capabilities.lock.json").read_text(encoding="utf-8")
            )
            capability = manifest["capabilities"][0]
            locked = lock["capabilities"][0]
            self.assertEqual("project", capability["scope"])
            self.assertEqual("skill-project", capability["type"])
            self.assertTrue(capability["state"]["installed"])
            self.assertTrue(capability["state"]["enabled"])
            self.assertFalse(capability["state"]["verified"])
            self.assertEqual(
                ".agents/skills/systematic-debugging",
                capability["selected_skills"][0]["installed_path"],
            )
            self.assertEqual("local", locked["revision"])
            self.assertRegex(locked["content_sha256"], r"^[0-9a-f]{64}$")

    def test_skill_install_does_not_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            source = root / "skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("first\n", encoding="utf-8")
            self.initialize(target)
            args = (
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(source),
            )
            self.run_script(INSTALL_SCRIPT, *args)
            (source / "SKILL.md").write_text("second\n", encoding="utf-8")

            refused = self.run_script(INSTALL_SCRIPT, *args, check=False)
            self.assertNotEqual(0, refused.returncode)
            self.assertEqual(
                "first\n",
                (target / ".agents/skills/systematic-debugging/SKILL.md").read_text(
                    encoding="utf-8"
                ),
            )

            self.run_script(INSTALL_SCRIPT, *args, "--force")
            self.assertEqual(
                "second\n",
                (target / ".agents/skills/systematic-debugging/SKILL.md").read_text(
                    encoding="utf-8"
                ),
            )

    def test_mcp_is_configured_in_project_disabled_and_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)

            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "npx",
                "--arg=-y",
                "--arg=@upstash/context7-mcp",
                "--env-var",
                "CONTEXT7_API_KEY",
            )

            config = (target / ".codex/config.toml").read_text(encoding="utf-8")
            self.assertIn("[mcp_servers.context7]", config)
            self.assertIn('command = "npx"', config)
            self.assertIn('args = ["-y", "@upstash/context7-mcp"]', config)
            self.assertIn('env_vars = ["CONTEXT7_API_KEY"]', config)
            self.assertIn("enabled = false", config)
            self.assertNotIn("api_key =", config.lower())

            manifest = json.loads(
                (target / "docs/ai/capabilities.json").read_text(encoding="utf-8")
            )
            state = manifest["capabilities"][0]["state"]
            self.assertFalse(state["installed"])
            self.assertFalse(state["enabled"])
            self.assertTrue(state["configured"])
            self.assertFalse(state["verified"])

    def test_mcp_can_be_explicitly_enabled_and_uses_environment_variable_names_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)

            enabled = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--url",
                "https://mcp.example.test/mcp",
                "--bearer-token-env-var",
                "CONTEXT7_TOKEN",
                "--enable",
            )
            self.assertIn("enabled", enabled.stdout.lower())
            config = (target / ".codex/config.toml").read_text(encoding="utf-8")
            self.assertIn('url = "https://mcp.example.test/mcp"', config)
            self.assertIn('bearer_token_env_var = "CONTEXT7_TOKEN"', config)
            self.assertIn("enabled = true", config)

            rejected = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--url",
                "https://mcp.example.test/mcp",
                "--bearer-token-env-var",
                "secret-value-not-a-name",
                "--force",
                check=False,
            )
            self.assertNotEqual(0, rejected.returncode)

            secret_arg = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "context7",
                "--arg=--api-key=sk-proj-abcdefghijklmnopqrstuvwxyz",
                "--force",
                check=False,
            )
            self.assertNotEqual(0, secret_arg.returncode)

    def test_mcp_installer_preserves_user_config_and_rejects_an_unmanaged_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)
            config = target / ".codex/config.toml"
            config.parent.mkdir(parents=True)
            config.write_text(
                'model = "gpt-example"\n\n[mcp_servers.context7]\ncommand = "custom"\n',
                encoding="utf-8",
            )

            result = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "npx",
                "--arg=@upstash/context7-mcp",
                check=False,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                'model = "gpt-example"\n\n[mcp_servers.context7]\ncommand = "custom"\n',
                config.read_text(encoding="utf-8"),
            )

    def test_source_available_integration_requires_exact_license_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)

            refused = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "sentry-mcp",
                "--url",
                "https://mcp.sentry.example/mcp",
                check=False,
            )
            self.assertNotEqual(0, refused.returncode)
            self.assertIn("FSL-1.1-Apache-2.0", refused.stderr)

            accepted = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "sentry-mcp",
                "--url",
                "https://mcp.sentry.example/mcp",
                "--accept-license",
                "FSL-1.1-Apache-2.0",
            )
            self.assertEqual(0, accepted.returncode)
            manifest = json.loads(
                (target / "docs/ai/capabilities.json").read_text(encoding="utf-8")
            )
            self.assertEqual("source-available", manifest["capabilities"][0]["license_kind"])

    def test_installer_respects_project_declared_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            source = root / "skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: systematic-debugging\ndescription: Debug systematically.\n---\n",
                encoding="utf-8",
            )
            self.initialize(target)
            manifest_path = target / "docs/ai/capabilities.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skill_directory"] = ".claude/skills"
            manifest["mcp_config"] = ".claude/mcp.toml"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(source),
            )
            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "npx",
                "--arg=@upstash/context7-mcp",
            )

            self.assertTrue((target / ".claude/skills/systematic-debugging/SKILL.md").is_file())
            self.assertTrue((target / ".claude/mcp.toml").is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            entries = {item["id"]: item for item in manifest["capabilities"]}
            self.assertEqual(
                ".claude/skills/systematic-debugging",
                entries["superpowers"]["selected_skills"][0]["installed_path"],
            )
            self.assertEqual(".claude/mcp.toml", entries["context7"]["config_path"])

            validated = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json"
            )
            payload = json.loads(validated.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertFalse(
                any(item["code"] == "capability-path-invalid" for item in payload["findings"])
            )

    def test_installer_rejects_unsafe_declared_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)
            manifest_path = target / "docs/ai/capabilities.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["mcp_config"] = "../outside.toml"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            refused = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "npx",
                "--arg=@upstash/context7-mcp",
                check=False,
            )

            self.assertNotEqual(0, refused.returncode)
            self.assertFalse(Path(tmp, "outside.toml").exists())

    def test_installer_rejects_a_missing_declared_path_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)
            manifest_path = target / "docs/ai/capabilities.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop("skill_directory")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            refused = self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(tmp),
                check=False,
            )

            self.assertNotEqual(0, refused.returncode)
            self.assertFalse((target / ".agents/skills/systematic-debugging").exists())

    def test_validator_rejects_non_project_scope_and_lock_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.initialize(target)
            manifest_path = target / "docs/ai/capabilities.json"
            lock_path = target / "docs/ai/capabilities.lock.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["default_scope"] = "global"
            manifest["capabilities"] = [
                {
                    "id": "context7",
                    "type": "mcp-server",
                    "scope": "global",
                    "state": {
                        "installed": False,
                        "enabled": False,
                        "configured": False,
                        "verified": False,
                    },
                }
            ]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            lock_path.write_text(
                json.dumps({"schema_version": 1, "scope": "project", "capabilities": []}),
                encoding="utf-8",
            )

            result = self.run_script(
                VALIDATE_SCRIPT,
                "--target",
                str(target),
                "--format",
                "json",
                check=False,
            )
            payload = json.loads(result.stdout)
            codes = {item["code"] for item in payload["findings"]}
            self.assertIn("capability-scope-invalid", codes)
            self.assertIn("capability-lock-drift", codes)


    def test_validator_detects_skill_content_and_mcp_config_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            source = root / "skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: systematic-debugging\ndescription: Debug systematically.\n---\n",
                encoding="utf-8",
            )
            self.initialize(target)
            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(source),
            )
            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "context7",
                "--command",
                "npx",
                "--arg=@upstash/context7-mcp",
            )

            baseline = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json"
            )
            self.assertEqual("pass", json.loads(baseline.stdout)["status"])

            skill_md = target / ".agents/skills/systematic-debugging/SKILL.md"
            original_skill = skill_md.read_text(encoding="utf-8")
            skill_md.write_text(original_skill + "tampered\n", encoding="utf-8")
            skill_drift = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            self.assertIn(
                "capability-hash-mismatch",
                {item["code"] for item in json.loads(skill_drift.stdout)["findings"]},
            )
            skill_md.write_text(original_skill, encoding="utf-8")

            config = target / ".codex/config.toml"
            original_config = config.read_text(encoding="utf-8")
            config.write_text(
                original_config.replace("enabled = false", "enabled = true"),
                encoding="utf-8",
            )
            config_drift = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            self.assertIn(
                "capability-hash-mismatch",
                {item["code"] for item in json.loads(config_drift.stdout)["findings"]},
            )

            config.write_text("user-owned config\n", encoding="utf-8")
            block_missing = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json", check=False
            )
            self.assertIn(
                "capability-config-drift",
                {item["code"] for item in json.loads(block_missing.stdout)["findings"]},
            )

    def test_validator_warns_when_lock_hashes_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            source = root / "skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(
                "---\nname: systematic-debugging\ndescription: Debug systematically.\n---\n",
                encoding="utf-8",
            )
            self.initialize(target)
            self.run_script(
                INSTALL_SCRIPT,
                "--target",
                str(target),
                "--id",
                "superpowers",
                "--skill",
                "systematic-debugging",
                "--source-dir",
                str(source),
            )
            lock_path = target / "docs/ai/capabilities.lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["capabilities"][0]["selected_skills"][0].pop("content_sha256")
            lock_path.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")

            result = self.run_script(
                VALIDATE_SCRIPT, "--target", str(target), "--format", "json"
            )
            payload = json.loads(result.stdout)

            self.assertEqual("pass", payload["status"])
            self.assertTrue(
                any(item["code"] == "capability-hash-missing" for item in payload["findings"])
            )


if __name__ == "__main__":
    unittest.main()
