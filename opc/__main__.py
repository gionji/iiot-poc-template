import json
from datetime import datetime

from opc import OpcUaClient

from libs.utils import connector, IIoT
from opc.OpcUaClient import SensorValue

global mqtt_client


def on_data_change(data):
    #convert data to SensorValue
    print('sono nel main con ')
    print(data)
    value = SensorValue(data['key'], data['value'], int(datetime.now().timestamp()))
    mqtt_client.publish(IIoT.MqttChannels.sensors, value.format())



if __name__ == "__main__":
    topics = [IIoT.MqttChannels.persist, IIoT.MqttChannels.sensors, IIoT.MqttChannels.telemetry]
    mqtt_client = connector.MqttLocalClient('OPC_UA', 'localhost', 1883)
    mqtt_client.start()

    client = OpcUaClient.OpcUaClient(on_data_change)
    # initialize the MCU object
    try:
        print('\nInitializing MCU connection...')
        client.init()
        client.start()
    except Exception as e:
        print(e)