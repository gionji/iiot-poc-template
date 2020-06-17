import sys
sys.path.insert(0, "..") # this allows to load upper level imports
import json
import threading
from time import sleep
from opcua import Client, ua
from common.services.publisher import MqttLocalClient
import libs.utils.IIoT as IIoT

import common.MyCommons as Commons


OUTPUT_CHANNEL = '/data'
MEAN_SAMPLES   = 10
VARIABLE_NAME  = 'panelVoltage'

MQTT_CLIENT_ID = "data-compute_mean"
SUBSCRIBED_MQTT_CHANNELS = [
                            IIoT.MqttChannels.sensors,
                           ]

def main():
    mqtt_client = MqttLocalClient(
                                  client_id          = MQTT_CLIENT_ID,
                                  host               = IIoT.MQTT_HOST,
                                  port               = IIoT.MQTT_PORT,
                                  subscription_paths = SUBSCRIBED_MQTT_CHANNELS
                                 )
    mqtt_client.start()

    # initialize ounter and mean var
    i = 0
    mean = 0

    while True:
        # Waiting for a new message in the queue
        message = mqtt_client.message_queue.get()

        #Get the message topic and its payload
        topic   = message.topic
        payload = message.payload
        json_payload = json.loads(payload)

        if json_payload['data']['name'] == VARIABLE_NAME:
            # perform calculation
            mean = mean + float(json_payload['data']['value'])
            i = i + 1

            if i == MEAN_SAMPLES:
                # the variable name containing mean is made by
                # original_var_name _ number_of_samples_ (seconds) _mean
                output_name = VARIABLE_NAME + "_" + str(MEAN_SAMPLES) + "_sec_mean"

                # compute the mean
                output_value = mean / MEAN_SAMPLES

                # reset counter and mean var
                i = 0
                mean = 0

                # pack the json publish message
                message = IIoT.packOutputMessage(output_name, output_value)

                # publish the message to the mqtt broker
                mqtt_client.publish(OUTPUT_CHANNEL, json.dumps(message))

if __name__ == "__main__":
    main()
