#!/usr/bin/env python

import sys, os, serial, commands
from PIL import Image
from time import sleep
from math import ceil
def image_to_bytes(img_path, color_mode):
	im = Image.open(img_path)
	w,h = im.size
	output = []
	if color_mode == "color":
		rgb_im = im.convert('RGB')
		for x in xrange(0, w):
			for y in xrange(0, h):
				r, g, b = rgb_im.getpixel((x, y))
				output.append(r)
				output.append(g)
				output.append(b)
	elif color_mode == "grayscale":
		gray_im = im.convert('LA')
		for x in xrange(0, w):
			for y in xrange(0, h):
				g = gray_im.getpixel((x, y))
				output.append(g[0])

	return output, w, h

def send_bytes(img_bytes, w, h, color_mode):

	img_bytes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	img_bytes = bytearray(img_bytes)

	# packet_size = 51

	print ""
	print "image size: {}x{} pixels. Total bytes: {}".format(w, h, len(img_bytes))
	print "At {} bytes per packet, with 1 packet per minute that's {} packets, which will take about: {} minutes, or {} hours".format(packet_size, total_packets, total_packets/60, total_packets/60/60)
	print "press [return] to start sending, or [x] to quit"
	user_input = raw_input()
	if user_input == "x":
		sys.exit(0)

	# Open serial
	status, address = commands.getstatusoutput('ls /dev | grep ttyUSB')
	ser = serial.Serial("/dev/{}".format(address), 115200)
	sleep(2) # turns out this pause is imporant! Without it, the serial
	# ser.isOpen()

	byte_counter = 0
	for byteset in xrange(0, total_packets):
		ser.write('b'.encode())
		ser.write(img_bytes[byteset*packet_size:byteset*packet_size+packet_size])
		ser.write('e'.encode())
	sleep(2)
	msg = ser.read(ser.inWaiting()) # read everything in the input buffer
	print ("Message from arduino: ", msg)
	"""
	for byte in output:
		if byte_counter == 0:
			current_packet += 1
			print "Sending packet {} of {}".format(current_packet, total_packets)

		# ser.write(x)
		byte_counter += 1
		if byte_counter >= packet_size:
			byte_counter = 0
			sleep(0.0) # wait for a minute before we continue
	#ser.close() # done!

	# keep sending packets so until we reached the total packet_size
	if byte_counter < packet_size:
		for x in xrange(0, packet_size-byte_counter):
			print write
			# ser.write(x)
	#ser.close() # done!
	"""

def send_partial_bytes(img_bytes, current_packet, packet_size):
	print "send_partial_bytes"
	current_packet -= 1
	bytes_to_send = img_bytes[current_packet*packet_size:current_packet*packet_size+packet_size]

	# Make sure our last packet is also <packet_size> long
	while len(bytes_to_send) < packet_size:
		bytes_to_send.append(0)

	global ser
	#ser.write(b'b')
	#print "Sending: ", bytes_to_send[0]
	ser.write(bytes_to_send)
	#ser.write(b'e')

def main():

	global ser
	if len(sys.argv) < 2:
		print "No image path specified"
		sys.exit(1)

	img_path = sys.argv[1]
	w, h = 0, 0
	if not os.path.isfile(img_path):
		print "Error: image does not exist: ", img_path
		sys.exit(1)

	color_mode = "color"
	if len(sys.argv) > 2:
		if sys.argv[2] not in ["color", "grayscale"]:
			print "Invalid color mode, use 'color' or 'grayscale'"
			sys.exit(1)
		else:
			color_mode = sys.argv[2]

	img_bytes, w, h = image_to_bytes(img_path, color_mode)

	status, address = commands.getstatusoutput('ls /dev | grep ttyUSB')
	ser = serial.Serial("/dev/{}".format(address), 9600)
	sleep(2) # turns out this pause is imporant! Without it, the serial
	# ser.isOpen()

	img_bytes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	img_bytes *= 100
	img_bytes = bytearray(img_bytes)

	packet_size = 3
	current_packet = 1
	total_packets = int(ceil(len(img_bytes)/float(packet_size)))
	while current_packet <= total_packets:
		msg = ser.read(ser.inWaiting())
		# msg = ser.read(1) # wait for sending confirmation
		if msg != "" and msg != "\n":
			print "=> ", msg
		# sleep(1)
		output = ""
		if msg == 's':
			print "Data requested, sending {} of {}".format(current_packet, total_packets)
			send_partial_bytes(img_bytes, current_packet, packet_size)
			current_packet+=1
		elif msg =='\n':
			if output != " ":
				print output
			output = ""
		elif msg != "":
			print "add to output: _{}_".format(msg)
			if msg == '\r\n':
				print "newline?"
			if msg == '\n':
				print "newline?2"
			output += msg
		#	print "other msg", msg
		# sleep(1)
	print "All packages have been sent."
	sys.exit(0)
	# send_bytes(img_bytes, w, h, color_mode)

if __name__ == "__main__":
	main();
#im = Image.open('image.gif')
#rgb_im = im.convert('RGB')
#r, g, b = rgb_im.getpixel((1, 1))

#print(r, g, b)
#(65, 100, 137)