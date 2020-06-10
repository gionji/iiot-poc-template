## Epever Charge controller
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import random


DEFAULT_BAUDRATE   = 115200
DEFAULT_PORT       = '/dev/ttyUSB0'


class EpeverChargeController:

    def __init__(self, port = DEFAULT_PORT, baudrate = DEFAULT_BAUDRATE, produce_dummy_data = False):
        self.port = port
        self.baudrate = baudrate
        self.produce_dummy_data = produce_dummy_data

    def __produceDummyData(self):
        data = dict()
        data['panelVoltage']       = float(random.random() * 22)
        data['panelCurrent']       = float(random.random() * 3)
        data['batteryVoltage']     = float(random.random() * 15)
        data['batteryCurrent']     = float(random.random() * 3)
        data['loadVoltage']        = float(random.random() * 15)
        data['loadCurrent']        = float(random.random() * 3)
        data['inPower']            = data['panelVoltage'] * data['panelCurrent']
        data['outPower']           = data['loadVoltage']  * data['loadCurrent']
        data['batteryTemperature'] = float(random.random() * 50)
        data['batteryCapacity']    = float(random.random() * 100)
        data['batteryStatus']      = int(random.random() * 10)

        return data


    def readAllData(self):
        if self.produce_dummy_data:
            return self.__produceDummyData()

        try:
            print("Connect modbus...")
            client = ModbusClient(method='rtu', port=self.port, baudrate=self.baudrate)
            client.connect()
        except Exception as e:
            err = 'Error in Modbus Connect: ' + str(e)
            print( err )

        try:
            result  = client.read_input_registers(0x3100, 15, unit=1)
            result1 = client.read_input_registers(0x3300, 14, unit=1)
            result2 = client.read_input_registers(0x3110, 2, unit=1)
            result3 = client.read_input_registers(0x311, 15, unit=1)
            result4 = client.read_input_registers(0x3200,15, unit=1)
        except Exception as e:
            err = 'Error in Modbus reading registers: ' + str(e)
            print( err )

            data = dict()

        try:
            #data['timestamp']          = datetime.datetime.now()
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
            data = None
            err = 'Error parsing Modbus readings: ' + str(e)
            print( err )

        return data



    def getPanelVoltage(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[0] / 100.0)
        client.close()
        return data

    def getPanelCurrent(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[1] / 100.0)
        client.close()
        return data

    def getBatteryVoltage(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[4] / 100.0)
        client.close()
        return data

    def getBatteryCurrent(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[5] / 100.0)
        client.close()
        return data

    def getLoadVoltage(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[12] / 100.0)
        client.close()
        return data

    def getLoadCurrent(self):
        client = ModbusClient(method='rtu', port=PORT, baudrate=BAUDRATE)
        client.connect()
        result = client.read_input_registers(0x3100, 15, unit=1)
        data = float(result.registers[13] / 100.0)
        client.close()
        return data
