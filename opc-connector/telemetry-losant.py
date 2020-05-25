import json
from services.publisher import MqttLocalClient
from losantmqtt import Device


class LosantClient(threading.Thread):

    def __init__(self, my_device_id, my_app_access_key, my_app_access_secret):
        threading.Thread.__init__(self)
        self.my_device_id         = my_device_id
        self.my_app_access_key    = my_app_access_key
        self.my_app_access_secret = my_app_access_secret
        self.message_queue        = queue.Queue()
        # Construct Losant device
        self.device = Device(self.my_device_id,
                        self.my_app_access_key,
                        self.my_app_access_secret)


    def run(self):
        # Connect to Losant and leave the connection open
        self.device.connect(blocking=True)


    def sendDeviceState(device, name, value):
        print("Sending Device State")
        device.send_state( {str(name) : value} )

    def on_comm
    and(device, command):
        print(command["name"] + " command received.")

        if command["name"] == "toggle":
            print("Do something")



MY_DEVICE_ID         = ''
MY_APP_ACCESS_KEY    = ''
MY_APP_ACCESS_SECRET = ''

def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message



def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = "telemetry-losant",
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = [
                                                        IIoT.MqttChannels.telemetry,
                                                       ]
                                 )
    mqtt_client.start()

    losant_client = LosantClient(
                                  my_device_id         = MY_DEVICE_ID,
                                  my_app_access_key    = MY_APP_ACCESS_KEY,
                                  my_app_access_secret = MY_APP_ACCESS_SECRET
                                )
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
        sendDeviceState(device, input_name, input_value)

        # Publish data
        message = packOutputMessage(output_value)
        mqtt_client.publish('/data', json.dumps(message))


if __name__ == "__main__":
    main()
