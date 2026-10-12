"""Exercise deployment ordering and failure handling without Docker or a VPS."""
import os
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class DeploymentTests(unittest.TestCase):
    def run_deploy(self, failure="", environment="staging", extra=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(Path(__file__).with_name("deploy.sh"), root / "deploy.sh")
            (root / environment).mkdir()
            (root / environment / f".env.{environment}").touch()
            log = root / "calls"
            stub = '#!/bin/bash\nprintf "%s\\n" "$*" >> "$DEPLOY_TEST_LOG"\nif [[ -n "$DEPLOY_TEST_FAIL" && "$*" == *"$DEPLOY_TEST_FAIL"* ]]; then exit 1; fi\n'
            for name in ("docker", "curl"):
                command = root / name
                command.write_text(stub)
                command.chmod(0o755)
            result = subprocess.run(
                ["bash", str(root / "deploy.sh"), environment, *extra], capture_output=True, text=True,
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
                 "https://rubennmg.cloud/api/health/db"]
        offsets = [calls.index(step) for step in steps]
        self.assertEqual(offsets, sorted(offsets))

    def test_failure_stops_before_replacement(self):
        for step in ("volume inspect", "network inspect", "build --pull", "--wait-timeout 120 db", "alembic upgrade head", "seed --missing-only"):
            with self.subTest(step=step):
                result, calls = self.run_deploy(step)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("--wait-timeout 180", calls)

    def test_unhealthy_service_or_public_endpoint_fails_deployment(self):
        for step in ("--wait-timeout 180", "exec -T backend", "https://rubennmg.cloud/games/"):
            with self.subTest(step=step):
                result, _ = self.run_deploy(step)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("staging deployment verified", result.stdout)

    def test_production_targets_only_production(self):
        result, calls = self.run_deploy(environment="production")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-p rubennmg-production --env-file .env.production", calls)
        self.assertIn("https://rubennmg.com/api/health/db", calls)
        self.assertNotIn("staging", calls)

    def test_staging_targets_only_staging(self):
        result, calls = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-p staging --env-file .env.staging", calls)
        self.assertNotIn("production", calls)

    def test_no_proxy_or_destructive_cleanup(self):
        for env in ("staging", "production"):
            _, calls = self.run_deploy(environment=env)
            for forbidden in ("caddy", "proxy", "down", "prune", "volume rm", "remove-orphans"):
                self.assertNotIn(forbidden, calls)

    def test_bootstrap_can_skip_only_public_checks(self):
        result, calls = self.run_deploy(extra=("--skip-public-checks",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("alembic upgrade head", calls)
        self.assertIn("exec -T backend", calls)
        self.assertNotIn("https://", calls)
        self.assertNotIn("deployment verified", result.stdout)


class ComposeIsolationTests(unittest.TestCase):
    def test_only_proxy_publishes_ports(self):
        path = Path(__file__).parent.resolve() / "proxy/compose.yml"
        config = json.loads(subprocess.check_output([
            "docker", "compose", "-f", str(path), "config", "--format", "json",
        ], text=True))
        self.assertEqual(config["name"], "rubennmg-proxy")
        self.assertEqual(set(config["services"]), {"caddy"})
        self.assertEqual({port["published"] for port in config["services"]["caddy"]["ports"]}, {"80", "443"})
        self.assertEqual({network["name"] for network in config["networks"].values()},
                         {"rubennmg_staging_web", "rubennmg_production_web"})

    def test_resolved_stacks_are_isolated(self):
        infra = Path(__file__).parent.resolve()
        configs = {}
        for env, project in (("staging", "staging"), ("production", "rubennmg-production")):
            configs[env] = config = json.loads(subprocess.check_output([
                "docker", "compose", "--env-file", str(infra / env / f".env.{env}.example"),
                "-f", str(infra / env / "compose.yml"), "config", "--format", "json",
            ], text=True))
            self.assertEqual(config["name"], project)
            self.assertEqual(set(config["services"]), {"frontend", "backend", "db"})
            for service in config["services"].values():
                self.assertFalse(service.get("ports"))
                self.assertNotIn("container_name", service)
            self.assertEqual(set(config["services"]["db"]["networks"]), {"internal"})
            self.assertTrue(config["networks"]["internal"]["internal"])
            self.assertEqual(config["services"]["backend"]["environment"]["APP_ENV"], env)
            self.assertTrue(config["services"]["backend"]["environment"]["DATABASE_URL"].endswith(f"@db:5432/rubennmg_{env}"))
            self.assertEqual(config["services"]["frontend"]["build"]["args"]["PUBLIC_API_URL"], "")
            self.assertEqual(config["services"]["backend"]["build"]["context"], str(infra.parent / "apps/backend"))
            self.assertTrue(config["volumes"]["postgres_data"]["external"])
        for kind in ("volumes", "networks"):
            staging = {item["name"] for item in configs["staging"][kind].values()}
            production = {item["name"] for item in configs["production"][kind].values()}
            self.assertFalse(staging & production)


class RemoteDeploymentTests(unittest.TestCase):
    def run_remote(self, environment, stale=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = Path(__file__).with_name("remote-deploy.sh").read_text()
            for path in ("/home/deploy/apps/rubennmg.com", "/home/deploy/apps/rubennmg-production"):
                target = root / Path(path).name
                target.mkdir()
                script = script.replace(path, str(target))
            (root / "remote.sh").write_text(script)
            log = root / "calls"
            for command in ("git", "bash"):
                stub = root / command
                stub.write_text('#!/bin/bash\nprintf "%s %s %s\\n" "$PWD" "${0##*/}" "$*" >> "$DEPLOY_TEST_LOG"\nif [[ "$1" == rev-parse ]]; then printf "%s\\n" "$TEST_HEAD"; fi\n')
                stub.chmod(0o755)
            result = subprocess.run(["/bin/bash", str(root / "remote.sh"), environment, "a" * 40],
                text=True, capture_output=True, env={**os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                    "DEPLOY_TEST_LOG": str(log), "TEST_HEAD": ("b" if stale else "a") * 40})
            return result, log.read_text()

    def test_each_branch_updates_its_own_checkout(self):
        for env, branch, checkout in (("staging", "develop", "rubennmg.com"), ("production", "main", "rubennmg-production")):
            result, calls = self.run_remote(env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"git fetch origin {branch}", calls)
            self.assertIn(f"bash infra/{env}/deploy.sh", calls)
            self.assertTrue(all(checkout in line.split()[0] for line in calls.splitlines()))

    def test_superseded_commit_does_not_deploy(self):
        result, calls = self.run_remote("production", stale=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("checkout --detach", calls)
        self.assertNotIn("bash infra/", calls)
        self.assertNotIn("DEPLOYED_SHA=", result.stdout)


if __name__ == "__main__":
    unittest.main()
