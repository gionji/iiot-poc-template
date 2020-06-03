import json
import datetime
from services.publisher import MqttLocalClient
from pymongo import MongoClient
import TemplateCommon as IIoT


def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message


sensors = ["panelVoltage",
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

events = []

def database_init():
    client = MongoClient('127.0.0.1', 27017)
    db     = client.local_mongo_db
    return db

def add_data(collection, document):
    ret = collection.insert_one( document )
    print("add " + str(document))
    return ret

def get_values_in_time_range( collection, key, start_time, end_time ):
    # Time format '2020-09-24T07:52:04.945306'
    query = { key : {'$exists' : True }, 'date': {'$lte': end_time , '$gte': start_time} }
    res = collection.find( query ).sort( 'date' )
    return res

def get_values_greater_than( collection, key, th ):
    query = { key : {'$exists' : True }, key : {'$gte': th} }
    res = collection.find( query ).sort( 'date' )
    return res

def get_pseudo_table(collection):
    return "TO_DO"


def dump_data():
    return 0


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = "database-mongodb",
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = [
                                                        IIoT.MqttChannels.persist,
                                                       ]
                                 )
    mqtt_client.start()

    db = database_init()

    print("pippaaaa")

    sensors_collection = db.sensors_collection
    events_collection  = db.events_collection
    data_collection    = db.data_collection


    print("pippaaaaaaaa")

    # Get the data from message_queue
    while True:
        # Waiting for a new message in the queue
        message = mqtt_client.message_queue.get()

        #Get the message topic and its payload
        topic        = message.topic
        payload      = message.payload
        json_payload = json.loads(payload)
        input_name   = json_payload['data']['name']
        input_value  = json_payload['data']['value']

        print(message)

        # Perform actions
        obj = {
                input_name : input_value,
                'date' : datetime.datetime.now()
            }

        if input_name in sensors:
            add_data( sensors_collection , obj )
        elif input_name in events:
            add_data( events_collection , obj )




if __name__ == "__main__":
    main()
