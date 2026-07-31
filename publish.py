"""把產生好的 dashboard.html 發布到 GitHub Pages（gh-pages 分支）。
每天覆蓋同一個 commit（--amend + force push），避免 repo 體積隨時間膨脹。
"""
import logging
import shutil
import subprocess

from config import DASHBOARD_HTML_PATH, PAGES_WORKTREE_DIR, PAGES_BRANCH

logger = logging.getLogger(__name__)


def _run_git(args: list[str]):
    result = subprocess.run(
        ["git", *args], cwd=PAGES_WORKTREE_DIR, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout


def publish_dashboard(date_str: str):
    if not PAGES_WORKTREE_DIR.exists():
        logger.warning("找不到 %s，略過發布（請先執行 git worktree add）", PAGES_WORKTREE_DIR)
        return
    if not DASHBOARD_HTML_PATH.exists():
        logger.warning("找不到儀表板檔案 %s，略過發布", DASHBOARD_HTML_PATH)
        return

    dest = PAGES_WORKTREE_DIR / "index.html"
    shutil.copyfile(DASHBOARD_HTML_PATH, dest)

    status = _run_git(["status", "--porcelain"])
    if not status.strip():
        logger.info("儀表板內容沒有變化，略過發布")
        return

    _run_git(["add", "index.html"])
    _run_git(["commit", "--amend", "-q", "-m", f"Dashboard update {date_str}"])
    _run_git(["push", "--force", "origin", PAGES_BRANCH])
    logger.info("已發布到 GitHub Pages（%s）", date_str)
