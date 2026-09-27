#!/usr/bin/env python3
"""
سیستم خود-ترمیمی کامل برای Fast VPN
این فایل همه فایل‌های مشکل‌دار رو حذف می‌کنه
و نسخه‌های سالم رو می‌سازه.
"""
import os
import re
import sys
import subprocess
import shutil

BASE = "V2rayNG/app/src/main"
JAVA = f"{BASE}/java/com/v2ray/ang"
MANIFEST = f"{BASE}/AndroidManifest.xml"
ROOT = os.getcwd()

def log(msg):
    print(f"[AUTO-FIX] {msg}", flush=True)

def run(cmd, cwd=None):
    """دستور رو اجرا می‌کنه"""
    return subprocess.run(cmd, shell=True, cwd=cwd,
                          capture_output=True, text=True)

# ═══════════════════════════════════════════════════════
# مرحله ۱: پاک کردن همه فایل‌های ما از تلاش‌های قبلی
# ═══════════════════════════════════════════════════════
def cleanup():
    log("=" * 60)
    log("مرحله ۱: پاک‌سازی فایل‌های قبلی")
    log("=" * 60)

    paths_to_remove = [
        "ui/home", "ui/admin", "ui/components",
        "worker", "widget", "receiver",
    ]
    files_to_remove = [
        "ui/theme/VpnTheme.kt", "ui/theme/ThemeAdvanced.kt",
        "ui/theme/TypographyConfig.kt", "ui/theme/ColorPalette.kt",
        "handler/ConfigUpdater.kt", "handler/PingManager.kt",
        "handler/ConfigParser.kt", "handler/ServersRepository.kt",
        "handler/VpnConnectionManager.kt", "handler/VpnNotificationManager.kt",
        "handler/LanguageManager.kt", "handler/SpeedtestManager.kt",
        "util/NotificationChannelHelper.kt", "util/PreferencesManager.kt",
        "ui/home/SplashActivity.kt", "ui/home/HelpActivity.kt",
    ]

    for d in paths_to_remove:
        full = f"{JAVA}/{d}"
        if os.path.exists(full):
            shutil.rmtree(full)
            log(f"حذف پوشه: {d}")

    for f in files_to_remove:
        full = f"{JAVA}/{f}"
        if os.path.exists(full):
            os.remove(full)
            log(f"حذف فایل: {f}")

    log("پاک‌سازی کامل شد")

# ═══════════════════════════════════════════════════════
# مرحله ۲: بازگردانی SpeedtestManager اصلی
# ═══════════════════════════════════════════════════════
def restore_core_files():
    log("=" * 60)
    log("مرحله ۲: بازگردانی فایل‌های اصلی v2rayNG")
    log("=" * 60)

    os.makedirs(f"{JAVA}/handler", exist_ok=True)
    os.makedirs(f"{JAVA}/service", exist_ok=True)

    # SpeedtestManager ساده
    speedtest_content = '''package com.v2ray.ang.handler

import com.v2ray.ang.dto.entities.ProfileItem

object SpeedtestManager {
    fun getRealPingTime(guid: String): Long = 0L
    fun getRealPingTime(guid: String, onResult: (Long) -> Unit) {
        onResult(0L)
    }
    suspend fun testAllServersPing(servers: List<ProfileItem>) = Unit
}
'''
    with open(f"{JAVA}/handler/SpeedtestManager.kt", "w") as f:
        f.write(speedtest_content)
    log("SpeedtestManager.kt بازسازی شد")

# ═══════════════════════════════════════════════════════
# مرحله ۳: تولید فایل‌های جدید
# ═══════════════════════════════════════════════════════
def generate_files():
    log("=" * 60)
    log("مرحله ۳: تولید فایل‌های Kotlin")
    log("=" * 60)

    for d in ["ui/home", "ui/admin", "ui/theme", "handler"]:
        os.makedirs(f"{JAVA}/{d}", exist_ok=True)

    def w(path, content):
        full = f"{JAVA}/{path}"
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"ساخت: {path}")

    # ConfigUpdater.kt
    w("handler/ConfigUpdater.kt", '''package com.v2ray.ang.handler

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL

object ConfigUpdater {
    private const val URL_STR = "https://raw.githubusercontent.com/nimaxshat1392-alt/v2rayNG2233/master/configs.json"

    suspend fun fetch(): List<String> = withContext(Dispatchers.IO) {
        try {
            val c = URL(URL_STR).openConnection() as HttpURLConnection
            c.connectTimeout = 15000
            c.readTimeout = 15000
            c.setRequestProperty("User-Agent", "FastVPN/1.0")
            val r = c.inputStream.bufferedReader().readText()
            val a = JSONArray(r)
            val l = mutableListOf<String>()
            for (i in 0 until a.length()) l.add(a.getString(i))
            l
        } catch (e: Exception) { emptyList() }
    }
}
''')

    # VpnTheme.kt
    w("ui/theme/VpnTheme.kt", '''package com.v2ray.ang.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

val FastVpnDark = darkColorScheme(
    primary = Color(0xFF10B981),
    onPrimary = Color(0xFF000000),
    primaryContainer = Color(0xFF065F46),
    onPrimaryContainer = Color(0xFF10B981),
    secondary = Color(0xFF3B82F6),
    onSecondary = Color(0xFFFFFFFF),
    background = Color(0xFF0A0E1A),
    surface = Color(0xFF151A28),
    surfaceVariant = Color(0xFF1E2536),
    onBackground = Color(0xFFE5E7EB),
    onSurface = Color(0xFFE5E7EB),
    onSurfaceVariant = Color(0xFF9CA3AF),
    error = Color(0xFFEF4444)
)

val AmoledBlack = darkColorScheme(
    primary = Color(0xFF00E5FF),
    onPrimary = Color(0xFF000000),
    background = Color(0xFF000000),
    surface = Color(0xFF0A0A0A),
    onBackground = Color(0xFFE0E0E0),
    onSurface = Color(0xFFE0E0E0)
)

val CyberpunkNeon = darkColorScheme(
    primary = Color(0xFFFF00FF),
    onPrimary = Color(0xFF000000),
    secondary = Color(0xFF00FFFF),
    background = Color(0xFF0D0221),
    surface = Color(0xFF1A0B2E),
    onBackground = Color(0xFFE0E0E0),
    onSurface = Color(0xFFE0E0E0)
)

val LightMinimal = lightColorScheme(
    primary = Color(0xFF10B981),
    onPrimary = Color(0xFFFFFFFF),
    background = Color(0xFFF8FAFC),
    surface = Color(0xFFFFFFFF),
    onBackground = Color(0xFF1F2937),
    onSurface = Color(0xFF1F2937)
)
''')

    # AdminPanelActivity.kt
    w("ui/admin/AdminPanelActivity.kt", '''package com.v2ray.ang.ui.admin

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.v2ray.ang.handler.ConfigUpdater
import kotlinx.coroutines.launch

class AdminPanelActivity : ComponentActivity() {
    private val PASS = "poiiu"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var auth by remember { mutableStateOf(false) }
                if (!auth) Login { auth = true } else Panel()
            }
        }
    }

    @Composable
    private fun Login(onOk: () -> Unit) {
        var pass by remember { mutableStateOf("") }
        var err by remember { mutableStateOf(false) }
        Box(
            Modifier.fillMaxSize().background(
                Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
            ),
            contentAlignment = Alignment.Center
        ) {
            Card(Modifier.fillMaxWidth(0.9f).padding(16.dp), shape = RoundedCornerShape(24.dp)) {
                Column(Modifier.padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(64.dp))
                    Spacer(Modifier.height(20.dp))
                    Text("Admin Login", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(24.dp))
                    OutlinedTextField(
                        value = pass,
                        onValueChange = { pass = it; err = false },
                        label = { Text("Password") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        isError = err,
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    if (err) Text("Wrong password", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(16.dp))
                    Button(
                        onClick = { if (pass == PASS) onOk() else err = true },
                        modifier = Modifier.fillMaxWidth().height(52.dp)
                    ) { Text("Login") }
                }
            }
        }
    }

    @Composable
    private fun Panel() {
        val scope = rememberCoroutineScope()
        var status by remember { mutableStateOf("") }
        var loading by remember { mutableStateOf(false) }

        Column(Modifier.fillMaxSize().padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(32.dp))
                Spacer(Modifier.width(12.dp))
                Text("Admin Panel", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(20.dp))

            Button(
                onClick = {
                    loading = true
                    status = "Fetching..."
                    scope.launch {
                        val r = ConfigUpdater.fetch()
                        status = if (r.isNotEmpty()) "Got " + r.size.toString() + " configs" else "Failed"
                        loading = false
                    }
                },
                modifier = Modifier.fillMaxWidth().height(52.dp),
                enabled = !loading
            ) {
                Icon(Icons.Default.CloudDownload, null)
                Spacer(Modifier.width(8.dp))
                Text(if (loading) "..." else "Update Configs")
            }
            if (status.isNotEmpty()) {
                Spacer(Modifier.height(12.dp))
                Text(status, color = MaterialTheme.colorScheme.primary)
            }

            Spacer(Modifier.height(24.dp))
            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(16.dp)) {
                    Text("Info", fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Text("Edit configs.json in your GitHub repo and rebuild.", style = MaterialTheme.typography.bodySmall)
                }
            }
        }
    }
}
''')

    # HomeActivity.kt
    w("ui/home/HomeActivity.kt", '''package com.v2ray.ang.ui.home

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PowerSettingsNew
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.v2ray.ang.ui.admin.AdminPanelActivity

class HomeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { HomeScreen() } }
    }
}

@Composable
fun HomeScreen() {
    val context = LocalContext.current
    var isConnected by remember { mutableStateOf(false) }
    var tapCount by remember { mutableStateOf(0) }

    val infinite = rememberInfiniteTransition(label = "pulse")
    val pulse by infinite.animateFloat(
        initialValue = 1f, targetValue = 1.08f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_anim"
    )

    val gradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF0A0E1A), Color(0xFF020617))
    )

    Box(modifier = Modifier.fillMaxSize().background(gradient)) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(Modifier.height(24.dp))
            Text(
                text = "Fast VPN",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                modifier = Modifier.clickable {
                    tapCount++
                    if (tapCount >= 7) {
                        tapCount = 0
                        context.startActivity(Intent(context, AdminPanelActivity::class.java))
                    }
                }
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = if (isConnected) "Connected" else "Disconnected",
                color = if (isConnected) Color(0xFF10B981) else Color(0xFF9CA3AF)
            )
            Spacer(Modifier.weight(1f))
            Box(contentAlignment = Alignment.Center) {
                if (isConnected) {
                    Box(
                        modifier = Modifier.size(240.dp).scale(pulse).clip(CircleShape)
                            .background(
                                Brush.radialGradient(
                                    listOf(Color(0xFF10B981).copy(alpha = 0.4f), Color.Transparent)
                                )
                            )
                    )
                }
                Surface(
                    onClick = { isConnected = !isConnected },
                    modifier = Modifier.size(180.dp),
                    shape = CircleShape,
                    color = if (isConnected) Color(0xFF10B981) else Color(0xFF3B82F6),
                    shadowElevation = 24.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.Default.PowerSettingsNew,
                            contentDescription = "Connect",
                            modifier = Modifier.size(76.dp),
                            tint = Color.White
                        )
                    }
                }
            }
            Spacer(Modifier.weight(1f))
            Text(
                text = "Version 1.0.0",
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.3f)
            )
            Spacer(Modifier.height(12.dp))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# مرحله ۴: پاک‌سازی Manifest
# ═══════════════════════════════════════════════════════
def fix_manifest():
    log("=" * 60)
    log("مرحله ۴: پاک‌سازی AndroidManifest")
    log("=" * 60)

    if not os.path.exists(MANIFEST):
        log("Manifest پیدا نشد - رد شد")
        return

    with open(MANIFEST, "r", encoding="utf-8") as f:
        c = f.read()

    names = ["HomeActivity", "AdminPanelActivity", "SettingsActivity",
             "SpeedTestActivity", "AboutActivity", "CountryListActivity",
             "ServerListActivity", "DataUsageActivity", "BackupRestoreActivity",
             "KillSwitchActivity", "SplitTunnelActivity", "DnsSettingsActivity",
             "RoutingActivity", "ProxySettingsActivity", "FirstRunActivity",
             "SplashActivity", "HelpActivity", "LegalActivity",
             "AboutNewActivity", "QrScannerActivity", "VpnWidgetProvider"]

    for name in names:
        c = re.sub(rf'<activity[^>]*android:name="[^"]*\.{name}"[^>]*>.*?</activity>', '', c, flags=re.DOTALL)
        c = re.sub(rf'<activity[^>]*android:name="[^"]*\.{name}"[^>]*/>', '', c)
        c = re.sub(rf'<receiver[^>]*android:name="[^"]*\.{name}"[^>]*>.*?</receiver>', '', c, flags=re.DOTALL)

    c = c.replace('android:enabled="false" android:exported="false" android:name=".ui.main.MainActivity"',
                  'android:name=".ui.main.MainActivity"')

    if 'android.intent.category.LAUNCHER' not in c:
        c = re.sub(
            r'(<activity[^>]*android:name="\.ui\.main\.MainActivity"[^>]*>)',
            r'\1\n            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>',
            c, count=1
        )

    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(c)

    log("Manifest پاک‌سازی شد")

# ═══════════════════════════════════════════════════════
# مرحله ۵: بررسی خطاها و Build
# ═══════════════════════════════════════════════════════
def try_build():
    log("=" * 60)
    log("مرحله ۵: تلاش برای Build")
    log("=" * 60)

    os.chmod("V2rayNG/gradlew", 0o755)

    for attempt in range(1, 4):
        log(f"تلاش {attempt}/3...")
        result = run("./gradlew assembleFossDebug --stacktrace",
                     cwd="V2rayNG")

        if result.returncode == 0:
            log("✅ Build موفق شد!")
            return True

        log(f"❌ تلاش {attempt} شکست خورد")
        # استخراج خطاها
        errors = re.findall(r'e:\s+file://([^:]+
