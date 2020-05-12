import json
from services.publisher import LocalClient

mean = 0


def main():
    global mean
    local_client = LocalClient(client_id="test", host="localhost", port=1883, subscription_paths=['/data', '/data2'])
    local_client.start()

    i = 0
    while True:
        message = local_client.message_queue.get()

        if message is None:
            continue
        topic = message.topic
        payload = message.payload
        json_payload = json.loads(payload)
        print('[MAIN] received ' + str(topic) + ' ' + str(json_payload))
        mean = mean + float(json_payload['data']['value'])
        i = i + 1

        if i == 10:
            message = {
                "data": {
                    "value": mean / i
                }
            }
            local_client.publish('/mean', json.dumps(message))
            i = 0
            mean = 0


if __name__ == "__main__":
    main()
