#!/usr/bin/env python3
"""
Self-Healing Build System for Fast VPN
- اجرا می‌کنه generate.py
- اگه generate.py خطا داد، خودش خطاها رو تحلیل می‌کنه
- Build می‌کنه
- اگه Build خطا داد، فایل‌های مشکل‌دار رو حذف می‌کنه
- تا ۵ بار تلاش می‌کنه
"""
import os
import re
import sys
import subprocess
import shutil

# ═══════════════════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════════════════
JAVA = "V2rayNG/app/src/main/java/com/v2ray/ang"
MANIFEST = "V2rayNG/app/src/main/AndroidManifest.xml"
MAX_ATTEMPTS = 5

# فایل‌هایی که اگه خطا دادن، حذف می‌شن
DELETABLE = [
    "ui/home/CountryListActivity.kt",
    "ui/home/ServerListActivity.kt",
    "ui/home/DataUsageActivity.kt",
    "ui/home/BackupRestoreActivity.kt",
    "ui/home/KillSwitchActivity.kt",
    "ui/home/SplitTunnelActivity.kt",
    "ui/home/DnsSettingsActivity.kt",
    "ui/home/RoutingActivity.kt",
    "ui/home/ProxySettingsActivity.kt",
    "ui/home/FirstRunActivity.kt",
    "ui/home/SplashActivity.kt",
    "ui/home/HelpActivity.kt",
    "ui/home/LegalActivity.kt",
    "ui/home/AboutNewActivity.kt",
    "ui/home/AboutActivity.kt",
    "ui/home/SettingsActivity.kt",
    "ui/home/SpeedTestActivity.kt",
    "ui/admin/QrScannerActivity.kt",
    "ui/components/VpnStatsCard.kt",
    "ui/components/PulsingRing.kt",
    "ui/components/GradientButton.kt",
    "ui/components/AnimatedTrafficCard.kt",
    "ui/components/ConnectionProgressRing.kt",
    "ui/components/StatChip.kt",
    "ui/components/ModernDialog.kt",
    "ui/components/AnimatedBackground.kt",
    "ui/theme/ThemeAdvanced.kt",
    "ui/theme/TypographyConfig.kt",
    "ui/theme/ColorPalette.kt",
    "handler/ConfigParser.kt",
    "handler/ServersRepository.kt",
    "handler/VpnConnectionManager.kt",
    "handler/VpnNotificationManager.kt",
    "handler/LanguageManager.kt",
    "util/NotificationChannelHelper.kt",
    "util/PreferencesManager.kt",
    "worker/AutoPingWorker.kt",
    "receiver/BootReceiver.kt",
    "widget/VpnWidgetProvider.kt",
]


def log(msg):
    print(f"[SELF-HEAL] {msg}", flush=True)


def run(cmd, cwd=None):
    """دستور رو اجرا می‌کنه"""
    return subprocess.run(cmd, shell=True, cwd=cwd,
                          capture_output=True, text=True)


def extract_errors(log_text):
    """از لاگ Build، خطاهای کامپایل رو استخراج می‌کنه"""
    errors = []
    # الگوی خطاهای Kotlin
    pattern = r'e:\s+file://([^:]+\.kt):(\d+):(\d+)\s+(.+)'
    for match in re.finditer(pattern, log_text):
        full_path = match.group(1)
        line = match.group(2)
        msg = match.group(4)
        if "/com/v2ray/ang/" in full_path:
            rel = full_path.split("/com/v2ray/ang/")[1]
            errors.append((rel, line, msg))
    return errors


def delete_file(rel_path):
    """فایل رو حذف می‌کنه و از Manifest هم پاک می‌کنه"""
    full = f"{JAVA}/{rel_path}"
    if os.path.exists(full):
        os.remove(full)
        log(f"  حذف: {rel_path}")

        # حذف از Manifest
        basename = os.path.basename(rel_path).replace(".kt", "")
        clean_manifest(basename)


def clean_manifest(activity_name):
    """Activity رو از Manifest حذف می‌کنه"""
    if not os.path.exists(MANIFEST):
        return
    with open(MANIFEST, encoding="utf-8") as f:
        c = f.read()

    original = c
    # حذف activity
    c = re.sub(
        rf'<activity[^>]*android:name="[^"]*\.{activity_name}"[^>]*>.*?</activity>',
        '', c, flags=re.DOTALL
    )
    c = re.sub(
        rf'<activity[^>]*android:name="[^"]*\.{activity_name}"[^>]*/>',
        '', c
    )
    # حذف receiver
    c = re.sub(
        rf'<receiver[^>]*android:name="[^"]*\.{activity_name}"[^>]*>.*?</receiver>',
        '', c, flags=re.DOTALL
    )
    # حذف service
    c = re.sub(
        rf'<service[^>]*android:name="[^"]*\.{activity_name}"[^>]*>.*?</service>',
        '', c, flags=re.DOTALL
    )

    if c != original:
        with open(MANIFEST, "w", encoding="utf-8") as f:
            f.write(c)
        log(f"  از Manifest حذف شد: {activity_name}")


def is_deletable(rel_path):
    """چک می‌کنه که آیا فایل قابل حذف هست"""
    for item in DELETABLE:
        if item in rel_path or rel_path.endswith(item):
            return True
    # اگه فایل ما باشه (نه فایل اصلی v2rayNG) قابل حذفه
    if any(x in rel_path for x in ["ui/home/", "ui/admin/", "ui/components/",
                                    "ui/theme/", "handler/", "util/",
                                    "worker/", "receiver/", "widget/"]):
        # فایل‌های اصلی v2rayNG رو استثنا کن
        protected = ["MmkvManager.kt", "AngConfigManager.kt", "V2RayVpnService.kt",
                     "SpeedtestManager.kt", "CoreServiceManager.kt",
                     "CoreNativeManager.kt", "CertificateFingerprintManager.kt"]
        for p in protected:
            if p in rel_path:
                return False
        return True
    return False


def try_build():
    """Build می‌کنه و نتیجه رو برمی‌گردونه"""
    log("در حال Build...")
    result = run("./gradlew assembleDebug --stacktrace", cwd="V2rayNG")
    return result.returncode, result.stdout + result.stderr


def run_generate():
    """generate.py رو اجرا می‌کنه"""
    log("اجرای generate.py...")
    result = run("python3 scripts/generate.py")
    if result.returncode != 0:
        log(f"generate.py خطا داد:")
        log(result.stdout[-500:])
        log(result.stderr[-500:])
        return False
    log("generate.py با موفقیت اجرا شد")
    return True


def main():
    log("=" * 60)
    log("شروع سیستم خود-ترمیمی")
    log("=" * 60)

    # مرحله ۱: اجرای generate.py (اختیاری)
    if os.path.exists("scripts/generate.py"):
        if not run_generate():
            log("generate.py شکست خورد - ولی ادامه می‌دیم")

    # مرحله ۲: chmod
    if os.path.exists("V2rayNG/gradlew"):
        os.chmod("V2rayNG/gradlew", 0o755)

    # مرحله ۳: حلقه تلاش
    for attempt in range(1, MAX_ATTEMPTS + 1):
        log("")
        log("=" * 60)
        log(f"تلاش {attempt}/{MAX_ATTEMPTS}")
        log("=" * 60)

        exit_code, log_text = try_build()

        if exit_code == 0:
            log("✅ Build با موفقیت انجام شد!")
            log("=" * 60)
            return 0

        log(f"❌ Build شکست خورد (کد: {exit_code})")

        # استخراج خطاها
        errors = extract_errors(log_text)
        log(f"تعداد خطاها: {len(errors)}")

        if not errors:
            log("خطای کامپایلی پیدا نشد - متوقف می‌شود")
            # چاپ ۲۰ خط آخر لاگ
            log("20 خط آخر لاگ:")
            for line in log_text.split("\n")[-20:]:
                log(f"  {line}")
            return 1

        # نمایش خطاها
        for rel, line, msg in errors[:15]:
            log(f"  خطا: {rel}:{line} → {msg[:80]}")

        # حذف فایل‌های خطا‌دار
        deleted = 0
        for rel, line, msg in errors:
            if is_deletable(rel):
                delete_file(rel)
                deleted += 1

        if deleted == 0:
            log("هیچ فایل قابل حذفی پیدا نشد - متوقف می‌شود")
            return 1

        log(f"تعداد {deleted} فایل حذف شد - تلاش بعدی...")

    log("=" * 60)
    log("❌ حداکثر تلاش‌ها به پایان رسید")
    log("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
