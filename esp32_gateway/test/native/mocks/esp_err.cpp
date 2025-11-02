#include "esp_err.h"
#include <map>
#include <string>

// No es necesario que sea thread-safe para los tests
static std::map<esp_err_t, std::string> err_map = {
    {ESP_OK, "ESP_OK"},
    {ESP_FAIL, "ESP_FAIL"},
    {ESP_ERR_INVALID_ARG, "ESP_ERR_INVALID_ARG"},
    {ESP_ERR_INVALID_STATE, "ESP_ERR_INVALID_STATE"},
    {ESP_ERR_NOT_FOUND, "ESP_ERR_NOT_FOUND"},
    {ESP_ERR_TIMEOUT, "ESP_ERR_TIMEOUT"}
};

const char* esp_err_to_name(esp_err_t code) {
    if (err_map.count(code)) {
        return err_map[code].c_str();
    }
    return "UNKNOWN_ERROR";
}
