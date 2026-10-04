"""Exercise deployment ordering and failure handling without Docker or a VPS."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class DeploymentTests(unittest.TestCase):
    def run_deploy(self, failure=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(Path(__file__).with_name("deploy.sh"), root / "deploy.sh")
            (root / ".env.staging").touch()
            log = root / "calls"
            stub = '#!/bin/bash\nprintf "%s\\n" "$*" >> "$DEPLOY_TEST_LOG"\nif [[ -n "$DEPLOY_TEST_FAIL" && "$*" == *"$DEPLOY_TEST_FAIL"* ]]; then exit 1; fi\n'
            for name in ("docker", "curl"):
                command = root / name
                command.write_text(stub)
                command.chmod(0o755)
            result = subprocess.run(
                ["bash", str(root / "deploy.sh")], capture_output=True, text=True,
                env={**os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                     "DEPLOY_TEST_LOG": str(log), "DEPLOY_TEST_FAIL": failure},
            )
            return result, log.read_text()

    def test_successful_sequence(self):
        result, calls = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        steps = ["config --quiet", "build --pull", "--wait-timeout 120 db",
                 "alembic upgrade head", "seed --missing-only", "--wait-timeout 180",
                 "exec -T backend", "https://rubennmg.cloud/games/",
                 "https://api.rubennmg.cloud/api/health/db"]
        offsets = [calls.index(step) for step in steps]
        self.assertEqual(offsets, sorted(offsets))

    def test_failure_stops_before_replacement(self):
        for step in ("build --pull", "--wait-timeout 120 db", "alembic upgrade head", "seed --missing-only"):
            with self.subTest(step=step):
                result, calls = self.run_deploy(step)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("--wait-timeout 180", calls)

    def test_unhealthy_service_or_public_endpoint_fails_deployment(self):
        for step in ("--wait-timeout 180", "exec -T backend", "https://rubennmg.cloud/games/"):
            with self.subTest(step=step):
                result, _ = self.run_deploy(step)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Staging deployment verified", result.stdout)


if __name__ == "__main__":
    unittest.main()
