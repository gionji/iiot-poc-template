import json
from services.publisher import MqttLocalClient

mean = 0

OUTPUT_CHANNEL = '/data'
MEAN_SAMPLES   = 10
VARIABLE_NAME  = 'panelVoltage'

def packOutputMessage(output_name ,output_value):
    message = {
        "data": {
            "name" : output_name,
            "value": output_value
        }
    }
    return message

def main():
    global mean
    local_client = MqttLocalClient(client_id="test", host="localhost", port=1883, subscription_paths=['/sensors'])
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
        #print('[MAIN] received ' + str(topic) + ' ' + str(json_payload))

        if json_payload['data']['name'] ==  VARIABLE_NAME:
            # perform calculation
            mean = mean + float(json_payload['data']['value'])
            i = i + 1

            if i == MEAN_SAMPLES:
                output_name = VARIABLE_NAME + "_" + str(MEAN_SAMPLES) + "_sec_mean"
                output_value = mean / MEAN_SAMPLES
                message = packOutputMessage(output_name ,output_value)

                i = 0
                mean = 0

                # publish the message to the mqtt broker
                local_client.publish(OUTPUT_CHANNEL, json.dumps(message))

if __name__ == "__main__":
    main()
