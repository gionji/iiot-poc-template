import time

import paho.mqtt.client as mqtt
import threading
import queue


class MqttLocalClient(threading.Thread):

    def __init__(self, client_id=None, host='localhost', port=1883, subscription_paths=None):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.subscription_paths = subscription_paths
        self.message_queue = queue.Queue()
        self.client = mqtt.Client(client_id=self.client_id)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        print('[MQTT_CLIENT] publish to ' + topic + ' payload: ' + payload)

    def run(self):
        print('[MQTT_CLIENT] connecting to mqtt -> ' + self.host + ':' + str(self.port))
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port, 60)
        self.subscribe_all(self.subscription_paths)
        self.client.loop_forever()

    def on_message(self, client, obj, msg):
        if msg != None:
            self.message_queue.put(msg)

    def subscribe_all(self, subscription_paths=None, qos=1):
        if subscription_paths is None:
            subscription_paths = []
        for path in subscription_paths:
            print('[MQTT_CLIENT] subscribe to ' + path)
            self.client.subscribe(path, qos=qos)
            time.sleep(0.5)
