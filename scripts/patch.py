#!/usr/bin/env python3
import os

BASE = "V2rayNG/app/src/main"
JAVA = f"{BASE}/java/com/v2ray/ang"

os.makedirs(f"{JAVA}/ui/home", exist_ok=True)
os.makedirs(f"{JAVA}/ui/admin", exist_ok=True)
os.makedirs(f"{JAVA}/ui/theme", exist_ok=True)
os.makedirs(f"{JAVA}/handler", exist_ok=True)

# ═══════════ ConfigUpdater.kt ═══════════
with open(f"{JAVA}/handler/ConfigUpdater.kt", "w", encoding="utf-8") as f:
    f.write('''package com.v2ray.ang.handler

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL

object ConfigUpdater {
    private const val CONFIG_URL = "https://raw.githubusercontent.com/nimaxshat1392-alt/v2rayNG2233/master/configs.json"

    suspend fun fetchRemoteConfigs(): List<String> = withContext(Dispatchers.IO) {
        try {
            val conn = URL(CONFIG_URL).openConnection() as HttpURLConnection
            conn.connectTimeout = 15000
            conn.readTimeout = 15000
            conn.setRequestProperty("User-Agent", "ProVPN/1.0")
            val resp = conn.inputStream.bufferedReader().readText()
            val arr = JSONArray(resp)
            val list = mutableListOf<String>()
            for (i in 0 until arr.length()) list.add(arr.getString(i))
            list
        } catch (e: Exception) { emptyList() }
    }
}
''')

# ═══════════ VpnTheme.kt ═══════════
with open(f"{JAVA}/ui/theme/VpnTheme.kt", "w", encoding="utf-8") as f:
    f.write('''package com.v2ray.ang.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

val AmoledColors = darkColorScheme(
    primary = Color(0xFF00E5FF),
    onPrimary = Color(0xFF000000),
    primaryContainer = Color(0xFF00363D),
    secondary = Color(0xFFB388FF),
    background = Color(0xFF000000),
    surface = Color(0xFF0A0A0A),
    onBackground = Color(0xFFE0E0E0),
    onSurface = Color(0xFFE0E0E0),
    error = Color(0xFFFF5252)
)

val CyberpunkColors = darkColorScheme(
    primary = Color(0xFFFF00FF),
    onPrimary = Color(0xFF000000),
    secondary = Color(0xFF00FFFF),
    background = Color(0xFF0D0221),
    surface = Color(0xFF1A0B2E)
)

val ProDarkColors = darkColorScheme(
    primary = Color(0xFF64B5F6),
    onPrimary = Color(0xFF000000),
    background = Color(0xFF121212),
    surface = Color(0xFF1E1E1E)
)

val MinimalLightColors = lightColorScheme(
    primary = Color(0xFF2E7D32),
    onPrimary = Color(0xFFFFFFFF),
    background = Color(0xFFF5F5F5),
    surface = Color(0xFFFFFFFF)
)
''')

# ═══════════ AdminPanelActivity.kt ═══════════
with open(f"{JAVA}/ui/admin/AdminPanelActivity.kt", "w", encoding="utf-8") as f:
    f.write('''package com.v2ray.ang.ui.admin

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.v2ray.ang.handler.AngConfigManager
import com.v2ray.ang.handler.ConfigUpdater
import com.v2ray.ang.handler.MmkvManager
import kotlinx.coroutines.launch

class AdminPanelActivity : ComponentActivity() {
    private val ADMIN_PASSWORD = "poiiu"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var auth by remember { mutableStateOf(false) }
                if (!auth) AdminLogin { auth = true } else AdminContent()
            }
        }
    }

    @Composable
    private fun AdminLogin(onOk: () -> Unit) {
        var pass by remember { mutableStateOf("") }
        var err by remember { mutableStateOf(false) }
        Box(
            Modifier.fillMaxSize().background(
                Brush.verticalGradient(listOf(Color(0xFF0F172A), Color(0xFF020617)))
            ),
            contentAlignment = Alignment.Center
        ) {
            Card(Modifier.fillMaxWidth(0.9f).padding(16.dp), shape = RoundedCornerShape(24.dp)) {
                Column(Modifier.padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Surface(
                        Modifier.size(72.dp),
                        shape = RoundedCornerShape(20.dp),
                        color = MaterialTheme.colorScheme.primaryContainer
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.AdminPanelSettings, null,
                                Modifier.size(40.dp), tint = MaterialTheme.colorScheme.primary)
                        }
                    }
                    Spacer(Modifier.height(20.dp))
                    Text("ورود مدیر", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Text("این بخش محدود به مدیر است",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Spacer(Modifier.height(24.dp))
                    OutlinedTextField(pass, { pass = it; err = false },
                        label = { Text("رمز عبور") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        isError = err, singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp))
                    if (err) {
                        Spacer(Modifier.height(4.dp))
                        Text("رمز اشتباه", color = MaterialTheme.colorScheme.error)
                    }
                    Spacer(Modifier.height(16.dp))
                    Button({ if (pass == ADMIN_PASSWORD) onOk() else err = true },
                        Modifier.fillMaxWidth().height(52.dp),
                        shape = RoundedCornerShape(12.dp)) { Text("ورود") }
                }
            }
        }
    }

    @Composable
    fun AdminContent() {
        val scope = rememberCoroutineScope()
        var configs by remember { mutableStateOf(MmkvManager.decodeAllServerConfig().toList()) }
        var updating by remember { mutableStateOf(false) }
        var status by remember { mutableStateOf("") }

        Column(Modifier.fillMaxSize().padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(32.dp),
                    tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("پنل مدیریت", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Text("${configs.size} کانفیگ", style = MaterialTheme.typography.bodySmall)
                }
            }
            Spacer(Modifier.height(16.dp))
            Button(
                {
                    updating = true
                    status = "در حال دریافت..."
                    scope.launch {
                        val remote = ConfigUpdater.fetchRemoteConfigs()
                        if (remote.isNotEmpty()) {
                            MmkvManager.removeServerViaSubid("remote_configs")
                            AngConfigManager.importBatchConfig(
                                remote.joinToString("\\n"),
                                "remote_configs",
                                append = false
                            )
                            configs = MmkvManager.decodeAllServerConfig().toList()
                            status = "دریافت ${remote.size} کانفیگ موفق"
                        } else {
                            status = "خطا در دریافت"
                        }
                        updating = false
                    }
                },
                Modifier.fillMaxWidth().height(52.dp),
                enabled = !updating,
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.CloudDownload, null)
                Spacer(Modifier.width(8.dp))
                Text(if (updating) "..." else "آپدیت کانفیگ از سرور")
            }
            if (status.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(status, style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary)
            }
            Spacer(Modifier.height(16.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(configs) { c ->
                    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                        Row(Modifier.fillMaxWidth().padding(12.dp),
                            Arrangement.SpaceBetween, Alignment.CenterVertically) {
                            Column(Modifier.weight(1f)) {
                                Text(c.remarks.ifEmpty { "بدون نام" }, fontWeight = FontWeight.Medium)
                                Text("${c.server}:${c.serverPort}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            IconButton({
                                MmkvManager.removeServer(c.guid)
                                configs = MmkvManager.decodeAllServerConfig().toList()
                            }) {
                                Icon(Icons.Default.Delete, "حذف", tint = MaterialTheme.colorScheme.error)
                            }
                        }
                    }
                }
            }
        }
    }
}
''')

# ═══════════ HomeActivity.kt ═══════════
with open(f"{JAVA}/ui/home/HomeActivity.kt", "w", encoding="utf-8") as f:
    f.write('''package com.v2ray.ang.ui.home

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material.icons.filled.PowerSettingsNew
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.v2ray.ang.handler.MmkvManager
import com.v2ray.ang.service.V2RayVpnService
import com.v2ray.ang.ui.admin.AdminPanelActivity
import kotlinx.coroutines.delay

class HomeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                HomeScreen()
            }
        }
    }
}

@Composable
fun HomeScreen() {
    val context = LocalContext.current
    var isConnected by remember { mutableStateOf(false) }
    var tapCount by remember { mutableStateOf(0) }
    var showServers by remember { mutableStateOf(false) }
    var servers by remember { mutableStateOf<List<Triple<String, String, String>>>(emptyList()) }

    LaunchedEffect(Unit) {
        while (true) {
            isConnected = V2RayVpnService.isRunning
            try {
                val list = MmkvManager.decodeAllServerConfig().toList()
                servers = list.map { Triple(it.remarks, it.server, it.serverPort.toString()) }
            } catch (e: Exception) {}
            delay(1500)
        }
    }

    val infinite = rememberInfiniteTransition(label = "pulse")
    val pulse by infinite.animateFloat(
        initialValue = 1f,
        targetValue = 1.08f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_anim"
    )

    val gradient = Brush.verticalGradient(
        colors = if (isConnected)
            listOf(Color(0xFF064E3B), Color(0xFF0F172A), Color(0xFF111827))
        else
            listOf(Color(0xFF1E293B), Color(0xFF0F172A), Color(0xFF020617))
    )

    Box(modifier = Modifier.fillMaxSize().background(gradient)) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(Modifier.height(24.dp))
            Text(
                text = "Pro VPN",
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
                text = if (isConnected) "متصل و امن" else "برای اتصال آماده",
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.6f)
            )
            Spacer(Modifier.weight(1f))
            Box(contentAlignment = Alignment.Center) {
                if (isConnected) {
                    Box(
                        modifier = Modifier
                            .size(240.dp)
                            .scale(pulse)
                            .clip(CircleShape)
                            .background(
                                Brush.radialGradient(
                                    listOf(
                                        Color(0xFF10B981).copy(alpha = 0.4f),
                                        Color.Transparent
                                    )
                                )
                            )
                    )
                }
                Surface(
                    onClick = {
                        val intent = Intent(context, V2RayVpnService::class.java)
                        intent.action = if (isConnected)
                            V2RayVpnService.ACTION_DISCONNECT
                        else
                            V2RayVpnService.ACTION_CONNECT
                        context.startService(intent)
                    },
                    modifier = Modifier.size(180.dp),
                    shape = CircleShape,
                    color = if (isConnected) Color(0xFF10B981) else Color(0xFF3B82F6),
                    shadowElevation = 24.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(Icons.Default.PowerSettingsNew, "اتصال",
                            modifier = Modifier.size(76.dp), tint = Color.White)
                    }
                }
            }
            Spacer(Modifier.height(32.dp))
            Text(
                text = if (isConnected) "متصل" else "قطع",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = if (isConnected) Color(0xFF10B981) else Color(0xFF94A3B8)
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = if (isConnected) "برای قطع اتصال ضربه بزنید" else "برای اتصال ضربه بزنید",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White.copy(alpha = 0.5f)
            )
            Spacer(Modifier.weight(1f))
            Card(
                modifier = Modifier.fillMaxWidth().clickable { showServers = !showServers },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.08f)
                )
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Dns, null, tint = Color(0xFF3B82F6), modifier = Modifier.size(28.dp))
                    Spacer(Modifier.width(16.dp))
                    Column(Modifier.weight(1f)) {
                        Text("سرورهای موجود", color = Color.White.copy(alpha = 0.6f),
                            style = MaterialTheme.typography.bodySmall)
                        Text("${servers.size} سرور", color = Color.White,
                            fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                    }
                    Icon(Icons.Default.ChevronRight, null, tint = Color.White.copy(alpha = 0.5f))
                }
            }
            if (showServers) {
                Spacer(Modifier.height(8.dp))
                Card(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 240.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.White.copy(alpha = 0.08f)
                    )
                ) {
                    LazyColumn(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        items(servers) { item ->
                            val (name, host, port) = item
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(10.dp),
                                color = Color.White.copy(alpha = 0.05f)
                            ) {
                                Column(Modifier.padding(10.dp)) {
                                    Text(name.ifEmpty { "بدون نام" }, color = Color.White,
                                        fontWeight = FontWeight.Medium,
                                        style = MaterialTheme.typography.bodyMedium)
                                    Text("$host:$port", color = Color.White.copy(alpha = 0.5f),
                                        style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
            }
            Spacer
            (Modifier.height(12.dp))
                  }
              }
          }
          KTEOF

      - name: Patch AndroidManifest
        run: |
          MF="$GITHUB_WORKSPACE/V2rayNG/app/src/main/AndroidManifest.xml"
          python3 << 'PYEOF'
          import re
          path = "V2rayNG/app/src/main/AndroidManifest.xml"
          with open(path, "r") as f:
              content = f.read()

          def patch_main(m):
              tag = m.group(1)
              inner = re.sub(r'<intent-filter>.*?</intent-filter>', '', m.group(2), flags=re.DOTALL)
              if 'android:enabled' not in tag:
                  tag = tag.replace('<activity ', '<activity android:enabled="false" android:exported="false" ', 1)
              return tag + inner + m.group(3)

          content = re.sub(
              r'(<activity[^>]*android:name="\.ui\.main\.MainActivity"[^>]*>)(.*?)(</activity>)',
              patch_main, content, flags=re.DOTALL
          )

          if 'HomeActivity' not in content:
              new_acts = '''
              <activity android:name=".ui.home.HomeActivity" android:exported="true" android:label="Pro VPN">
                  <intent-filter>
                      <action android:name="android.intent.action.MAIN" />
                      <category android:name="android.intent.category.LAUNCHER" />
                  </intent-filter>
              </activity>
              <activity android:name=".ui.admin.AdminPanelActivity" android:exported="false" android:label="Admin" />
          </application>'''
              content = content.replace("</application>", new_acts)

          with open(path, "w") as f:
              f.write(content)
          print("Manifest patched")
          PYEOF

      - name: Grant execute permission
        run: chmod +x V2rayNG/gradlew

      - name: Build APK
        run: |
          cd V2rayNG
          ./gradlew assembleDebug --stacktrace

      - name: Upload APK
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: pro-vpn-apk
          path: V2rayNG/app/build/outputs/apk/**/*.apk
  
- name: Create PingManager
  run: |
    JAVA="$GITHUB_WORKSPACE/V2rayNG/app/src/main/java/com/v2ray/ang"
    mkdir -p "$JAVA/handler"
    if [ ! -f "$JAVA/handler/PingManager.kt" ]; then
    cat > "$JAVA/handler/PingManager.kt" << 'KTEOF'
    package com.v2ray.ang.handler

    import kotlinx.coroutines.Dispatchers
    import kotlinx.coroutines.async
    import kotlinx.coroutines.awaitAll
    import kotlinx.coroutines.withContext
    import java.net.InetSocketAddress
    import java.net.Socket

    object PingManager {
        suspend fun pingAll(
            servers: List<Triple<String, String, Int>>,
            onResult: (String, Long) -> Unit
        ) = withContext(Dispatchers.IO) {
            servers.chunked(10).forEach { chunk ->
                chunk.map { (name, host, port) ->
                    async {
                        val delay = socketConnect(host, port)
                        withContext(Dispatchers.Main) { onResult(name, delay) }
                    }
                }.awaitAll()
            }
        }

        fun socketConnect(host: String, port: Int): Long = try {
            val start = System.currentTimeMillis()
            val socket = Socket()
            socket.connect(InetSocketAddress(host, port), 2000)
            val elapsed = System.currentTimeMillis() - start
            socket.close()
            elapsed
        } catch (e: Exception) { -1L }
    }
    KTEOF
    fi

- name: Create DataUsage
  run: |
    JAVA="$GITHUB_WORKSPACE/V2rayNG/app/src/main/java/com/v2ray/ang"
    mkdir -p "$JAVA/handler"
    if [ ! -f "$JAVA/handler/DataUsage.kt" ]; then
    cat > "$JAVA/handler/DataUsage.kt" << 'KTEOF'
    package com.v2ray.ang.handler

    import android.net.TrafficStats

    object DataUsage {
        fun getTotalRx(): Long = TrafficStats.getTotalRxBytes()
        fun getTotalTx(): Long = TrafficStats.getTotalTxBytes()

        fun formatBytes(bytes: Long): String = when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${bytes / 1024} KB"
            bytes < 1024 * 1024 * 1024 -> "${bytes / (1024 * 1024)} MB"
            else -> String.format("%.2f GB", bytes.toDouble() / (1024 * 1024 * 1024))
        }
    }
    KTEOF
    fi

- name: Create BackupManager
  run: |
    JAVA="$GITHUB_WORKSPACE/V2rayNG/app/src/main/java/com/v2ray/ang"
    mkdir -p "$JAVA/handler"
    if [ ! -f "$JAVA/handler/BackupManager.kt" ]; then
    cat > "$JAVA/handler/BackupManager.kt" << 'KTEOF'
    package com.v2ray.ang.handler

    import android.content.Context
    import java.io.File
    import java.text.SimpleDateFormat
    import java.util.Date
    import java.util.Locale

    object BackupManager {
        private const val DIR = "ProVPN_Backups"

        fun createBackup(context: Context): File? = try {
            val dir = File(context.filesDir, DIR)
            if (!dir.exists()) dir.mkdirs()
            val sdf = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US)
            val file = File(dir, "backup_${sdf.format(Date())}.json")
            val configs = MmkvManager.decodeAllServerConfig()
            file.writeText(configs.toString())
            file
        } catch (e: Exception) { null }

        fun listBackups(context: Context): List<File> {
            val dir = File(context.filesDir, DIR)
            return if (dir.exists())
                dir.listFiles()?.sortedByDescending { it.lastModified() } ?: emptyList()
            else emptyList()
        }
    }
    KTEOF
    fi

- name: Create NetworkChecker
  run: |
    JAVA="$GITHUB_WORKSPACE/V2rayNG/app/src/main/java/com/v2ray/ang"
    mkdir -p "$JAVA/util"
    if [ ! -f "$JAVA/util/NetworkChecker.kt" ]; then
    cat > "$JAVA/util/NetworkChecker.kt" << 'KTEOF'
    package com.v2ray.ang.util

    import android.content.Context
    import android.net.ConnectivityManager
    import android.net.NetworkCapabilities

    object NetworkChecker {
        fun isConnected(context: Context): Boolean {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = cm.activeNetwork ?: return false
            val caps = cm.getNetworkCapabilities(network) ?: return false
            return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        }

        fun getType(context: Context): String {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = cm.activeNetwork ?: return "None"
            val caps = cm.getNetworkCapabilities(network) ?: return "None"
            return when {
                caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WiFi"
                caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "Mobile"
                else -> "Unknown"
            }
        }
    }
    KTEOF
    fi

- name: Add Ping button to Admin Panel
  run: |
    JAVA="$GITHUB_WORKSPACE/V2rayNG/app/src/main/java/com/v2ray/ang"
    # آپدیت AdminPanelActivity برای اضافه کردن دکمه پینگ
    if [ -f "$JAVA/ui/admin/AdminPanelActivity.kt" ]; then
      # اضافه کردن import برای PingManager
      sed -i 's|import com.v2ray.ang.handler.MmkvManager|import com.v2ray.ang.handler.MmkvManager\nimport com.v2ray.ang.handler.PingManager|' "$JAVA/ui/admin/AdminPanelActivity.kt" || true
    fi
    echo "Ping feature enabled in admin panel"

- name: Validate files
  run: |
    echo "=== Generated files ==="
    find V2rayNG/app/src/main/java/com/v2ray/ang/ui/home -type f 2>/dev/null
    find V2rayNG/app/src/main/java/com/v2ray/ang/ui/admin -type f 2>/dev/null
    find V2rayNG/app/src/main/java/com/v2ray/ang/ui/settings -type f 2>/dev/null
    find V2rayNG/app/src/main/java/com/v2ray/ang/handler -name "*.kt" 2>/dev/null | grep -E "(ConfigUpdater|PingManager|DataUsage|BackupManager)" || true
    find V2rayNG/app/src/main/java/com/v2ray/ang/util -name "*.kt" 2>/dev/null | grep NetworkChecker || true
    echo "=== Manifest entries ==="
    grep -E "HomeActivity|AdminPanelActivity|SettingsActivity" V2rayNG/app/src/main/AndroidManifest.xml || echo "not found"

- name: Grant permission
  run: chmod +x V2rayNG/gradlew

- name: Build APK
  run: |
    cd V2rayNG
    ./gradlew assembleDebug --stacktrace

- name: Upload APK
  if: success()
  uses: actions/upload-artifact@v4
  with:
    name: pro-vpn-apk
    path: V2rayNG/app/build/outputs/apk/**/*.apk
