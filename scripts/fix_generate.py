#!/usr/bin/env python3
"""Auto-fix syntax errors in generate.py"""
import re
import subprocess
import sys

FILE = "scripts/generate.py"

def check():
    r = subprocess.run(["python3", "-m", "py_compile", FILE],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr

def fix_line(line_num):
    with open(FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    idx = line_num - 1
    if idx < 0 or idx >= len(lines):
        return False

    original = lines[idx]
    s = original.rstrip("\n")

    # خط خالی
    if not s.strip():
        return False

    # اگر تعداد کوتیشن دوتایی فرد است، آخرش کوتیشن بسته نشده
    if s.count('"') % 2 == 1:
        # پیدا کن آخرین کاراکتر چی هست
        if s.endswith('"'):
            return False
        # اضافه کردن ")" برای بستن
        lines[idx] = s + '")' + "\n"
        print(f"Fixed line {line_num}: added closing quote + paren")
        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    # اگر تعداد کوتیشن تکی فرد است
    if s.count("'") % 2 == 1 and s.count('"') % 2 == 0:
        if s.endswith("'"):
            return False
        lines[idx] = s + "')" + "\n"
        print(f"Fixed line {line_num}: added closing quote + paren")
        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    return False

def main():
    max_iter = 200
    for i in range(max_iter):
        ok, err = check()
        if ok:
            print(f"✅ File compiles successfully after {i} fixes")
            return 0

        m = re.search(r'line (\d+)', err)
        if not m:
            print("❌ Cannot parse error")
            print(err[:500])
            return 1

        line_num = int(m.group(1))
        print(f"Fix #{i+1}: syntax error at line {line_num}")

        if not fix_line(line_num):
            print(f"❌ Cannot auto-fix line {line_num}")
            print("Error:")
            print(err[:500])
            return 1

    print("❌ Max iterations reached")
    return 1

if __name__ == "__main__":
    sys.exit(main())
