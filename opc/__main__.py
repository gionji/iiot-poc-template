import json
from opc import OpcUaClient

from libs.utils import connector, IIoT

if __name__ == "__main__":
    topics = [IIoT.MqttChannels.persist, IIoT.MqttChannels.sensors, IIoT.MqttChannels.telemetry]
    mqtt_client = connector.MqttLocalClient('OPC_UA', 'localhost', 1883)
    mqtt_client.start()

    # initialize the MCU object
    try:
        print('\nInitializing MCU connection...')
        client = OpcUaClient.OpcUaClient()
        client.init()
        client.start()
    except Exception as e:
        print(e)

    data = client.read()
    #mqtt_client.publish_on_many_topics(topics, json.dumps(data))
