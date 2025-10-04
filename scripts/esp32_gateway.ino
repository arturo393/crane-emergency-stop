/*
 * Gateway CAN-WiFi para Control Danfoss R13 Puente Grúa
 * Hardware: ESP32-S3 con CAN TWAI integrado
 * 
 * Este código implementa un gateway que recibe comandos por WiFi
 * y los envía por CAN bus al receptor Danfoss R13.
 * 
 * Autor: Proyecto Puente Grúa
 * Fecha: Septiembre 2025
 */

#include <WiFi.h>
#include <WiFiServer.h>
#include <ArduinoJson.h>
#include "driver/twai.h"

// Configuración WiFi
const char* ssid = "TU_WIFI_SSID";
const char* password = "TU_WIFI_PASSWORD";
const int serverPort = 9999;

// Configuración CAN
#define CAN_TX_PIN GPIO_NUM_21
#define CAN_RX_PIN GPIO_NUM_22
#define CAN_BITRATE TWAI_TIMING_CONFIG_250KBITS()

// Servidor WiFi
WiFiServer server(serverPort);

// Configuración TWAI (CAN)
twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
twai_timing_config_t t_config = CAN_BITRATE;
twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

// Estado del sistema
bool canBusReady = false;
unsigned long lastHeartbeat = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("=== Gateway ESP32 CAN-WiFi para R13 ===");
  
  // Inicializar CAN bus
  initCAN();
  
  // Inicializar WiFi
  initWiFi();
  
  // Iniciar servidor TCP
  server.begin();
  Serial.printf("Servidor TCP iniciado en puerto %d\n", serverPort);
  
  Serial.println("Gateway listo - Esperando conexiones...");
}

void loop() {
  // Verificar conexiones WiFi
  WiFiClient client = server.available();
  
  if (client) {
    Serial.println("Cliente conectado");
    
    while (client.connected()) {
      if (client.available()) {
        String request = client.readStringUntil('\n');
        processCommand(request, client);
      }
      
      // Procesar mensajes CAN recibidos
      processCANMessages();
      
      delay(10);
    }
    
    client.stop();
    Serial.println("Cliente desconectado");
  }
  
  // Heartbeat
  if (millis() - lastHeartbeat > 5000) {
    Serial.println("Gateway activo - CAN: " + String(canBusReady ? "OK" : "ERROR"));
    lastHeartbeat = millis();
  }
  
  delay(50);
}

void initCAN() {
  Serial.println("Inicializando CAN bus...");
  
  // Instalar driver TWAI
  if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
    Serial.println("Driver TWAI instalado");
  } else {
    Serial.println("ERROR: Fallo al instalar driver TWAI");
    return;
  }
  
  // Iniciar TWAI
  if (twai_start() == ESP_OK) {
    Serial.println("CAN bus iniciado exitosamente");
    canBusReady = true;
  } else {
    Serial.println("ERROR: Fallo al iniciar CAN bus");
  }
}

void initWiFi() {
  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("ERROR: No se pudo conectar a WiFi");
  }
}

void processCommand(String jsonCommand, WiFiClient &client) {
  Serial.println("Comando recibido: " + jsonCommand);
  
  // Parsear JSON
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, jsonCommand);
  
  if (error) {
    Serial.println("ERROR: JSON inválido");
    sendResponse(client, "error", "JSON inválido");
    return;
  }
  
  // Extraer comando
  String command = doc["command"];
  uint16_t index = doc["index"];
  uint8_t subindex = doc["subindex"];
  uint32_t data = doc["data"];
  uint8_t nodeId = doc.containsKey("node_id") ? doc["node_id"] : 1;
  
  // Procesar comandos CANopen
  if (command == "sdo_write") {
    sendSDOWrite(nodeId, index, subindex, data, client);
  } else if (command == "sdo_read") {
    sendSDORead(nodeId, index, subindex, client);
  } else {
    Serial.println("ERROR: Comando desconocido");
    sendResponse(client, "error", "Comando no reconocido");
  }
}

void sendSDOWrite(uint8_t nodeId, uint16_t index, uint8_t subindex, uint32_t data, WiFiClient &client) {
  if (!canBusReady) {
    sendResponse(client, "error", "CAN bus no disponible");
    return;
  }
  
  // Crear mensaje SDO Write (Expedited Transfer)
  twai_message_t message;
  message.identifier = 0x600 + nodeId;  // SDO Request
  message.flags = TWAI_MSG_FLAG_NONE;
  message.data_length_code = 8;
  
  // SDO Write Expedited Transfer
  message.data[0] = 0x23;  // Command Specifier (expedited, 4 bytes)
  message.data[1] = index & 0xFF;        // Index LSB
  message.data[2] = (index >> 8) & 0xFF; // Index MSB
  message.data[3] = subindex;            // Subindex
  message.data[4] = data & 0xFF;         // Data LSB
  message.data[5] = (data >> 8) & 0xFF;  // Data
  message.data[6] = (data >> 16) & 0xFF; // Data
  message.data[7] = (data >> 24) & 0xFF; // Data MSB
  
  // Enviar mensaje
  if (twai_transmit(&message, pdMS_TO_TICKS(1000)) == ESP_OK) {
    Serial.printf("SDO Write enviado - Node: %d, Index: 0x%04X, Subindex: %d, Data: 0x%08X\n", 
                  nodeId, index, subindex, data);
    sendResponse(client, "success", "SDO Write enviado");
  } else {
    Serial.println("ERROR: Fallo al enviar SDO Write");
    sendResponse(client, "error", "Fallo al enviar comando CAN");
  }
}

void sendSDORead(uint8_t nodeId, uint16_t index, uint8_t subindex, WiFiClient &client) {
  if (!canBusReady) {
    sendResponse(client, "error", "CAN bus no disponible");
    return;
  }
  
  // Crear mensaje SDO Read
  twai_message_t message;
  message.identifier = 0x600 + nodeId;  // SDO Request
  message.flags = TWAI_MSG_FLAG_NONE;
  message.data_length_code = 8;
  
  // SDO Read Request
  message.data[0] = 0x40;  // Command Specifier
  message.data[1] = index & 0xFF;        // Index LSB
  message.data[2] = (index >> 8) & 0xFF; // Index MSB
  message.data[3] = subindex;            // Subindex
  message.data[4] = 0x00;  // Reserved
  message.data[5] = 0x00;  // Reserved
  message.data[6] = 0x00;  // Reserved
  message.data[7] = 0x00;  // Reserved
  
  // Enviar mensaje
  if (twai_transmit(&message, pdMS_TO_TICKS(1000)) == ESP_OK) {
    Serial.printf("SDO Read enviado - Node: %d, Index: 0x%04X, Subindex: %d\n", 
                  nodeId, index, subindex);
    sendResponse(client, "success", "SDO Read enviado");
  } else {
    Serial.println("ERROR: Fallo al enviar SDO Read");
    sendResponse(client, "error", "Fallo al enviar comando CAN");
  }
}

void processCANMessages() {
  twai_message_t message;
  
  // Verificar mensajes recibidos
  if (twai_receive(&message, 0) == ESP_OK) {
    Serial.printf("CAN RX - ID: 0x%03X, DLC: %d, Data: ", message.identifier, message.data_length_code);
    
    for (int i = 0; i < message.data_length_code; i++) {
      Serial.printf("0x%02X ", message.data[i]);
    }
    Serial.println();
    
    // Procesar respuestas SDO (0x580 + nodeId)
    if ((message.identifier & 0xFF80) == 0x580) {
      processSDOResponse(message);
    }
  }
}

void processSDOResponse(twai_message_t &message) {
  uint8_t nodeId = message.identifier & 0x7F;
  uint8_t command = message.data[0];
  uint16_t index = message.data[1] | (message.data[2] << 8);
  uint8_t subindex = message.data[3];
  
  Serial.printf("SDO Response - Node: %d, Command: 0x%02X, Index: 0x%04X, Subindex: %d\n", 
                nodeId, command, index, subindex);
  
  // Aquí se podría enviar la respuesta de vuelta al cliente Python
  // Por simplicidad, solo se registra en el log
}

void sendResponse(WiFiClient &client, String status, String message) {
  DynamicJsonDocument response(512);
  response["status"] = status;
  response["message"] = message;
  response["timestamp"] = millis();
  
  String jsonString;
  serializeJson(response, jsonString);
  
  client.println(jsonString);
  Serial.println("Respuesta enviada: " + jsonString);
}

// Funciones de diagnóstico
void printSystemStatus() {
  Serial.println("=== Estado del Sistema ===");
  Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado"));
  Serial.println("IP: " + WiFi.localIP().toString());
  Serial.println("CAN: " + String(canBusReady ? "Activo" : "Inactivo"));
  Serial.println("Uptime: " + String(millis() / 1000) + " segundos");
  Serial.println("========================");
}
