import json
from services.publisher import MqttLocalClient
from losantmqtt import Device

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

def on_command(device, command):
    print(command["name"] + " command received.")

    # Listen for the gpioControl. This name configured in Losant
    if command["name"] == "toggle":
        # toggle the LED
        led.toggle()

def sendDeviceState(device, name, value):
    print("Sending Device State")
    device.send_state( {str(name) : value} )


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

    # Construct Losant device
    device = Device(MY_DEVICE_ID, MY_APP_ACCESS_KEY, MY_APP_ACCESS_SECRET)

    # Connect to Losant and leave the connection open
    device.connect(blocking=False)

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
