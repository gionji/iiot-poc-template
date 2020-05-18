import json
import sys
import threading
from time import sleep

from services.publisher import LocalClient

import EpeverChargeController as epever

DELAY = 1.0
IS_RUNNING = True


def mqtt_connection():
    global mqtt_client
    mqtt_client = LocalClient('sensor-modbus_rtu', 'localhost', 1883)
    mqtt_client.run()



if __name__ == "__main__":

    mqtt_connection()

    data = dict()

    while IS_RUNNING:
        ## Read Charge Controller Data
        data = chargeController.readAll()

        publishData( data )

        tie.delay( DELAY )
