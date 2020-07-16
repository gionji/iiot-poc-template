import json
from datetime import datetime
from time import sleep

from sensor import reader
from libs.utils import connector, IIoT


if __name__ == "__main__":
    topics = [IIoT.MqttChannels.sensors]  # canali a cui mi sottoscrivo
    mqtt_client = connector.MqttLocalClient('SENSORS', 'localhost', 1883, topics)
    mqtt_client.start()

    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }

    reader = reader.DummyReader("S_1")

    while True:
        value = reader.read()
        # Publish the data
        mqtt_client.publish(IIoT.MqttChannels.sensors, format(reader.key, value, int(datetime.now().timestamp())))

        sleep(10)
