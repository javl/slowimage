#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===========================================================================
# This script takes an image, convertes it to a list of bytes and sends
# those over serial to an Arduino that will send them over LORA. See the
# repository for those two scripts.
#
# run using:
# ./img_sender.py <filename>
#===========================================================================-

import sys, os, serial, commands
from PIL import Image
from time import sleep
from math import ceil

#=================================================================================
# Convert our image to bytes we can send later
#=================================================================================
def image_to_bytes(img_path):
	global packet_size

	im = Image.open(img_path)
	w,h = im.size
	output = []
	packet_size = 3
	rgb_im = im.convert('RGB')
	for x in xrange(0, w):
		for y in xrange(0, h):
			r, g, b = rgb_im.getpixel((x, y))
			output.append(r)
			output.append(g)
			output.append(b)

	return output, w, h

#=================================================================================
# Send a part of our image
#=================================================================================
def send_partial_bytes(img_data, current_packet, packet_size, img_width, total_packets):
	global ser

	packet_index = current_packet - 1
	data_to_send = img_data[packet_index*packet_size:packet_index*packet_size+packet_size]

	#============================
	# add a 4th byte to indicate the type of pixel
	#============================
	if current_packet == 1: # the first pixel
		data_to_send.append(1)
	elif current_packet == total_packets: # the last pixel
		data_to_send.append(3)
	elif current_packet % img_width == 1: # first pixel in a row
		data_to_send.append(2)
	else: # regular pixels
		data_to_send.append(0)

	print "Sending data to Arduino: ", data_to_send

	for d in data_to_send:
		ser.write('{}>'.format(d)) # send with '>' as a delimiter

#=================================================================================
# Main loop
#=================================================================================
def main():
	global ser

	if len(sys.argv) < 2:
		print "No image path specified"
		sys.exit(1)

	img_path = sys.argv[1]
	if not os.path.isfile(img_path):
		print "Error: image does not exist: ", img_path
		sys.exit(1)

	img_bytes, w, h = image_to_bytes(img_path)

	# find our Arduino. This path depends on your system. OsX uses ttyACM for instance
	status, address = commands.getstatusoutput('ls /dev | grep ttyUSB')
	ser = serial.Serial("/dev/{}".format(address), 9600)
	sleep(2) # turns out this is important, wait for the connection to be made

	current_packet = 1
	total_packets = int(ceil(len(img_bytes)/float(packet_size)))
	output = ""

	while True:
		msg = ser.read(1)
		if ord(msg) == 11: # using VT character
			print "Data requested, sending {} of {}".format(current_packet, total_packets)
			sleep(1)
			send_partial_bytes(img_bytes, current_packet, packet_size, w, total_packets)
			current_packet+=1
		elif msg != "" and msg != "\r":
			# combine seperate serial data into a full message
			output += msg
		elif msg =='\r':
			# print the complete serial message
			print output
			output = ""
		msg = "" # clear the last message

	if current_packet > total_packets:
		current_packet = 1
		print "All packages have been sent. Restarting"

if __name__ == "__main__":
	main();