from __future__ import print_function

import pygame
import pygame.midi
from pygame.locals import *

import sys
import os

from ola.ClientWrapper import ClientWrapper
import array
import sys

wrapper = None

values=[0 for t in range(30)]


 
def DmxSent(status):
  if status.Succeeded():
    print('Success!')
  else:
    print('Error: %s' % status.message, file=sys.stderr)

  global wrapper
  if wrapper:
    wrapper.Stop()

def dmxSend():
  universe = 1
  data = array.array('B')
  for x in range(1,25):
    data.append(values[x])
  

  global wrapper
  wrapper = ClientWrapper()
  client = wrapper.Client()
  client.SendDmx(universe, data, DmxSent)
  wrapper.Run()

def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()

def _print_device_info():
    for i in range( pygame.midi.get_count() ):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
               (i, interf, name, opened, in_out))
        

def input_main(device_id):
    pygame.init()
    pygame.midi.init()

    input_id = device_id

    print ("using input_id %s" % input_id)

    i = pygame.midi.Input( input_id )

    going = True

    active=[0 for v in range(121)]
    stack = [8,7,6,5,4,3,2,1]

    while going:

        if i.poll():
            midi_events = i.read(10)

            #if midi_events[0][0][0] != 248:
                #print (midi_events[0][0][0])
		
	    if midi_events[0][0][0] == 144:
		
	        key = (midi_events[0][0][1])
		active[key] = stack.pop()
		velocity = midi_events[0][0][2]
		
		if key % 12 == 0:
			
			values[((active[key]*3)-2)] = 255
			values[((active[key]*3)-1)] = 0
			values[(active[key]*3)] = 0
			dmxSend()
		
		elif key % 12 == 1:
			
			values[((active[key]*3)-2)] = 190
			values[((active[key]*3)-1)] = 0
			values[(active[key]*3)] = 60
			dmxSend()
		
		elif key % 12 == 2:
			
			values[((active[key]*3)-2)] = 140
			values[((active[key]*3)-1)] = 0
			values[(active[key]*3)] = 120
			dmxSend()

		elif key % 12 == 3:
			values[((active[key]*3)-2)] = 60
			values[((active[key]*3)-1)] = 0
			values[(active[key]*3)] = 190
			dmxSend()
	
		elif key % 12 == 4:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 0
			values[(active[key]*3)] = 255
			dmxSend()

		elif key % 12 == 5:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 60
			values[(active[key]*3)] = 190
			dmxSend()

		elif key % 12 == 6:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 90
			values[(active[key]*3)] = 150
			dmxSend()

		elif key % 12 == 7:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 120
			values[(active[key]*3)] = 120
			dmxSend()
		
		elif key % 12 == 8:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 190
			values[(active[key]*3)] = 60
			dmxSend()
		
		elif key % 12 == 9:
			values[((active[key]*3)-2)] = 0
			values[((active[key]*3)-1)] = 255
			values[(active[key]*3)] = 0
			dmxSend()
		
		elif key % 12 == 10:
			values[((active[key]*3)-2)] = 60
			values[((active[key]*3)-1)] = 190
			values[(active[key]*3)] = 0
			dmxSend()
		
		elif key % 12 == 11:
			values[((active[key]*3)-2)] = 110
			values[((active[key]*3)-1)] = 120
			values[(active[key]*3)] = 0
			dmxSend()
		
    	    elif midi_events[0][0][0] == 128:
		key = (midi_events[0][0][1])
		
		values[((active[key]*3)-2)] = 0
		values[((active[key]*3)-1)] = 0
		values[(active[key]*3)] = 0
		
		dmxSend()
		stack.append(active[key])
		stack.sort(reverse=True)
		active[key] = 0
		
		
    del i
    pygame.midi.quit()



	


def main():
    
    print_device_info()
    device_id = int(input("Enter the device ID to use: "))
    input_main(device_id)
    input_main(3)

main()

