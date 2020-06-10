import sys
sys.path.insert(0, "..") # this allows to load upper level imports
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT
import common.MyCommons as Commons

import json
import threading
from time import sleep
from opcua import Client, ua
import datetime
import sqlite3
import time


DATABASE_PATH            = r"./database.sqlite"
MQTT_CLIENT_ID           = "database-sqlite"
SUBSCRIBED_MQTT_CHANNELS = [
                               IIoT.MqttChannels.persist,
                           ]

sensors = Commons.OPC_SENSORS
events  = []

def database_init():
    conn= create_connection(DATABASE_PATH)
    create_tables(conn)
    return conn

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    sql_create_table_sensors = """ CREATE TABLE IF NOT EXISTS sensors (
                                        id integer            PRIMARY KEY AUTOINCREMENT,
                                        panelVoltage          real,
                                        panelCurrent          real,
                                        batteryVoltage        real,
                                        batteryCurrent        real,
                                        loadVoltage           real,
                                        loadCurrent           real,
                                        inPower            real,
                                        outPower           real,
                                        batteryStatus         real,
                                        batteryCapacity       real,
                                        batteryTemperature    real,
                                        time                  timestamp NOT NULL
                                    ); """

    sql_create_table_single_sensors = """ CREATE TABLE IF NOT EXISTS single_sensors (
                                        id integer            PRIMARY KEY AUTOINCREMENT,
                                        sensor                text,
                                        value                 real,
                                        time                  timestamp NOT NULL
                                    ); """

    sql_create_table_events = """ CREATE TABLE IF NOT EXISTS  events (
                                        id integer            PRIMARY KEY AUTOINCREMENT,
                                        event_message         text,
                                        time                  timestamp NOT NULL
                                    ); """

    try:
        c = conn.cursor()
        c.execute( sql_create_table_sensors )
        c.execute( sql_create_table_single_sensors )
        conn.commit()
    except Error as e:
        print(e)

    try:
        c = conn.cursor()
        c.execute( sql_create_table_events )
        conn.commit()
    except Error as e:
        print(e)

def add_sensors_data(conn, data):
    data = dictToTuple(data)
    data = data + ( datetime.datetime.now(), )
    #data = (data, datetime.datetime.now() )

    sql = ''' INSERT INTO sensors( panelVoltage,
                                   panelCurrent,
                                   batteryVoltage,
                                   batteryCurrent,
                                   loadVoltage,

                                   loadCurrent,
                                   inPower,
                                   outPower,
                                   batteryStatus,
                                   batteryCapacity,

                                   batteryTemperature,
                                   time
                                )
              VALUES( ?,?,?,?,?, ?,?,?,?,?,?,? ) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
    except Exception as e:
        print(e)


def add_sensor_data(conn, sensor, value):

    data = (sensor, value, datetime.datetime.now())

    sql = ''' INSERT INTO single_sensors ( sensor,
                                   value,
                                   time
                                )
              VALUES( ?,?,? ) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
    except Exception as e:
        print(e)

def add_event_data(conn, data):
    data = (data, datetime.datetime.now() )

    sql = ''' INSERT INTO events( event_message,
                                   time
                                    )
              VALUES( ?,? ) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
    except Exception as e:
        print(e)

def dictToTuple(data):
    ret = (
        data['panelVoltage'],
        data['panelCurrent'],
        data['batteryVoltage'],
        data['batteryCurrent'],
        data['loadVoltage'],
        data['loadCurrent'],
        data['inPower'],
        data['outPower'],
        data['batteryStatus'],
        data['batteryCapacity'],
        data['batteryTemperature']
    )
    return ret



def get_values_in_time_range( conn, table, start_time, end_time ):
    cur = conn.cursor()
    cur.execute("SELECT * FROM "+ str(table) +" WHERE time >= ? AND time <= ?", (start, end))

    rows = cur.fetchall()
    return res



def get_last_sensors_data(conn):
    data = dict()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensors ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()

    if result != None:
        data['panelVoltage']       = result[ 1  ]
        data['panelCurrent']       = result[ 2  ]
        data['batteryVoltage']     = result[ 3  ]
        data['batteryCurrent']     = result[ 4  ]
        data['loadVoltage']        = result[ 5  ]
        data['loadCurrent']        = result[ 6  ]
        data['inPower']            = result[ 7  ]
        data['outPower']           = result[ 8  ]
        data['batteryStatus']      = result[ 9  ]
        data['batteryCapacity']    = result[ 10 ]
        data['batteryTemperature'] = result[ 11 ]
        data['time']               = result[ 12 ]
    else:
        data = None

    return data

def dump_data(conn, table):
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + str(table) )
    rows = cur.fetchall()


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = MQTT_CLIENT_ID,
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = SUBSCRIBED_MQTT_CHANNELS,
                                 )
    mqtt_client.start()

    conn = database_init()

    sensors_data = dict()
    last_data_arrived = None
    # Get the data from message_queue
    while True:
        # Waiting for a new message in the queue
        message = mqtt_client.message_queue.get()

        topic        = message.topic
        payload      = message.payload
        json_payload = json.loads(payload)
        input_name   = json_payload['data']['name']
        input_value  = json_payload['data']['value']

        now = time.time()

        # Perform actions
        if input_name in sensors:
            sensors_data[ input_name ] = input_value
            add_sensor_data( conn , input_name, input_value)

        if input_name in sensors and last_data_arrived is not None:
            if now - last_data_arrived > 1:
                add_sensors_data( conn , sensors_data )
                #:print(sensors_data)
        else:
            add_event_data( conn , input_value )
            # print( input_value )



if __name__ == "__main__":
    main()
