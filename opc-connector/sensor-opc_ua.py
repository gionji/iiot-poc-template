import json
import sys
import threading
from time import sleep

from services.publisher import LocalClient

mqtt_client = None

sys.path.insert(0, "..")

from opcua import Client


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def event_notification(self, event):
        message = {
            "data": {
                "panelVoltage": event.get_event_props_as_fields_dict()['panelVoltage'].Value,
                "panelCurrent": event.get_event_props_as_fields_dict()['panelCurrent'].Value,
                "batteryVoltage": event.get_event_props_as_fields_dict()['batteryVoltage'].Value,
                "batteryCurrent": event.get_event_props_as_fields_dict()['batteryCurrent'].Value,
                "loadVoltage": event.get_event_props_as_fields_dict()['loadVoltage'].Value,
                "loadCurrent": event.get_event_props_as_fields_dict()['loadCurrent'].Value,
                "inPower": event.get_event_props_as_fields_dict()['inPower'].Value,
                "outPower": event.get_event_props_as_fields_dict()['outPower'].Value,
                "batteryStatus": event.get_event_props_as_fields_dict()['batteryStatus'].Value,
                "batteryCapacity": event.get_event_props_as_fields_dict()['batteryCapacity'].Value,
                "batteryTemperature": event.get_event_props_as_fields_dict()['batteryTemperature'].Value,
            }
        }
        mqtt_client.publish('/sensors', json.dumps(message))


def mqtt_connection():
    global mqtt_client
    mqtt_client = LocalClient('sensor-opc_ua', 'localhost', 1883)
    mqtt_client.run()


if __name__ == "__main__":

    t1 = threading.Thread(target=mqtt_connection)
    t1.daemon = True
    t1.start()

    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Now getting a variable node using its browse path
        obj = root.get_child(["0:Objects", "2:MyObject"])
        print("MyObject is: ", obj)

        myevent = root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:MyFirstEvent"])
        print("MyFirstEventType is: ", myevent)

        while (True):
            msclt = SubHandler()
            sub = client.create_subscription(100, msclt)
            handle = sub.subscribe_events(obj, myevent)
            sleep(1)

        sub.unsubscribe(handle)
        sub.delete()
    finally:
        client.disconnect()
