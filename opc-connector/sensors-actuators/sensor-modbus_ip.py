import sys
sys.path.insert(0, "..") # this allows to load upper level imports
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT
import common.MyCommons as Commons

import json
import sys
import threading
from time import sleep

import FdsChargeController as FdsCC
import FdsCommon as fds

DELAY = 1.0
IS_RUNNING = True


def mqtt_connection():
    global mqtt_client
    mqtt_client = LocalClient('sensor-modbus_ip', 'localhost', 1883)
    mqtt_client.run()


if __name__ == "__main__":

    mqtt_connection()
    ## initialize the ChargeController and Relaybox
    try:
        print('Initializing Charge Controller connection...')
        chargeController = FdsCC.FdsChargeController(FdsCC.MODBUS_ETH, isDebug = IS_MODBUS_IN_DEBUG_MODE )
        chargeController.connect()
    except Exception as e:
        print(e)


    while IS_RUNNING:

        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print( dt_string )

        print("Sensors reading " + str( cycle ))

        try:
            dataCC = chargeController.getChargeControllerData()
        except Exception as e:
            dataCC = None
            print("READING MODBUS CC: " + str(e))

        try:
            dataRB = chargeController.getRelayBoxData()
        except Exception as e:
            dataRB = None
            print("READING MODBUS RB: " + str(e))

        try:
            dataRS = chargeController.getRelayBoxState()
        except Exception as e:
            dataRS = None
            print("READING MODBUS RS: " + str(e))

        publish_data( data )

        time.delay( DELAY )
