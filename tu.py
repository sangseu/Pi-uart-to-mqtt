#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import serial

# uart
ser = serial.Serial("/dev/ttyAMA0", baudrate=115200)
print("[+] UART ready")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("[+] rc: "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.publish("agrita/stt", "pi_connected", qos=0, retain=False)
    client.subscribe("agrita/+/in")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    msg_print = "[r] " + str(msg.payload)
    print(msg_print)
    split_topic = str(msg.topic).split("/")
    if len(split_topic)==3:
	#print(split_topic[2])
	if split_topic[2] == "in":
	  print("[t] uart: " + str(msg.payload))
	  ctrl = str(msg.payload) + "\r\n"
	  ser.write(ctrl)
    

# mqtt

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("128.199.139.40", 1883, 60)


# uart
# ser = serial.Serial("/dev/ttyAMA0", baudrate=115200)
# print("[+] UART ready")

def PUB(topic, data):
    client.publish( topic, data, qos=0, retain=False)	

# this will store the uart frame
seq = []

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while True:
	#time.sleep(1)
	#print ("tick")
	for c in ser.read():
		seq.append(c)
		joined_seq = ''.join(str(v) for v in seq) #Make a string from array
    
		if c is 'W': #Welcome to...
			break
		if c is '#': #end of uart frame
			print(joined_seq)
			split_seq = joined_seq.split(",")
			if len(split_seq) > 7: # frame length with data
				print("[+] id: " + split_seq[3])

        			seq = []
				topic = "agrita/" + split_seq[3] + "/out"

				PUB(topic, joined_seq)
				#client.publish( topic, joined_seq, qos=0, retain=False)
				print("[p] mqtt: " + topic)
			else:
				PUB("agrita/stt", joined_seq)
				seq = []
				print("[p] mqtt: agrita/stt")

        			break
