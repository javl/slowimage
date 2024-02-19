## Lora Image Sender ##
Made during [Hackers & Designers Summer Academy 2017, On & Off the grid](https://hackersanddesigners.nl/s/Summer_Academy_2017). During this workshop we were introducted to LoRa, a low-power, low-bandwidth network technology using [The Things Network](https://www.thethingsnetwork.org/) (TTN). 

Did you find this script useful? Feel free to support my open source software:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/javl?label=Sponsor&logo=GitHub)](https://github.com/sponsors/javl)


`slowimage_sender.py` takes an image and converts it to bytes. When ready, the Arduino (programmed with `ttn_img_sender.ino`) will request four bytes from this script and send them over LoRa. It will then sleep for about a minute before requesting the next four bytes.
`slow_receiver.py` uses MQTT to connect to TTN to get the sent data and will try to rebuild the image.

This repo contains a 3x3 image (`test.png`) for quick testing, and `buda.png` which is the image we worked with during the workshop.

More info on the used node hardware can be found [here](https://www.thethingsnetwork.org/labs/story/creating-a-ttn-node). The two needed Arduino libraries can be downloaded [here](https://www.thethingsnetwork.org/labs/story/creating-a-ttn-node).
