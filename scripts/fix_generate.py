#!/usr/bin/env python3
import re
import subprocess
import sys

FILE = "scripts/generate.py"

def check():
    r = subprocess.run(["python3", "-m", "py_compile", FILE],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr

def fix_line(line_num, err_text):
    with open(FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    idx = line_num - 1
    if idx < 0 or idx >= len(lines):
        return False

    s = lines[idx].rstrip("\n")
    print(f"Line {line_num}: {repr(s)}")

    # خطوطی که با content.replace("</application>", تمام می‌شن
    if 'content.replace("</application>",' in s and s.endswith(","):
        lines[idx] = '        content = content.replace("</application>", new_acts2 + "\\n    </application>")\n'
        print(f"Fixed: closed replace paren")
        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    # اگه تعداد پرانتز باز بیشتر از بسته است
    open_parens = s.count("(")
    close_parens = s.count(")")
    if open_parens > close_parens:
        diff = open_parens - close_parens
        lines[idx] = s + (")" * diff) + "\n"
        print(f"Fixed: added {diff} closing parens")
        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    # اگه تعداد کوتیشن دوتایی فرد است
    if s.count('"') % 2 == 1:
        lines[idx] = s + '"\n'
        print(f"Fixed: added closing quote")
        with open(FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True

    return False

def main():
    for i in range(50):
        ok, err = check()
        if ok:
            print(f"✅ Compiles after {i} fixes")
            return 0

        m = re.search(r'line (\d+)', err)
        if not m:
            print("Cannot find line number")
            print(err[:500])
            return 1

        line_num = int(m.group(1))
        print(f"Fix #{i+1}: line {line_num}")

        if not fix_line(line_num, err):
            print(f"❌ Cannot fix line {line_num}")
            print(err[:300])
            return 1

    return 1

if __name__ == "__main__":
    sys.exit(main())
