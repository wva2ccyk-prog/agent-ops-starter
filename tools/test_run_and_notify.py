import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_and_notify


class CompletionNotificationTests(unittest.TestCase):
    def run_case(self, command, queue_outcome=0):
        with tempfile.TemporaryDirectory(prefix="codex completion ") as directory:
            output_dir = Path(directory) / "job with spaces"
            real_run = subprocess.run
            notifications = []

            def run_command(arguments, **kwargs):
                if arguments[0] != "fake-codex":
                    return real_run(arguments, **kwargs)
                saved_result = json.loads((output_dir / "result.json").read_text(encoding="utf-8"))
                self.assertIn("finished_at", saved_result)
                notifications.append(arguments)
                if isinstance(queue_outcome, Exception):
                    raise queue_outcome
                return subprocess.CompletedProcess(arguments, queue_outcome, "queued", "queue diagnostic")

            arguments = ["helper", "--thread", "test-thread", "--codex-bin", "fake-codex", "--output-dir", str(output_dir), "--", *command]
            with patch.object(sys, "argv", arguments), patch.object(subprocess, "run", side_effect=run_command), contextlib.redirect_stdout(io.StringIO()):
                status = run_and_notify.main()
            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0][1:4], ["queue", "--thread", "test-thread"])
            self.assertIn(str(output_dir / "result.json"), notifications[0][-1])
            return (
                status,
                json.loads((output_dir / "result.json").read_text(encoding="utf-8")),
                json.loads((output_dir / "notification.json").read_text(encoding="utf-8")),
                (output_dir / "stdout.log").read_text(encoding="utf-8"),
                (output_dir / "stderr.log").read_text(encoding="utf-8"),
            )

    def test_success_saves_result_before_one_notification(self):
        status, result, notification, stdout, stderr = self.run_case([sys.executable, "-c", "print('OK 42')"])
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (0, 0, 0))
        self.assertEqual((stdout, stderr), ("OK 42\n", ""))

    def test_failed_job_still_notifies(self):
        status, result, notification, stdout, stderr = self.run_case([sys.executable, "-c", "import sys; print('failed', file=sys.stderr); sys.exit(7)"])
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (1, 7, 0))
        self.assertEqual(stderr, "failed\n")

    def test_job_launch_failure_still_notifies(self):
        missing_command = str(Path(tempfile.gettempdir()) / "codex-not-a-real-command" / "missing")
        status, result, notification, stdout, stderr = self.run_case([missing_command])
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (1, 127, 0))
        self.assertIn("launch_error", result)

    def test_failed_queue_preserves_job_result(self):
        status, result, notification, stdout, stderr = self.run_case([sys.executable, "-c", "print('saved')"], 9)
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (1, 0, 9))
        self.assertEqual(notification["stderr"], "queue diagnostic")
        self.assertEqual(stdout, "saved\n")

    def test_queue_timeout_does_not_retry(self):
        status, result, notification, stdout, stderr = self.run_case([sys.executable, "-c", "print('saved')"], subprocess.TimeoutExpired("queue", 30))
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (1, 0, 1))
        self.assertIn("error", notification)

    def test_missing_queue_binary_does_not_retry(self):
        status, result, notification, stdout, stderr = self.run_case([sys.executable, "-c", "print('saved')"], FileNotFoundError("codex unavailable"))
        self.assertEqual((status, result["exit_code"], notification["exit_code"]), (1, 0, 1))
        self.assertIn("codex unavailable", notification["error"])

    def test_existing_directory_prevents_job_and_notification(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = ["helper", "--thread", "test-thread", "--output-dir", directory, "--", sys.executable, "-c", "print('must not run')"]
            with patch.object(sys, "argv", arguments), patch.object(subprocess, "run") as process_mock:
                with self.assertRaises(FileExistsError):
                    run_and_notify.main()
                process_mock.assert_not_called()

    def test_missing_thread_prevents_job_and_notification(self):
        arguments = ["helper", "--output-dir", "unused", "--", "unused-command"]
        with patch.dict("os.environ", {}, clear=True), patch.object(sys, "argv", arguments), patch.object(subprocess, "run") as process_mock, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:
                run_and_notify.main()
            self.assertEqual(failure.exception.code, 2)
            process_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
