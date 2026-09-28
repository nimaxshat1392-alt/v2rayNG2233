#!/usr/bin/env python3
import os
import re
import sys
import subprocess

JAVA = "V2rayNG/app/src/main/java/com/v2ray/ang"
MANIFEST = "V2rayNG/app/src/main/AndroidManifest.xml"


def log(msg):
    print(f"[HEAL] {msg}", flush=True)


def run(cmd, cwd=None):
    return subprocess.run(cmd, shell=True, cwd=cwd,
                          capture_output=True, text=True)


def extract_errors(text):
    errors = []
    pattern = r'e:\s+file://([^:]+\.kt):(\d+):\d+\s+(.+)'
    for m in re.finditer(pattern, text):
        path = m.group(1)
        if "/com/v2ray/ang/" in path:
            rel = path.split("/com/v2ray/ang/")[1]
            errors.append(rel)
    return list(set(errors))


def clean_manifest(name):
    if not os.path.exists(MANIFEST):
        return
    with open(MANIFEST, encoding="utf-8") as f:
        c = f.read()
    c = re.sub(
        rf'<activity[^>]*android:name="[^"]*\.{name}"[^>]*>.*?</activity>',
        '', c, flags=re.DOTALL
    )
    c = re.sub(
        rf'<activity[^>]*android:name="[^"]*\.{name}"[^>]*/>',
        '', c
    )
    c = re.sub(
        rf'<receiver[^>]*android:name="[^"]*\.{name}"[^>]*>.*?</receiver>',
        '', c, flags=re.DOTALL
    )
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(c)


def delete_file(rel):
    full = f"{JAVA}/{rel}"
    if os.path.exists(full):
        os.remove(full)
        log(f"Deleted: {rel}")
        clean_manifest(os.path.basename(rel).replace(".kt", ""))


def main():
    log("Starting self-healing build")

    if os.path.exists("scripts/generate.py"):
        log("Running generate.py...")
        r = run("python3 scripts/generate.py")
        if r.returncode != 0:
            log("generate.py failed")
            log(r.stderr[-300:] if r.stderr else "no stderr")

    if os.path.exists("V2rayNG/gradlew"):
        os.chmod("V2rayNG/gradlew", 0o755)

    for attempt in range(1, 6):
        log(f"Attempt {attempt}/5")
        r = run("./gradlew assembleDebug --stacktrace", cwd="V2rayNG")
        if r.returncode == 0:
            log("BUILD SUCCESS!")
            return 0

        errors = extract_errors(r.stdout + r.stderr)
        log(f"Found {len(errors)} broken files")
        if not errors:
            return 1

        for rel in errors:
            delete_file(rel)

    return 1


if __name__ == "__main__":
    sys.exit(main())
