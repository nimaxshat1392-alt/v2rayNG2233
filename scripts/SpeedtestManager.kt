package com.v2ray.ang.handler

import com.v2ray.ang.dto.entities.ProfileItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.InetSocketAddress
import java.net.Socket

data class RemoteIPInfo(
    val ipAddress: String = "",
    val country: String = ""
)

object SpeedtestManager {

    fun socketConnectTime(address: String, port: Int): Long {
        return try {
            val start = System.currentTimeMillis()
            val socket = Socket()
            socket.connect(InetSocketAddress(address, port), 2000)
            val end = System.currentTimeMillis()
            socket.close()
            end - start
        } catch (e: Exception) { -1L }
    }

    suspend fun getRemoteIPInfo(): RemoteIPInfo = withContext(Dispatchers.IO) {
        try {
            val url = java.net.URL("https://api.ipify.org?format=json")
            val conn = url.openConnection() as java.net.HttpURLConnection
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            val response = conn.inputStream.bufferedReader().readText()
            val ip = Regex("\"ip\"\\s*:\\s*\"([^\"]+)\"").find(response)?.groupValues?.get(1) ?: ""
            RemoteIPInfo(ipAddress = ip, country = "")
        } catch (e: Exception) {
            RemoteIPInfo()
        }
    }

    fun getRealPingTime(guid: String): Long = 0L

    fun getRealPingTime(guid: String, onResult: (Long) -> Unit) {
        onResult(0L)
    }

    suspend fun testAllServersPing(servers: List<ProfileItem>) = Unit
}
