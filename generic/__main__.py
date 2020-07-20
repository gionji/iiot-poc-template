import json
from datetime import datetime
from time import sleep

from libs.utils import connector, IIoT


class GenericValue:
    def __init__(self, key, value, timestamp):
        self.key       = key
        self.value     = value
        self.timestamp = timestamp

    def format(self):
        return json.dumps({
            "key"      : self.key,
            "value"    : self.value,
            "timestamp": self.timestamp
        })


if __name__ == "__main__":

    # Subscribed channels
    topics = [IIoT.MqttChannels.sensors]

    # Connect to MQTT clients
    mqtt_client = connector.MqttLocalClient('GENERIC', 'localhost', 1883, topics)
    mqtt_client.start()

    ## Init the module core object
    #

    while True:
        ## Waiting for messages from the subscribed mqtt channels
        message = mqtt_client.message_queue.get()
        print(message.payload)

        json_payload = json.loads(message.payload)
        timestamp = json_payload['timestamp']
        key = json_payload['key']
        value = json_payload['value']


        ## Publish the data
        # mqtt_client.publish(IIoT.MqttChannels.sensors, format(reader.key, value, int(datetime.now().timestamp())))

        sleep(10)
