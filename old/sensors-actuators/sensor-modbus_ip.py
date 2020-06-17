import sys
sys.path.insert(0, "..") # this allows to load upper level imports

import FdsChargeController as FdsCC

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
            dataCC = chargeController.get_charge_controller_data()
        except Exception as e:
            dataCC = None
            print("READING MODBUS CC: " + str(e))

        try:
            dataRB = chargeController.get_relay_box_data()
        except Exception as e:
            dataRB = None
            print("READING MODBUS RB: " + str(e))

        try:
            dataRS = chargeController.get_relay_box_state()
        except Exception as e:
            dataRS = None
            print("READING MODBUS RS: " + str(e))

        publish_data( data )

        time.delay( DELAY )
