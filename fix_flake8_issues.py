#!/usr/bin/env python3
"""Script to fix remaining flake8 issues in the codebase."""

import os
import re
from pathlib import Path


def fix_file(file_path):
    """Fix common flake8 issues in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix F401: Remove unused imports
    if 'from datetime import date' in content and 'datetime.now()' in content:
        content = content.replace('from datetime import date', 'from datetime import date, datetime')

    # Fix W291: Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Save changes if any
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Main function to fix all files."""
    # Define directories to process
    base_dir = Path(__file__).parent
    dirs_to_process = [
        'app',
        'tests',
    ]

    # Process each Python file
    for dir_path in dirs_to_process:
        for root, _, files in os.walk(base_dir / dir_path):
            for file in files:
                if file.endswith('.py') and not any(x in root for x in ['venv', '.venv', 'env', '__pycache__']):
                    file_path = Path(root) / file
                    if fix_file(file_path):
                        print(f"Fixed: {file_path}")


if __name__ == '__main__':
    main()

