#!/usr/bin/env python3
import os
import re

BASE = "V2rayNG/app/src/main"
JAVA = f"{BASE}/java/com/v2ray/ang"

for d in ["ui/home", "ui/admin", "ui/theme", "ui/settings", "handler", "util"]:
    os.makedirs(f"{JAVA}/{d}", exist_ok=True)

def w(path, content):
    full = f"{JAVA}/{path}"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {path}")

# ═══════════ ConfigUpdater.kt ═══════════
CONFIG_UPDATER = r'''package com.v2ray.ang.handler

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
'''
w("handler/ConfigUpdater.kt", CONFIG_UPDATER)

# ═══════════ VpnTheme.kt ═══════════
VPN_THEME = r'''package com.v2ray.ang.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

val AmoledColors = darkColorScheme(
    primary = Color(0xFF00E5FF),
    onPrimary = Color(0xFF000000),
    background = Color(0xFF000000),
    surface = Color(0xFF0A0A0A)
)

val CyberpunkColors = darkColorScheme(
    primary = Color(0xFFFF00FF),
    secondary = Color(0xFF00FFFF),
    background = Color(0xFF0D0221),
    surface = Color(0xFF1A0B2E)
)

val ProDarkColors = darkColorScheme(
    primary = Color(0xFF64B5F6),
    background = Color(0xFF121212),
    surface = Color(0xFF1E1E1E)
)

val MinimalLightColors = lightColorScheme(
    primary = Color(0xFF2E7D32),
    background = Color(0xFFF5F5F5),
    surface = Color(0xFFFFFFFF)
)
'''
w("ui/theme/VpnTheme.kt", VPN_THEME)

# ═══════════ AdminPanelActivity.kt ═══════════
ADMIN_PANEL = r'''package com.v2ray.ang.ui.admin

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
            Card(
                Modifier.fillMaxWidth(0.9f).padding(16.dp),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(
                    Modifier.padding(28.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Surface(
                        Modifier.size(72.dp),
                        shape = RoundedCornerShape(20.dp),
                        color = MaterialTheme.colorScheme.primaryContainer
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                Icons.Default.AdminPanelSettings, null,
                                Modifier.size(40.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                    Spacer(Modifier.height(20.dp))
                    Text(
                        "ورود مدیر",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "دسترسی محدود",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(Modifier.height(24.dp))
                    OutlinedTextField(
                        pass, { pass = it; err = false },
                        label = { Text("رمز عبور") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        isError = err, singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )
                    if (err) {
                        Spacer(Modifier.height(4.dp))
                        Text("رمز اشتباه", color = MaterialTheme.colorScheme.error)
                    }
                    Spacer(Modifier.height(16.dp))
                    Button(
                        { if (pass == ADMIN_PASSWORD) onOk() else err = true },
                        Modifier.fillMaxWidth().height(52.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) { Text("ورود") }
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
                Icon(
                    Icons.Default.AdminPanelSettings, null,
                    Modifier.size(32.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(Modifier.width(12.dp))
                Column {
                    Text(
                        "پنل مدیریت",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        configs.size.toString() + " کانفیگ",
                        style = MaterialTheme.typography.bodySmall
                    )
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
                                remote.joinToString("\n"),
                                "remote_configs",
                                append = false
                            )
                            configs = MmkvManager.decodeAllServerConfig().toList()
                            status = "دریافت " + remote.size + " کانفیگ موفق"
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
                Text(
                    status,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            Spacer(Modifier.height(16.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(configs) { c ->
                    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                        Row(
                            Modifier.fillMaxWidth().padding(12.dp),
                            Arrangement.SpaceBetween,
                            Alignment.CenterVertically
                        ) {
                            Column(Modifier.weight(1f)) {
                                Text(
                                    c.remarks.ifEmpty { "بدون نام" },
                                    fontWeight = FontWeight.Medium
                                )
                                Text(
                                    c.server + ":" + c.serverPort,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            IconButton({
                                MmkvManager.removeServer(c.guid)
                                configs = MmkvManager.decodeAllServerConfig().toList()
                            }) {
                                Icon(
                                    Icons.Default.Delete, "حذف",
                                    tint = MaterialTheme.colorScheme.error
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
'''
w("ui/admin/AdminPanelActivity.kt", ADMIN_PANEL)

# ═══════════ HomeActivity.kt ═══════════
HOME_ACTIVITY = r'''package com.v2ray.ang.ui.home

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
import androidx.compose.material.icons.filled.Settings
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
        setContent { MaterialTheme { HomeScreen() } }
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
        initialValue = 1f, targetValue = 1.08f,
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
                        context.startActivity(
                            Intent(context, AdminPanelActivity::class.java)
                        )
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
                        Icon(
                            Icons.Default.PowerSettingsNew, "اتصال",
                            modifier = Modifier.size(76.dp),
                            tint = Color.White
                        )
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
                    Icon(
                        Icons.Default.Dns, null,
                        tint = Color(0xFF3B82F6),
                        modifier = Modifier.size(28.dp)
                    )
                    Spacer(Modifier.width(16.dp))
                    Column(Modifier.weight(1f)) {
                        Text(
                            "سرورهای موجود",
                            color = Color.White.copy(alpha = 0.6f),
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            servers.size.toString() + " سرور",
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                    Icon(
                        Icons.Default.ChevronRight, null,
                        tint = Color.White.copy(alpha = 0.5f)
                    )
                }
            }
            if (showServers) {
                Spacer(Modifier.height(8.dp))
                Card(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 240.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.White.co
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
                            val name = item.first
                            val host = item.second
                            val port = item.third
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(10.dp),
                                color = Color.White.copy(alpha = 0.05f)
                            ) {
                                Column(Modifier.padding(10.dp)) {
                                    Text(
                                        name.ifEmpty { "بدون نام" },
                                        color = Color.White,
                                        fontWeight = FontWeight.Medium,
                                        style = MaterialTheme.typography.bodyMedium
                                    )
                                    Text(
                                        host + ":" + port,
                                        color = Color.White.copy(alpha = 0.5f),
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                            }
                        }
                    }
                }
            }
            Spacer(Modifier.height(12.dp))
        }
    }
}
'''
w("ui/home/HomeActivity.kt", HOME_ACTIVITY)

# ═══════════ Patch AndroidManifest ═══════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r'(<activity[^>]*android:name="\.ui\.main\.MainActivity"[^>]*>)(.*?)(</activity>)'

def patch_main(m):
    tag = m.group(1)
    inner = re.sub(r'<intent-filter>.*?</intent-filter>', '', m.group(2), flags=re.DOTALL)
    if 'android:enabled' not in tag:
        tag = tag.replace('<activity ', '<activity android:enabled="false" android:exported="false" ', 1)
    return tag + inner + m.group(3)

content = re.sub(pattern, patch_main, content, flags=re.DOTALL)

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

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

# ═══════════ Patch strings.xml ═══════════
strings_path = f"{BASE}/res/values/strings.xml"
if os.path.exists(strings_path):
    with open(strings_path, "r", encoding="utf-8") as f:
        s = f.read()
    s = re.sub(
        r'<string name="app_name">.*?</string>',
        '<string name="app_name">Pro VPN</string>',
        s
    )
    with open(strings_path, "w", encoding="utf-8") as f:
        f.write(s)

print("Done! All files created successfully.")
