import os
import sys                                 
import ssl
import json
import paho.mqtt.client as mqtt
import grove

class Led():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.__led__ = grove.ChainableLED(18,16,1)
        self.setColorRGB(r,g,b)

    def __del__(self):
        self.__led__.setColorRGB(0, 0, 0, 0)
    def setColorRGB(self, r, g, b): 
        self.r = r
        self.g = g
        self.b = b
        self.__led__.setColorRGB(0, r,g,b)

led = Led(0, 0, 0) 
pathPrefix = "$aws/things/grove-led-cheng/shadow" 

#called while client tries to establish connection with the server
def on_connect(mqttc, obj, flags, rc):
    if rc==0:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: successful")

        mqttc.subscribe([
            (pathPrefix + "/get/rejected", 1), 
            (pathPrefix + "/get/accepted", 1),
            (pathPrefix + "/update/delta", 1)]) 

        
    elif rc==1:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: Connection refused")

#called when a topic is successfully subscribed to
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos)+" data: "+str(obj))
    print "Retrieving reported state"
    mqttc.publish(pathPrefix + "/get")
          
#called when a message is received by a topic
def on_message(mqttc, obj, msg):
    print("Received message from topic: "+msg.topic+" | QoS: "+str(msg.qos)+" | Data Received: "+str(msg.payload))
    switcher = {
            pathPrefix + "/get/accepted": lambda: initColor(msg.payload),
            pathPrefix + "/get/rejected": lambda: (), 
            pathPrefix + "/update/delta": lambda: updateColor(msg.payload) 
    }
    func = switcher.get(msg.topic, lambda: ())
    func()

# set init color
def initColor(payload):
    data = json.loads(payload)
    state = data["state"]["reported"]
    color = state["color"]

    red = color.get('r', led.r)
    green = color.get('g', led.g)
    blue = color.get('b', led.b)

    led.setColorRGB(red, green, blue)
    
    mqttc.publish(pathPrefix + "/update", json.dumps({
                "state":{
                    "desired": {
                        "color": { "r": red, "g": green, "b": blue }
                    }
                }
            }))

# set delta color and publish the state
def updateColor(payload):
    data = json.loads(payload)
    state = data["state"]
    color = state["color"]

    red = color.get('r', led.r)
    green = color.get('g', led.g)
    blue = color.get('b', led.b)

    led.setColorRGB(red, green, blue)

    mqttc.publish(pathPrefix + "/update", json.dumps({
              "state": {
                  "reported": {
                      "color": { "r": red, "g": green, "b": blue }
                   }
               }
            }))
    
#creating a client with client-id=mqtt-test
mqttc = mqtt.Client(client_id="cheng")

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

#Configure network encryption and authentication options. Enables SSL/TLS support.
#adding client-side certificates and enabling tlsv1.2 support as required by aws-iot service
mqttc.tls_set(os.getcwd() + "/certs/root-CA.crt",
        certfile=os.getcwd() + "/certs/8561ed615e-certificate.pem.crt",
        keyfile=os.getcwd() + "/certs/8561ed615e-private.pem.key",
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None)

#connecting to aws-account-specific-iot-endpoint
mqttc.connect("AQNWQCI27L920.iot.us-west-2.amazonaws.com", port=8883) #AWS IoT service hostname and portno

mqttc.loop_forever()
