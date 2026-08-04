import os
import subprocess
import sys
import tempfile
import time

from analytics.service import analytics_service
from utils.model_router import coder_model
from utils.logger import get_logger

logger = get_logger("tester")


def _generate_tests(file_path: str, task: str) -> str:

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return ""

    prompt = f"""You are an expert Python test engineer.

Write pytest unit tests for the following modified file.
The task that was applied is: {task}

Focus on testing the functions that were likely affected by the task.
Use mocks where needed for external dependencies.

FILE: {file_path}

CODE:
{source[:3000]}

Return ONLY valid pytest code. No explanation. No markdown wrapper.
"""

    start_time = time.perf_counter()
    execution_status = "success"
    quality_score = 0.0
    try:
        response = coder_model(prompt)
        quality_score = 1.0 if response.strip() else 0.0
        return response
    except Exception as e:
        logger.error("Test generation failed for %s: %s", file_path, e)
        execution_status = "error"
        return ""
    finally:
        analytics_service.record_request(
            repository=os.getenv("REPO_NAME", "unknown"),
            user_prompt=task,
            selected_files=[file_path],
            total_files=1,
            model=os.getenv("OPENROUTER_CODER_MODEL", "anthropic/claude-3.7-sonnet"),
            provider=os.getenv("LLM_PROVIDER", "openrouter"),
            quality_score=quality_score,
            execution_status=execution_status,
            latency_ms=(time.perf_counter() - start_time) * 1000,
        )


def tester_node(state):

    logger.info("Tester Agent running")

    edited_files = state.get("edited_files", [])
    plan         = state.get("plan", {})
    task         = plan.get("task", "")

    if not edited_files:
        logger.warning("No edited files — skipping test generation")
        state["tests_passed"] = True
        state["test_results"] = {}
        return state

    test_results = {}
    all_passed   = True

    for file_path in edited_files:

        logger.info("Generating tests for: %s", file_path)

        test_code = _generate_tests(file_path, task)

        if not test_code.strip():
            logger.warning("No test code generated for %s", file_path)
            test_results[file_path] = {"status": "skipped", "output": ""}
            continue

        # Write test to a temp file and run pytest
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix="_test.py",
            prefix="ai_agent_",
            delete=False,
            encoding="utf-8"
        ) as tmp:
            tmp.write(test_code)
            tmp_path = tmp.name

        try:

            result = subprocess.run(
                [sys.executable, "-m", "pytest", tmp_path, "-v", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )

            passed = result.returncode == 0

            if passed:
                logger.info("Tests PASSED for %s", file_path)
            else:
                logger.warning("Tests FAILED for %s:\n%s", file_path, result.stdout[-1500:])
                all_passed = False

            test_results[file_path] = {
                "status": "passed" if passed else "failed",
                "output": result.stdout[-2000:]
            }

        except subprocess.TimeoutExpired:

            logger.error("Test timed out for %s", file_path)
            test_results[file_path] = {"status": "timeout", "output": ""}
            all_passed = False

        finally:

            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    state["test_results"] = test_results
    state["tests_passed"] = all_passed

    return state
