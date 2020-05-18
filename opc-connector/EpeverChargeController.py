## Epever Charge controller

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

BAUDRATE = 115200
PORT     = '/dev/ttyUSB0'

def readAll():
    data = dict()

    try:
        print("Connect modbus...")
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()

        result = client.read_input_registers(0x3100, 15, unit=1)
        #result1 = client.read_input_registers(0x3300, 14, unit=1)
        result2 = client.read_input_registers(0x3110, 2, unit=1)
        result3 = client.read_input_registers(0x311, 15, unit=1)
        result4 = client.read_input_registers(0x3200,15, unit=1)

        #data['date'] = datetime.datetime.now()
        data['panelVoltage']       = float(result.registers[0] / 100.0)
        data['panelCurrent']       = float(result.registers[1] / 100.0)
        data['batteryVoltage']     = float(result.registers[4] / 100.0)
        data['batteryCurrent']     = float(result.registers[5] / 100.0)
        data['loadVoltage']        = float(result.registers[12] / 100.0)
        data['loadCurrent']        = float(result.registers[13] / 100.0)
        data['inPower']            = data['panelVoltage'] * data['panelCurrent']
        data['outPower']           = data['loadVoltage']  * data['loadCurrent']
        data['batteryTemperature'] = float(result2.registers[0] / 100)
        data['batteryCapacity']    = float(result3.registers[10] /100)
        data['batteryStatus']      = (result4.registers[0])
    except Exception as e:
        data['panelVoltage']    = None
        data['panelCurrent']    = None
        data['batteryVoltage']  = None
        data['batteryCurrent']  = None
        data['loadVoltage']     = None
        data['loadCurrent']     = None
        data['inPower']         = None
        data['outPower']        = None
        data['batteryCapacity'] = None
        data['batteryStatus']   = None
        print(e)
    return data



def getPanelVoltage():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[0] / 100.0)
    client.close()
    return data

def getPanelCurrent():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[1] / 100.0)
    client.close()
    return data

def getBatteryVoltage():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[4] / 100.0)
    client.close()
    return data

def getBatteryCurrent():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[5] / 100.0)
    client.close()
    return data

def getLoadVoltage():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[12] / 100.0)
    client.close()
    return data

def getLoadCurrent():
    client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
    client.connect()
    result = client.read_input_registers(0x3100, 15, unit=1)
    data = float(result.registers[13] / 100.0)
    client.close()
    return data
