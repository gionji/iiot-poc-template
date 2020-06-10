import json
from common.services.publisher import MqttLocalClient
import common.IIoT as IIoT

import common.MyCommons as Commons

MQTT_CLIENT_ID           = "genric"
SUBSCRIBED_MQTT_CHANNELS = [
                               #IIoT.MqttChannels.persist,
                           ]

def data_manipulation( value ):
    return value


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = MQTT_CLIENT_ID,
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = [
                                                        SUBSCRIBED_MQTT_CHANNELS,
                                                       ]
                                 )
    mqtt_client.start()

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
        output_value = data_manipulation( input_value )

        # Publish data
        message = packOutputMessage(output_value)
        mqtt_client.publish(IIoT.MqttChannels.persist, json.dumps(message))


if __name__ == "__main__":
    main()
