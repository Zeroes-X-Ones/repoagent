import os
import subprocess
import time

import requests

from analytics.service import analytics_service
from utils.model_router import planner_model
from utils.logger import get_logger

logger = get_logger("pr_agent")


def _get_git_diff(repo_path: str) -> str:
    """Return the commit diff stat for the most recent commit."""

    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "HEAD~1", "HEAD", "--stat"],
            capture_output=True,
            text=True,
            timeout=15
        )
        diff = result.stdout.strip()
        return diff[:4000] if diff else "No diff available"
    except Exception as e:
        return f"Diff unavailable: {e}"


def _generate_pr_summary(diff: str, task: str, test_results: dict) -> str:
    """Use LLM to write a rich, structured PR description."""

    test_section = ""
    if test_results:
        lines = []
        for f, r in test_results.items():
            lines.append(f"- `{f}`: **{r.get('status', 'unknown')}**")
        test_section = "### Test Results\n" + "\n".join(lines)

    prompt = f"""You are a senior software engineer writing a GitHub Pull Request description.

The AI engineer agent performed this task:
{task}

Git diff summary:
{diff}

{test_section}

Write a professional Pull Request description in Markdown with these sections:
## Summary
## Changes Made
## Testing
## Notes

Be concise and technical.
"""

    start_time = time.perf_counter()
    execution_status = "success"
    quality_score = 0.0
    try:
        response = planner_model(prompt)
        quality_score = 1.0 if response.strip() else 0.0
        return response
    except Exception as e:
        logger.error("PR summary generation failed: %s", e)
        execution_status = "error"
        return f"Automated PR by AI Engineer agent.\n\nTask: {task}"
    finally:
        analytics_service.record_request(
            repository=os.getenv("REPO_NAME", "unknown"),
            user_prompt=task,
            selected_files=[],
            total_files=0,
            model=os.getenv("OPENROUTER_PLANNER_MODEL", "anthropic/claude-3.7-sonnet"),
            provider=os.getenv("LLM_PROVIDER", "openrouter"),
            quality_score=quality_score,
            execution_status=execution_status,
            latency_ms=(time.perf_counter() - start_time) * 1000,
        )


def pr_agent_node(state):

    logger.info("PR Agent running")

    repo_url     = state["repo_url"]
    repo_path    = state.get("repo_path", "./workspace/repo")
    branch       = state.get("branch_name")
    task         = state.get("plan", {}).get("task", state.get("user_prompt", ""))
    test_results = state.get("test_results", {})

    if not branch:
        logger.warning("No branch found — skipping PR creation")
        return state

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        logger.warning("No GITHUB_TOKEN found — skipping PR creation")
        return state

    repo = repo_url.replace("https://github.com/", "").replace(".git", "")

    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github+json"
    }

    # Detect the actual default branch (avoids hardcoding main vs master)
    try:
        repo_info      = requests.get(
            f"https://api.github.com/repos/{repo}", headers=headers
        )
        default_branch = repo_info.json().get("default_branch", "main")
    except Exception:
        default_branch = "main"

    # Build rich PR body with git diff and test results
    diff    = _get_git_diff(repo_path)
    pr_body = _generate_pr_summary(diff, task, test_results)

    data = {
        "title": f"AI Engineer: {task[:72]}",
        "body":  pr_body,
        "head":  branch,
        "base":  default_branch
    }

    try:

        response = requests.post(
            f"https://api.github.com/repos/{repo}/pulls",
            json=data,
            headers=headers
        )

        if response.status_code == 201:

            pr_url = response.json()["html_url"]
            logger.info("Pull Request created: %s", pr_url)
            state["pr_url"] = pr_url

        else:

            logger.error("PR creation failed: %s", response.text)

    except Exception as e:

        logger.exception("PR error: %s", e)

    return state
