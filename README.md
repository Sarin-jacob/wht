# wht

`wht` is a lightning-fast, Python-based CLI utility that turns a structured GitHub repository of Markdown files into an interactive, searchable library of scripts. Designed for speed and minimal friction, it features clipboard integration, automatic shell script minification, and ephemeral Python execution via `uv`.

---

## Features

* **Interactive Search:** Fuzzy search by title, tags, or content with an arrow-key menu interface.
* **Smart Ranking:** Tracks frequently used snippets and automatically boosts them to the top of your search results.
* **Auto-Shell Detection:** Detects your active shell (Bash, Zsh, PowerShell, CMD) to prioritize the correct code block.
* **One-Lineifier:** Automatically strips comments and joins shell commands with the appropriate separators for instant copy-pasting.
* **Ephemeral Python Execution:** Generates temporary, PEP 723-compliant scripts and executes them on the fly using `uv run`.

---

## Installation

`wht` is built to be distributed and run using `uv`.

To install globally from your local project directory:

```bash
uv tool install .
```

To install directly from a Git repository (once published):

```bash
uv tool install git+https://github.com/Sarin-jacob/wht.git
```

---

## Quick Start

1. **Configure your repository**
Set the URL to your Markdown snippet repository and your default shell:
```bash
wht config
```


2. **Sync your snippets**
Pull down the latest files to your local cache (`~/.config/wht/`):
```bash
wht sync
```


3. **Find and view**
Search for a snippet and print it to the terminal with syntax highlighting:
```bash
wht find yaml
```


4. **Get and execute**
Search for a snippet and either copy the minified shell command to your clipboard or instantly run the Python code:
```bash
wht get "nb2md"
```

---

## The Markdown Schema

`wht` relies on a simple, readable Markdown structure. Group your snippets by functional domain (e.g., `networking.md`, `docker.md`).

Use standard `##` headings for titles, inline code block backticks for tags, and `###` headings to specify the target environment.

### Example File

```markdown
## Convert Jupyter to Markdown
`jupyter` `nb2md` `converter`
Quick shell command to invoke the nb2md utility.

---
### bash
 ```bash
uvx nb2md notebook.ipynb
``

## Outline Sync Backup

`docker` `outline` `backup`
Triggers the custom Outline to Git sync container.

---

### bash

```bash
docker run --rm -v ~/.outline-backup:/data outline-sync-tool:latest
``
### pwsh

```powershell
docker run --rm -v ~/.outline-backup:/data outline-sync-tool:latest
``

## Convert YAML to Table

`yaml` `python` `cli`
Reads a local data file and prints it as a formatted console table.

---

### python

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "rich"]
# ///
import yaml
from rich.console import Console
from rich.table import Table

with open("data.yaml", "r") as f:
    data = yaml.safe_load(f)

# ... table logic ...

``

```

---

## Command Reference

| Command | Argument | Description |
|:--------|:---------|:------------|
| `wht find` | `<query>` | Interactive search; prints selection to terminal. |
| `wht get` | `<query>` | Interactive search; copies one-liner or runs Python file. |
| `wht sync` | *(none)* | Forces a `git pull` on the local snippet repository. |
| `wht config` | *(none)* | Set the GitHub Repository URL and default shell preference. |

---
