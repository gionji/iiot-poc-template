import json
from services.publisher import LocalClient


def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message


def data_manipulation( value ):
    output_value = input_value * 1
    return output_value


def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = "generic-client",
                                  host               = "localhost",
                                  port               = 1883,
                                  subscription_paths = [
                                                        '/persistence',
                                                        '/sensors',
                                                        '/data'
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
        mqtt_client.publish('/data', json.dumps(message))


if __name__ == "__main__":
    main()
