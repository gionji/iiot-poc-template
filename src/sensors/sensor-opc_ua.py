import json
import threading
from time import sleep
import sys
sys.path.insert(0, "..")

from services.publisher import MqttLocalClient
import TemplateCommon as IIoT
from opcua import Client, ua


OPC_SERVER_URL   = "opc.tcp://localhost:4840/freeopcua/server/"
SERVER_NAMESPACE = "http://examples.freeopcua.github.io"

MQTT_CLIENT_ID = 'sensor-opc_ua'

MY_OBJECT_NAME = "2:MyObjectName"

## This is a list of variable names, present in the OPC server, we want to monitor
# We created a list to use a for loop enable the notification subscription
VARS_NAMES = [
                "MyFirstVariable", ## example,
             ]


mqtt_client = None

global subscribed_variables_dict

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
        message  = IIoT.packOutputMessage(var_name ,val)
        mqtt_client.publish( IIoT.MqttChannels.persist , json.dumps(message) )

    def event_notification(self, event):
        print("# EVENT # Python: New event", event.Message)



def mqtt_connection():
    global mqtt_client
    mqtt_client = MqttLocalClient(
                                  client_id          = MQTT_CLIENT_ID,
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = []
                                 )
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

    client = Client( OPC_SERVER_URL )

    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()

        print("Children of root are: ", root.get_children())


        myvar = root.get_child(["0:Objects", "2:MyObjectName", "2:" + str( 'MyFirstVariable' )])
        print( 'Variable value: ' + myvar.get_value() )

        # in dthis variable we are going to add the varaiable we want to receive snotifications
        subscribed_variables_dict = dict()
        subscribed_variables      = list()

        for var_name in VARS_NAMES:
            # Get the variable by exploring the opc object tree
            myvar = root.get_child(["0:Objects", "2:MyObjectName", "2:" + str(var_name)])

            # add the variable to a list. The returned variable is identified by a nod id and
            subscribed_variables.append( myvar )

            # in the dictionary we save the id and ind al dict labe and the Browse name
            subscribed_variables_dict[ str(myvar)  ] = str(myvar.get_browse_name().to_string())

        # GEt my event
        myevent = root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:MyEvent"])
        print("MyFirstEvent is: ", myevent)

        #while (True):
        msclt = SubHandler()
        sub = client.create_subscription(100, msclt)

        # Subscibe the varable to the notification handler. A messagge will be notified when the value on the server change
        for var in subscribed_variables:
            handle = sub.subscribe_data_change(var)

        # subscribe to the event notificaton
        handle = sub.subscribe_events(obj, myevent)

        while True:
            sleep(1)

        sub.unsubscribe(handle)
        sub.delete()
    finally:
        client.disconnect()
