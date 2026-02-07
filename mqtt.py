import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    status = str(message.payload.decode("utf-8"))
    if status == "FINISHED":
        # Call your existing Telegram bot send function here
        # bot.send_message(chat_id, "Laundry is done!")
        print("hi")


client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe("myhome/laundry/+")
client.loop_forever()
client.loop_forever()
