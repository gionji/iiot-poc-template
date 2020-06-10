from pymodbus.exceptions import ModbusIOException
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

import random
import logging

import FdsCommon as fds

MODBUS_RTU = 0x01
MODBUS_ETH = 0x02

CHARGE_CONTROLLER_UNIT  = 0x01
RELAYBOX_UNIT          = 0x09
MODBUS_PORT             = 502

DEFAULT_CHARGE_CONTROLLER_IP   = '192.168.2.253'
DEFAULT_C23_RS485              = '/dev/ttymxc2' # mxc3 on schematics

# from pymodbus.client.sync import ModbusTcpClient



class FdsChargeController():
    comunicationType = ""
    serialPort       = ""
    ipAddress        = ""
    modbusClient     = None
    isDebug          = False

    client = None

    def __init__(self,
        communicationType,
        port=DEFAULT_C23_RS485,
        ipAddress=DEFAULT_CHARGE_CONTROLLER_IP,
        isDebug=False):

        self.isDebug = isDebug

        if (communicationType == MODBUS_ETH):
            self.communicationType = communicationType
            self.ipAddress = ipAddress
            logging.debug("FdsChargeController: ETH enabled ")
        elif (communicationType == MODBUS_RTU):
            self.communicationType = communicationType
            self.serialPort = port
            logging.debug("FdsChargeController: RTU enabled ")
        else:
            raise ValueError("Unsupported Modbus Communication Type. Choose MODBUS_RTU or MODBUS_ETH.")


    def connect(self):
        if(self.communicationType == MODBUS_ETH):
            logging.debug("FdsChargeController: connect EHT called")

            if self.isDebug == False:
                    print("Trying to connect to Modbus IP Host %s ..." % self.ipAddress)
                    self.client = ModbusClient(self.ipAddress, MODBUS_PORT)
                    self.client.connect()

        elif (self.communicationType == MODBUS_RTU):
                        logging.debug("FdsChargeController: connect RTU called")



    def getChargeControllerData(self):
        data = {'type':'chargecontroller'}

        if self.client != None:
            try:
                # read registers. Start at 0 for convenience
                rr = self.client.read_holding_registers(0,80, unit=CHARGE_CONTROLLER_UNIT)

                # for all indexes, subtract 1 from what's in the manual
                V_PU_hi = rr.registers[0]
                V_PU_lo = rr.registers[1]
                I_PU_hi = rr.registers[2]
                I_PU_lo = rr.registers[3]

                V_PU = float(V_PU_hi) + float(V_PU_lo)
                I_PU = float(I_PU_hi) + float(I_PU_lo)

                v_scale = V_PU * 2**(-15)
                i_scale = I_PU * 2**(-15)
                p_scale = V_PU * I_PU * 2**(-17)

                # battery sense voltage, filtered
                data[ fds.LABEL_CC_BATTS_V ]       = rr.registers[24] * v_scale
                data[ fds.LABEL_CC_BATT_SENSED_V ] = rr.registers[26] * v_scale
                data[ fds.LABEL_CC_BATTS_I ]       = rr.registers[28] * i_scale
                data[ fds.LABEL_CC_ARRAY_V ]       = rr.registers[27] * v_scale
                data[ fds.LABEL_CC_ARRAY_I ]       = rr.registers[29] * i_scale
                data[ fds.LABEL_CC_STATENUM ]     = rr.registers[50]
                data[ fds.LABEL_CC_HS_TEMP]       = rr.registers[35]
                data[ fds.LABEL_CC_RTS_TEMP]      = rr.registers[36]
                data[ fds.LABEL_CC_OUT_POWER]     = rr.registers[58] * p_scale
                data[ fds.LABEL_CC_IN_POWER]      = rr.registers[59] * p_scale
                data[ fds.LABEL_CC_MINVB_DAILY ]  = rr.registers[64] * v_scale
                data[ fds.LABEL_CC_MAXVB_DAILY ]  = rr.registers[65] * v_scale
                data[ fds.LABEL_CC_MINTB_DAILY ]  = rr.registers[71]
                data[ fds.LABEL_CC_MAXTB_DAILY ]  = rr.registers[72]
                data[ fds.LABEL_CC_DIPSWITCHES ]  = bin(rr.registers[48])[::-1][:-2].zfill(8)
                #led_state            = rr.registers
            except ModbusIOException as e:
                logging.error('Charge Controller: modbusIOException')
                raise e
            except Exception as e:
                logging.error('Charge Controller: unpredicted exception')
                raise e
        else:
            data[ fds.LABEL_CC_BATTS_V ]       = random.uniform(0, 60)
            data[ fds.LABEL_CC_BATT_SENSED_V ] = random.uniform(0, 60)
            data[ fds.LABEL_CC_BATTS_I ]       = random.uniform(0, 60)
            data[ fds.LABEL_CC_ARRAY_V ]       = random.uniform(0, 60)
            data[ fds.LABEL_CC_ARRAY_I ]       = random.uniform(0, 60)
            data[ fds.LABEL_CC_STATENUM ]     = random.uniform(0, 60)
            data[ fds.LABEL_CC_HS_TEMP]       = random.uniform(0, 60)
            data[ fds.LABEL_CC_RTS_TEMP]      = random.uniform(0, 60)
            data[ fds.LABEL_CC_OUT_POWER]     = random.uniform(0, 60)
            data[ fds.LABEL_CC_IN_POWER]      = random.uniform(0, 60)
            data[ fds.LABEL_CC_MINVB_DAILY ]  = random.uniform(0, 60)
            data[ fds.LABEL_CC_MAXVB_DAILY ]  = random.uniform(0, 60)
            data[ fds.LABEL_CC_MINTB_DAILY ]  = random.uniform(0, 60)
            data[ fds.LABEL_CC_MAXTB_DAILY ]  = random.uniform(0, 60)
            data[ fds.LABEL_CC_DIPSWITCHES ]  =bin(0x02)[::-1][:-2].zfill(8)

        return data



    def getRelayBoxData(self):
        data = {'type':'relaybox'}

        if self.client != None:
            try:
                # read registers. Start at 0 for convenience
                rr = self.client.read_holding_registers(0,18, unit=RELAYBOX_UNIT)
                v_scale = float(78.421 * 2**(-15))

                data[ fds.LABEL_RB_VB     ]        = rr.registers[0] * v_scale
                data[ fds.LABEL_RB_ADC_VCH_1 ]     = rr.registers[1] * v_scale
                data[ fds.LABEL_RB_ADC_VCH_2 ]     = rr.registers[2] * v_scale
                data[ fds.LABEL_RB_ADC_VCH_3 ]     = rr.registers[3] * v_scale
                data[ fds.LABEL_RB_ADC_VCH_4 ]     = rr.registers[4] * v_scale
                data[ fds.LABEL_RB_T_MOD ]         = rr.registers[5]
                data[ fds.LABEL_RB_GLOBAL_FAULTS ] = rr.registers[6]
                data[ fds.LABEL_RB_GLOBAL_ALARMS ] = rr.registers[7]
                data[ fds.LABEL_RB_HOURMETER_HI ]  = rr.registers[8]
                data[ fds.LABEL_RB_HOURMETER_LO ]  = rr.registers[9]
                data[ fds.LABEL_RB_CH_FAULTS_1 ]   = rr.registers[10]
                data[ fds.LABEL_RB_CH_FAULTS_2 ]   = rr.registers[11]
                data[ fds.LABEL_RB_CH_FAULTS_3 ]   = rr.registers[12]
                data[ fds.LABEL_RB_CH_FAULTS_4 ]   = rr.registers[13]
                data[ fds.LABEL_RB_CH_ALARMS_1 ]   = rr.registers[14]
                data[ fds.LABEL_RB_CH_ALARMS_2 ]   = rr.registers[15]
                data[ fds.LABEL_RB_CH_ALARMS_3 ]   = rr.registers[16]
                data[ fds.LABEL_RB_CH_ALARMS_4 ]   = rr.registers[17]
            except ModbusIOException as e:
                logging.error('RelayBoxRead: modbusIOException')
                raise e
            except Exception as e:
                logging.error('RelayBoxRead: unpredicted exception')
                raise e

        else:
            data[ fds.LABEL_RB_VB     ]        = random.uniform(0, 60)
            data[ fds.LABEL_RB_ADC_VCH_1 ]     = random.uniform(0, 60)
            data[ fds.LABEL_RB_ADC_VCH_2 ]     = random.uniform(0, 60)
            data[ fds.LABEL_RB_ADC_VCH_3 ]     = random.uniform(0, 60)
            data[ fds.LABEL_RB_ADC_VCH_4 ]     = random.uniform(0, 60)
            data[ fds.LABEL_RB_T_MOD ]         = random.uniform(0, 60)
            data[ fds.LABEL_RB_GLOBAL_FAULTS ] = random.uniform(0, 60)
            data[ fds.LABEL_RB_GLOBAL_ALARMS ] = random.uniform(0, 60)
            data[ fds.LABEL_RB_HOURMETER_HI ]  = random.uniform(0, 60)
            data[ fds.LABEL_RB_HOURMETER_LO ]  = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_FAULTS_1 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_FAULTS_2 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_FAULTS_3 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_FAULTS_4 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_ALARMS_1 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_ALARMS_2 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_ALARMS_3 ]   = random.uniform(0, 60)
            data[ fds.LABEL_RB_CH_ALARMS_4 ]   = random.uniform(0, 60)
        return data



    def getRelayBoxState(self):
        data = {'type':'relayState'}
        if self.client != None:
            try:
                rr = self.client.read_coils(0, 8, unit=RELAYBOX_UNIT)
                data[ fds.LABEL_RS_RELAY_1 ]   = rr.bits[0]
                data[ fds.LABEL_RS_RELAY_2 ]   = rr.bits[1]
                data[ fds.LABEL_RS_RELAY_3 ]   = rr.bits[2]
                data[ fds.LABEL_RS_RELAY_4 ]   = rr.bits[3]
                data[ fds.LABEL_RS_RELAY_5 ]   = rr.bits[4]
                data[ fds.LABEL_RS_RELAY_6 ]   = rr.bits[5]
                data[ fds.LABEL_RS_RELAY_7 ]   = rr.bits[6]
                data[ fds.LABEL_RS_RELAY_8 ]   = rr.bits[7]
            except ModbusIOException as e:
                logging.error( 'RelayState: modbusIOException')
                raise e
            except Exception as e:
                logging.error('RelayState: unpredicted exception')
                raise
        else:
            data[ fds.LABEL_RS_RELAY_1 ]   = 0x1
            data[ fds.LABEL_RS_RELAY_2 ]   = 0x1
            data[ fds.LABEL_RS_RELAY_3 ]   = 0x1
            data[ fds.LABEL_RS_RELAY_4 ]   = 0x0
            data[ fds.LABEL_RS_RELAY_5 ]   = 0x0
            data[ fds.LABEL_RS_RELAY_6 ]   = 0x0
            data[ fds.LABEL_RS_RELAY_7 ]   = 0x0
            data[ fds.LABEL_RS_RELAY_8 ]   = 0x0
        return data
