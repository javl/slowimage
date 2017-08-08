#!/usr/bin/env python
# -*- coding: utf-8 -*

#===========================================================================
# This MQTT receiver that will reconstruct an image from the data sent by
# a LORA device (see ttn_img_sender.ino in this repo)
# Each incoming packet is 4 bytes, for R,G,B & special.
#
# Special can be:
# 0 = a regular pixel
# 1 = the first pixel of the image,
# 2 = first pixel of a line (except first of the image)
# 3 = last pixel of the image
#
# Run using ./img_receiver.py
#===========================================================================-
import paho.mqtt.client as mqtt
import json
import Image, ImageDraw, sys, os

# Start size of our image
img_width = 1
img_height = 1

# create a new image
im= Image.new('RGB', (img_width, img_height))
draw = ImageDraw.Draw(im)

# start position for drawing
x = 0
y = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hdsa/devices/imgsender/up")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global x, y, im, draw, img_width, img_height
    #print(msg.topic+" "+str(msg.payload))

    # get the result. read it as json and get our values
    result = json.loads(str(msg.payload));
    data = result['payload_fields']

    r = data['r']
    g = data['g']
    b = data['b']
    s = data['s']

    print "Received: {}, {}, {}, {}".format(r, g, b, s)

    #=================================================
    # Normal pixel, increment x and draw, expand
    # canvas if needed
    #=================================================
    if s == 0:
        x += 1
        print "Draw {}, {}, {} at {}, {}".format(r, g, b, x, y)
        draw.point((x, y), fill=(r, g, b))
        if x+1 > img_width: # increate the canvas size
            print "increase image width"
            print im.size
            img_width = x+1
            im_new = Image.new('RGB', (img_width, img_height))
            im_new.paste(im, (0,0))
            im = im_new

    #=================================================
    # First pixel of image, move to 0,0 and draw
    #=================================================
    elif s == 1:
        x = 0
        y = 0
        print "Draw {}, {}, {} at {}, {}".format(r, g, b, x, y)
        draw.point((x, y), fill=(r, g, b))

    #=================================================
    # First pixel of line, but not first of image
    # reset x, increment y, expand canvas if needed
    #=================================================
    elif s == 2:
        x = 0
        y += 1

        if y+1 > img_height:
            print im.size
            print "update size height"
            img_height = y+1
            im_new = Image.new('RGB', (img_width, img_height))
            im_new.paste(im, (0,0))
            im = im_new
            print im.size
        print "Draw {}, {}, {} at {}, {}".format(r, g, b, x, y)
        draw.point((x, y), fill=(r, g, b))

    #=================================================
    # Last pixel of image,
    #=================================================
    elif s == 3: # last pixel
        x+=1
        print "Draw {}, {}, {} at {}, {}".format(r, g, b, x, y)
        draw.point((x, y), fill=(r, g, b))

    #=================================================
    # An unknown special value
    #=================================================
    else:
        print "Unknown special value: ", s

    im.save("slowImage.png", "PNG")
    # optionaly upload the file using ssh
    #os.system("scp slowImage.png user@host:path/for/saving/result")
    print "done"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# connect to the MQTT server
application_name = ''
password = ''
client.username_pw_set(application_name, password)
client.connect("eu.thethings.network", port=1883)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# meansual interface.
client.loop_forever()