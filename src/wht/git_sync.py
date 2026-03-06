import subprocess
import sys
from pathlib import Path
from . import config

def _run_git_command(args: list[str], cwd: Path | None = None) -> bool:
    """Helper to run git commands and handle standard errors."""
    try:
        subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except FileNotFoundError:
        print("Error: 'git' is not installed or not in your system PATH.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr.strip()}", file=sys.stderr)
        return False

def sync() -> bool:
    """Clones the snippet repository or pulls the latest changes if it exists."""
    cfg = config.load_config()
    repo_url = cfg.get("repo_url")

    if not repo_url:
        print("Error: No repository URL configured. Set it first using 'wht config'.", file=sys.stderr)
        return False

    repo_dir = config.REPO_DIR

    # Check if the directory exists and is a git repository
    if repo_dir.exists() and (repo_dir / ".git").exists():
        return _run_git_command(["pull", "--rebase"], cwd=repo_dir)
    else:
        # If it doesn't exist, create the base directory and clone
        config.init_dirs()
        return _run_git_command(["clone", repo_url, str(repo_dir)])