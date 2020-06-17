import json
from threading import Thread
import datetime

from opcua import Client

from libs.utils import IIoT
from libs.utils.IIoT import packOutputMessage

mqtt_client = None

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

subscribed_variables_dict = dict()
subscribed_variables = list()

# this dictionary contains the opc variables we want to to subscribe


# this method returns the OPC variable name by NodeID and ....
def get_variable_name_by_node(_node):
    return str(subscribed_variables_dict[str(_node)].split(":")[1])


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        var_name = get_variable_name_by_node(node)
        message = packOutputMessage(var_name, val)
        payload = {
            'key': message['data']['name'],
            'value': message['data']['value'],
            'timestamp': int(datetime.datetime.now().timestamp())
        }
        print(payload)

    def event_notification(self, event):
        message = packOutputMessage('event', str(event.Message))
        print(message)
        # mqtt_client.publish(IIoT.MqttChannels.sensors, json.dumps(message))
        # mqtt_client.publish(IIoT.MqttChannels.persist, json.dumps(message))
        # mqtt_client.publish(IIoT.MqttChannels.telemetry, json.dumps(message))


class OpcUaClient(Thread):

    def __init__(self):
        super().__init__()
        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")


    def init(self):
        self.client.connect()
        self.get_properties()

    def get_properties(self):
        root = self.client.get_root_node()
        print("Objects node is: ", root)
        print("Children of root are: ", root.get_children())

        # browse_recursive(root)

        server_namespace = "http://examples.freeopcua.github.io"
        idx = self.client.get_namespace_index(server_namespace)

        # Now getting a variable node using its browse path
        obj = root.get_child(["0:Objects", "2:" + MY_OBJECT_NAME])
        print("ChargeController object is: ", obj)

        for var in OPC_SENSORS:
            myvar = root.get_child(["0:Objects", "2:" + MY_OBJECT_NAME, "2:" + str(var)])
            subscribed_variables.append(myvar)
            subscribed_variables_dict[str(myvar)] = str(myvar.get_browse_name().to_string())

        myevent = root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:" + MY_FIRST_EVENT_NAME])
        print("MyFirstEventType is: ", myevent)

    def read(self):
        msclt = SubHandler()
        sub = self.client.create_subscription(100, msclt)
        for var in subscribed_variables:
            handle = sub.subscribe_data_change(var)
            print(handle)
        # handle = sub.subscribe_events(obj, myevent)
