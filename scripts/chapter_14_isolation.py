"""Run the Chapter 14 Docker isolation probe.

The deterministic example and tests are the portable acceptance path. This
script is the optional host-level probe described in the manuscript. It builds
a tiny local image, runs it with the chapter's Docker restrictions, and feeds
each observed result back through the same artifact-admission function.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from orders_investigation.runtime.sandbox import (
    ExecutorResult,
    admit_execution,
    make_request,
)


IMAGE = "engineering-agentic-ai-chapter-14:local"


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, check=False, capture_output=True, **kwargs)


def main() -> None:
    if shutil.which("docker") is None or run(["docker", "info"]).returncode:
        raise SystemExit(
            "Docker is unavailable. The offline demo and tests remain runnable; "
            "run this optional probe on a Docker-capable host."
        )

    request = make_request(b"analysis code", b"evidence bundle")
    with tempfile.TemporaryDirectory(prefix="chapter-14-") as temporary:
        root = Path(temporary)
        (root / "input").mkdir()
        (root / "output").mkdir()
        (root / "input" / "evidence.json").write_text('{"writer_pressure":"high"}')
        (root / "Dockerfile").write_text(
            "FROM python:3.12-alpine\n"
            "RUN adduser -D -u 10001 sandbox\n"
            "USER sandbox\n"
            "COPY runner.py /runner.py\n"
            "ENTRYPOINT [\"python\", \"/runner.py\"]\n"
        )
        (root / "runner.py").write_text(
            "import json, pathlib, socket, sys, time\n"
            "mode, output, request_digest, input_sha, image_digest = sys.argv[1:]\n"
            "if mode == 'network':\n"
            "    socket.create_connection(('example.com', 443), timeout=1)\n"
            "elif mode == 'outside':\n"
            "    pathlib.Path('/work/secret.txt').read_text()\n"
            "elif mode == 'nonzero':\n"
            "    raise SystemExit(7)\n"
            "elif mode == 'timeout':\n"
            "    time.sleep(5)\n"
            "elif mode == 'oversized':\n"
            "    pathlib.Path(output).write_bytes(b'x' * 16385)\n"
            "elif mode == 'invalid':\n"
            "    pathlib.Path(output).write_text('{\"findings\":[]}')\n"
            "else:\n"
            "    pathlib.Path(output).write_text(json.dumps({\n"
            "      'analysis_id':'compare-writer-pressure',\n"
            "      'artifact_schema':'diagnostic-artifact/v1',\n"
            "      'request_digest':request_digest,\n"
            "      'input_sha256':input_sha,\n"
            "      'image_digest':image_digest,\n"
            "      'findings':['Writer pressure rises after the migration starts.']}))\n"
        )
        built = run(["docker", "build", "-t", IMAGE, str(root)])
        if built.returncode:
            raise SystemExit(built.stderr.decode(errors="replace"))
        image_digest = run(
            ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"]
        ).stdout.decode().strip()

        for mode in (
            "success",
            "network",
            "outside",
            "nonzero",
            "timeout",
            "oversized",
            "invalid",
        ):
            output = root / "output" / "artifact.json"
            output.unlink(missing_ok=True)
            command = [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--memory",
                "256m",
                "--cpus",
                "0.5",
                "--mount",
                f"type=bind,src={root / 'input'},dst=/work/input,readonly",
                "--mount",
                f"type=bind,src={root / 'output'},dst=/work/output",
                IMAGE,
                mode,
                "/work/output/artifact.json",
                request.digest,
                request.input_sha256,
                image_digest,
            ]
            try:
                observed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    timeout=2 if mode == "timeout" else 15,
                )
                result = ExecutorResult(
                    observed.returncode,
                    network_denied=mode == "network" and observed.returncode != 0,
                    input_denied=mode == "outside" and observed.returncode != 0,
                    artifact_bytes=output.read_bytes() if output.exists() else b"",
                )
            except subprocess.TimeoutExpired:
                result = ExecutorResult(None, timed_out=True)
            decision = admit_execution(result, request, image_digest=image_digest)
            print(mode, decision.outcome.value, decision.detail)


if __name__ == "__main__":
    main()
