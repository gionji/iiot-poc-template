
OPC_SENSORS = ["panelVoltage",
                "panelCurrent",
                "batteryVoltage",
                "batteryCurrent",
                "loadVoltage",
                "loadCurrent",
                "inPower",
                "outPower",
                "batteryStatus",
                "batteryCapacity",
                "batteryTemperature",
                ]

class MqttChannels:
    persist   = "/persist"
    sensors   = "/sensors"
    data      = "/data"
    telemetry = "/telemetry"
    gui       = "/gui"
    actuators = "/actuators"

MQTT_PORT = 1883
MQTT_HOST = 'localhost'


def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message
