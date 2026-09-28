#!/usr/bin/env python3
"""
Auto-fix indentation and syntax errors in generate.py
Combined version with multiple strategies
"""
import ast
import re
import sys
import subprocess

FILE = "scripts/generate.py"


def check_syntax():
    """Check if file compiles using ast"""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None, 0
    except SyntaxError as e:
        return False, e.msg, e.lineno
    except Exception as e:
        return False, str(e), 0


def fix_line_remove_indent(line_num):
    """Fix a single line by removing ALL leading spaces"""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        idx = line_num - 1
        if idx < 0 or idx >= len(lines):
            return False

        line = lines[idx]

        if not line.strip() or line.strip().startswith("#"):
            return False

        fixed = line.lstrip()

        if fixed == line:
            return False

        lines[idx] = fixed

        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"[FIX] Removed leading spaces at line {line_num}")
        return True
    except Exception as e:
        print(f"[FIX] Error fixing line {line_num}: {e}")
        return False


def fix_bulk_indentation():
    """Remove leading whitespace from lines that look like top-level Python"""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        inside_string = False
        quote_char = None
        modified_count = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track triple-quoted strings
            if not inside_string:
                # Check for opening triple quotes
                if "r'''" in line:
                    if line.count("'''") % 2 == 1:
                        inside_string = True
                        quote_char = "'''"
                    continue
                if 'r"""' in line:
                    if line.count('"""') % 2 == 1:
                        inside_string = True
                        quote_char = '"""'
                    continue
                if "'''" in line:
                    if line.count("'''") % 2 == 1:
                        inside_string = True
                        quote_char = "'''"
                    continue
                if '"""' in line:
                    if line.count('"""') % 2 == 1:
                        inside_string = True
                        quote_char = '"""'
                    continue

                # Not inside string - check if line is wrongly indented
                if line and (line[0] == " " or line[0] == "\t"):
                    content = line.lstrip()

                    # Only fix lines that look like top-level Python
                    top_level_prefixes = [
                        "w(",
                        "import ",
                        "from ",
                        "def ",
                        "class ",
                        "print(",
                        "#",
                        "BASE ",
                        "JAVA ",
                        "manifest",
                        "if __name__",
                    ]

                    if any(content.startswith(p) for p in top_level_prefixes):
                        # But skip if it's inside a Python block (has parent indented)
                        # For now, we just fix it
                        lines[i] = content
                        modified_count += 1
            else:
                # Inside string - look for closing quote
                if quote_char and quote_char in line:
                    if line.count(quote_char) % 2 == 1:
                        inside_string = False
                        quote_char = None

        if modified_count > 0:
            with open(FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"[FIX] Bulk fixed {modified_count} lines")
            return True
        return False
    except Exception as e:
        print(f"[FIX] Error in bulk fix: {e}")
        return False


def fix_triple_quote_balance():
    """Fix unbalanced triple quotes by adding missing closing quote"""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Count triple single quotes
        count_single = content.count("'''")
        count_double = content.count('"""')

        modified = False

        if count_single % 2 == 1:
            print(f"[FIX] Unbalanced ''' detected (count: {count_single})")
            # Try to find the last unclosed r''' and close it
            last_open = content.rfind("r'''")
            if last_open > 0:
                # Find the end of the file, add closing
                if not content.rstrip().endswith("'''"):
                    content = content.rstrip() + "\n'''\n"
                    modified = True
                    print("[FIX] Added closing '''")

        if count_double % 2 == 1:
            print(f"[FIX] Unbalanced \"\"\" detected (count: {count_double})")

        if modified:
            with open(FILE, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"[FIX] Error in triple quote fix: {e}")
        return False


def main():
    print("[FIX] Starting auto-fixer for generate.py")
    print("=" * 60)

    # First, try to fix unbalanced triple quotes
    fix_triple_quote_balance()

    max_attempts = 100

    for attempt in range(1, max_attempts + 1):
        ok, msg, line_num = check_syntax()

        if ok:
            print("=" * 60)
            print(f"[FIX] ✅ File compiles successfully after {attempt - 1} fixes")
            print("=" * 60)
            return 0

        print(f"[FIX] Attempt {attempt}: error at line {line_num}: {msg[:80] if msg else 'unknown'}")

        # Strategy 1: Fix the specific line
        if line_num and line_num > 0:
            if fix_line_remove_indent(line_num):
                continue

        # Strategy 2: Bulk fix indentation
        if fix_bulk_indentation():
            continue

        # Strategy 3: Try to fix triple quote
        if fix_triple_quote_balance():
            continue

        # Can't fix anymore
        print("=" * 60)
        print(f"[FIX] ❌ Cannot auto-fix line {line_num}: {msg}")
        print("=" * 60)
        return 1

    print("=" * 60)
    print("[FIX] ❌ Max attempts reached")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
