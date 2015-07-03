#!/usr/bin/env python

#
# Example using Dynamic Payloads

import time
from RF24 import *

class EmonHubRF24Interfacer(EmonHubInterfacer):

    def __init__(self, name):
        ########### USER CONFIGURATION ###########
        # See https://github.com/TMRh20/RF24/blob/master/RPi/pyRF24/readme.md
        
        # CE Pin, CSN Pin, SPI Speed
        
        # Setup for GPIO 22 CE and GPIO 25 CSN with SPI Speed @ 1Mhz
        #radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_18, BCM2835_SPI_SPEED_1MHZ)
        
        # Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 4Mhz
        #radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_4MHZ)
        
        #RPi B
        # Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
        self._radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)
        
        #RPi B+
        # Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
        #radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)
        
        ##########################################
        
        """Initialize Interfacer

        port_nb (string): port number on which to open the socket

        """
        pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
        min_payload_size = 4
        max_payload_size = 32
        payload_size_increments_by = 1
        next_payload_size = min_payload_size
        inp_role = 'none'
        send_payload = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012'
        millis = lambda: int(round(time.time() * 1000))        
               
        self._radio.begin()
        self._radio.enableDynamicPayloads()
        self._radio.setRetries(5,15)
        self._radio.printDetails()        
        
        self._radio.openWritingPipe(pipes[1])
        self._radio.openReadingPipe(1,pipes[0])
        self._radio.startListening()

    def close(self):
        """Close socket."""
        
        # Close socket
        if self._radio is not None:
            self._log.debug('Closing socket')
            self._radio.close()

    def read(self):
        """Read data from socket and process if complete line received.

        Return data as a list: [NodeID, val1, val2]
        
        """
        # if there is data ready
        if self._radio.available():
            while self._radio.available():
                # Fetch the payload, and see if this was the last one.
	            len = self._radio.getDynamicPayloadSize()
	            receive_payload = self._radio.read(len)

	            # Spew it
	            print 'Got payload size=', len, ' value="', receive_payload, '"'

        # First, stop listening so we can talk
        self._radio.stopListening()

        # Send the final one back.
        self._radio.write(receive_payload)
        print 'Sent response.'

        # Now, resume listening so we catch the next packets.
        self._radio.startListening()
        
        # unix timestamp
        t = round(time.time(), 2)
        
        # Process data frame
        return self._process_frame(f, t)