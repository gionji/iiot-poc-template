import sys
sys.path.insert(0, "..") # this allows to load upper level imports
import json
import threading
from time import sleep
from opcua import Client, ua
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT
import datetime
from pymongo import MongoClient


import common.MyCommons as Commons

MQTT_CLIENT_ID           = "database-mongodb"
SUBSCRIBED_MQTT_CHANNELS = [
                      IIoT.MqttChannels.persist,
                     ]


sensors = Commons.OPC_SENSORS
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
                                  subscription_paths = SUBSCRIBED_MQTT_CHANNELS
                                 )
    mqtt_client.start()

    # initialize database
    db = database_init()

    ## initialize db collections
    sensors_collection = db.sensors_collection
    events_collection  = db.events_collection
    data_collection    = db.data_collection

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

        # depending on the input_name te value is written in a different caollection0
        if input_name in sensors:
            add_data( sensors_collection , obj )

        elif input_name in events:
            add_data( events_collection , obj )




if __name__ == "__main__":
    main()
