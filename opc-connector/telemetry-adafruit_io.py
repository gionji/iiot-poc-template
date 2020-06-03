import json
from services.publisher import MqttLocalClient
from Adafruit_IO import Client, Feed


# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = 'YOUR_AIO_KEY'

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'YOUR_AIO_USERNAME'


def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message


## subscibe frome aoi see here:
#https://github.com/adafruit/Adafruit_IO_Python/blob/master/examples/basics/subscribe.py


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

    # Create an instance of the REST client.
    aio      = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Create a new feed named 'counter'
    feed     = Feed(name="Counter")
    response = aio.create_feed(feed)

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
        aio.send_data( input_name, input_value )

        # Publish data
        message = packOutputMessage(output_value)
        mqtt_client.publish('/data', json.dumps(message))


if __name__ == "__main__":
    main()
