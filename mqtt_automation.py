# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import paho.mqtt.client as mqtt
import pandas as pd
import datetime as dt
import brightness_lookup

# mqtt setup
brokerAddress = '192.168.1.158'
brokerPort = 1883
pyClient = mqtt.Client()
pyClient.connect(brokerAddress, brokerPort)

# Input subscriptions
pyClient.subscribe("zigbee2mqtt/switch_hallway", 0)
pyClient.subscribe("zigbee2mqtt/switch_livingRoom", 0)
pyClient.subscribe("zigbee2mqtt/motion_hallway", 0)
pyClient.subscribe("zigbee2mqtt/ceilingLamp_hallway", 0)

# Create functions
# Hallway switch actuation
def on_message_switch_hallway(pyClient, userdata, message):
    state_switchHallway = pd.read_json(message.payload.decode("UTF-8"))
    if state_switchHallway['action'].iloc[0] == "on":
        pyClient.publish("zigbee2mqtt/ceilingLamp_hallway/set", '{"brightness":254, "state":"ON"}')
    else:
        pyClient.publish("zigbee2mqtt/ceilingLamp_hallway/set", '{"state":"OFF"}')
        
# Living room switch actuation
def on_message_switch_livingRoom(pyClient, userdata, message):
    state_switchLivingRoom = pd.read_json(message.payload.decode("UTF-8"))
    if state_switchLivingRoom['action'].iloc[0] == "on":
        pyClient.publish("zigbee2mqtt/floorLamp_livingRoom/set", '{"state":"ON"}')
    elif state_switchLivingRoom['action'].iloc[0] == "off":
        pyClient.publish("zigbee2mqtt/floorLamp_livingRoom/set", '{"state":"OFF"}')
    elif state_switchLivingRoom['action'].iloc[0] == "brightness_move_up":
        pyClient.publish("zigbee2mqtt/floorLamp_livingRoom/set", '{"brightness_move":100}')
    elif state_switchLivingRoom['action'].iloc[0] == "brightness_move_down":
        pyClient.publish("zigbee2mqtt/floorLamp_livingRoom/set", '{"brightness_move":-100}')
    elif state_switchLivingRoom['action'].iloc[0] == "brightness_stop":
        pyClient.publish("zigbee2mqtt/floorLamp_livingRoom/set", '{"brightness_move":0}')

# Hallway motion sensor activation
def on_message_motion_hallway(pyClient, userdata, message):
    state_motionHallway = pd.read_json(message.payload.decode("UTF-8"), typ='series')
    if state_motionHallway['occupancy'] == 1:
        brightnessSetpoint = brightness_lookup.getBrightness(dt.datetime.now())
        if brightnessSetpoint > 0:
            payload = '{"brightness":'+str(brightnessSetpoint)+', "state":"ON"}'
            pyClient.publish("zigbee2mqtt/ceilingLamp_hallway/set", payload)
    elif state_motionHallway['occupancy'] == 0:
        pyClient.publish("zigbee2mqtt/ceilingLamp_hallway/set", '{"state":"OFF"}')  

while True:
    pyClient.message_callback_add("zigbee2mqtt/switch_hallway", on_message_switch_hallway)
    pyClient.message_callback_add("zigbee2mqtt/switch_livingRoom", on_message_switch_livingRoom)
    pyClient.message_callback_add("zigbee2mqtt/motion_hallway", on_message_motion_hallway)
    pyClient.loop_forever()