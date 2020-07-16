import json

from database import WebServer
from database import persistence
from libs.utils import connector, IIoT

if __name__ == "__main__":
    # The array contains the channels you want to subscribe
    topics = [IIoT.MqttChannels.sensors]
    # Start the mqtt connection and assign the module name 'persistance"'
    mqtt_client = connector.MqttLocalClient('PERSISTENCE', 'localhost', 1883, topics)
    mqtt_client.start()

    # this object maps the topic to tables. to separe the data source from the rapresentation
    topics_tables_mapper = {
        IIoT.MqttChannels.sensors: 'sensors',
    }

    # initialize the physical database

    ## mongo DB
    db = persistence.MongoDB('localhost', 27018)
    db.add_collections([t[1] for t in topics_tables_mapper.items()])

    # initialaze the API REST Server
    web_server = WebServer(db)
    web_server.start()

    while True:
        message = mqtt_client.message_queue.get()
        print(message.payload)

        json_payload = json.loads(message.payload)
        timestamp = json_payload['timestamp']
        key = json_payload['key']
        value = json_payload['value']

        # Send the data to the db
        response = db.insert(topics_tables_mapper[message.topic], timestamp, key, value)

        print(response)
