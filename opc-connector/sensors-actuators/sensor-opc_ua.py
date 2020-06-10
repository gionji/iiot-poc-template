import sys
sys.path.insert(0, "..") # this allows to load upper level imports
import json
import threading
from time import sleep
from opcua import Client, ua
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT

import common.MyCommons as Commons

MY_OBJECT_NAME = "2:ChargeController"
VARS_NAMES  = Commons.OPC_SENSORS

mqtt_client = None

## this dictionary contains the opc variables we wanto to subscribe
global subscribed_variables_dict

## this method returns the OPC variable name by NodeID and ....
def get_variable_name_by_node(_node):
    return str( subscribed_variables_dict[str(_node)].split(":")[1] )


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        var_name = get_variable_name_by_node(node)
        message = packOutputMessage(var_name ,val)
        mqtt_client.publish(IIoT.MqttChannels.sensors, json.dumps(message))
        mqtt_client.publish(IIoT.MqttChannels.persist, json.dumps(message))
        mqtt_client.publish(IIoT.MqttChannels.telemetry, json.dumps(message))

    def event_notification(self, event):
        message = packOutputMessage('event' , str(event.Message))
        mqtt_client.publish(IIoT.MqttChannels.sensors, json.dumps(message))
        mqtt_client.publish(IIoT.MqttChannels.persist, json.dumps(message))
        mqtt_client.publish(IIoT.MqttChannels.telemetry, json.dumps(message))


def mqtt_connection():
    global mqtt_client
    mqtt_client = MqttLocalClient('sensor-opc_ua', 'localhost', 1883)
    mqtt_client.run()


def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message


if __name__ == "__main__":
    t1 = threading.Thread(target=mqtt_connection)
    t1.daemon = True
    t1.start()

    client = Client("opc.tcp://localhost:4840/freeopcua/server/")

    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)
        print("Children of root are: ", root.get_children())

        #browse_recursive(root)

        server_namespace = "http://examples.freeopcua.github.io"
        idx = client.get_namespace_index( server_namespace )

        # Now getting a variable node using its browse path
        obj = root.get_child(["0:Objects", "2:" + Commons.MY_OBJECT_NAME])
        print("ChargeController object is: ", obj)

        subscribed_variables_dict = dict()
        subscribed_variables   = list()

        for var in VARS_NAMES:
            myvar = root.get_child(["0:Objects", "2:" + Commons.MY_OBJECT_NAME, "2:" + str(var)])
            subscribed_variables.append( myvar )
            subscribed_variables_dict[ str(myvar)  ] = str(myvar.get_browse_name().to_string())

        myevent = root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:" + Commons.MY_FIRST_EVENT_NAME])
        print("MyFirstEventType is: ", myevent)

        #while (True):
        msclt = SubHandler()
        sub = client.create_subscription(100, msclt)
        for var in subscribed_variables:
            handle = sub.subscribe_data_change(var)
        handle = sub.subscribe_events(obj, myevent)

        while True:
            sleep(1)

        sub.unsubscribe(handle)
        sub.delete()
    finally:
        client.disconnect()
