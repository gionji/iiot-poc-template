import json
from services.publisher import LocalClient

mean = 0


def main():
    global mean
    local_client = MqttLocalClient(client_id="test", host="localhost", port=1883, subscription_paths=['/data', '/data2'])
    local_client.start()

    i = 0
    while True:
        # Waiting for a new message in the queue
        message = local_client.message_queue.get()

        # if the message is not none
        if message is None:
            continue

        #Get the message topic and its payload
        topic   = message.topic
        payload = message.payload
        json_payload = json.loads(payload)
        print('[MAIN] received ' + str(topic) + ' ' + str(json_payload))

        # perform calculation
        mean = mean + float(json_payload['data']['value'])
        i = i + 1

        if i == 10:
            message = {
                "data": {
                    "value": mean / i
                }
            }

            i = 0
            mean = 0

            # publish the message to the mqtt broker
            local_client.publish('/mean', json.dumps(message))



if __name__ == "__main__":
    main()
