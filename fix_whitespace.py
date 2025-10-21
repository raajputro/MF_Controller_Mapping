#!/usr/bin/env python3
import sys

def fix_trailing_whitespace(filepath):
    """Remove trailing spaces/tabs from each line while preserving original line endings."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return False

    fixed_lines = []
    changed = False

    for line in lines:
        # preserve original line ending (\r\n, \n, or \r)
        if line.endswith('\r\n'):
            ending = '\r\n'
            content = line[:-2]
        elif line.endswith('\n') or line.endswith('\r'):
            ending = line[-1]
            content = line[:-1]
        else:
            ending = ''
            content = line

        # only strip spaces and tabs at end (keep other whitespace characters)
        new_content = content.rstrip(' \t')
        if new_content != content:
            changed = True

        fixed_lines.append(new_content + ending)

    if changed:
        with open(filepath, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
            f.writelines(fixed_lines)
        return True

    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            if fix_trailing_whitespace(filepath):
                print(f"Fixed: {filepath}")
    else:
        print("Usage: python fix_whitespace.py <file1> <file2> ...")