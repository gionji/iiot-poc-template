import json
from abc import abstractmethod, ABC

from threading import Thread
import datetime

from opcua import Client

from libs.utils.IIoT import packOutputMessage
from opc.config import OPC_SENSORS, MY_OBJECT_NAME, MY_FIRST_EVENT_NAME


class SensorValue:
    def __init__(self, key, value, timestamp):
        self.key = key
        self.value = value
        self.timestamp = timestamp

    def format(self):
        return json.dumps({
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp
        })


class Reader(ABC):

    @abstractmethod
    def read(self) -> SensorValue:
        pass



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

    def __init__(self, cb):
        self.cb = cb

    def datachange_notification(self, node, val, data):
        var_name = get_variable_name_by_node(node)
        message = packOutputMessage(var_name, val)
        payload = {
            'key': message['data']['name'],
            'value': message['data']['value'],
            'timestamp': int(datetime.datetime.now().timestamp())
        }
        self.cb(payload)

    def event_notification(self, event):
        message = packOutputMessage('event', str(event.Message))
        print(message)
        # mqtt_client.publish(IIoT.MqttChannels.sensors, json.dumps(message))
        # mqtt_client.publish(IIoT.MqttChannels.persist, json.dumps(message))
        # mqtt_client.publish(IIoT.MqttChannels.telemetry, json.dumps(message))


class OpcUaClient(Thread, Reader):

    def __init__(self, cb):
        super().__init__()
        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        self.on_data_change_callback = cb

    def init(self):
        self.client.connect()
        self.get_properties()

    def set_on_data_change_callback(self, cb):
        self.on_data_change_callback = cb

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
            print(myvar)
            subscribed_variables.append(myvar)
            subscribed_variables_dict[str(myvar)] = str(myvar.get_browse_name().to_string())

        myevent = root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:" + MY_FIRST_EVENT_NAME])
        print("MyFirstEventType is: ", myevent)

    def start(self) -> None:
        self.read()

    def read(self):
        msclt = SubHandler(self.on_data_change_callback)
        sub = self.client.create_subscription(100, msclt)
        for var in subscribed_variables:
            handle = sub.subscribe_data_change(var)
            print(handle)
        # handle = sub.subscribe_events(obj, myevent)
