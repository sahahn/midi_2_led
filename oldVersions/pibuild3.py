from __future__ import print_function
import pygame
import pygame.midi
from pygame.locals import *
import sys
import os
from ola.ClientWrapper import ClientWrapper
import array
import sys

NUM_LIGHTS = 4
CHAN = NUM_LIGHTS * 3

#The amount of semi_tones the pitch wheel controls
SEMI_TONE = 2

#Array to store light values, slot 0 stays empty
values=[0 for t in range(CHAN + 2)]

global wrapper
wrapper = ClientWrapper()
client = wrapper.Client()


def DmxSent(status):
  if status.Succeeded():
    r = 7   #this was just a useless operation
  else:
    print('Error: %s' % status.message, file=sys.stderr)

  global wrapper
  if wrapper:
    wrapper.Stop()

def dmxSend():
  universe = 1
  data = array.array('B')
  for x in range(1,(CHAN+1)):
    data.append(values[x])
  
  client.SendDmx(universe, data, DmxSent)
  wrapper.Run()

def dmxSendBlack():
  universe = 1
  data = array.array('B')
  for x in range(1,(CHAN+1)):
    data.append(0)
  
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

    
    L = 0 #Intialize light number
    
    N = 0 #Initialize light value

    mod = 0 #Initialize the mod value
    modCounter = 0 #Initialize value to be used w/ the modwheel

    strobeSpeed = 200 #Value used to determine strobe speed w/ the mod effect

    bend = 0 #Initialize the bend value
    
    active=[0 for v in range(121)] #Create an empty array associated with key values, to keep track of keys being held down

    stack = range(1,(NUM_LIGHTS+1)) #Create a stack (list) for assigning new lights
    stack.sort(reverse=True) #In this build, the stack is contantly sorted so that lights fill in a predictable way

    #Info on active lights (used with the pitch wheel) 
    lights = [[0 for x in range(2)] for d in range(NUM_LIGHTS+2)]  #lights[x][0] = N Value lights[x][1] = initial velocity

    while going:

        if i.poll():
            midi_events = i.read(10)

            #For testing MIDI input
            #if midi_events[0][0][0] != 248:
                #print (midi_events[0][0][0])
		
	    if midi_events[0][0][0] == 144:  #Key pressed
		
	        key = midi_events[0][0][1] #Set the kay value (different range for different devices)

                L = stack.pop() #Assign a light number from the stack, and set the associated light in active to it
		active[key] = L 

		velocity = midi_events[0][0][2]  #Set the velocity, and store it in the lights multiarray 
		lights[L][1] = velocity  
		
                N = ((key % 12) * 63.75) #Set the pre-bend N value based on what note is played, and store it
                lights[L][0] = N

                
                N = N + bend #Add bend if already set
                
                
                #The color of the light is determined by an N value between 0-764, if higher or lower, convert to within the acceptable range
                if (N < 0):
                  N = 765 + N
                elif (N > 764):
                  N = N - 765

               

                #Assign the appropriate color based on the N value, based on the following general guiding idea:
                #If between 0-255, the closer to 0 the more red, the closer to 255 the more blue, everything in between some combination.
                #If between 255-510, 255 max blue, 510 max green, everything in between, and 510-764(765 = 0), 510 green, and 764/0 red.
                #Lastly, actual light values also consider the velocity at which they are played, if max velocity 127, then full brightness, ect...

                if ((N >= 0) and (N < 255)):

                  values[((L*3)-2)] = int(((255 - N) / 127) * velocity)
		  #values[((L*3)-1)] = 0
		  values[(L*3)] = int((N / 127) * velocity)

                  dmxSend() #Send out the new DMX information

                elif ((N >= 255) and (N < 510)):
                  N = (N - 255)

                  #values[((L*3)-2)] = 0
		  values[((L*3)-1)] = int((N / 127) * velocity)
		  values[(L*3)] = int(((255 - N) / 127) * velocity)

		  dmxSend()
                  
                elif ((N >= 510) and (N < 765)):
                  N = (N - 510)

                  values[((L*3)-2)] = int((N / 127) * velocity)
		  values[((L*3)-1)] = int(((255 - N) / 127) * velocity)
		  #values[(L*3)] = 0

		  dmxSend()
		
		
    	    elif midi_events[0][0][0] == 128: #Key released
		key = (midi_events[0][0][1])

		#Set all three active channels to 0, the key is released
		values[((active[key]*3)-2)] = 0
		values[((active[key]*3)-1)] = 0
		values[(active[key]*3)] = 0
		
		dmxSend()

		stack.append(active[key]) #Return the light number to the stack, and resort
		stack.sort(reverse=True)

                #Set the appropriate values back to 0
                lights[active[key]][0] = 0
                lights[active[key]][1] = 0

                active[key] = 0


	    elif midi_events[0][0][0] == 176: #Mod Wheel

              if (mod != midi_events[0][0][2]):
                mod = midi_events[0][0][2]    #If the value is new for mod, set it to the new value
              if (mod == 0):
                dmxSend() #If the mod is set back to 0, re-send dmx, as error handling
                

            elif (midi_events[0][0][0] == 248) and (mod > 0):  #248 is the tick's from the MIDI, used if mod wheel is active
              modCounter = modCounter + mod #modCounter use's the mod value to determine strobe speed

              if (modCounter > strobeSpeed) and (modCounter < (strobeSpeed + 200)): #Blackout portion of strobe
                dmxSendBlack()
                modCounter = modCounter + 200 
                
              elif (modCounter > (strobeSpeed + strobeSpeed + 200)): #Light portion of strobe
                dmxSend()
                
                modCounter = 0

            
            elif (midi_events[0][0][0] == 224):   #Pitch Wheel
              
              bend = ((midi_events[0][0][2] - 64) * SEMI_TONE) #Set the bend value

              #Update all lights that are on with their new values
              for z in range(1,(NUM_LIGHTS + 1)):
                if (lights[z][1] != 0):

                  velocity = lights[z][1] #Get the lights initial velocity
                  N = lights[z][0] + bend #Get the N value, and add the new bend

                  #Slightly modified version of setting a lights color (described above),
                  #Used to update all active lights according to the pitch wheel changes
                  if (N < 0):
                    N = 765 + N
                  elif (N > 764):
                    N = N - 765

                  if ((N >= 0) and (N < 255)):

                    values[((z*3)-2)] = int(((255 - N) / 127) * velocity)
                    values[((z*3)-1)] = 0
                    values[(z*3)] = int((N / 127) * velocity)

                    dmxSend()

                  elif ((N >= 255) and (N < 510)):
                    N = (N - 255)

                    values[((z*3)-2)] = 0
                    values[((z*3)-1)] = int((N / 127) * velocity)
                    values[(z*3)] = int(((255 - N) / 127) * velocity)

                    dmxSend()
                    
                  elif ((N >= 510) and (N < 765)):
                    N = (N - 510)

                    values[((z*3)-2)] = int((N / 127) * velocity)
                    values[((z*3)-1)] = int(((255 - N) / 127) * velocity)
                    values[(z*3)] = 0

                    dmxSend()

		
    del i
    pygame.midi.quit()
                


def main():
  
    print_device_info()
    device_id = int(input("Enter the device ID to use: "))
    input_main(device_id)
    input_main(3)

main()

