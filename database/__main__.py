import json

from database import server as srv
from database import persistence
from libs.utils import connector, IIoT

if __name__ == "__main__":
    topics = [IIoT.MqttChannels.sensors]
    mqtt_client = connector.MqttLocalClient('PERSISTENCE', 'localhost', 1883, topics)
    mqtt_client.start()
    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }

    db = persistence.MongoDB()
    db.add_collections([t[1] for t in topics_tables_mapper.items()])

    web_server = srv.WebServer(db)
    web_server.start()

    while True:
        message = mqtt_client.message_queue.get()
        print(message.payload)

        json_payload = json.loads(message.payload)
        timestamp = json_payload['timestamp']
        key = json_payload['key']
        value = json_payload['value']
        response = db.insert(topics_tables_mapper[message.topic], timestamp, key, value)
        print(response)
