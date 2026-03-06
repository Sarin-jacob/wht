import os
import secrets
import subprocess
from pathlib import Path
from typing import Optional

import pyperclip
import questionary
import typer
from rich.console import Console
from rich.syntax import Syntax

from . import config, git_sync, parser, transformers

app = typer.Typer(help="wht - The lightning-fast snippet library and executor.")
console = Console()

def _update_weight(title: str):
    """Increments the usage count for a snippet to boost future search rankings."""
    cfg = config.load_config()
    weights = cfg.get("usage_weights", {})
    weights[title] = weights.get(title, 0) + 1
    cfg["usage_weights"] = weights
    config.save_config(cfg)

def _search_and_select(query: str) -> Optional[parser.Snippet]:
    """Handles the fuzzy search, weighting, and interactive selection."""
    all_snippets = parser.load_all_snippets()
    if not all_snippets:
        console.print("[red]No snippets found. Did you run `wht sync`?[/red]")
        raise typer.Exit(1)

    # 1. Fuzzy Search
    query_lower = query.lower()
    matches = [s for s in all_snippets if query_lower in s.searchable_text]

    if not matches:
        console.print(f"[yellow]No snippets found matching '{query}'.[/yellow]")
        raise typer.Exit(1)

    # 2. Weight-based Ranking
    cfg = config.load_config()
    weights = cfg.get("usage_weights", {})
    matches.sort(key=lambda s: weights.get(s.title, 0), reverse=True)

    # 3. Interactive Selection
    if len(matches) == 1:
        return matches[0]

    choices = [f"{s.title} ({s.file_source})" for s in matches]
    selection_str = questionary.select(
        "Multiple matches found. Select a snippet:",
        choices=choices
    ).ask()

    if not selection_str:
        raise typer.Exit() # User hit Ctrl+C

    # Find the original object based on the selection string
    for s in matches:
        if f"{s.title} ({s.file_source})" == selection_str:
            return s
            
    return None

@app.command("config")
def config_app():
    """Set the GitHub Repository URL and default shell preference."""
    cfg = config.load_config()
    
    repo_url = questionary.text(
        "Enter the GitHub repository URL for your snippets:",
        default=cfg.get("repo_url", "")
    ).ask()
    
    shell_choice = questionary.select(
        "Select your default shell environment:",
        choices=["bash", "zsh", "pwsh", "cmd"],
        default=cfg.get("default_shell", "bash")
    ).ask()

    if repo_url is not None and shell_choice is not None:
        cfg["repo_url"] = repo_url
        cfg["default_shell"] = shell_choice
        config.save_config(cfg)
        console.print("[green]Configuration saved![/green]")

@app.command()
def sync():
    """Forces a git pull/clone on the local snippet repository."""
    console.print("Syncing snippets repository...")
    if git_sync.sync():
        console.print("[green]Successfully synced![/green]")
    else:
        raise typer.Exit(1)

@app.command()
def find(query: str):
    """Interactive search; prints selection to terminal with syntax highlighting."""
    snippet = _search_and_select(query)
    if not snippet:
        return

    _update_weight(snippet.title)
    
    console.print(f"\n[bold cyan]{snippet.title}[/bold cyan]")
    if snippet.description:
        console.print(f"[italic]{snippet.description}[/italic]")
    console.print("---")

    for lang, code in snippet.code_blocks.items():
        console.print(f"Environment: [bold yellow]{lang}[/bold yellow]")
        syntax = Syntax(code, lang if lang != "pwsh" else "powershell", theme="monokai", line_numbers=False)
        console.print(syntax)
        console.print()

@app.command()
def get(query: str):
    """Interactive search; copies one-liner or runs Python file via uv."""
    snippet = _search_and_select(query)
    if not snippet:
        return

    _update_weight(snippet.title)

    cfg = config.load_config()
    target_shell = cfg.get("default_shell", transformers.detect_default_shell())

    # Determine which code block to use
    if "python" in snippet.code_blocks:
        lang = "python"
        code = snippet.code_blocks["python"]
    elif target_shell in snippet.code_blocks:
        lang = target_shell
        code = snippet.code_blocks[target_shell]
    else:
        # Fallback to the first available block if target isn't found
        lang = list(snippet.code_blocks.keys())[0]
        code = snippet.code_blocks[lang]

    if lang == "python":
        # Python Execution Logic via uv
        console.print("[cyan]Python snippet detected. Preparing uv execution...[/cyan]")
        code = transformers.inject_uv_header(code)
        
        # Generate random temp file in current directory
        temp_filename = f"run-{secrets.token_hex(4)}.py"
        temp_path = Path.cwd() / temp_filename
        
        try:
            temp_path.write_text(code, encoding="utf-8")
            console.print(f"[dim]Running {temp_filename} via uv run...[/dim]\n")
            subprocess.run(["uv", "run", temp_filename])
        finally:
            # Clean up the temporary file
            if temp_path.exists():
                temp_path.unlink()
    else:
        # Shell Execution Logic (Minify & Clipboard)
        oneliner = transformers.minify_to_oneliner(code, lang)
        pyperclip.copy(oneliner)
        console.print(f"[green]Copied {lang} one-liner to clipboard![/green]")
        console.print(f"[dim]{oneliner}[/dim]")

if __name__ == "__main__":
    app()