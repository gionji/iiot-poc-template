import sys
sys.path.insert(0, "..") # this allows to load upper level imports
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT
import common.MyCommons as Commons

import json
from losantmqtt import Device
import threading


MQTT_CLIENT_ID           = "telemetry-losant"
SUBSCRIBED_MQTT_CHANNELS = [
                               IIoT.MqttChannels.telemetry,
                           ]



class LosantClient(threading.Thread):

    def __init__(self, my_device_id, my_app_access_key, my_app_access_secret):
        threading.Thread.__init__(self)
        self.my_device_id         = my_device_id
        self.my_app_access_key    = my_app_access_key
        self.my_app_access_secret = my_app_access_secret

        # Construct Losant device
        self.device = Device(self.my_device_id,
                        self.my_app_access_key,
                        self.my_app_access_secret)

        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def run(self):
        # Connect to Losant and leave the connection open
        self.device.add_event_observer("command", self.on_command)
        self.device.connect(blocking=True)


    def sendDeviceState(self, name, value):
        print("Sending Device State")
        self.device.send_state( {str(name) : value} )

    def on_command(self, device, command):
        print(command["name"] + " command received.")

        if command["name"] == "toggle":
            self.callback(command)
            print("Do something")




def command_from_losant_callback(command):
    print(">>>>>>> " + str( command ) + "<<<<<<<")
    return "TO_DO"



MY_DEVICE_ID         = ''
MY_APP_ACCESS_KEY    = ''
MY_APP_ACCESS_SECRET = ''

MY_DEVICE_ID         = '5ee0e07c5aada0000646678c'
MY_APP_ACCESS_KEY    = '0a2a14c7-b5f1-4690-bdc2-cec7c7806767'
MY_APP_ACCESS_SECRET = '8c1e327a4edbcfac3bea399203885e09c1ea1a0c9ddadbe7ae06cf9e8e2878bc'



def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = MQTT_CLIENT_ID,
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = SUBSCRIBED_MQTT_CHANNELS
                                 )
    mqtt_client.start()

    losant_client = LosantClient(
                                  my_device_id         = MY_DEVICE_ID,
                                  my_app_access_key    = MY_APP_ACCESS_KEY,
                                  my_app_access_secret = MY_APP_ACCESS_SECRET,
                                )
    losant_client.set_callback(command_from_losant_callback)
    losant_client.name = 'Losant Thread'
    losant_client.start()

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
        if input_name == 'panelVoltage':
            losant_client.sendDeviceState( "my_first_numeric_value", input_value)




if __name__ == "__main__":
    main()
