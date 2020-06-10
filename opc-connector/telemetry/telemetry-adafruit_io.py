import sys
sys.path.insert(0, "..") # this allows to load upper level imports
import json
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT
from Adafruit_IO import MQTTClient, Client, Feed
import threading

import common.MyCommons as Commons


# Set to your Adafruit IO key.
ADAFRUIT_IO_KEY      = 'YOUR_AIO_KEY'
ADAFRUIT_IO_USERNAME = 'YOUR_AIO_USERNAME'

ADAFRUIT_IO_USERNAME = "gionji"
ADAFRUIT_IO_KEY      = "84f37c4b486645d3b246be43f810543d"

sensors          = Commons.OPC_SENSORS
SUBSCRIBED_TOPIC = 'message'

## subscibe frome aoi see here:
#https://github.com/adafruit/Adafruit_IO_Python/blob/master/examples/basics/subscribe.py

class AdafruitIoClient(threading.Thread):

    def __init__(self, my_key, my_username):
        threading.Thread.__init__(self)
        self.my_key         = my_key
        self.my_username    = my_username
        self.mqttdevice         = MQTTClient( self.my_username, self.my_key )
        self.device         = Client( self.my_username, self.my_key )

    def subscribe(self, feed_id):
        self.mqttdevice.subscribe(feed_id)


    def set_on_connect(self, callback):
        self.mqttdevice.on_connect = callback

    def set_on_disconnect(self, callback):
        self.mqttdevice.on_disconnect = callback

    def set_on_message(self, callback):
        self.mqttdevice.on_message = callback


    def get_feeds(self):
        return self.device.feeds()

    def create_feed(self, feed):
        return self.device.create_feed(feed)


    def run(self):
        self.mqttdevice.connect()
        self.mqttdevice.loop_blocking()

    def send_data( self, name, value):
        self.device.send_data( str(name).lower() , value )



def on_message_received_from_telemetry(client, feed_id, payload):
    print(">>>>>>> " + str( payload ) + "  " + str(feed_id) + "<<<<<<<")
    return "TO_DO"


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = "telemetry-adafruitio",
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = [
                                                            IIoT.MqttChannels.telemetry,
                                                       ]
                                 )
    mqtt_client.start()

    aio_client = AdafruitIoClient(
                                  my_key         = ADAFRUIT_IO_KEY,
                                  my_username    = ADAFRUIT_IO_USERNAME
                             )
    aio_client.name = 'Adafruitio Thread'
    aio_client.subscribe( SUBSCRIBED_TOPIC )
    aio_client.on_message = on_message_received_from_telemetry
    aio_client.start()

    # Create a new feed in the cloud telemetry MAX 10 !!
    # You can create them also on the adafruit portal
    """
    for feedName in sensors:
        try:
            print(feedName)
            feed     = Feed(name = feedName )
            response = aio_client.create_feed(feed)
        except Exception as e:
            print( e )
    """

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

        # Perform actions
        try:
            if input_name == 'panelVoltage++':
                aio_client.send_data( input_name.lower(), input_value )
        except Exception as e:
            print( e )


if __name__ == "__main__":
    main()
