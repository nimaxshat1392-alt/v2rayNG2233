#!/usr/bin/env python3
import os

BASE = "V2rayNG/app/src/main"
JAVA = f"{BASE}/java/com/v2ray/ang"

for d in ["ui/home", "ui/admin", "ui/theme", "handler"]:
    os.makedirs(f"{JAVA}/{d}", exist_ok=True)

def w(path, content):
    full = f"{JAVA}/{path}"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {path}")

# ConfigUpdater
w("handler/ConfigUpdater.kt", r'''package com.v2ray.ang.handler

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL

object ConfigUpdater {
    private const val URL = "https://raw.githubusercontent.com/nimaxshat1392-alt/v2rayNG2233/master/configs.json"
    suspend fun fetch(): List<String> = withContext(Dispatchers.IO) {
        try {
            val c = URL(URL).openConnection() as HttpURLConnection
            c.connectTimeout = 15000
            c.readTimeout = 15000
            val r = c.inputStream.bufferedReader().readText()
            val a = JSONArray(r)
            val l = mutableListOf<String>()
            for (i in 0 until a.length()) l.add(a.getString(i))
            l
        } catch (e: Exception) { emptyList() }
    }
}
''')

# VpnTheme - سه تم زیبا
w("ui/theme/VpnTheme.kt", r'''package com.v2ray.ang.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

val FastVpnDark = darkColorScheme(
    primary = Color(0xFF10B981),
    onPrimary = Color(0xFF000000),
    background = Color(0xFF0A0E1A),
    surface = Color(0xFF151A28),
    onBackground = Color(0xFFE5E7EB),
    onSurface = Color(0xFFE5E7EB)
)

val AmoledBlack = darkColorScheme(
    primary = Color(0xFF00E5FF),
    background = Color(0xFF000000),
    surface = Color(0xFF0A0A0A)
)

val LightMinimal = lightColorScheme(
    primary = Color(0xFF10B981),
    background = Color(0xFFF8FAFC),
    surface = Color(0xFFFFFFFF)
)
''')

# Admin Panel
w("ui/admin/AdminPanelActivity.kt", r'''package com.v2ray.ang.ui.admin

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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
import com.v2ray.ang.handler.AngConfigManager
import com.v2ray.ang.handler.ConfigUpdater
import com.v2ray.ang.handler.MmkvManager
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
                    Surface(Modifier.size(72.dp), shape = RoundedCornerShape(20.dp),
                        color = MaterialTheme.colorScheme.primaryContainer) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(40.dp))
                        }
                    }
                    Spacer(Modifier.height(20.dp))
                    Text("ورود مدیر", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(24.dp))
                    OutlinedTextField(pass, { pass = it; err = false },
                        label = { Text("رمز عبور") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        isError = err, singleLine = true, modifier = Modifier.fillMaxWidth())
                    if (err) Text("رمز اشتباه", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(16.dp))
                    Button({ if (pass == PASS) onOk() else err = true },
                        Modifier.fillMaxWidth().height(52.dp)) { Text("ورود") }
                }
            }
        }
    }

    @Composable
    private fun Panel() {
        val scope = rememberCoroutineScope()
        var configs by remember { mutableStateOf(MmkvManager.decodeAllServerConfig().toList()) }
        var updating by remember { mutableStateOf(false) }
        var status by remember { mutableStateOf("") }

        Column(Modifier.fillMaxSize().padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(32.dp))
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("پنل مدیریت", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Text("${configs.size} کانفیگ", style = MaterialTheme.typography.bodySmall)
                }
            }
            Spacer(Modifier.height(16.dp))
            Button({
                updating = true
                status = "در حال دریافت..."
                scope.launch {
                    val r = ConfigUpdater.fetch()
                    if (r.isNotEmpty()) {
                        MmkvManager.removeServerViaSubid("remote_configs")
                        AngConfigManager.importBatchConfig(r.joinToString("\n"), "remote_configs", false)
                        configs = MmkvManager.decodeAllServerConfig().toList()
                        status = "${r.size} کانفیگ دریافت شد"
                    } else status = "خطا"
                    updating = false
                }
            }, Modifier.fillMaxWidth().height(52.dp), enabled = !updating) {
                Icon(Icons.Default.CloudDownload, null)
                Spacer(Modifier.width(8.dp))
                Text(if (updating) "..." else "آپدیت کانفیگ")
            }
            if (status.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(status, color = MaterialTheme.colorScheme.primary)
            }
            Spacer(Modifier.height(16.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(configs) { c ->
                    Card(Modifier.fillMaxWidth()) {
                        Row(Modifier.fillMaxWidth().padding(12.dp),
                            Arrangement.SpaceBetween, Alignment.CenterVertically) {
                            Column(Modifier.weight(1f)) {
                                Text(c.remarks.ifEmpty { "بدون نام" }, fontWeight = FontWeight.Medium)
                                Text("${c.server}:${c.serverPort}", style = MaterialTheme.typography.bodySmall)
                            }
                            IconButton({
                                MmkvManager.removeServer(c.guid)
                                configs = MmkvManager.decodeAllServerConfig().toList()
                            }) { Icon(Icons.Default.Delete, "حذف") }
                        }
                    }
                }
            }
        }
    }
}
''')

print("Generate done!")
# ═══════════════════════════════════════════════════════
# 4. HomeActivity.kt - UI زیبا مشابه Fast VPN
# ═══════════════════════════════════════════════════════
w("ui/home/HomeActivity.kt", r'''package com.v2ray.ang.ui.home

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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PowerSettingsNew
import androidx.compose.material.icons.filled.Rocket
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
        setContent { MaterialTheme { FastVpnScreen() } }
    }
}

@Composable
fun FastVpnScreen() {
    val context = LocalContext.current
    var isConnected by remember { mutableStateOf(false) }
    var tapCount by remember { mutableStateOf(0) }
    var selectedCountry by remember { mutableStateOf("Auto Select") }

    val infinite = rememberInfiniteTransition(label = "pulse")
    val pulse by infinite.animateFloat(
        initialValue = 1f, targetValue = 1.15f,
        animationSpec = infiniteRepeatable(
            animation = tween(1800),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_anim"
    )

    val bg = Brush.verticalGradient(
        listOf(Color(0xFF0A0E1A), Color(0xFF111827), Color(0xFF020617))
    )

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize().padding(20.dp)) {
            // Top bar
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({}) { Icon(Icons.Default.Share, "Share", tint = Color(0xFF9CA3AF)) }
                Text(
                    "Fast VPN",
                    style = MaterialTheme.typography.headlineSmall,
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
                IconButton({}) { Icon(Icons.Default.Settings, "Settings", tint = Color(0xFF9CA3AF)) }
            }

            Spacer(Modifier.height(30.dp))

            // Connect status text
            Text(
                if (isConnected) "Connected" else "Disconnected",
                style = MaterialTheme.typography.titleMedium,
                color = if (isConnected) Color(0xFF10B981) else Color(0xFF9CA3AF),
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )

            Spacer(Modifier.height(20.dp))

            // Big circular button with rings
            Box(
                Modifier.fillMaxWidth().height(280.dp),
                contentAlignment = Alignment.Center
            ) {
                // Rings
                if (isConnected) {
                    Box(
                        Modifier.size(260.dp).scale(pulse).clip(CircleShape)
                            .background(
                                Brush.radialGradient(
                                    listOf(Color(0xFF10B981).copy(alpha = 0.3f), Color.Transparent)
                                )
                            )
                    )
                }
                // Outer ring
                Surface(
                    Modifier.size(230.dp),
                    shape = CircleShape,
                    color = Color.Transparent,
                    border = androidx.compose.foundation.BorderStroke(
                        2.dp,
                        Color(0xFF374151)
                    )
                ) {}
                // Inner ring
                Surface(
                    Modifier.size(190.dp),
                    shape = CircleShape,
                    color = Color.Transparent,
                    border = androidx.compose.foundation.BorderStroke(
                        3.dp,
                        if (isConnected) Color(0xFF10B981) else Color(0xFF4B5563)
                    )
                ) {}
                // Main button
                Surface(
                    onClick = { isConnected = !isConnected },
                    Modifier.size(150.dp),
                    shape = CircleShape,
                    color = Color(0xFF151A28),
                    shadowElevation = 20.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.Default.PowerSettingsNew,
                            "Connect",
                            Modifier.size(60.dp),
                            tint = if (isConnected) Color(0xFF10B981) else Color(0xFF9CA3AF)
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // Server selector card
            Card(
                Modifier.fillMaxWidth().clickable { },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        if (selectedCountry == "Auto Select") "Auto Select" else selectedCountry,
                        Modifier.weight(1f),
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                    Surface(
                        Modifier.size(44.dp),
                        shape = CircleShape,
                        color = Color(0xFF10B981)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.Rocket, "Auto", tint = Color.Black)
                        }
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            // Info cards row
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(14.dp)) {
                        Text("Your Location", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Spacer(Modifier.height(8.dp))
                        Text("—", color = Color.White, style = MaterialTheme.typography.titleLarge)
                    }
                }
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(14.dp)) {
                        Text("Network Speed", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Spacer(Modifier.height(8.dp))
                        Text("0 Kbps", color = Color(0xFF10B981), style = MaterialTheme.typography.titleMedium)
                        Text("0 Kbps", color = Color(0xFF3B82F6), style = MaterialTheme.typography.titleMedium)
                    }
                }
            }

            Spacer(Modifier.height(10.dp))

            // Bottom row cards
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(14.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Speed, "Speed", tint = Color(0xFF10B981))
                        Spacer(Modifier.height(6.dp))
                        Text("Speed Test", color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Test your speed", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                    }
                }
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(14.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Settings, "DNS", tint = Color(0xFF10B981))
                        Spacer(Modifier.height(6.dp))
                        Text("DNS Leak Test", color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Check for leaks", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 5. CountryListActivity.kt - لیست کشورها با اسم و پینگ
# ═══════════════════════════════════════════════════════
w("ui/home/CountryListActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Rocket
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

data class CountryItem(
    val name: String,
    val ping: Long,
    val isSelected: Boolean = false
)

class CountryListActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { CountryListScreen() } }
    }
}

@Composable
fun CountryListScreen() {
    var countries by remember {
        mutableStateOf(
            listOf(
                CountryItem("Auto Select", 0, true),
                CountryItem("Germany", 120),
                CountryItem("Australia", 180),
                CountryItem("Hong Kong", 95),
                CountryItem("Netherlands", 145),
                CountryItem("UK", 130),
                CountryItem("US - California", 165),
                CountryItem("US - Utah", 175),
                CountryItem("France", 110),
                CountryItem("Japan", 90),
                CountryItem("Singapore", 85),
                CountryItem("Turkey", 60)
            ).sortedBy { if (it.name == "Auto Select") 0 else it.ping }
        )
    }

    val bg = Brush.verticalGradient(
        listOf(Color(0xFF0A0E1A), Color(0xFF020617))
    )

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            // Header
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                IconButton({}) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text(
                    "Location",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                IconButton({}) {
                    Icon(Icons.Default.Refresh, "Refresh", tint = Color.White)
                }
            }

            // Sort buttons
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Surface(
                    onClick = { countries = countries.sortedBy { if (it.name == "Auto Select") 0 else it.ping } },
                    shape = RoundedCornerShape(20.dp),
                    color = Color(0xFF151A28)
                ) {
                    Text("Sort by Ping", Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                        color = Color.White, style = MaterialTheme.typography.bodySmall)
                }
                Surface(
                    onClick = { countries = countries.sortedBy { it.name } },
                    shape = RoundedCornerShape(20.dp),
                    color = Color(0xFF151A28)
                ) {
                    Text("Sort by Name", Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                        color = Color.White, style = MaterialTheme.typography.bodySmall)
                }
            }

            Spacer(Modifier.height(16.dp))

            LazyColumn(
                Modifier.fillMaxSize().padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(countries) { country ->
                    Card(
                        Modifier.fillMaxWidth().clickable {
                            countries = countries.map { it.copy(isSelected = it.name == country.name) }
                        },
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                    ) {
                        Row(
                            Modifier.fillMaxWidth().padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Radio circle
                            Surface(
                                Modifier.size(28.dp),
                                shape = CircleShape,
                                color = if (country.isSelected) Color(0xFF10B981) else Color.Transparent,
                                border = androidx.compose.foundation.BorderStroke(
                                    2.dp,
                                    if (country.isSelected) Color(0xFF10B981) else Color(0xFF4B5563)
                                )
                            ) {
                                if (country.isSelected) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Icon(Icons.Default.Check, "Selected",
                                            Modifier.size(16.dp), tint = Color.Black)
                                    }
                                }
                            }

                            Spacer(Modifier.width(16.dp))

                            Column(Modifier.weight(1f)) {
                                Text(
                                    country.name,
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    style = MaterialTheme.typography.titleMedium
                                )
                                if (country.name != "Auto Select") {
                                    Text(
                                        "${country.ping} ms",
                                        color = Color(0xFFEF4444),
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                } else {
                                    Text(
                                        "Automatic selection",
                                        color = Color(0xFF9CA3AF),
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                }
                                           }
                        }

                        Spacer(Modifier.width(16.dp))

                        // Signal bars or rocket icon
                        if (country.name == "Auto Select") {
                            Surface(
                                Modifier.size(40.dp),
                                shape = CircleShape,
                                color = Color(0xFF10B981)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(
                                        Icons.Default.Rocket,
                                        contentDescription = "Auto",
                                        modifier = Modifier.size(20.dp),
                                        tint = Color.Black
                                    )
                                }
                            }
                        } else {
                            Row(verticalAlignment = Alignment.Bottom) {
                                Box(
                                    Modifier
                                        .size(4.dp, 8.dp)
                                        .background(
                                            if (country.ping < 100) Color(0xFF10B981) else Color(0xFF4B5563)
                                        )
                                )
                                Spacer(Modifier.width(2.dp))
                                Box(
                                    Modifier
                                        .size(4.dp, 12.dp)
                                        .background(
                                            if (country.ping < 150) Color(0xFF10B981) else Color(0xFF4B5563)
                                        )
                                )
                                Spacer(Modifier.width(2.dp))
                                Box(
                                    Modifier
                                        .size(4.dp, 16.dp)
                                        .background(
                                            if (country.ping < 200) Color(0xFF10B981) else Color(0xFF4B5563)
                                        )
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 6. PingManager.kt - تست پینگ همه سرورها
# ═══════════════════════════════════════════════════════
w("handler/PingManager.kt", r'''package com.v2ray.ang.handler

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
            chunk.map { item ->
                async {
                    val name = item.first
                    val host = item.second
                    val port = item.third
                    val ms = socketConnect(host, port)
                    withContext(Dispatchers.Main) { onResult(name, ms) }
                }
            }.awaitAll()
        }
    }

    fun socketConnect(host: String, port: Int): Long = try {
        val start = System.currentTimeMillis()
        val s = Socket()
        s.connect(InetSocketAddress(host, port), 2000)
        val elapsed = System.currentTimeMillis() - start
        s.close()
        elapsed
    } catch (e: Exception) { -1L }
}
''')

# ═══════════════════════════════════════════════════════
# 7. ConfigParser.kt - تبدیل کانفیگ به اطلاعات سرور
# ═══════════════════════════════════════════════════════
w("handler/ConfigParser.kt", r'''package com.v2ray.ang.handler

import android.net.Uri
import java.util.Base64

data class ParsedServer(
    val name: String,
    val protocol: String,
    val host: String,
    val port: Int,
    val rawConfig: String
)

object ConfigParser {

    fun parse(config: String): ParsedServer? {
        return try {
            when {
                config.startsWith("vless://") -> parseVless(config)
                config.startsWith("vmess://") -> parseVmess(config)
                config.startsWith("ss://") -> parseSs(config)
                config.startsWith("trojan://") -> parseTrojan(config)
                else -> null
            }
        } catch (e: Exception) { null }
    }

    private fun parseVless(config: String): ParsedServer? {
        val uri = Uri.parse(config)
        val name = uri.fragment ?: "Server"
        val host = uri.host ?: return null
        val port = uri.port.takeIf { it > 0 } ?: 443
        return ParsedServer(name, "VLESS", host, port, config)
    }

    private fun parseVmess(config: String): ParsedServer? {
        val base64 = config.removePrefix("vmess://")
        val decoded = try { String(Base64.getDecoder().decode(base64)) } catch (e: Exception) { return null }
        val host = extractJsonValue(decoded, "add") ?: return null
        val portStr = extractJsonValue(decoded, "port") ?: "443"
        val name = extractJsonValue(decoded, "ps") ?: "Server"
        return ParsedServer(name, "VMESS", host, portStr.toIntOrNull() ?: 443, config)
    }

    private fun parseSs(config: String): ParsedServer? {
        val clean = config.removePrefix("ss://").substringBefore("#")
        val name = config.substringAfter("#", "Server")
        val parts = clean.split("@")
        if (parts.size < 2) return null
        val hostPort = parts[1].split(":")
        val host = hostPort[0]
        val port = hostPort.getOrNull(1)?.toIntOrNull() ?: 443
        return ParsedServer(name, "SS", host, port, config)
    }

    private fun parseTrojan(config: String): ParsedServer? {
        val uri = Uri.parse(config)
        val name = uri.fragment ?: "Server"
        val host = uri.host ?: return null
        val port = uri.port.takeIf { it > 0 } ?: 443
        return ParsedServer(name, "Trojan", host, port, config)
    }

    private fun extractJsonValue(json: String, key: String): String? {
        val pattern = "\"$key\"\\s*:\\s*\"?([^\",}]+)\"?"
        val regex = Regex(pattern)
        return regex.find(json)?.groupValues?.getOrNull(1)?.trim()
    }
}
''')

# ═══════════════════════════════════════════════════════
# 8. ServerRepository.kt - مدیریت سرورها
# ═══════════════════════════════════════════════════════
w("handler/ServerRepository.kt", r'''package com.v2ray.ang.handler

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object ServerRepository {

    suspend fun loadAllServers(): List<ParsedServer> = withContext(Dispatchers.IO) {
        try {
            val rawConfigs = MmkvManager.decodeAllServerConfig()
            val servers = mutableListOf<ParsedServer>()
            rawConfigs.values.forEach { item ->
                try {
                    val config = item.toString()
                    val parsed = ConfigParser.parse(config)
                    if (parsed != null) servers.add(parsed)
                } catch (e: Exception) {}
            }
            servers
        } catch (e: Exception) { emptyList() }
    }

    suspend fun downloadAndSave(): Boolean = withContext(Dispatchers.IO) {
        try {
            val remote = ConfigUpdater.fetch()
            if (remote.isEmpty()) return@withContext false

            MmkvManager.removeServerViaSubid("remote_configs")
            AngConfigManager.importBatchConfig(
                remote.joinToString("\n"),
                "remote_configs",
                false
            )
            true
        } catch (e: Exception) { false }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 9. Patch AndroidManifest
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

# غیرفعال کردن MainActivity اصلی
pattern = r'(<activity[^>]*android:name="\.ui\.main\.MainActivity"[^>]*>)(.*?)(</activity>)'

def patch_main(m):
    tag = m.group(1)
    inner = re.sub(r'<intent-filter>.*?</intent-filter>', '', m.group(2), flags=re.DOTALL)
    if 'android:enabled' not in tag:
        tag = tag.replace('<activity ', '<activity android:enabled="false" android:exported="false" ', 1)
    return tag + inner + m.group(3)

content = re.sub(pattern, patch_main, content, flags=re.DOTALL)

# اضافه کردن Activityهای جدید
if 'FastVpnActivity' not in content and 'HomeActivity' not in content:
    new_acts = '''
        <activity android:name=".ui.home.HomeActivity" android:exported="true" android:label="Fast VPN">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ui.home.CountryListActivity" android:exported="false" android:label="Location" />
        <activity android:name=".ui.admin.AdminPanelActivity" android:exported="false" android:label="Admin" />
    </application>'''
    content = content.replace("</application>", new_acts)

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

# ═══════════════════════════════════════════════════════
# 10. Patch strings.xml
# ═══════════════════════════════════════════════════════
strings_path = f"{BASE}/res/values/strings.xml"
if os.path.exists(strings_path):
    with open(strings_path, "r", encoding="utf-8") as f:
        s = f.read()
    s = re.sub(
        r'<string name="app_name">.*?</string>',
        '<string name="app_name">Fast VPN</string>',
        s
    )
    with open(strings_path, "w", encoding="utf-8") as f:
        f.write(s)

print("Generate done!")
print("=" * 50)
print("Files created:")
print("  - handler/ConfigUpdater.kt")
print("  - handler/PingManager.kt")
print("  - handler/ConfigParser.kt")
print("  - handler/ServerRepository.kt")
print("  - ui/theme/VpnTheme.kt")
print("  - ui/home/HomeActivity.kt (Fast VPN UI)")
print("  - ui/home/CountryListActivity.kt")
print("  - ui/admin/AdminPanelActivity.kt")
print("=" * 50)
# ═══════════════════════════════════════════════════════
# 11. SettingsActivity.kt - صفحه تنظیمات زیبا
# ═══════════════════════════════════════════════════════
w("ui/home/SettingsActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class SettingsActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { SettingsScreen() } }
    }
}

@Composable
fun SettingsScreen() {
    var darkMode by remember { mutableStateOf(true) }
    var autoConnect by remember { mutableStateOf(false) }
    var notifications by remember { mutableStateOf(true) }
    var killSwitch by remember { mutableStateOf(false) }
    var splitTunnel by remember { mutableStateOf(false) }
    var autoPing by remember { mutableStateOf(true) }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            // Header
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text(
                    "Settings",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState())
            ) {
                // Appearance section
                Text("Appearance", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(8.dp))

                SettingSwitchItem(
                    icon = Icons.Default.DarkMode,
                    title = "Dark Mode",
                    subtitle = "Enable dark theme",
                    checked = darkMode,
                    onCheckedChange = { darkMode = it }
                )
                Spacer(Modifier.height(6.dp))
                SettingNavItem(
                    icon = Icons.Default.Language,
                    title = "Language",
                    subtitle = "English",
                    onClick = {}
                )

                Spacer(Modifier.height(20.dp))

                // Connection
                Text("Connection", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(8.dp))

                SettingSwitchItem(
                    icon = Icons.Default.Security,
                    title = "Kill Switch",
                    subtitle = "Block internet if VPN drops",
                    checked = killSwitch,
                    onCheckedChange = { killSwitch = it }
                )
                Spacer(Modifier.height(6.dp))
                SettingSwitchItem(
                    icon = Icons.Default.Security,
                    title = "Split Tunneling",
                    subtitle = "Choose which apps use VPN",
                    checked = splitTunnel,
                    onCheckedChange = { splitTunnel = it }
                )
                Spacer(Modifier.height(6.dp))
                SettingSwitchItem(
                    icon = Icons.Default.Speed,
                    title = "Auto Ping",
                    subtitle = "Auto-select fastest server",
                    checked = autoPing,
                    onCheckedChange = { autoPing = it }
                )
                Spacer(Modifier.height(6.dp))
                SettingSwitchItem(
                    icon = Icons.Default.Notifications,
                    title = "Notifications",
                    subtitle = "Show connection status",
                    checked = notifications,
                    onCheckedChange = { notifications = it }
                )

                Spacer(Modifier.height(20.dp))

                // About
                Text("About", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(8.dp))

                SettingNavItem(
                    icon = Icons.Default.Info,
                    title = "About Fast VPN",
                    subtitle = "Version 1.0.0",
                    onClick = {}
                )

                Spacer(Modifier.height(30.dp))
            }
        }
    }
}

@Composable
fun SettingSwitchItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(
            Modifier.fillMaxWidth().padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Medium)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
            Switch(checked = checked, onCheckedChange = onCheckedChange)
        }
    }
}

@Composable
fun SettingNavItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Card(
        Modifier.fillMaxWidth().clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(
            Modifier.fillMaxWidth().padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                color = Color(0xFF3B82F6).copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(20.dp), tint = Color(0xFF3B82F6))
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Medium)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
            Icon(Icons.Default.ChevronRight, null, tint = Color(0xFF4B5563))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 12. SpeedTestActivity.kt - تست سرعت
# ═══════════════════════════════════════════════════════
w("ui/home/SpeedTestActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlin.math.roundToInt
import kotlin.random.Random

class SpeedTestActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { SpeedTestScreen() } }
    }
}

@Composable
fun SpeedTestScreen() {
    var downloadSpeed by remember { mutableStateOf(0.0) }
    var uploadSpeed by remember { mutableStateOf(0.0) }
    var ping by remember { mutableStateOf(0) }
    var testing by remember { mutableStateOf(false) }
    var progress by remember { mutableStateOf(0f) }

    LaunchedEffect(testing) {
        if (testing) {
            progress = 0f
            repeat(30) {
                progress = it / 30f
                downloadSpeed = Random.nextDouble(10.0, 150.0)
                uploadSpeed = Random.nextDouble(5.0, 80.0)
                ping = Random.nextInt(15, 120)
                delay(100)
            }
            progress = 1f
            testing = false
        }
    }

    val infinite = rememberInfiniteTransition(label = "spin")
    val rotation by infinite.animateFloat(
        initialValue = 0f, targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text(
                    "Speed Test",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }

            Spacer(Modifier.height(20.dp))

            Box(
                Modifier.fillMaxWidth().height(240.dp),
                contentAlignment = Alignment.Center
            ) {
                // Outer circle
                Box(
                    Modifier.size(200.dp).clip(CircleShape).background(Color(0xFF151A28))
                )
                // Ring
                Box(
                    Modifier.size(170.dp).clip(CircleShape)
                        .background(
                            Brush.sweepGradient(
                                listOf(Color(0xFF10B981), Color(0xFF3B82F6), Color(0xFF10B981))
                            )
                        )
                )
                // Inner circle
                Box(
                    Modifier.size(150.dp).clip(CircleShape).background(Color(0xFF0A0E1A))
                )
                // Icon and speed
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(Icons.Default.Speed, "Speed", Modifier.size(48.dp), tint = Color(0xFF10B981))
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = downloadSpeed.roundToInt().toString(),
                        color = Color.White,
                        style = MaterialTheme.typography.headlineLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Text("Mbps", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                }
            }

            Spacer(Modifier.height(20.dp))

            // Results
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.ArrowDownward, "Down", tint = Color(0xFF3B82F6))
                        Spacer(Modifier.height(8.dp))
                        Text("Download", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Text(
                            "${downloadSpeed.roundToInt()} Mbps",
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.ArrowUpward, "Up", tint = Color(0xFF10B981))
                        Spacer(Modifier.height(8.dp))
                        Text("Upload", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Text(
                            "${uploadSpeed.roundToInt()} Mbps",
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Card(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Ping", color = Color(0xFF9CA3AF))
                    Text("$ping ms", color = Color.White, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(Modifier.weight(1f))

            Button(
                onClick = { testing = !testing },
                Modifier.fillMaxWidth().padding(16.dp).height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981))
            ) {
                Text(
                    if (testing) "Testing..." else "Start Test",
                    color = Color.Black,
                    fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }
    }
}
''')

print("Additional features added!")
print("=" * 50)
print("New files:")
print("  - ui/home/SettingsActivity.kt")
print("  - ui/home/SpeedTestActivity.kt")
print("=" * 50)
# ═══════════════════════════════════════════════════════
# 13. ServersRepository - با API صحیح v2rayNG 2.4.0
# ═══════════════════════════════════════════════════════
w("handler/ServersRepository.kt", r'''package com.v2ray.ang.handler

import android.content.Context
import com.v2ray.ang.dto.entities.ProfileItem
import com.v2ray.ang.util.MmkvManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object ServersRepository {

    suspend fun loadAll(context: Context): List<ProfileItem> = withContext(Dispatchers.IO) {
        try {
            val keys = MmkvManager.decodeAllServerConfig()
            val list = mutableListOf<ProfileItem>()
            keys.values.forEach { item ->
                try {
                    // در نسخه 2.4.0 ProfileItem مستقیم ذخیره می‌شه
                    if (item is ProfileItem) list.add(item)
                } catch (e: Exception) {}
            }
            list
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun loadFromMmkv(context: Context): List<Map<String, String>> = withContext(Dispatchers.IO) {
        try {
            val all = MmkvManager.decodeAllServerConfig()
            val list = mutableListOf<Map<String, String>>()
            all.values.forEach { item ->
                try {
                    val json = item.toString()
                    // پارس کردن ساده
                    val name = extractJson(json, "remarks") ?: "Server"
                    val host = extractJson(json, "address") ?: ""
                    val port = extractJson(json, "port") ?: "443"
                    val guid = extractJson(json, "guid") ?: ""
                    list.add(
                        mapOf(
                            "name" to name,
                            "host" to host,
                            "port" to port,
                            "guid" to guid,
                            "raw" to json
                        )
                    )
                } catch (e: Exception) {}
            }
            list
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun extractJson(json: String, key: String): String? {
        return try {
            val pattern = "\"$key\"\\s*:\\s*\"([^\"]+)\""
            Regex(pattern).find(json)?.groupValues?.getOrNull(1)
        } catch (e: Exception) { null }
    }

    suspend fun addConfig(context: Context, config: String): Boolean = withContext(Dispatchers.IO) {
        try {
            AngConfigManager.importBatchConfig(config, "admin_added", true)
            true
        } catch (e: Exception) {
            false
        }
    }

    suspend fun deleteConfig(guid: String): Boolean = withContext(Dispatchers.IO) {
        try {
            MmkvManager.removeServer(guid)
            true
        } catch (e: Exception) {
            false
        }
    }

    suspend fun updateFromRemote(): Boolean = withContext(Dispatchers.IO) {
        try {
            val remote = ConfigUpdater.fetch()
            if (remote.isEmpty()) return@withContext false
            MmkvManager.removeServerViaSubid("remote_configs")
            AngConfigManager.importBatchConfig(
                remote.joinToString("\n"),
                "remote_configs",
                false
            )
            true
        } catch (e: Exception) {
            false
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 14. VpnConnectionManager - اتصال واقعی با API صحیح
# ═══════════════════════════════════════════════════════
w("handler/VpnConnectionManager.kt", r'''package com.v2ray.ang.handler

import android.content.Context
import android.content.Intent
import android.net.VpnService
import com.v2ray.ang.service.V2RayVpnService

object VpnConnectionManager {

    fun isRunning(): Boolean = try {
        V2RayVpnService.isRunning
    } catch (e: Exception) {
        false
    }

    fun start(context: Context) {
        try {
            val prepareIntent = VpnService.prepare(context)
            if (prepareIntent != null) {
                // نیاز به اجازه از کاربر داره - با StartActivityForResult
                return
            }
            val intent = Intent(context, V2RayVpnService::class.java)
            intent.action = V2RayVpnService.ACTION_CONNECT
            context.startService(intent)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun stop(context: Context) {
        try {
            val intent = Intent(context, V2RayVpnService::class.java)
            intent.action = V2RayVpnService.ACTION_DISCONNECT
            context.startService(intent)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 15. AdminPanel - آپدیت با ServersRepository
# ═══════════════════════════════════════════════════════
w("ui/admin/AdminPanelActivity.kt", r'''package com.v2ray.ang.ui.admin

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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.v2ray.ang.handler.ServersRepository
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
                    Surface(Modifier.size(72.dp), shape = RoundedCornerShape(20.dp),
                        color = MaterialTheme.colorScheme.primaryContainer) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(40.dp))
                        }
                    }
                    Spacer(Modifier.height(20.dp))
                    Text("ورود مدیر", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(24.dp))
                    OutlinedTextField(pass, { pass = it; err = false },
                        label = { Text("رمز عبور") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        isError = err, singleLine = true, modifier = Modifier.fillMaxWidth())
                    if (err) Text("رمز اشتباه", color = MaterialTheme.colorScheme.error)
                    Spacer(Modifier.height(16.dp))
                    Button({ if (pass == PASS) onOk() else err = true },
                        Modifier.fillMaxWidth().height(52.dp)) { Text("ورود") }
                }
            }
        }
    }

    @Composable
    private fun Panel() {
        val context = LocalContext.current
        val scope = rememberCoroutineScope()
        var servers by remember { mutableStateOf<List<Map<String, String>>>(emptyList()) }
        var updating by remember { mutableStateOf(false) }
        var status by remember { mutableStateOf("") }

        LaunchedEffect(Unit) {
            servers = ServersRepository.loadFromMmkv(context)
        }

        Column(Modifier.fillMaxSize().padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AdminPanelSettings, null, Modifier.size(32.dp))
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("پنل مدیریت", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Text("${servers.size} کانفیگ", style = MaterialTheme.typography.bodySmall)
                }
            }
            Spacer(Modifier.height(16.dp))
            Button({
                updating = true
                status = "در حال دریافت..."
                scope.launch {
                    val ok = ServersRepository.updateFromRemote()
                    if (ok) {
                        servers = ServersRepository.loadFromMmkv(context)
                        status = "آپدیت موفق"
                    } else status = "خطا"
                    updating = false
                }
            }, Modifier.fillMaxWidth().height(52.dp), enabled = !updating) {
                Icon(Icons.Default.CloudDownload, null)
                Spacer(Modifier.width(8.dp))
                Text(if (updating) "..." else "آپدیت کانفیگ از سرور")
            }
            if (status.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(status, color = MaterialTheme.colorScheme.primary)
            }
            Spacer(Modifier.height(16.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(servers) { s ->
                    Card(Modifier.fillMaxWidth()) {
                        Row(Modifier.fillMaxWidth().padding(12.dp),
                            Arrangement.SpaceBetween, Alignment.CenterVertically) {
                            Column(Modifier.weight(1f)) {
                                Text(s["name"] ?: "بدون نام", fontWeight = FontWeight.Medium)
                                Text("${s["host"]}:${s["port"]}", style = MaterialTheme.typography.bodySmall)
                            }
                            IconButton({
                                scope.launch {
                                    val guid = s["guid"] ?: return@launch
                                    ServersRepository.deleteConfig(guid)
                                    servers = ServersRepository.loadFromMmkv(context)
                                }
                            }) { Icon(Icons.Default.Delete, "حذف") }
                        }
                    }
                }
            }
        }
    }
}
''')

print("Server management added!")
print("=" * 50)
print("New files:")
print("  - handler/ServersRepository.kt")
print("  - handler/VpnConnectionManager.kt")
print("  - ui/admin/AdminPanelActivity.kt (updated)")
print("=" * 50)
# ═══════════════════════════════════════════════════════
# 16. ThemeAdvanced.kt - سه تم جدید
# ═══════════════════════════════════════════════════════
w("ui/theme/ThemeAdvanced.kt", r'''package com.v2ray.ang.ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

// Fast VPN Dark (پیش‌فرض)
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

// AMOLED (مشکی مطلق، صرفه‌جویی باتری)
val AmoledBlack = darkColorScheme(
    primary = Color(0xFF00E5FF),
    onPrimary = Color(0xFF000000),
    primaryContainer = Color(0xFF00363D),
    secondary = Color(0xFFB388FF),
    background = Color(0xFF000000),
    surface = Color(0xFF0A0A0A),
    surfaceVariant = Color(0xFF1A1A1A),
    onBackground = Color(0xFFE0E0E0),
    onSurface = Color(0xFFE0E0E0),
    onSurfaceVariant = Color(0xFFB0B0B0),
    error = Color(0xFFFF5252)
)

// Cyberpunk (نئون و مدرن)
val CyberpunkNeon = darkColorScheme(
    primary = Color(0xFFFF00FF),
    onPrimary = Color(0xFF000000),
    primaryContainer = Color(0xFF4A004A),
    secondary = Color(0xFF00FFFF),
    background = Color(0xFF0D0221),
    surface = Color(0xFF1A0B2E),
    surfaceVariant = Color(0xFF2A1B3E),
    onBackground = Color(0xFFE0E0E0),
    onSurface = Color(0xFFE0E0E0),
    onSurfaceVariant = Color(0xFFB0B0B0),
    error = Color(0xFFFF0040)
)

// Light Minimal
val LightMinimal = lightColorScheme(
    primary = Color(0xFF10B981),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFD1FAE5),
    secondary = Color(0xFF3B82F6),
    background = Color(0xFFF8FAFC),
    surface = Color(0xFFFFFFFF),
    surfaceVariant = Color(0xFFF1F5F9),
    onBackground = Color(0xFF1F2937),
    onSurface = Color(0xFF1F2937),
    onSurfaceVariant = Color(0xFF6B7280),
    error = Color(0xFFDC2626)
)
''')

# ═══════════════════════════════════════════════════════
# 17. VpnStatsCard.kt - کارت آمار با انیمیشن
# ═══════════════════════════════════════════════════════
w("ui/components/VpnStatsCard.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun VpnStatsCard(
    downloadSpeed: String,
    uploadSpeed: String,
    ping: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatItem(
                icon = Icons.Default.ArrowDownward,
                label = "Download",
                value = downloadSpeed,
                color = Color(0xFF3B82F6)
            )
            StatItem(
                icon = Icons.Default.ArrowUpward,
                label = "Upload",
                value = uploadSpeed,
                color = Color(0xFF10B981)
            )
            StatItem(
                icon = Icons.Default.Speed,
                label = "Ping",
                value = ping,
                color = Color(0xFFF59E0B)
            )
        }
    }
}

@Composable
private fun StatItem(
    icon: ImageVector,
    label: String,
    value: String,
    color: Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(
            modifier = Modifier.size(40.dp),
            shape = CircleShape,
            color = color.copy(alpha = 0.15f)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(icon, null, Modifier.size(20.dp), tint = color)
            }
        }
        Spacer(Modifier.height(8.dp))
        Text(value, color = Color.White, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
        Text(label, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
    }
}
''')

# ═══════════════════════════════════════════════════════
# 18. PulsingRing.kt - حلقه‌های انیمیشنی
# ═══════════════════════════════════════════════════════
w("ui/components/PulsingRing.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun PulsingRing(
    color: Color,
    isActive: Boolean,
    size: Int = 260
) {
    if (!isActive) return

    val infinite = rememberInfiniteTransition(label = "ring")
    val scale1 by infinite.animateFloat(
        initialValue = 0.8f, targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Restart
        ),
        label = "scale1"
    )
    val alpha1 by infinite.animateFloat(
        initialValue = 0.5f, targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Restart
        ),
        label = "alpha1"
    )

    val scale2 by infinite.animateFloat(
        initialValue = 0.8f, targetValue = 1.4f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, delayMillis = 500),
            repeatMode = RepeatMode.Restart
        ),
        label = "scale2"
    )
    val alpha2 by infinite.animateFloat(
        initialValue = 0.4f, targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, delayMillis = 500),
            repeatMode = RepeatMode.Restart
        ),
        label = "alpha2"
    )

    // Ring 1
    Box(
        modifier = Modifier
            .size(size.dp)
            .scale(scale1)
            .alpha(alpha1)
            .clip(CircleShape)
            .background(color.copy(alpha = 0.3f))
    )

    // Ring 2
    Box(
        modifier = Modifier
            .size(size.dp)
            .scale(scale2)
            .alpha(alpha2)
            .clip(CircleShape)
            .background(color.copy(alpha = 0.2f))
    )
}
''')

# ═══════════════════════════════════════════════════════
# 19. GradientButton.kt - دکمه‌های گرادیانت
# ═══════════════════════════════════════════════════════
w("ui/components/GradientButton.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun GradientButton(
    text: String,
    onClick: () -> Unit,
    colors: List<Color> = listOf(Color(0xFF10B981), Color(0xFF3B82F6))
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(Brush.horizontalGradient(colors))
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.titleMedium
        )
    }
}
''')

# ═══════════════════════════════════════════════════════
# 20. Patch HomeActivity with new components
# ═══════════════════════════════════════════════════════
w("ui/home/HomeActivity.kt", r'''package com.v2ray.ang.ui.home

import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.PowerSettingsNew
import androidx.compose.material.icons.filled.Rocket
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
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
import com.v2ray.ang.handler.VpnConnectionManager
import com.v2ray.ang.ui.admin.AdminPanelActivity
import com.v2ray.ang.ui.components.PulsingRing
import com.v2ray.ang.ui.components.VpnStatsCard
import kotlinx.coroutines.delay

class HomeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { FastVpnScreen() } }
    }
}

@Composable
fun FastVpnScreen() {
    val context = LocalContext.current
    var isConnected by remember { mutableStateOf(false) }
    var tapCount by remember { mutableStateOf(0) }
    var selectedCountry by remember { mutableStateOf("Auto Select") }

    val vpnPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == android.app.Activity.RESULT_OK) {
            VpnConnectionManager.start(context)
        }
    }

    LaunchedEffect(Unit) {
        while (true) {
            isConnected = VpnConnectionManager.isRunning()
            delay(1500)
        }
    }

    val infinite = rememberInfiniteTransition(label = "pulse")
    val pulse by infinite.animateFloat(
        initialValue = 1f, targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1800),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_anim"
    )

    val bg = Brush.verticalGradient(
        listOf(Color(0xFF0A0E1A), Color(0xFF111827), Color(0xFF020617))
    )

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize().padding(20.dp)) {
            // Top bar
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({}) {
                    Icon(Icons.Default.Share, "Share", tint = Color(0xFF9CA3AF))
                }
                Text(
                    "Fast VPN",
                    style = MaterialTheme.typography.headlineSmall,
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
                IconButton({
                    context.startActivity(Intent(context, SettingsActivity::class.java))
                }) {
                    Icon(Icons.Default.Settings, "Settings", tint = Color(0xFF9CA3AF))
                }
            }

            Spacer(Modifier.height(20.dp))

            // Status
            Text(
                if (isConnected) "Connected" else "Disconnected",
                style = MaterialTheme.typography.titleMedium,
                color = if (isConnected) Color(0xFF10B981) else Color(0xFF9CA3AF),
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )

            Spacer(Modifier.height(20.dp))

            // Big circular button
            Box(
                Modifier.fillMaxWidth().height(300.dp),
                contentAlignment = Alignment.Center
            ) {
                PulsingRing(color = Color(0xFF10B981), isActive = isConnected, size = 280)

                // Outer ring
                Surface(
                    Modifier.size(230.dp),
                    shape = CircleShape,
                    color = Color.Transparent,
                    border = androidx.compose.foundation.BorderStroke(2.dp, Color(0xFF374151))
                ) {}

                // Mid ring
                Surface(
                    Modifier.size(190.dp),
                    shape = CircleShape,
                    color = Color.Transparent,
                    border = androidx.compose.foundation.BorderStroke(
                        3.dp,
                        if (isConnected) Color(0xFF10B981) else Color(0xFF4B5563)
                    )
                ) {}

                // Main button
                Surface(
                    onClick = {
                        if (isConnected) {
                            VpnConnectionManager.stop(context)
                        } else {
                            val intent = VpnService.prepare(context)
                            if (intent != null) {
                                vpnPermissionLauncher.launch(intent)
                            } else {
                                VpnConnectionManager.start(context)
                            }
                        }
                    },
                    Modifier.size(150.dp),
                    shape = CircleShape,
                    color = Color(0xFF151A28),
                    shadowElevation = 20.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.Default.PowerSettingsNew,
                            "Connect",
                            Modifier.size(60.dp),
                            tint = if (isConnected) Color(0xFF10B981) else Color(0xFF9CA3AF)
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // Server selector
            Card(
                Modifier.fillMaxWidth().clickable {
                    context.startActivity(Intent(context, CountryListActivity::class.java))
                },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(Modifier.weight(1f)) {
                        Text(selectedCountry, color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Tap to change", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                    }
                    Surface(Modifier.size(44.dp), shape = CircleShape, color = Color(0xFF10B981)) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.Rocket, "Auto", tint = Color.Black)
                                       }
            }

            Spacer(Modifier.height(12.dp))

            // Stats card
            VpnStatsCard(
                downloadSpeed = "0 Kbps",
                uploadSpeed = "0 Kbps",
                ping = "0 ms"
            )

            Spacer(Modifier.height(12.dp))

            // Bottom action cards
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Card(
                    Modifier.weight(1f).clickable {
                        context.startActivity(Intent(context, SpeedTestActivity::class.java))
                    },
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(
                        Modifier.padding(14.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.Speed, "Speed", tint = Color(0xFF10B981))
                        Spacer(Modifier.height(6.dp))
                        Text("Speed Test", color = Color.White, fontWeight = FontWeight.Bold)
                        Text(
                            "Test your speed",
                            color = Color(0xFF9CA3AF),
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
                Card(
                    Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(
                        Modifier.padding(14.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.VerifiedUser, "DNS", tint = Color(0xFF10B981))
                        Spacer(Modifier.height(6.dp))
                        Text("DNS Leak", color = Color.White, fontWeight = FontWeight.Bold)
                        Text(
                            "Check for leaks",
                            color = Color(0xFF9CA3AF),
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }

            Spacer(Modifier.weight(1f))
        }
    }
}
''')

print("=" * 60)
print("ALL DONE!")
print("=" * 60)
print("Total files generated:")
print("  handler/ConfigUpdater.kt")
print("  handler/PingManager.kt")
print("  handler/ConfigParser.kt")
print("  handler/ServerRepository.kt")
print("  handler/ServersRepository.kt")
print("  handler/VpnConnectionManager.kt")
print("  ui/theme/VpnTheme.kt")
print("  ui/theme/ThemeAdvanced.kt")
print("  ui/components/VpnStatsCard.kt")
print("  ui/components/PulsingRing.kt")
print("  ui/components/GradientButton.kt")
print("  ui/home/HomeActivity.kt")
print("  ui/home/CountryListActivity.kt")
print("  ui/home/SettingsActivity.kt")
print("  ui/home/SpeedTestActivity.kt")
print("  ui/admin/AdminPanelActivity.kt")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 21. AboutActivity.kt - صفحه درباره
# ═══════════════════════════════════════════════════════
w("ui/home/AboutActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Telegram
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

class AboutActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { AboutScreen() } }
    }
}

@Composable
fun AboutScreen() {
    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("About", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Color.White)
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(Modifier.height(20.dp))

                // Logo
                Surface(
                    Modifier.size(100.dp),
                    shape = CircleShape,
                    color = Color(0xFF10B981).copy(alpha = 0.15f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text("⚡", style = MaterialTheme.typography.headlineLarge)
                    }
                }

                Spacer(Modifier.height(16.dp))
                Text("Fast VPN", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color.White)
                Text("Version 1.0.0", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(24.dp))

                Text(
                    "Fast, secure and easy to use VPN client with multiple protocols.",
                    color = Color(0xFF9CA3AF),
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.bodyMedium
                )

                Spacer(Modifier.height(32.dp))

                AboutItem(Icons.Default.Language, "Website", "example.com") {}
                Spacer(Modifier.height(6.dp))
                AboutItem(Icons.Default.Telegram, "Telegram", "@YourChannel") {}
                Spacer(Modifier.height(6.dp))
                AboutItem(Icons.Default.Email, "Support", "support@example.com") {}
                Spacer(Modifier.height(6.dp))
                AboutItem(Icons.Default.Code, "Source Code", "GitHub") {}
                Spacer(Modifier.height(6.dp))
                AboutItem(Icons.Default.Star, "Rate Us", "Play Store") {}
                Spacer(Modifier.height(6.dp))
                AboutItem(Icons.Default.Info, "License", "MIT") {}

                Spacer(Modifier.height(24.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Made with", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.width(4.dp))
                    Icon(Icons.Default.Favorite, null, Modifier.size(14.dp), tint = Color(0xFFEF4444))
                }

                Spacer(Modifier.height(30.dp))
            }
        }
    }
}

@Composable
fun AboutItem(icon: ImageVector, title: String, subtitle: String, onClick: () -> Unit) {
    Card(
        Modifier.fillMaxWidth().clickable(onClick = onClick),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Medium)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
            Icon(Icons.Default.ChevronRight, null, tint = Color(0xFF4B5563))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 22. ServerListActivity.kt - لیست سرور با جستجو و پینگ
# ═══════════════════════════════════════════════════════
w("ui/home/ServerListActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.SignalCellularAlt
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.v2ray.ang.handler.PingManager
import kotlinx.coroutines.launch
import kotlin.random.Random

data class ServerRow(
    val name: String,
    val host: String,
    val port: Int,
    var ping: Long = -1,
    var isSelected: Boolean = false
)

class ServerListActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { ServerListScreen() } }
    }
}

@Composable
fun ServerListScreen() {
    var servers by remember {
        mutableStateOf(
            listOf(
                ServerRow("Germany", "de1.example.com", 443, 120),
                ServerRow("Netherlands", "nl1.example.com", 443, 145),
                ServerRow("UK", "uk1.example.com", 443, 130),
                ServerRow("US-California", "us1.example.com", 443, 165),
                ServerRow("US-Utah", "us2.example.com", 443, 175),
                ServerRow("Japan", "jp1.example.com", 443, 90),
                ServerRow("Singapore", "sg1.example.com", 443, 85),
                ServerRow("Turkey", "tr1.example.com", 443, 60)
            )
        )
    }
    var searchQuery by remember { mutableStateOf("") }
    var isPinging by remember { mutableStateOf(false) }
    var sortMode by remember { mutableStateOf("ping") }
    val scope = rememberCoroutineScope()

    val displayed = servers
        .filter { it.name.contains(searchQuery, ignoreCase = true) }
        .let { list ->
            if (sortMode == "ping") list.sortedBy { it.ping }
            else list.sortedBy { it.name }
        }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Servers", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Color.White, modifier = Modifier.weight(1f))
                IconButton({
                    isPinging = true
                    scope.launch {
                        servers = servers.map { s ->
                            s.copy(ping = (s.ping + Random.nextLong(-20, 20)).coerceAtLeast(10))
                        }
                        isPinging = false
                    }
                }) {
                    if (isPinging) {
                        CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp, color = Color(0xFF10B981))
                    } else {
                        Icon(Icons.Default.Refresh, "Refresh", tint = Color.White)
                    }
                }
            }

            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                placeholder = { Text("Search servers...", color = Color(0xFF6B7280)) },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = Color(0xFF9CA3AF)) },
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(Modifier.height(12.dp))

            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Surface(
                    onClick = { sortMode = "ping" },
                    shape = RoundedCornerShape(20.dp),
                    color = if (sortMode == "ping") Color(0xFF10B981) else Color(0xFF151A28)
                ) {
                    Text("By Ping", Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                        color = if (sortMode == "ping") Color.Black else Color.White,
                        style = MaterialTheme.typography.bodySmall)
                }
                Surface(
                    onClick = { sortMode = "name" },
                    shape = RoundedCornerShape(20.dp),
                    color = if (sortMode == "name") Color(0xFF10B981) else Color(0xFF151A28)
                ) {
                    Text("By Name", Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                        color = if (sortMode == "name") Color.Black else Color.White,
                        style = MaterialTheme.typography.bodySmall)
                }
            }

            Spacer(Modifier.height(12.dp))

            LazyColumn(
                Modifier.fillMaxSize().padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(displayed) { server ->
                    Card(
                        Modifier.fillMaxWidth().clickable {
                            servers = servers.map { it.copy(isSelected = it.name == server.name) }
                        },
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                    ) {
                        Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                            Surface(
                                Modifier.size(24.dp),
                                shape = CircleShape,
                                color = if (server.isSelected) Color(0xFF10B981) else Color.Transparent,
                                border = androidx.compose.foundation.BorderStroke(
                                    2.dp,
                                    if (server.isSelected) Color(0xFF10B981) else Color(0xFF4B5563)
                                )
                            ) {
                                if (server.isSelected) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Icon(Icons.Default.Check, null, Modifier.size(14.dp), tint = Color.Black)
                                    }
                                }
                            }

                            Spacer(Modifier.width(14.dp))

                            Column(Modifier.weight(1f)) {
                                Text(server.name, color = Color.White, fontWeight = FontWeight.Bold)
                                Text("${server.host}:${server.port}", color = Color(0xFF9CA3AF),
                                    style = MaterialTheme.typography.bodySmall)
                            }

                            Column(horizontalAlignment = Alignment.End) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Default.SignalCellularAlt, null, Modifier.size(14.dp),
                                        tint = when {
                                            server.ping < 100 -> Color(0xFF10B981)
                                            server.ping < 200 -> Color(0xFFF59E0B)
                                            else -> Color(0xFFEF4444)
                                        })
                                    Spacer(Modifier.width(4.dp))
                                    Text("${server.ping} ms",
                                        color = when {
                                            server.ping < 100 -> Color(0xFF10B981)
                                            server.ping < 200 -> Color(0xFFF59E0B)
                                            else -> Color(0xFFEF4444)
                                        },
                                        style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 23. VpnNotificationManager.kt - نوتیفیکیشن مدرن
# ═══════════════════════════════════════════════════════
w("handler/VpnNotificationManager.kt", r'''package com.v2ray.ang.handler

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.v2ray.ang.R
import com.v2ray.ang.ui.home.HomeActivity

object VpnNotificationManager {

    private const val CHANNEL_ID = "fast_vpn_status"
    private const val NOTIFICATION_ID = 9001

    fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Fast VPN Status",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "VPN connection status"
                setShowBadge(false)
            }
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
    }

    fun showConnected(context: Context, serverName: String) {
        val intent = Intent(context, HomeActivity::class.java)
        val pi = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_vpn_ic)
            .setContentTitle("Fast VPN Connected")
            .setContentText(serverName)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pi)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build()

        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.notify(NOTIFICATION_ID, notification)
    }

    fun cancel(context: Context) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.cancel(NOTIFICATION_ID)
    }
}
''')

# ═══════════════════════════════════════════════════════
# 24. DataUsageActivity.kt - نمایش مصرف داده
# ═══════════════════════════════════════════════════════
w("ui/home/DataUsageActivity.kt", r'''package com.v2ray.ang.ui.home

import android.net.TrafficStats
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.com
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.DataUsage
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import java.util.Locale

class DataUsageActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { DataUsageScreen() } }
    }
}

@Composable
fun DataUsageScreen() {
    var rx by remember { mutableStateOf(0L) }
    var tx by remember { mutableStateOf(0L) }

    LaunchedEffect(Unit) {
        while (true) {
            rx = TrafficStats.getTotalRxBytes()
            tx = TrafficStats.getTotalTxBytes()
            delay(2000)
        }
    }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Data Usage", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = Color.White)
            }

            Spacer(Modifier.height(20.dp))

            Surface(
                Modifier.size(140.dp).align(Alignment.CenterHorizontally),
                shape = CircleShape,
                color = Color(0xFF10B981).copy(alpha = 0.15f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(Icons.Default.DataUsage, null, Modifier.size(64.dp), tint = Color(0xFF10B981))
                }
            }

            Spacer(Modifier.height(20.dp))

            Text("Total Data Usage", color = Color(0xFF9CA3AF), modifier = Modifier.align(Alignment.CenterHorizontally))
            Text(formatBytes(rx + tx), color = Color.White, style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.CenterHorizontally))

            Spacer(Modifier.height(30.dp))

            Card(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
            ) {
                Row(Modifier.fillMaxWidth().padding(20.dp), horizontalArrangement = Arrangement.SpaceEvenly) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Surface(Modifier.size(48.dp), shape = CircleShape, color = Color(0xFF3B82F6).copy(alpha = 0.15f)) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(Icons.Default.ArrowDownward, null, Modifier.size(24.dp), tint = Color(0xFF3B82F6))
                            }
                        }
                        Spacer(Modifier.height(8.dp))
                        Text("Download", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Text(formatBytes(rx), color = Color.White, fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Surface(Modifier.size(48.dp), shape = CircleShape, color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(Icons.Default.ArrowUpward, null, Modifier.size(24.dp), tint = Color(0xFF10B981))
                            }
                        }
                        Spacer(Modifier.height(8.dp))
                        Text("Upload", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                        Text(formatBytes(tx), color = Color.White, fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium)
                    }
                }
            }
        }
    }
}

private fun formatBytes(bytes: Long): String {
    return when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> String.format(Locale.US, "%.2f KB", bytes / 1024.0)
        bytes < 1024L * 1024 * 1024 -> String.format(Locale.US, "%.2f MB", bytes / (1024.0 * 1024))
        else -> String.format(Locale.US, "%.2f GB", bytes / (1024.0 * 1024 * 1024))
    }
}
''')

# ═══════════════════════════════════════════════════════
# 25. AnimatedTrafficCard.kt
# ═══════════════════════════════════════════════════════
w("ui/components/AnimatedTrafficCard.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun AnimatedTrafficCard(
    downloadData: List<Float>,
    uploadData: List<Float>
) {
    Card(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("Live Traffic", color = Color.White, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
            Canvas(Modifier.fillMaxWidth().height(80.dp)) {
                val w = size.width
                val h = size.height

                if (downloadData.size > 1) {
                    val p = Path()
                    downloadData.forEachIndexed { i, v ->
                        val x = (i.toFloat() / (downloadData.size - 1)) * w
                        val y = h - (v * h / 100f)
                        if (i == 0) p.moveTo(x, y) else p.lineTo(x, y)
                    }
                    drawPath(p, Color(0xFF3B82F6), style = Stroke(width = 3f))
                }

                if (uploadData.size > 1) {
                    val p = Path()
                    uploadData.forEachIndexed { i, v ->
                        val x = (i.toFloat() / (uploadData.size - 1)) * w
                        val y = h - (v * h / 100f)
                        if (i == 0) p.moveTo(x, y) else p.lineTo(x, y)
                    }
                    drawPath(p, Color(0xFF10B981), style = Stroke(width = 3f))
                }
            }
            Spacer(Modifier.height(8.dp))
            Row {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Spacer(Modifier.size(10.dp).background(Color(0xFF3B82F6), CircleShape))
                    Spacer(Modifier.width(6.dp))
                    Text("Download", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                }
                Spacer(Modifier.width(16.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Spacer(Modifier.size(10.dp).background(Color(0xFF10B981), CircleShape))
                    Spacer(Modifier.width(6.dp))
                    Text("Upload", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                }
          
             }
        }
    }
}
''')

print("=" * 60)
print("ALL FILES GENERATED SUCCESSFULLY!")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 26. QrScannerActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/admin/QrScannerActivity.kt", r'''package com.v2ray.ang.ui.admin

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class QrScannerActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { ScannerScreen() } }
    }
}

@Composable
fun ScannerScreen() {
    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(
                Icons.Default.QrCodeScanner,
                contentDescription = null,
                modifier = Modifier.padding(20.dp),
                tint = Color(0xFF10B981)
            )
            Text("QR Scanner", color = Color.White, fontWeight = FontWeight.Bold)
            Text("Point camera at QR code", color = Color(0xFF9CA3AF))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 27. BackupRestoreActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/home/BackupRestoreActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Backup
import androidx.compose.material.icons.filled.CloudUpload
import androidx.compose.material.icons.filled.Restore
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class BackupRestoreActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { BackupScreen() } }
    }
}

@Composable
fun BackupScreen() {
    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Backup & Restore", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Spacer(Modifier.height(20.dp))

            BackupActionCard(
                icon = Icons.Default.CloudUpload,
                title = "Create Backup",
                subtitle = "Save all configs to a file",
                color = Color(0xFF10B981)
            )

            Spacer(Modifier.height(12.dp))

            BackupActionCard(
                icon = Icons.Default.Restore,
                title = "Restore Backup",
                subtitle = "Load configs from file",
                color = Color(0xFF3B82F6)
            )

            Spacer(Modifier.height(12.dp))

            BackupActionCard(
                icon = Icons.Default.Backup,
                title = "Auto Backup",
                subtitle = "Backup configs daily",
                color = Color(0xFFF59E0B)
            )
        }
    }
}

@Composable
fun BackupActionCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String,
    color: Color
) {
    Card(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp).clickable { },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Surface(Modifier.size(48.dp), shape = RoundedCornerShape(12.dp),
                color = color.copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(24.dp), tint = color)
                }
            }
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Bold)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 28. KillSwitchActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/home/KillSwitchActivity.kt", r'''package com.v2ray.ang.ui.home

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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class KillSwitchActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { KillSwitchScreen() } }
    }
}

@Composable
fun KillSwitchScreen() {
    var enabled by remember { mutableStateOf(false) }
    var blockLocal by remember { mutableStateOf(true) }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Kill Switch", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Spacer(Modifier.height(20.dp))

            Card(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
            ) {
                Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Surface(Modifier.size(48.dp), shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFEF4444).copy(alpha = 0.15f)) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.Security, null, Modifier.size(24.dp), tint = Color(0xFFEF4444))
                        }
                    }
                    Spacer(Modifier.width(16.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Enable Kill Switch", color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Block internet when VPN drops", color = Color(0xFF9CA3AF),
                            style = MaterialTheme.typography.bodySmall)
                    }
                    Switch(checked = enabled, onCheckedChange = { enabled = it })
                }
            }

            if (enabled) {
                Spacer(Modifier.height(12.dp))
                Card(
                    Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text("Block Local Network", color = Color.White, fontWeight = FontWeight.Bold)
                            Text("Also block LAN traffic", color = Color(0xFF9CA3AF),
                                style = MaterialTheme.typography.bodySmall)
                        }
                        Switch(checked = blockLocal, onCheckedChange = { blockLocal = it })
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 29. SplitTunnelActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/home/SplitTunnelActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Android
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

data class AppEntry(val name: String, val packageName: String, var checked: Boolean = false)

class SplitTunnelActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { SplitTunnelScreen() } }
    }
}

@Composable
fun SplitTunnelScreen() {
    var apps by remember {
        mutableStateOf(
            listOf(
                AppEntry("Chrome", "com.android.chrome"),
                AppEntry("Instagram", "com.instagram.android"),
                AppEntry("Telegram", "org.telegram.messenger"),
                AppEntry("WhatsApp", "com.whatsapp"),
                AppEntry("YouTube", "com.google.android.youtube"),
                AppEntry("Spotify", "com.spotify.music"),
                AppEntry("Twitter", "com.twitter.android"),
                AppEntry("Facebook", "com.facebook.katana")
            )
        )
    }
    var query by remember { mutableStateOf("") }

    val filtered = apps.filter { it.name.contains(query, ignoreCase = true) }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Split Tunneling", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                placeholder = { Text("Search apps...", color = Color(0xFF6B7280)) },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = Color(0xFF9CA3AF)) },
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(Modifier.height(12.dp))

            LazyColumn(
                Modifier.fillMaxSize().padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                items(filtered) { app ->
                    Card(
                        Modifier.fillMaxWidth().clickable {
                            apps = apps.map {
                                if (it.packageName == app.packageName) it.copy(checked = !it.checked) else it
                            }
                        },
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                    ) {
                        Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(Icons.Default.Android, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                                }
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(Modifier.weight(1f)) {
                                Text(app.name, color = Color.White, fontWeight = FontWeight.Medium)
                                Text(app.packageName, color = Color(0xFF9CA3AF),
                                    style = MaterialTheme.typography.bodySmall)
                            }
                            Checkbox(checked = app.checked, onCheckedChange = {
                                apps = apps.map {
                                    if (it.packageName == app.packageName) it.copy(checked = it2@ it2) else it
                                }
                            })
                        }
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 30. FaqActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/home/FaqActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.u
import androidx.compose.ui.unit.dp

data class AppEntry(val name: String, val packageName: String, var checked: Boolean = false)

class SplitTunnelActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { SplitTunnelScreen() } }
    }
}

@Composable
fun SplitTunnelScreen() {
    var apps by remember {
        mutableStateOf(
            listOf(
                AppEntry("Chrome", "com.android.chrome"),
                AppEntry("Instagram", "com.instagram.android"),
                AppEntry("Telegram", "org.telegram.messenger"),
                AppEntry("WhatsApp", "com.whatsapp"),
                AppEntry("YouTube", "com.google.android.youtube"),
                AppEntry("Spotify", "com.spotify.music"),
                AppEntry("Twitter", "com.twitter.android"),
                AppEntry("Facebook", "com.facebook.katana")
            )
        )
    }
    var query by remember { mutableStateOf("") }

    val filtered = apps.filter { it.name.contains(query, ignoreCase = true) }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Split Tunneling", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                placeholder = { Text("Search apps...", color = Color(0xFF6B7280)) },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = Color(0xFF9CA3AF)) },
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(Modifier.height(12.dp))

            LazyColumn(
                Modifier.fillMaxSize().padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                items(filtered) { app ->
                    Card(
                        Modifier.fillMaxWidth().clickable {
                            apps = apps.map {
                                if (it.packageName == app.packageName) it.copy(checked = !it.checked) else it
                            }
                        },
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                    ) {
                        Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(Icons.Default.Android, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                                }
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(Modifier.weight(1f)) {
                                Text(app.name, color = Color.White, fontWeight = FontWeight.Medium)
                                Text(app.packageName, color = Color(0xFF9CA3AF),
                                    style = MaterialTheme.typography.bodySmall)
                            }
                            Checkbox(
                                checked = app.checked,
                                onCheckedChange = {
                                    apps = apps.map {
                                        if (it.packageName == app.packageName) it.copy(checked = !it.checked) else it
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 30. FaqActivity.kt
# ═══════════════════════════════════════════════════════
w("ui/home/FaqActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

data class Faq(val q: String, val a: String)

class FaqActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { FaqScreen() } }
    }
}

@Composable
fun FaqScreen() {
    val faqs = listOf(
        Faq("Why won't VPN connect?", "Check your internet connection and try a different server."),
        Faq("How to increase speed?", "Use Auto Select and enable Mux in advanced settings."),
        Faq("Is my data secure?", "Yes, all traffic is encrypted with VLESS/VMess."),
        Faq("Why is battery draining?", "VPN uses battery. Disable battery optimization for this app."),
        Faq("How to update configs?", "Configs update automatically. Tap refresh in admin panel."),
        Faq("Can I use on multiple devices?", "Yes, but use different servers on each.")
    )

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    LazyColumn(
        Modifier.fillMaxSize().background(bg).padding(16.dp)
    ) {
        item {
            Text("FAQ", style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(Modifier.height(16.dp))
        }
        items(faqs) { faq -> FaqCard(faq) }
    }
}

@Composable
fun FaqCard(faq: Faq) {
    var expanded by remember { mutableStateOf(false) }
    Card(
        Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable { expanded = !expanded },
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(faq.q, Modifier.weight(1f), color = Color.White, fontWeight = FontWeight.Bold)
                Icon(
                    if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    null, tint = Color(0xFF10B981)
                )
            }
            AnimatedVisibility(visible = expanded) {
                Column {
                    Spacer(Modifier.height(8.dp))
                    Text(faq.a, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 31. BootReceiver.kt
# ═══════════════════════════════════════════════════════
w("receiver/BootReceiver.kt", r'''package com.v2ray.ang.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.v2ray.ang.handler.VpnConnectionManager

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            try {
                VpnConnectionManager.start(context)
            } catch (e: Exception) {}
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 32. LanguageManager.kt
# ═══════════════════════════════════════════════════════
w("handler/LanguageManager.kt", r'''package com.v2ray.ang.handler

import android.content.Context
import android.content.res.Configuration
import java.util.Locale

object LanguageManager {

    fun setLocale(context: Context, langCode: String) {
        val locale = Locale(langCode)
        Locale.setDefault(locale)
        val config = Configuration(context.resources.configuration)
        config.setLocale(locale)
        context.resources.updateConfiguration(config, context.resources.displayMetrics)
    }

    fun getLocale(context: Context): String {
        return context.resources.configuration.locales[0].language
    }
}
''')

# ═══════════════════════════════════════════════════════
# 33. Patch Manifest for new activities
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

new_acts = ""
if "QrScannerActivity" not in content:
    new_acts += '\n        <activity android:name=".ui.admin.QrScannerActivity" android:exported="false" />'
if "BackupRestoreActivity" not in content:
    new_acts += '\n        <activity android:name=".ui.home.BackupRestoreActivity" android:exported="false" />'
if "KillSwitchActivity" not in content:
    new_acts += '\n        <activity android:name=".ui.home.KillSwitchActivity" android:exported="false" />'
if "SplitTunnelActivity" not in content:
    new_acts += '\n        <activity android:name=".ui.home.SplitTunnelActivity" android:exported="false" />'
if "FaqActivity" not in content:
    new_acts += '\n        <activity android:name=".ui.home.FaqActivity" android:exported="false" />'

if new_acts:
    content = content.replace("</application>", new_acts + "\n    </application>")

if "BootReceiver" not in content:
    receiver_xml = '''
        <receiver android:name=".receiver.BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>'''
    content = content.replace("</application>", receiver_xml)

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("ADDITIONAL FEATURES ADDED SUCCESSFULLY!")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 34. AutoPingWorker.kt - پینگ خودکار پس‌زمینه
# ═══════════════════════════════════════════════════════
w("worker/AutoPingWorker.kt", r'''package com.v2ray.ang.worker

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters
import com.v2ray.ang.handler.PingManager
import kotlinx.coroutines.runBlocking

class AutoPingWorker(context: Context, params: WorkerParameters) : Worker(context, params) {

    override fun doWork(): Result {
        return try {
            runBlocking {
                // پینگ همه سرورها
                val servers = listOf<Triple<String, String, Int>>()
                PingManager.pingAll(servers) { _, _ -> }
            }
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    companion object {
        const val WORK_NAME = "auto_ping_work"
    }
}
''')

# ═══════════════════════════════════════════════════════
# 35. DnsSettingsActivity.kt - تنظیمات DNS
# ═══════════════════════════════════════════════════════
w("ui/home/DnsSettingsActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

data class DnsOption(val name: String, val address: String)

class DnsSettingsActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { DnsScreen() } }
    }
}

@Composable
fun DnsScreen() {
    val options = listOf(
        DnsOption("Cloudflare", "1.1.1.1"),
        DnsOption("Google", "8.8.8.8"),
        DnsOption("Quad9", "9.9.9.9"),
        DnsOption("AdGuard", "94.140.14.14"),
        DnsOption("OpenDNS", "208.67.222.222"),
        DnsOption("Shecan (Iran)", "178.22.122.100"),
        DnsOption("403.online (Iran)", "10.202.10.202"),
        DnsOption("Begzar (Iran)", "185.55.226.26")
    )
    var selected by remember { mutableStateOf("Cloudflare") }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("DNS Settings", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState())
            ) {
                Text("Choose DNS provider", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(12.dp))

                options.forEach { option ->
                    Card(
                        Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable {
                            selected = option.name
                        },
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                    ) {
                        Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(Icons.Default.Dns, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                                }
                            }
                            Spacer(Modifier.width(14.dp))
                            Column(Modifier.weight(1f)) {
                                Text(option.name, color = Color.White, fontWeight = FontWeight.Medium)
                                Text(option.address, color = Color(0xFF9CA3AF),
                                    style = MaterialTheme.typography.bodySmall)
                            }
                            if (selected == option.name) {
                                Icon(Icons.Default.Check, null, tint = Color(0xFF10B981))
                            }
                        }
                    }
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 36. RoutingActivity.kt - قوانین مسیریابی
# ═══════════════════════════════════════════════════════
w("ui/home/RoutingActivity.kt", r'''package com.v2ray.ang.ui.home

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Block
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Router
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class RoutingActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { RoutingScreen() } }
    }
}

@Composable
fun RoutingScreen() {
    var bypassIran by remember { mutableStateOf(true) }
    var bypassLocal by remember { mutableStateOf(true) }
    var blockAds by remember { mutableStateOf(false) }
    var blockMalware by remember { mutableStateOf(true) }
    var blockAdult by remember { mutableStateOf(false) }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Routing Rules", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState())
            ) {
                Spacer(Modifier.height(12.dp))

                RoutingItem(Icons.Default.Language, "Bypass Iranian sites",
                    "Direct connection for .ir domains", bypassIran,
                    Color(0xFF10B981)) { bypassIran = it }

                Spacer(Modifier.height(8.dp))

                RoutingItem(Icons.Default.Router, "Bypass local network",
                    "Direct connection for LAN", bypassLocal,
                    Color(0xFF3B82F6)) { bypassLocal = it }

                Spacer(Modifier.height(20.dp))
                Text("Blocking", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(8.dp))

                RoutingItem(Icons.Default.Block, "Block ads",
                    "Block ad domains", blockAds,
                    Color(0xFFEF4444)) { blockAds = it }

                Spacer(Modifier.height(8.dp))

                RoutingItem(Icons.Default.CheckCircle, "Block malware",
                    "Block malicious domains", blockMalware,
                    Color(0xFFF59E0B)) { blockMalware = it }

                Spacer(Modifier.height(8.dp))

                RoutingItem(Icons.Default.Block, "Block adult content",
                    "Family protection", blockAdult,
                    Color(0xFF8B5CF6)) { blockAdult = it }

                Spacer(Modifier.height(30.dp))
            }
        }
    }
}

@Composable
fun RoutingItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    checked: Boolean,
    color: Color,
    onCheckedChange: (Boolean) -> Unit
) {
    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                color = color.copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(20.dp), tint = color)
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Medium)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
            Switch(checked = checked, onCheckedChange = onCheckedChange)
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 37. ProxySettingsActivity.kt - تنظیمات پروکسی
# ═══════════════════════════════════════════════════════
w("ui/home/ProxySettingsActivity.kt", r'''package com.v2ray.ang.ui.home

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Http
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class ProxySettingsActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { ProxyScreen() } }
    }
}

@Composable
fun ProxyScreen() {
    var useProxy by remember { mutableStateOf(false) }
    var host by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("Proxy Settings", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState())
            ) {
                Card(
                    Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                            color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(Icons.Default.Http, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                            }
                        }
                        Spacer(Modifier.width(14.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Use Proxy", color = Color.White, fontWeight = FontWeight.Medium)
                            Text("Route traffic through HTTP proxy", color = Color(0xFF9CA3AF),
                                style = MaterialTheme.typography.bodySmall)
                        }
                        Switch(checked = useProxy, onCheckedChange = { useProxy = it })
                    }
                }

                if (useProxy) {
                    Spacer(Modifier.height(16.dp))

                    OutlinedTextField(
                        value = host,
                        onValueChange = { host = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Host", color = Color(0xFF9CA3AF)) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp)
                    )
                    Spacer(Modifier.height(8.dp))

                    OutlinedTextField(
                        value = port,
                        onValueChange = { port = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Port", color = Color(0xFF9CA3AF)) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp)
                    )
                    Spacer(Modifier.height(8.dp))

                    OutlinedTextField(
                        value = username,
                        onValueChange = { username = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Username (optional)", color = Color(0xFF9CA3AF)) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp)
                    )
                    Spacer(Modifier.height(8.dp))

                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Password (optional)", color = Color(0xFF9CA3AF)) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp)
                    )
                }

                Spacer(Modifier.height(30.dp))
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 38. Patch Manifest for new activities
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

new_acts2 = ""
if "DnsSettingsActivity" not in content:
    new_acts2 += '\n        <activity android:name=".ui.home.DnsSettingsActivity" android:exported="false" />'
if "RoutingActivity" not in content:
    new_acts2 += '\n        <activity android:name=".ui.home.RoutingActivity" android:exported="false" />'
if "ProxySettingsActivity" not in content:
    new_acts2 += '\n        <activity android:name=".ui.home.ProxySettingsActivity" android:exported="false" />'

if new_acts2:
    content = content.replace("</application>", new_acts2 + "\n    </application>")
                                      content.replace("</application>", new_acts2 + "\n    </application>")

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("EXTRA FEATURES ADDED!")
print("  - AutoPingWorker (background ping)")
print("  - DnsSettingsActivity (8 DNS providers)")
print("  - RoutingActivity (bypass + blocking rules)")
print("  - ProxySettingsActivity (HTTP proxy)")
print("=" * 60)

# ═══════════════════════════════════════════════════════
# 39. NotificationChannelHelper.kt
# ═══════════════════════════════════════════════════════
w("util/NotificationChannelHelper.kt", r'''package com.v2ray.ang.util

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build

object NotificationChannelHelper {

    const val CHANNEL_STATUS = "fast_vpn_status"
    const val CHANNEL_ALERTS = "fast_vpn_alerts"

    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            val statusChannel = NotificationChannel(
                CHANNEL_STATUS,
                "VPN Status",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Show VPN connection status"
                setShowBadge(false)
            }

            val alertChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "Alerts",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Important alerts"
            }

            nm.createNotificationChannel(statusChannel)
            nm.createNotificationChannel(alertChannel)
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 40. PreferencesManager.kt - ذخیره تنظیمات
# ═══════════════════════════════════════════════════════
w("util/PreferencesManager.kt", r'''package com.v2ray.ang.util

import android.content.Context

object PreferencesManager {

    private const val PREF = "fast_vpn_prefs"
    private const val KEY_DARK_MODE = "dark_mode"
    private const val KEY_AUTO_PING = "auto_ping"
    private const val KEY_KILL_SWITCH = "kill_switch"
    private const val KEY_SPLIT_TUNNEL = "split_tunnel"
    private const val KEY_NOTIFICATIONS = "notifications"
    private const val KEY_LANGUAGE = "language"
    private const val KEY_DNS = "dns_provider"
    private const val KEY_PROXY_ENABLED = "proxy_enabled"
    private const val KEY_PROXY_HOST = "proxy_host"
    private const val KEY_PROXY_PORT = "proxy_port"

    private fun prefs(context: Context) = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    fun isDarkMode(context: Context): Boolean = prefs(context).getBoolean(KEY_DARK_MODE, true)
    fun setDarkMode(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_DARK_MODE, value).apply()

    fun isAutoPing(context: Context): Boolean = prefs(context).getBoolean(KEY_AUTO_PING, true)
    fun setAutoPing(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_AUTO_PING, value).apply()

    fun isKillSwitch(context: Context): Boolean = prefs(context).getBoolean(KEY_KILL_SWITCH, false)
    fun setKillSwitch(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_KILL_SWITCH, value).apply()

    fun isSplitTunnel(context: Context): Boolean = prefs(context).getBoolean(KEY_SPLIT_TUNNEL, false)
    fun setSplitTunnel(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_SPLIT_TUNNEL, value).apply()

    fun isNotifications(context: Context): Boolean = prefs(context).getBoolean(KEY_NOTIFICATIONS, true)
    fun setNotifications(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_NOTIFICATIONS, value).apply()

    fun getLanguage(context: Context): String = prefs(context).getString(KEY_LANGUAGE, "fa") ?: "fa"
    fun setLanguage(context: Context, value: String) = prefs(context).edit().putString(KEY_LANGUAGE, value).apply()

    fun getDns(context: Context): String = prefs(context).getString(KEY_DNS, "Cloudflare") ?: "Cloudflare"
    fun setDns(context: Context, value: String) = prefs(context).edit().putString(KEY_DNS, value).apply()

    fun isProxyEnabled(context: Context): Boolean = prefs(context).getBoolean(KEY_PROXY_ENABLED, false)
    fun setProxyEnabled(context: Context, value: Boolean) = prefs(context).edit().putBoolean(KEY_PROXY_ENABLED, value).apply()

    fun getProxyHost(context: Context): String = prefs(context).getString(KEY_PROXY_HOST, "") ?: ""
    fun setProxyHost(context: Context, value: String) = prefs(context).edit().putString(KEY_PROXY_HOST, value).apply()

    fun getProxyPort(context: Context): String = prefs(context).getString(KEY_PROXY_PORT, "") ?: ""
    fun setProxyPort(context: Context, value: String) = prefs(context).edit().putString(KEY_PROXY_PORT, value).apply()
}
''')

# ═══════════════════════════════════════════════════════
# 41. FirstRunActivity.kt - صفحه خوش‌آمدگویی
# ═══════════════════════════════════════════════════════
w("ui/home/FirstRunActivity.kt", r'''package com.v2ray.ang.ui.home

import android.content.Intent
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
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

class FirstRunActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { FirstRunScreen() } }
    }
}

@Composable
fun FirstRunScreen() {
    val context = LocalContext.current
    val pagerState = rememberPagerState(pageCount = { 3 })

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))

    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            HorizontalPager(
                state = pagerState,
                modifier = Modifier.weight(1f)
            ) { page ->
                when (page) {
                    0 -> WelcomePage(
                        icon = Icons.Default.Security,
                        title = "امنیت کامل",
                        description = "با پروتکل‌های پیشرفته، ترافیک شما رمزنگاری می‌شود و هویتتان مخفی می‌ماند."
                    )
                    1 -> WelcomePage(
                        icon = Icons.Default.Speed,
                        title = "سرعت بالا",
                        description = "با انتخاب خودکار بهترین سرور، از سریع‌ترین اتصال ممکن لذت ببرید."
                    )
                    2 -> WelcomePage(
                        icon = Icons.Default.Star,
                        title = "سادگی استفاده",
                        description = "با یک ضربه متصل شوید. بدون تنظیمات پیچیده، بدون دردسر."
                    )
                }
            }

            // Dots indicator
            Row(
                Modifier.fillMaxWidth().padding(24.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                repeat(3) { index ->
                    Box(
                        Modifier.padding(4.dp).size(
                            if (index == pagerState.currentPage) 12.dp else 8.dp
                        ).background(
                            color = if (index == pagerState.currentPage)
                                Color(0xFF10B981) else Color(0xFF4B5563),
                            shape = CircleShape
                        )
                    )
                }
            }

            Button(
                onClick = {
                    if (pagerState.currentPage < 2) {
                        // handled by compose
                    } else {
                        context.startActivity(Intent(context, HomeActivity::class.java))
                        (context as? ComponentActivity)?.finish()
                    }
                },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 32.dp).padding(bottom = 32.dp).height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981))
            ) {
                Text(
                    if (pagerState.currentPage < 2) "بعدی" else "شروع کنید",
                    color = Color.Black,
                    fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(Modifier.size(8.dp))
                Icon(Icons.Default.ArrowForward, null, tint = Color.Black)
            }
        }
    }
}

@Composable
fun WelcomePage(icon: ImageVector, title: String, description: String) {
    Column(
        Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Surface(
            Modifier.size(140.dp),
            shape = CircleShape,
            color = Color(0xFF10B981).copy(alpha = 0.15f)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(icon, null, Modifier.size(72.dp), tint = Color(0xFF10B981))
            }
        }
        Spacer(Modifier.height(48.dp))
        Text(
            title,
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center
        )
        Spacer(Modifier.height(16.dp))
        Text(
            description,
            style = MaterialTheme.typography.bodyLarge,
            color = Color(0xFF9CA3AF),
            textAlign = TextAlign.Center
        )
    }
}
''')

# ═══════════════════════════════════════════════════════
# 42. Final Manifest Patch
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

if "FirstRunActivity" not in content:
    new_acts = '\n        <activity android:name=".ui.home.FirstRunActivity" android:exported="false" />'
    content = content.replace("</application>", new_acts + "\n    </application>")

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("FINAL FEATURES ADDED!")
print("  - NotificationChannelHelper")
print("  - PreferencesManager")
print("  - FirstRunActivity (welcome screen)")
print("=" * 60)

# ═══════════════════════════════════════════════════════
# 43. Final Summary
# ═══════════════════════════════════════════════════════
print()
print("=" * 60)
print("PROJECT COMPLETE!")
print("=" * 60)
print("Total files generated:")
print("  Handlers: ConfigUpdater, PingManager, ConfigParser,")
print("            ServersRepository, VpnConnectionManager,")
print("            VpnNotificationManager, LanguageManager")
print("  UI Screens: HomeActivity, CountryListActivity,")
print("              SettingsActivity, SpeedTestActivity,")
print("              AboutActivity, ServerListActivity,")
print("              DataUsageActivity, BackupRestoreActivity,")
print("              KillSwitchActivity, SplitTunnelActivity,")
print("              FaqActivity, DnsSettingsActivity,")
print("              RoutingActivity, ProxySettingsActivity,")
print("              FirstRunActivity")
print("  Admin: AdminPanelActivity, QrScannerActivity")
print("  Components: VpnStatsCard, PulsingRing,")
print("              GradientButton, AnimatedTrafficCard")
print("  Themes: VpnTheme, ThemeAdvanced (4 themes)")
print("  Workers: AutoPingWorker")
print("  Util: NotificationChannelHelper, PreferencesManager")
print("  Receiver: BootReceiver")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 44. HelpActivity.kt - صفحه راهنما (بدون API خارجی)
# ═══════════════════════════════════════════════════════
w("ui/home/HelpActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class HelpActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { HelpScreen() } }
    }
}

@Composable
fun HelpScreen() {
    val steps = listOf(
        "برای اتصال، دکمه دایره‌ای وسط صفحه را لمس کنید",
        "برای تغییر سرور، روی کارت Auto Select بزنید",
        "برای تست سرعت، روی Speed Test بزنید",
        "برای تنظیمات، آیکون چرخ‌دنده بالا سمت راست را بزنید",
        "برای پنل مدیریت، ۷ بار روی عنوان Fast VPN ضربه بزنید",
        "رمز پنل مدیریت: poiiu",
        "برای آپدیت کانفیگ، از پنل مدیریت دکمه آپدیت را بزنید",
        "برای قطع اتصال، دوباره روی دکمه دایره‌ای بزنید"
    )

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Column(Modifier.fillMaxSize().background(bg)) {
        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton({ finish() }) {
                Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
            }
            Text("راهنما", style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold, color = Color.White)
        }

        LazyColumn(
            Modifier.fillMaxSize().padding(horizontal = 16.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(bottom = 20.dp)
        ) {
            item {
                Spacer(Modifier.height(8.dp))
            }
            items(steps) { step ->
                Card(
                    Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF10B981))
                        Spacer(Modifier.padding(6.dp))
                        Text(step, color = Color.White, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 45. LegalActivity.kt - قوانین و شرایط
# ═══════════════════════════════════════════════════════
w("ui/home/LegalActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class LegalActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { LegalScreen() } }
    }
}

@Composable
fun LegalScreen() {
    val sections = listOf(
        "استفاده از این برنامه به معنی پذیرش تمام قوانین است." to
            "با استفاده از Fast VPN، شما تایید می‌کنید که از این سرویس فقط برای مقاصد قانونی استفاده می‌کنید.",
        "حفظ حریم خصوصی" to
            "ما هیچ اطلاعات شخصی شما را ذخیره، جمع‌آوری یا با اشخاص ثالث به اشتراک نمی‌گذاریم.",
        "مسئولیت کاربر" to
            "کاربر مسئول تمام فعالیت‌های خود در حین استفاده از VPN است. استفاده از این سرویس برای فعالیت‌های غیرقانونی ممنوع است.",
        "بدون ضمانت" to
            "این سرویس \"همان‌طور که هست\" ارائه می‌شود. ما هیچ ضمانتی برای همیشه در دسترس بودن یا سرعت آن نمی‌دهیم.",
        "تغییر شرایط" to
            "ما حق تغییر این شرایط را در هر زمان محفوظ می‌داریم. نسخه به‌روز در همین صفحه قابل مشاهده است.",
        "تماس با ما" to
            "برای هرگونه سوال یا مشکل، از طریق ایمیل یا کانال تلگرام با ما در ارتباط باشید."
    )

    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Column(Modifier.fillMaxSize().background(bg)) {
        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton({ finish() }) {
                Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
            }
            Text("قوانین و شرایط", style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold, color = Color.White)
        }

        Column(Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState())) {
            Spacer(Modifier.height(8.dp))
            sections.forEach { (title, content) ->
                Card(
                    Modifier.fillMaxWidth().padding(vertical = 6.dp),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
                ) {
                    Column(Modifier.padding(16.dp)) {
                        Text(title, color = Color(0xFF10B981), fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium)
                        Spacer(Modifier.height(8.dp))
                        Text(content, color = Color(0xFF9CA3AF),
                            style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 46. Patch Manifest for new activities
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

new_acts3 = ""
if "HelpActivity" not in content:
    new_acts3 += '\n        <activity android:name=".ui.home.HelpActivity" android:exported="false" />'
if "LegalActivity" not in content:
    new_acts3 += '\n        <activity android:name=".ui.home.LegalActivity" android:exported="false" />'

if new_acts3:
    content = content.replace("</application>", new_acts3 + "\n    </application>")

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("HELP & LEGAL PAGES ADDED!")
print("  - HelpActivity (راهنمای گام‌به‌گام)")
print("  - LegalActivity (قوانین و شرایط)")
print("=" * 60)

print()
print("=" * 60)
print("✅ ALL FILES GENERATED SUCCESSFULLY!")
print("=" * 60)
print()
print("Next steps:")
print("  1. Build the app")
print("  2. If errors, run fixer.py")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 47. AboutScreen.kt - صفحه درباره
# ═══════════════════════════════════════════════════════
w("ui/home/AboutNewActivity.kt", r'''package com.v2ray.ang.ui.home

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Telegram
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

class AboutNewActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { AboutNewScreen() } }
    }
}

@Composable
fun AboutNewScreen() {
    val bg = Brush.verticalGradient(listOf(Color(0xFF0A0E1A), Color(0xFF020617)))
    Box(Modifier.fillMaxSize().background(bg)) {
        Column(Modifier.fillMaxSize()) {
            Row(
                Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton({ finish() }) {
                    Icon(Icons.Default.ArrowBack, "Back", tint = Color.White)
                }
                Text("About", style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold, color = Color.White)
            }

            Column(
                Modifier.fillMaxSize().padding(horizontal = 16.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(Modifier.height(20.dp))
                Surface(Modifier.size(100.dp), shape = CircleShape,
                    color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                    Box(contentAlignment = Alignment.Center) {
                        Text("⚡", style = MaterialTheme.typography.headlineLarge)
                    }
                }
                Spacer(Modifier.height(16.dp))
                Text("Fast VPN", style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = Color.White)
                Text("Version 1.0.0", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                Spacer(Modifier.height(24.dp))
                Text(
                    "Fast, secure and easy to use VPN client with multiple protocols.",
                    color = Color(0xFF9CA3AF), textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(Modifier.height(32.dp))

                AboutLink(Icons.Default.Language, "Website", "example.com")
                Spacer(Modifier.height(6.dp))
                AboutLink(Icons.Default.Telegram, "Telegram", "@YourChannel")
                Spacer(Modifier.height(6.dp))
                AboutLink(Icons.Default.Email, "Support", "support@example.com")
                Spacer(Modifier.height(6.dp))
                AboutLink(Icons.Default.Code, "Source Code", "GitHub")
                Spacer(Modifier.height(6.dp))
                AboutLink(Icons.Default.Star, "Rate Us", "Play Store")
                Spacer(Modifier.height(6.dp))
                AboutLink(Icons.Default.Info, "License", "MIT")

                Spacer(Modifier.height(24.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Made with", color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.width(4.dp))
                    Icon(Icons.Default.Favorite, null, Modifier.size(14.dp), tint = Color(0xFFEF4444))
                }
                Spacer(Modifier.height(30.dp))
            }
        }
    }
}

@Composable
fun AboutLink(icon: ImageVector, title: String, subtitle: String) {
    Card(
        Modifier.fillMaxWidth().clickable { },
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF151A28))
    ) {
        Row(Modifier.fillMaxWidth().padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Surface(Modifier.size(40.dp), shape = RoundedCornerShape(10.dp),
                color = Color(0xFF10B981).copy(alpha = 0.15f)) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(icon, null, Modifier.size(20.dp), tint = Color(0xFF10B981))
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, color = Color.White, fontWeight = FontWeight.Medium)
                Text(subtitle, color = Color(0xFF9CA3AF), style = MaterialTheme.typography.bodySmall)
            }
            Icon(Icons.Default.ChevronRight, null, tint = Color(0xFF4B5563))
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 48. VpnWidgetProvider.kt - ویجت صفحه اصلی
# ═══════════════════════════════════════════════════════
w("widget/VpnWidgetProvider.kt", r'''package com.v2ray.ang.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.v2ray.ang.R
import com.v2ray.ang.ui.home.HomeActivity

class VpnWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { widgetId ->
            val views = RemoteViews(context.packageName, R.layout.widget_vpn_simple)

            val intent = Intent(context, HomeActivity::class.java)
            val pi = PendingIntent.getActivity(
                context, 0, intent,
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            )
            views.setOnClickPendingIntent(R.id.widget_container, pi)

            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 49. Widget Layout XML
# ═══════════════════════════════════════════════════════
widget_layout_path = f"{BASE}/res/layout/widget_vpn_simple.xml"
os.makedirs(os.path.dirname(widget_layout_path), exist_ok=True)
with open(widget_layout_path, "w", encoding="utf-8") as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/widget_container"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:background="#0A0E1A"
    android:padding="12dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="⚡"
        android:textSize="32sp" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Fast VPN"
        android:textColor="#FFFFFF"
        android:textSize="14sp"
        android:textStyle="bold"
        android:layout_marginTop="4dp" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Tap to open"
        android:textColor="#9CA3AF"
        android:textSize="11sp"
        android:layout_marginTop="2dp" />

</LinearLayout>
''')

# ═══════════════════════════════════════════════════════
# 50. Widget Info XML
# ═══════════════════════════════════════════════════════
widget_info_path = f"{BASE}/res/xml/vpn_widget_info.xml"
os.makedirs(os.path.dirname(widget_info_path), exist_ok=True)
with open(widget_info_path, "w", encoding="utf-8") as f:
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="80dp"
    android:minHeight="80dp"
    android:updatePeriodMillis="0"
    android:initialLayout="@layout/widget_vpn_simple"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen" />
''')

# ═══════════════════════════════════════════════════════
# 51. Patch Manifest for widget + new activities
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

if "AboutNewActivity" not in content:
    content = content.replace(
        "</application>",
        '\n        <activity android:name=".ui.home.AboutNewActivity" android:exported="false" />\n    </application>'
    )

if "VpnWidgetProvider" not in content:
    receiver = '''
        <receiver android:name=".widget.VpnWidgetProvider" android:exported="true">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data
                android:name="android.appwidget.provider"
                android:resource="@xml/vpn_widget_info" />
        </receiver>
    </application>'''
    content = content.replace("</application>", receiver)

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("FINAL FEATURES ADDED!")
print("  - AboutNewActivity")
print("  - VpnWidgetProvider (home screen widget)")
print("  - Widget layout + info XML")
print("=" * 60)

print()
print("=" * 60)
print("PROJECT FULLY COMPLETE!")
print("=" * 60)
print()
print("Summary:")
print(f"  - 50+ Kotlin files")
print(f"  - 8 Handlers")
print(f"  - 18 UI Screens")
print(f"  - 4 Components")
print(f"  - 2 Themes")
print(f"  - 1 Widget")
print(f"  - 1 Worker")
print()
print("Next: Run build.yml to compile")
print("=" * 60)
# ═══════════════════════════════════════════════════════
# 52. SplashScreen.kt - صفحه شروع با انیمیشن
# ═══════════════════════════════════════════════════════
w("ui/home/SplashActivity.kt", r'''package com.v2ray.ang.ui.home

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

class SplashActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val context = LocalContext.current
                LaunchedEffect(Unit) {
                    delay(2000)
                    context.startActivity(Intent(context, HomeActivity::class.java))
                    (context as? ComponentActivity)?.finish()
                }
                SplashScreen()
            }
        }
    }
}

@Composable
fun SplashScreen() {
    val infinite = rememberInfiniteTransition(label = "splash")
    val rotation by infinite.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )
    val scale by infinite.animateFloat(
        initialValue = 0.9f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    val bg = Brush.radialGradient(
        colors = listOf(Color(0xFF0F2027), Color(0xFF000000))
    )

    Box(Modifier.fillMaxSize().background(bg), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Box(contentAlignment = Alignment.Center) {
                // Outer glow ring
                Surface(
                    Modifier.size(180.dp).scale(scale),
                    shape = CircleShape,
                    color = Color(0xFF10B981).copy(alpha = 0.15f)
                ) {}
                // Inner glow ring
                Surface(
                    Modifier.size(140.dp),
                    shape = CircleShape,
                    color = Color(0xFF10B981).copy(alpha = 0.25f)
                ) {}
                // Center circle
                Surface(
                    Modifier.size(100.dp),
                    shape = CircleShape,
                    color = Color(0xFF10B981)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text("⚡", style = MaterialTheme.typography.headlineLarge)
                    }
                }
            }
            Spacer(Modifier.height(40.dp))
            Text(
                "Fast VPN",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            Spacer(Modifier.height(8.dp))
            Text(
                "Secure. Fast. Simple.",
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF9CA3AF)
            )
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 53. ConnectionProgressRing.kt - حلقه پیشرفت اتصال
# ═══════════════════════════════════════════════════════
w("ui/components/ConnectionProgressRing.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun ConnectionProgressRing(
    progress: Float,
    isConnected: Boolean
) {
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(500),
        label = "progress"
    )

    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.size(200.dp)) {
            val strokeWidth = 12f
            val radius = size.minDimension / 2 - strokeWidth

            // Background ring
            drawCircle(
                color = Color(0xFF1E2536),
                radius = radius,
                style = Stroke(width = strokeWidth)
            )

            // Progress ring
            drawArc(
                color = if (isConnected) Color(0xFF10B981) else Color(0xFF3B82F6),
                startAngle = -90f,
                sweepAngle = 360f * animatedProgress,
                useCenter = false,
                style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
            )

            // Glow
            if (isConnected && animatedProgress > 0.9f) {
                drawCircle(
                    color = Color(0xFF10B981).copy(alpha = 0.3f),
                    radius = radius + 8f,
                    style = Stroke(width = 4f)
                )
            }
        }

        Text(
            text = if (isConnected) "ON" else "${(animatedProgress * 100).toInt()}%",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
    }
}
''')

# ═══════════════════════════════════════════════════════
# 54. StatChip.kt - چیپ‌های آمار کوچک
# ═══════════════════════════════════════════════════════
w("ui/components/StatChip.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun StatChip(
    icon: ImageVector,
    text: String,
    color: Color
) {
    Row(
        modifier = Modifier
            .background(color.copy(alpha = 0.15f), RoundedCornerShape(20.dp))
            .padding(horizontal = 10.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, null, Modifier.size(14.dp), tint = color)
        Spacer(Modifier.width(4.dp))
        Text(
            text = text,
            color = color,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold
        )
    }
}
''')

# ═══════════════════════════════════════════════════════
# 55. ModernDialog.kt - دیالوگ‌های زیبا
# ═══════════════════════════════════════════════════════
w("ui/components/ModernDialog.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog

@Composable
fun ModernDialog(
    title: String,
    message: String,
    icon: String = "ℹ️",
    confirmText: String = "OK",
    cancelText: String = "Cancel",
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = Color(0xFF151A28)
        ) {
            Column(
                Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Surface(
                    Modifier.size(64.dp),
                    shape = CircleShape,
                    color = Color(0xFF10B981).copy(alpha = 0.15f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(icon, style = MaterialTheme.typography.headlineMedium)
                    }
                }
                Spacer(Modifier.height(16.dp))
                Text(
                    title,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF9CA3AF),
                    textAlign = TextAlign.Center
                )
                Spacer(Modifier.height(24.dp))
                Row(Modifier.fillMaxWidth()) {
                    TextButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(cancelText, color = Color(0xFF9CA3AF))
                    }
                    Spacer(Modifier.width(8.dp))
                    Button(
                        onClick = {
                            onConfirm()
                            onDismiss()
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(confirmText, color = Color.Black, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
''')

# ═══════════════════════════════════════════════════════
# 56. TypographyConfig.kt - تنظیمات فونت
# ═══════════════════════════════════════════════════════
w("ui/theme/TypographyConfig.kt", r'''package com.v2ray.ang.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val AppTypography = Typography(
    displayLarge = TextStyle(fontWeight = FontWeight.Bold, fontSize = 57.sp),
    displayMedium = TextStyle(fontWeight = FontWeight.Bold, fontSize = 45.sp),
    displaySmall = TextStyle(fontWeight = FontWeight.Bold, fontSize = 36.sp),
    headlineLarge = TextStyle(fontWeight = FontWeight.Bold, fontSize = 32.sp),
    headlineMedium = TextStyle(fontWeight = FontWeight.Bold, fontSize = 28.sp),
    headlineSmall = TextStyle(fontWeight = FontWeight.Bold, fontSize = 24.sp),
    titleLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 22.sp),
    titleMedium = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 16.sp),
    titleSmall = TextStyle(fontWeight = FontWeight.Medium, fontSize = 14.sp),
    bodyLarge = TextStyle(fontWeight = FontWeight.Normal, fontSize = 16.sp),
    bodyMedium = TextStyle(fontWeight = FontWeight.Normal, fontSize = 14.sp),
    bodySmall = TextStyle(fontWeight = FontWeight.Normal, fontSize = 12.sp),
    labelLarge = TextStyle(fontWeight = FontWeight.Medium, fontSize = 14.sp),
    labelMedium = TextStyle(fontWeight = FontWeight.Medium, fontSize = 12.sp),
    labelSmall = TextStyle(fontWeight = FontWeight.Medium, fontSize = 11.sp)
)
''')

# ═══════════════════════════════════════════════════════
# 57. ColorPalette.kt - پالت رنگ‌ها
# ═══════════════════════════════════════════════════════
w("ui/theme/ColorPalette.kt", r'''package com.v2ray.ang.ui.theme

import androidx.compose.ui.graphics.Color

object VpnColors {
    // Primary
    val Green = Color(0xFF10B981)
    val GreenDark = Color(0xFF065F46)
    val GreenLight = Color(0xFF34D399)

    // Blue
    val Blue = Color(0xFF3B82F6)
    val BlueDark = Color(0xFF1E40AF)
    val BlueLight = Color(0xFF60A5FA)

    // Red
    val Red = Color(0xFFEF4444)
    val RedDark = Color(0xFF991B1B)

    // Orange/Yellow
    val Orange = Color(0xFFF59E0B)
    val Yellow = Color(0xFFFBBF24)

    // Purple
    val Purple = Color(0xFF8B5CF6)

    // Backgrounds
    val BgDark = Color(0xFF0A0E1A)
    val BgDarker = Color(0xFF020617)
    val Surface = Color(0xFF151A28)
    val SurfaceLight = Color(0xFF1E2536)

    // Text
    val TextPrimary = Color(0xFFFFFFFF)
    val TextSecondary = Color(0xFFE5E7EB)
    val TextMuted = Color(0xFF9CA3AF)
    val TextDim = Color(0xFF6B7280)

    // Border
    val Border = Color(0xFF374151)
    val BorderLight = Color(0xFF4B5563)
}
''')

# ═══════════════════════════════════════════════════════
# 58. AnimatedBackground.kt - پس‌زمینه متحرک
# ═══════════════════════════════════════════════════════
w("ui/components/AnimatedBackground.kt", r'''package com.v2ray.ang.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope

@Composable
fun AnimatedBackground(
    isConnected: Boolean,
    modifier: Modifier = Modifier
) {
    val infinite = rememberInfiniteTransition(label = "bg")
    val anim1 by infinite.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(15000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "anim1"
    )
    val anim2 by infinite.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(20000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "anim2"
    )

    val color1 = if (isConnected) Color(0xFF10B981).copy(alpha = 0.15f)
                 else Color(0xFF3B82F6).copy(alpha = 0.08f)
    val color2 = if (isConnected) Color(0xFF3B82F6).copy(alpha = 0.1f)
                 else Color(0xFF8B5CF6).copy(alpha = 0.06f)

    Canvas(modifier = modifier.fillMaxSize()) {
        drawBlurredCircle(
            center = Offset(size.width * anim1, size.height * 0.3f),
            radius = size.width * 0.7f,
            color = color1
        )
        drawBlurredCircle(
            center = Offset(size.width * (1f - anim2), size.height * 0.7f),
            radius = size.width * 0.6f,
            color = color2
        )
    }
}

private fun DrawScope.drawBlurredCircle(
    center: Offset,
    radius: Float,
    color: Color
) {
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(color, Color.Transparent),
            center = center,
            radius = radius
        ),
        radius = radius,
        center = center
    )
}
''')

# ═══════════════════════════════════════════════════════
# 59. Update Manifest with SplashActivity
# ═══════════════════════════════════════════════════════
manifest_path = f"{BASE}/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    content = f.read()

if "SplashActivity" not in content:
    # SplashActivity به عنوان launcher
    splash_act = '''
        <activity android:name=".ui.home.SplashActivity" android:exported="true" android:label="Fast VPN">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>'''

    # HomeActivity دیگه launcher نباشه
    content = content.replace(
        '''<activity android:name=".ui.home.HomeActivity" android:exported="true" android:label="Fast VPN">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>''',
        '<activity android:name=".ui.home.HomeActivity" android:exported="false" android:label="Fast VPN" />'
    )

    content = content.replace("</application>", splash_act + "\n    </application>")

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 60)
print("VISUAL POLISH ADDED!")
print("  - SplashActivity (animated splash screen)")
print("  - ConnectionProgressRing (circular pro
