import json
from services.publisher import MqttLocalClient
import datetime
import time
import TemplateCommon as IIoT


DATABASE_PATH = r"./database.sqlite"

sensors = IIoT.OPC_SENSORS
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
                                        panelVoltage         real,
                                        panelCurrent         real,
                                        batteryVoltage       real,
                                        batteryCurrent       real,
                                        loadVoltage          real,
                                        loadCurrent          real,
                                        powerInput           real,
                                        powerOoutput          real,
                                        batteryStatus         real,
                                        batteryCapacity       real,
                                        batteryTemperature    real,
                                        time                  timestamp NOT NULL
                                    ); """

    sql_create_table_events = """ CREATE TABLE IF NOT EXISTS events (
                                        id integer            PRIMARY KEY AUTOINCREMENT,
                                        event_message         text,
                                        time                  timestamp NOT NULL
                                    ); """

    try:
        c = conn.cursor()
        c.execute( sql_create_table_sensors )
        c.commit()
    except Error as e:
        print(e)

    try:
        c = conn.cursor()
        c.execute( sql_create_table_events )
        c.commit()
    except Error as e:
        print(e)

def add_sensors_data(conn, data):

    data = dictToTuple

    data = data + (datetime.datetime.now(), )

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


def add_event_data(conn, data):
    data = (data, datetime.datetime.now() )

    sql = ''' INSERT INTO sensors( event_message
                                   time
                                    )
              VALUES( ?,? ) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        conn.close()
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
        data['panelVoltage'] = result[ 1 ]
        data['panel_current'] = result[ 2 ]
        data['battery_voltage'] = result[ 3 ]
        data['battery_current'] = result[ 4]
        data['load_voltage'] = result[5]
        data['load_current'] = result[6]
        data['power_input'] = result[7]
        data['power_output'] = result[8]
        data['battery_status'] = result[ 9]
        data['battery_capacity'] = result[ 10]
        data['battery_temperature'] = result[ 11]
        data['time'] = result[12]
    else:
        data = None

    return data

def dump_data(conn, table):
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + str(table) )
    rows = cur.fetchall()


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = "database-sqlite",
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = [
                                                        IIoT.MqttChannels.persist,
                                                       ]
                                 )
    mqtt_client.start()

    conn = database_init()

    sensors_data = dict()
    last_data_arrived = time.time()
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


        if input_name in sensors:
            if now - last_data_arrived > 1:
                add_sensors_data( conn , sensors_data )
        else:
            add_event_data( conn , input_value )



if __name__ == "__main__":
    main()
