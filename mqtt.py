import os

import paho.mqtt.client as paho
from dotenv import load_dotenv
from paho import mqtt

broker_url, username, password = None, None, None


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
    Prints the result of the connection with a reason code to stdout ( used as callback for connect )

    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param flags: these are response flags sent by the broker
    :param rc: stands for reasonCode, which is a code for the connection result
    :param properties: can be used in MQTTv5, but is optional
    """
    print(f"Connected with result code {rc}")


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
    Prints a reassurance for successfully subscribing

    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
    :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
    :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
    Prints a mqtt message to stdout ( used as callback for subscribe )

    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param msg: the message with topic and payload
    """
    print(f"{msg.topic}: {msg.payload.decode()}")


def paho_init():
    if broker_url is None or username is None or password is None:
        return None
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    return client


def paho_connect(client):
    assert client is not None

    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.connect(broker_url, 8883)
    return client


if __name__ == "__main__":
    load_dotenv()
    broker_url = os.getenv("MQTT_SERVER")
    username = os.getenv("MQTT_USER")
    password = os.getenv("MQTT_PASS")
    print(broker_url, username, password)

    client = paho_init()
    paho_connect(client)

    client.subscribe("laundry/+")

    client.loop_forever()
