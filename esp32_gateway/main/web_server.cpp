/**
 * @file web_server.cpp
 * @brief Implementación del servidor web
 */

#include "web_server.h"
#include "esp_log.h"
#include <string.h>
#include <stdio.h>

static const char *TAG = "WEB_SERVER";

// Instancia global
WebServer* web_server = nullptr;

// HTML embebido para el panel de control
static const char index_html[] = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D13 Gateway - Panel de Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .status-item:last-child { border-bottom: none; }
        .label { font-weight: 600; color: #555; }
        .value {
            font-family: 'Courier New', monospace;
            color: #333;
            font-weight: bold;
        }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .status-warning { color: #ffc107; }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .controls {
            text-align: center;
            padding: 20px;
            background: #f1f3f5;
        }
        #connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: #28a745;
            color: white;
            border-radius: 25px;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .chart-container {
            height: 200px;
            margin-top: 15px;
        }
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="connection-status">🔴 Desconectado</div>
    
    <div class="container">
        <header>
            <h1>🔧 D13 Gateway</h1>
            <p class="subtitle">Panel de Control y Monitoreo</p>
        </header>

        <div class="grid">
            <!-- CAN Bus Status -->
            <div class="card">
                <h2>🚌 CAN Bus</h2>
                <div class="status-item">
                    <span class="label">Estado:</span>
                    <span class="value" id="can-status">●</span>
                </div>
                <div class="status-item">
                    <span class="label">RX Count:</span>
                    <span class="value" id="can-rx">0</span>
                </div>
                <div class="status-item">
                    <span class="label">TX Count:</span>
                    <span class="value" id="can-tx">0</span>
                </div>
                <div class="status-item">
                    <span class="label">Errores:</span>
                    <span class="value" id="can-errors">0</span>
                </div>
            </div>

            <!-- CiA402 State -->
            <div class="card">
                <h2>⚙️ CiA402 State</h2>
                <div class="status-item">
                    <span class="label">Estado:</span>
                    <span class="value" id="cia402-state">--</span>
                </div>
                <div class="status-item">
                    <span class="label">Status Word:</span>
                    <span class="value" id="status-word">0x0000</span>
                </div>
                <div class="status-item">
                    <span class="label">Control Word:</span>
                    <span class="value" id="control-word">0x0000</span>
                </div>
            </div>

            <!-- Network Status -->
            <div class="card">
                <h2>🌐 Network</h2>
                <div class="status-item">
                    <span class="label">Ethernet:</span>
                    <span class="value" id="eth-status">●</span>
                </div>
                <div class="status-item">
                    <span class="label">IP Address:</span>
                    <span class="value" id="ip-address">0.0.0.0</span>
                </div>
                <div class="status-item">
                    <span class="label">TCP Port:</span>
                    <span class="value" id="tcp-port">5000</span>
                </div>
                <div class="status-item">
                    <span class="label">Clientes:</span>
                    <span class="value" id="clients">0</span>
                </div>
            </div>

            <!-- System Status -->
            <div class="card">
                <h2>💻 System</h2>
                <div class="status-item">
                    <span class="label">Uptime:</span>
                    <span class="value" id="uptime">0s</span>
                </div>
                <div class="status-item">
                    <span class="label">Free Heap:</span>
                    <span class="value" id="heap">0 KB</span>
                </div>
                <div class="status-item">
                    <span class="label">CPU Usage:</span>
                    <span class="value" id="cpu">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-bar" style="width: 0%">0%</div>
                </div>
            </div>

            <!-- SD Logger Status -->
            <div class="card">
                <h2>💾 SD Logger</h2>
                <div class="status-item">
                    <span class="label">Estado:</span>
                    <span class="value" id="sd-status">●</span>
                </div>
                <div class="status-item">
                    <span class="label">Total:</span>
                    <span class="value" id="sd-total">0 MB</span>
                </div>
                <div class="status-item">
                    <span class="label">Usado:</span>
                    <span class="value" id="sd-used">0 MB</span>
                </div>
                <div class="status-item">
                    <span class="label">Archivos Log:</span>
                    <span class="value" id="log-files">0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="sd-bar" style="width: 0%">0%</div>
                </div>
            </div>

            <!-- OTA Status -->
            <div class="card">
                <h2>🔄 OTA Updates</h2>
                <div class="status-item">
                    <span class="label">Firmware:</span>
                    <span class="value" id="fw-version">--</span>
                </div>
                <div class="status-item">
                    <span class="label">Partition:</span>
                    <span class="value" id="ota-partition">--</span>
                </div>
                <div class="status-item">
                    <span class="label">Pendiente:</span>
                    <span class="value" id="ota-pending">NO</span>
                </div>
            </div>
        </div>

        <div class="controls">
            <h2>Control de Estado CiA402</h2>
            <button class="btn" onclick="sendCommand('SHUTDOWN')">Shutdown</button>
            <button class="btn" onclick="sendCommand('SWITCH_ON')">Switch On</button>
            <button class="btn" onclick="sendCommand('ENABLE')">Enable Operation</button>
            <button class="btn" onclick="sendCommand('DISABLE')">Disable</button>
            <button class="btn" onclick="sendCommand('QUICK_STOP')">Quick Stop</button>
            <button class="btn btn-danger" onclick="sendCommand('OTA_ROLLBACK')">⚠️ Rollback</button>
        </div>
    </div>

    <script>
        let updateInterval = null;

        function startPolling() {
            // Actualizar cada 2 segundos
            updateInterval = setInterval(updateStatus, 2000);
            updateStatus(); // Primera actualización inmediata
        }

        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('connection-status').innerHTML = '🟢 Conectado';
                    document.getElementById('connection-status').style.background = '#28a745';
                    updateUI(data);
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                    document.getElementById('connection-status').innerHTML = '🔴 Desconectado';
                    document.getElementById('connection-status').style.background = '#dc3545';
                });
        }

        function updateUI(data) {
            // CAN Bus
            document.getElementById('can-status').innerHTML = data.can_online ? '<span class="status-online">● Online</span>' : '<span class="status-offline">● Offline</span>';
            document.getElementById('can-rx').textContent = data.can_rx_count.toLocaleString();
            document.getElementById('can-tx').textContent = data.can_tx_count.toLocaleString();
            document.getElementById('can-errors').textContent = data.can_errors;

            // CiA402
            document.getElementById('cia402-state').textContent = data.cia402_state;
            document.getElementById('status-word').textContent = '0x' + data.status_word.toString(16).toUpperCase().padStart(4, '0');
            document.getElementById('control-word').textContent = '0x' + data.control_word.toString(16).toUpperCase().padStart(4, '0');

            // Network
            document.getElementById('eth-status').innerHTML = data.eth_connected ? '<span class="status-online">● Connected</span>' : '<span class="status-offline">● Disconnected</span>';
            document.getElementById('ip-address').textContent = data.ip_address;
            document.getElementById('tcp-port').textContent = data.tcp_port;
            document.getElementById('clients').textContent = data.clients_connected;

            // System
            const hours = Math.floor(data.uptime_seconds / 3600);
            const mins = Math.floor((data.uptime_seconds % 3600) / 60);
            const secs = data.uptime_seconds % 60;
            document.getElementById('uptime').textContent = `${hours}h ${mins}m ${secs}s`;
            document.getElementById('heap').textContent = (data.free_heap / 1024).toFixed(1) + ' KB';
            document.getElementById('cpu').textContent = data.cpu_usage + '%';
            document.getElementById('cpu-bar').style.width = data.cpu_usage + '%';
            document.getElementById('cpu-bar').textContent = data.cpu_usage + '%';

            // SD Logger
            document.getElementById('sd-status').innerHTML = data.sd_mounted ? '<span class="status-online">● Mounted</span>' : '<span class="status-offline">● Not Mounted</span>';
            document.getElementById('sd-total').textContent = data.sd_total_mb + ' MB';
            document.getElementById('sd-used').textContent = data.sd_used_mb + ' MB';
            document.getElementById('log-files').textContent = data.log_files_count;
            if (data.sd_total_mb > 0) {
                const sdPercent = (data.sd_used_mb / data.sd_total_mb * 100).toFixed(1);
                document.getElementById('sd-bar').style.width = sdPercent + '%';
                document.getElementById('sd-bar').textContent = sdPercent + '%';
            }

            // OTA
            document.getElementById('fw-version').textContent = data.firmware_version;
            document.getElementById('ota-partition').textContent = data.ota_partition;
            document.getElementById('ota-pending').textContent = data.ota_pending ? 'YES ⚠️' : 'NO';
        }

        function sendCommand(cmd) {
            fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd })
            })
            .then(response => response.json())
            .then(data => {
                alert(`Comando ${cmd}: ${data.result}`);
            })
            .catch(error => {
                alert(`Error: ${error}`);
            });
        }

        // Iniciar polling al cargar la página
        startPolling();
    </script>
</body>
</html>
)rawliteral";

WebServer::WebServer() : 
    server_(nullptr),
    status_callback_(nullptr) {
}

WebServer::~WebServer() {
    stop();
}

esp_err_t WebServer::init(uint16_t port) {
    if (server_) {
        ESP_LOGW(TAG, "Server already running");
        return ESP_OK;
    }

    ESP_LOGI(TAG, "Starting web server on port %d...", port);

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = port;
    config.max_uri_handlers = 10;
    config.max_open_sockets = 7;
    config.stack_size = 8192;

    esp_err_t ret = httpd_start(&server_, &config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to start server: %s", esp_err_to_name(ret));
        return ret;
    }

    register_handlers();

    ESP_LOGI(TAG, "✅ Web server started successfully");
    return ESP_OK;
}

esp_err_t WebServer::stop() {
    if (!server_) {
        return ESP_OK;
    }

    esp_err_t ret = httpd_stop(server_);
    server_ = nullptr;
    
    ESP_LOGI(TAG, "Web server stopped");
    return ret;
}

void WebServer::register_handlers() {
    // Página principal
    httpd_uri_t index_uri = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = index_handler,
        .user_ctx = this
    };
    httpd_register_uri_handler(server_, &index_uri);

    // WebSocket (sin campo is_websocket en ESP-IDF 5.1)
    httpd_uri_t ws_uri = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = ws_handler,
        .user_ctx = this
    };
    httpd_register_uri_handler(server_, &ws_uri);

    // API Status
    httpd_uri_t status_uri = {
        .uri = "/api/status",
        .method = HTTP_GET,
        .handler = api_status_handler,
        .user_ctx = this
    };
    httpd_register_uri_handler(server_, &status_uri);
}

esp_err_t WebServer::index_handler(httpd_req_t *req) {
    httpd_resp_set_type(req, "text/html");
    httpd_resp_send(req, index_html, HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

esp_err_t WebServer::ws_handler(httpd_req_t *req) {
    if (req->method == HTTP_GET) {
        ESP_LOGI(TAG, "WebSocket client connected");
        return ESP_OK;
    }

    // Echo simple para mantener conexión viva  
    uint8_t buf[128] = {0};
    httpd_req_recv(req, (char*)buf, sizeof(buf));
    
    return ESP_OK;
}

esp_err_t WebServer::api_status_handler(httpd_req_t *req) {
    WebServer* server = (WebServer*)req->user_ctx;
    
    GatewayStatus status = {};
    if (server->status_callback_) {
        server->status_callback_(status);
    }

    char json[1024];
    build_status_json(status, json, sizeof(json));

    httpd_resp_set_type(req, "application/json");
    httpd_resp_send(req, json, HTTPD_RESP_USE_STRLEN);
    
    return ESP_OK;
}

void WebServer::build_status_json(const GatewayStatus& status, char* buffer, size_t size) {
    snprintf(buffer, size,
        "{"
        "\"can_online\":%s,"
        "\"can_rx_count\":%lu,"
        "\"can_tx_count\":%lu,"
        "\"can_errors\":%lu,"
        "\"cia402_state\":%u,"
        "\"status_word\":%u,"
        "\"control_word\":%u,"
        "\"eth_connected\":%s,"
        "\"ip_address\":\"%s\","
        "\"tcp_port\":%u,"
        "\"clients_connected\":%u,"
        "\"uptime_seconds\":%lu,"
        "\"free_heap\":%lu,"
        "\"cpu_usage\":%u,"
        "\"sd_mounted\":%s,"
        "\"sd_total_mb\":%lu,"
        "\"sd_used_mb\":%lu,"
        "\"log_files_count\":%u,"
        "\"firmware_version\":\"%s\","
        "\"ota_partition\":\"%s\","
        "\"ota_pending\":%s"
        "}",
        status.can_online ? "true" : "false",
        status.can_rx_count,
        status.can_tx_count,
        status.can_errors,
        status.cia402_state,
        status.status_word,
        status.control_word,
        status.eth_connected ? "true" : "false",
        status.ip_address,
        status.tcp_port,
        status.clients_connected,
        status.uptime_seconds,
        status.free_heap,
        status.cpu_usage,
        status.sd_mounted ? "true" : "false",
        status.sd_total_mb,
        status.sd_used_mb,
        status.log_files_count,
        status.firmware_version,
        status.ota_partition,
        status.ota_pending ? "true" : "false"
    );
}

void WebServer::set_status_callback(StatusUpdateCallback callback) {
    status_callback_ = callback;
}

void WebServer::update_status(const GatewayStatus& status) {
    if (!server_) {
        return;
    }

    // Por ahora solo loggeamos, WebSocket requiere API más avanzada
    ESP_LOGD(TAG, "Status update: CAN=%s, CiA402=%u, Heap=%lu", 
             status.can_online ? "ON" : "OFF",
             status.cia402_state,
             status.free_heap);
             
    // TODO: Implementar broadcast WebSocket cuando se actualice ESP-IDF
}
