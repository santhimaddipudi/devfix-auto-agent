import subprocess
import tempfile
import os
import sys


def _run_with_docker(temp_file: str) -> tuple[bool, str]:
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{temp_file}:/tmp/code.py",
        "-m", "512m",
        "--cpu-quota", "50000",
        "python:3.12-slim",
        "sh", "-c",
        "pip install pytest -q && python -m pytest /tmp/code.py -q --tb=short"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    output = result.stdout.strip()
    if result.stderr:
        output += "\n" + result.stderr.strip()
    output_lines = [l for l in output.split('\n')
                    if 'ev_poll_posix.cc' not in l and 'FD from fork parent' not in l]
    clean_output = '\n'.join(output_lines).strip()
    success = "passed" in clean_output and "failed" not in clean_output
    return success, clean_output


def _run_directly(temp_file: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", temp_file, "-q", "--tb=short"],
        capture_output=True, text=True, timeout=30
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    success = "passed" in output and "failed" not in output
    return success, output


def execute_code_in_docker(code: str) -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            try:
                return _run_with_docker(temp_file)
            except FileNotFoundError:
                return _run_directly(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        return False, "Execution timeout"
    except Exception as e:
        return False, str(e)
