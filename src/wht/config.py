import json
from pathlib import Path
from typing import Dict, Any

# Define core paths
CONFIG_DIR = Path.home() / ".config" / "wht"
REPO_DIR = CONFIG_DIR / "repo"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "repo_url": "",          # The GitHub repo containing the markdown snippets
    "default_shell": "bash", # 'bash', 'pwsh', or 'cmd'
    "usage_weights": {}      # Tracks execution frequency for search ranking
}

def init_dirs() -> None:
    """Ensure the base configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict[str, Any]:
    """
    Load the configuration file. 
    Creates a default config if one does not exist or is corrupted.
    """
    init_dirs()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge defaults to handle upgrades where new keys are added
            return {**DEFAULT_CONFIG, **config}
    except json.JSONDecodeError:
        # If the file is somehow corrupted, fallback to default
        return DEFAULT_CONFIG

def save_config(config_data: Dict[str, Any]) -> None:
    """Save the configuration dictionary to disk as JSON."""
    init_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)