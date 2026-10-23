import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run one command and queue one completion notification.")
    parser.add_argument("--thread", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not args.thread or not command:
        parser.error("a target thread and command are required")
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    result = {"started_at": timestamp(), "thread": args.thread, "command": command}
    with (output_dir / "stdout.log").open("w", encoding="utf-8") as stdout_log, (output_dir / "stderr.log").open("w", encoding="utf-8") as stderr_log:
        try:
            completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout_log, stderr=stderr_log)
            result["exit_code"] = completed.returncode
        except OSError as error:
            result["exit_code"] = 127
            result["launch_error"] = str(error)
    result["finished_at"] = timestamp()
    result_path = output_dir / "result.json"
    save_json(result_path, result)
    message = (
        f"CODEX_JOB_COMPLETED: exit_code={result['exit_code']}; result={result_path}. "
        "Read this result and its logs once, then continue the authorized task. "
        "This notification is not a request to rerun the job."
    )
    notification = {"attempted_at": timestamp()}
    try:
        queued = subprocess.run(
            [args.codex_bin, "queue", "--thread", args.thread, "--message", message],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        notification.update(exit_code=queued.returncode, stdout=queued.stdout, stderr=queued.stderr)
    except (OSError, subprocess.TimeoutExpired) as error:
        notification.update(exit_code=1, error=str(error))
    save_json(output_dir / "notification.json", notification)
    print(json.dumps({"result": str(result_path), "job_exit_code": result["exit_code"], "queue_exit_code": notification["exit_code"]}))
    if notification["exit_code"]:
        return 1
    return 0 if result["exit_code"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
