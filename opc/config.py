

MY_OBJECT_NAME = "ChargeController"
MY_FIRST_EVENT_NAME = "LowBatteryEvent"

OPC_ENDPOINT = "opc.tcp://0.0.0.0:4840/freeopcua/server/"

OPC_NAMESPACE = "http://examples.freeopcua.github.io"

OPC_SENSORS = [
    "panelVoltage",
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
