import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from . import config

@dataclass
class Snippet:
    title: str
    tags: List[str]
    description: str
    file_source: str
    code_blocks: Dict[str, str] = field(default_factory=dict)
    
    # We can use this property later for our fuzzy search
    @property
    def searchable_text(self) -> str:
        return f"{self.title} {' '.join(self.tags)} {self.description}".lower()


def parse_file(filepath: Path) -> List[Snippet]:
    """Reads a single markdown file and extracts all snippets based on the schema."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the file by "## " to isolate individual snippets
    chunks = re.split(r'^##\s+', content, flags=re.MULTILINE)
    snippets = []

    for chunk in chunks:
        if not chunk.strip():
            continue

        lines = chunk.splitlines()
        title = lines[0].strip()
        tags = []
        description_lines = []
        code_blocks = {}

        current_lang = "default"
        in_code_block = False
        current_code = []

        i = 1
        # 1. Extract Tags (lines starting with backticks immediately after the title)
        while i < len(lines) and lines[i].strip().startswith('`'):
            tags.extend(re.findall(r'`([^`]+)`', lines[i]))
            i += 1

        # 2. Extract Description (everything up to the --- separator or ### heading)
        while i < len(lines):
            line = lines[i]
            if line.startswith('---') or line.startswith('###'):
                break
            if line.strip():
                description_lines.append(line.strip())
            i += 1
        
        description = " ".join(description_lines)

        # 3. Extract Code Blocks based on language/shell headings
        while i < len(lines):
            line = lines[i]
            if line.startswith('###'):
                # Extract the target environment (e.g., 'bash', 'pwsh', 'python')
                current_lang = line.replace('###', '').strip().lower()
            elif line.startswith('```'):
                if in_code_block:
                    # Closing the block
                    in_code_block = False
                    code_blocks[current_lang] = "\n".join(current_code)
                    current_code = []
                else:
                    # Opening the block
                    in_code_block = True
            elif in_code_block:
                current_code.append(line)
            i += 1

        # Only add valid snippets that have a title and at least one code block
        if title and code_blocks:
            snippets.append(Snippet(
                title=title,
                tags=tags,
                description=description,
                file_source=filepath.name,
                code_blocks=code_blocks
            ))

    return snippets


def load_all_snippets() -> List[Snippet]:
    """Scans the repository directory and parses all markdown files."""
    repo_dir = config.REPO_DIR
    all_snippets = []
    
    if not repo_dir.exists():
        return all_snippets

    for md_file in repo_dir.rglob("*.md"):
        # Ignore standard repository files that aren't snippet collections
        if md_file.name.lower() in ["readme.md", "contributing.md"]:
            continue
        all_snippets.extend(parse_file(md_file))

    return all_snippets