import json
import sys
import threading
from time import sleep

from services.publisher import LocalClient

mqtt_client = None

sys.path.insert(0, "..")

DELAY = 1.0


def mqtt_connection():
    global mqtt_client
    mqtt_client = LocalClient('sensor-opc_da', 'localhost', 1883)
    mqtt_client.run()


def get_opcda_server_connection():
    # Initialize client DCOM mode
    opc = OpenOPC.client()
    # Get available servers on localhost
    available_servers = opc.servers()
    # Open Server
    opc.connect( SERVER_NAME )

    return opc


def readGroupData( _opcServer, opcLabels ):
	val = None
	try:
		val = _opcServer.read( opcLabels )
	except OpenOPC.TimeoutError:
		print "TimeoutError occured: PLC is probably pauser or shouted down"

	return val


def createJson(*elements):
    callerInfo = {
        "culture": "it-IT",
        "timezone": "+01:00",
        "version": "1.0.0" }

#    output = {"machineryId": "gelli-belloi_01", "timestamp":"dd/MM/yyyy HH:mm:ss"}
    output = { "machineryId" : MACHINERY_ID }

    try:
        for couple in elements:

            if not isinstance(couple,tuple):
                print('Problem with data: nON E UNATUPLA')
            elif not len(couple) == 2:
                print('Problem with data: non ci sono due elementi nella tupla: ', len(couple))
            elif not len(couple[LABELS]) == len(couple[DATA]):
                print('Problem with data: le liste non sono lunghe uguali: ', len(couple[DATA]), len(couple[LABELS]))
                for i in range(0, max(len(couple[DATA]), len(couple[LABELS])) - 1):
                    print(i, couple[DATA][i], couple[LABELS][i])
            else:
                # print( 'OK' )
                output.update( dict( zip( couple[LABELS], couple[DATA] ) ) )
    except Exception as e:
        print( str(e) )
        return None

    startitJson = {'output' : output, 'callerInfo' : callerInfo}

    return startitJson


def read_PLC_data( opcGroups ):
    res = None
    res = readGroupData( opcGroups )
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")

    if res != None:
        try:
            data = createJson(
                (res[0][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Generale] ),
                (res[1][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo1.Fasi] ),
                (res[2][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo1.Ingressi] ),
                (res[3][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo1.Allarmi] ),
                (res[4][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo2.Fasi] ),
                (res[5][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo2.Ingressi] ),
                (res[6][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo2.Allarmi] ),
                (res[7][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo3.Fasi] ),
                (res[8][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo3.Ingressi] ),
                (res[9][1], [elem[ LABELS ] for elem in GelliBelloi.Labels.Gruppo3.Allarmi] )
                )

    return data

def publish_data( data ):
    return 0;


if __name__ == "__main__":

    mqtt_connection()

    # Chose the groups of vars
    opcGroups = GelliBelloi.VAR_GROUPS_SUPER_COMPACT
    opcServer = get_opcda_server_connection()

    while True:
        data = read_PLC_data( opcServer, opcGroups )

        publish_data( data )

        time.delay( DELAY )
