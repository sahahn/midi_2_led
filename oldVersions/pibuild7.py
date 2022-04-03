from __future__ import print_function
import pygame
import pygame.midi
from pygame.locals import *
import sys
import os
from ola.ClientWrapper import ClientWrapper
import array
import heapq


c = open('pi_config.txt','r')
config = c.readlines()
config = [x.strip() for x in config]

c.close()

#Default Values
DEVICE_TYPE = int(config[1])
MIDI_CHANNEL = int(config[4])
NUM_LIGHTS = int(config[7])
COLOR_MODE = int(config[10])
STICKY = int(config[13])
SYNTH_MODE = int(config[16])
COLOR_RANGE = int(config[19])
SEMI_TONE = int(config[22])
LEFTIFY = int(config[25])

STROBE_SPEED = 200 #Value used to determine strobe speed w/ the mod effect
CHAN = NUM_LIGHTS * 3 

values=[0 for t in range(CHAN + 2)] #Array to store light values, slot 0 stays empty


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
        

def mainProgram(device_id):

    pygame.init()
    pygame.midi.init()

    input_id = device_id
    print ("using input_id %s" % input_id)

    i = pygame.midi.Input( input_id )

    going = True

    keyPress = 144 + MIDI_CHANNEL
    keyRelease = 128 + MIDI_CHANNEL

    N = 0 #Initialize light value
    L = 0 #Intialize light number

    modWheel = 176 + MIDI_CHANNEL
    pitchWheel = 224 + MIDI_CHANNEL
    
    mod = 0 #Initialize the mod value
    modCounter = 0 #Initialize value to be used w/ the modwheel
    bend = 0 #Initialize the bend value
  
    active=[0 for v in range(121)] #Create an empty array associated with key values, to keep track of keys being held down

    stack = range(1,(NUM_LIGHTS+1)) #Create a stack (list) for assigning new lights
    stack.sort(reverse=True) #In this build, the stack is contantly sorted so that lights fill in a predictable way

    heap = [] #Heap used in LEFTIFY

    stickyCount = 1

    lights = [[0 for x in range(2)] for d in range(NUM_LIGHTS+2)]  #lights[x][0] = N Value lights[x][1] = initial velocity
    light = [0 for x in range(3)]  #light[0] = latest N of pressed light[1] = velocity of latest pressed, light[2] = key

    while going:

        if i.poll():
            midi_events = i.read(10)

            #For testing MIDI input
            #if midi_events[0][0][0] != 248:
                #print (midi_events[0][0][0])

            if midi_events[0][0][0] == keyPress:  #Key pressed


		key = midi_events[0][0][1] #Set the key value (different range for different devices)
                velocity = midi_events[0][0][2]


                if COLOR_MODE == 0:
                  N = ((key % COLOR_RANGE) * (765 / COLOR_RANGE)) #Set the pre-bend N value based on what note is played, and store it

                elif COLOR_MODE == 1:
                  N = ((key % COLOR_RANGE) * (360 / COLOR_RANGE)) 

                elif COLOR_MODE == 2:
                  N = ((key % COLOR_RANGE) * (560 / COLOR_RANGE))
                  
                if DEVICE_TYPE == 1:

                  if SYNTH_MODE == 1:

                    if ((STICKY == 0) and (LEFTIFY == 0)):
                      L = stack.pop() #Assign a light number from the stack, and set the associated light in active to it
          
                    elif ((STICKY == 1) and (LEFTIFY == 0)): #If sticky is on, assign lights sequentially, returning to 1 when the max is hit
                      L = stickyCount

                      if stickyCount == NUM_LIGHTS:
                        stickyCount = 1
                      else:
                        stickyCount = stickyCount + 1

                    elif (LEFTIFY == 1):

                      heap.append(key)
                      heap.sort()

                      L = (heap.index(key) + 1)

                      #Starting with the new end array spot, ending at the item just entered, update the lights values in order, and assign new colors
                      for r in range(len(heap),L,-1): 

                        lights[r][0] = lights[r-1][0]
                        lights[r][1] = lights[r-1][1]

                        assignColor(lights[r][0],lights[r][1],r)

                    active[key] = L

                    lights[L][1] = velocity #Set the velocity, and store it in the lights multiarray 
                    lights[L][0] = N

                  elif SYNTH_MODE == 2:

                    light[2] = key
                    light[1] = velocity
                    light[0] = N
                    

                  N = N + bend #Add bend if already set

                assignColor(N,velocity,L)

                dmxSend()

            elif midi_events[0][0][0] == keyRelease: #Key/hit released
		key = (midi_events[0][0][1])

                if STICKY == 0:

                  if DEVICE_TYPE == 1:
                    if SYNTH_MODE == 1:
                      if LEFTIFY == 0:

                        #Set all three active channels to 0, the key is released
                        values[((active[key]*3)-2)] = 0
                        values[((active[key]*3)-1)] = 0
                        values[(active[key]*3)] = 0

                        stack.append(active[key]) #Return the light number to the stack, and resort
                        stack.sort(reverse=True)

                        #Set the appropriate values back to 0
                        lights[active[key]][0] = 0
                        lights[active[key]][1] = 0

                        active[key] = 0

                      elif LEFTIFY == 1:

                        hole = heap.index(key)

                        del(heap[hole])
                        heap.sort()
                        

                        for x in range((hole+1),(len(heap)+1)):

                          lights[x][0] = lights[x+1][0]
                          lights[x][1] = lights[x+1][1]

                          velocity = lights[x][1] 
                          N = lights[x][0]

                          assignColor(N,velocity,x)

                        lights[(len(heap)+1)][0] = 0
                        lights[(len(heap)+1)][1] = 0

                        values[((len(heap)+1) * 3) -2] = 0
                        values[((len(heap)+1) * 3) -1] = 0
                        values[(len(heap)+1) * 3] = 0

                        active[key] = 0

                    elif SYNTH_MODE == 2:

                      if (light[2] == key):   #Only go to blackout if the note being released is the latest played
                          for h in range(1,(CHAN + 1),3):
                              values[h] = 0
                              values[h+1] = 0
                              values[h+2] = 0

                          light[0] = 0
                          light[1] = 0
                          light[2] = 0

                  elif DEVICE_TYPE == 2:
                    for h in range(1,(CHAN + 1),3):
                       values[h] = 0
                       values[h+1] = 0
                       values[h+2] = 0
                      
                  dmxSend()

            if DEVICE_TYPE == 1:

              if midi_events[0][0][0] == modWheel: #Mod Wheel

                if (mod != midi_events[0][0][2]):
                  mod = midi_events[0][0][2]    #If the value is new for mod, set it to the new value
                if (mod == 0):
                  dmxSend() #If the mod is set back to 0, re-send dmx, as error handling
                

              elif (midi_events[0][0][0] == 248) and (mod > 0):  #248 is the tick's from the MIDI, used if mod wheel is active
                modCounter = modCounter + mod #modCounter use's the mod value to determine strobe speed

                if (modCounter > STROBE_SPEED) and (modCounter < (STROBE_SPEED + 200)): #Blackout portion of strobe
                  dmxSendBlack()
                  modCounter = modCounter + 200 
                  
                elif (modCounter > (STROBE_SPEED + STROBE_SPEED + 200)): #Light portion of strobe
                  dmxSend()
                  modCounter = 0


              elif (midi_events[0][0][0] == pitchWheel):   #Pitch Wheel

                bend = ((midi_events[0][0][2] - 64) * SEMI_TONE) #Set the bend value

                if SYNTH_MODE == 1:

                  #Update all lights that are on with there new values
                  for z in range(1,(NUM_LIGHTS + 1)):
                    if (lights[z][1] != 0):

                      velocity = lights[z][1] #Get the lights initial velocity
                      N = lights[z][0] + bend #Get the N value, and add the new bend

                      assignColor(N,velocity,L)

                elif SYNTH_MODE == 2:

                  #Update the lights with new values
                  if light[2] != 0:
                      velocity = light[1]
                      N = light[0] + bend

                      assignColor(N,velocity,L)
    

                dmxSend() #Send out the new DMX information
                  

def assignColor(N, velocity, L):

  N = N * 1.0
  velocity = velocity

  if COLOR_MODE == 0:

    if (N < 0):
      N = 765 + N
    elif (N > 764):
      N = N - 765


    if ((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)):

      if ((N >= 0) and (N < 255)):

        values[((L*3)-2)] = int(((255 - N) / 127) * velocity)
        values[((L*3)-1)] = 0
        values[(L*3)] = int((N / 127) * velocity)

      elif ((N >= 255) and (N < 510)):
        N = (N - 255)

        values[((L*3)-2)] = 0
        values[((L*3)-1)] = int((N / 127) * velocity)
        values[(L*3)] = int(((255 - N) / 127) * velocity)

      elif ((N >= 510) and (N < 765)):
        N = (N - 510)

        values[((L*3)-2)] = int((N / 127) * velocity)
        values[((L*3)-1)] = int(((255 - N) / 127) * velocity)
        values[(L*3)] = 0

    #For second synth setting and Octo-Pad
    elif ((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)):


      for h in range(1,(CHAN + 1),3):
  
        if ((N >= 0) and (N < 255)):

          values[h] = int(((255 - N) / 127) * velocity)
          values[h+1] = 0
          values[h+2] = int((N / 127) * velocity)

        elif ((N >= 255) and (N < 510)):
          N = (N - 255)

          values[h] = 0
          values[h+1] = int((N / 127) * velocity)
          values[h+2] = int(((255 - N) / 127) * velocity)

        elif ((N >= 510) and (N < 765)):
          N = (N - 510)

          values[h] = int((N / 127) * velocity)
          values[h+1] = int(((255 - N) / 127) * velocity)
          values[h+2] = 0

  elif COLOR_MODE == 1:

    if (N < 0):
      N = 360 + N
    elif (N > 360):
      N = N - 360

    if ((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)):

      if ((N >= 0) and (N < 50)):

        values[((L*3)-2)] = (2 * velocity)
        values[((L*3)-1)] = 0
        values[(L*3)] = int(((50-N) / 127) * velocity)

      elif ((N >= 50) and (N < 305)):
        N = (N - 50)

        values[((L*3)-2)] = (2 * velocity)
        values[((L*3)-1)] = int((N / 127) * velocity)
        values[(L*3)] = 0

      elif ((N >= 305) and (N < 360)):
        N = (N - 305)

        values[((L*3)-2)] = int(((255 - N) / 127) * velocity)
        values[((L*3)-1)] = (2 * velocity)
        values[(L*3)] = 0

    #For second synth setting and Octo-Pad
    elif ((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)):

      for h in range(1,(CHAN + 1),3):
    
        if ((N >= 0) and (N < 50)):

          values[h] = (2 * velocity)
          values[h+1] = 0
          values[h+2] = int(((50-N) / 127) * velocity)

        elif ((N >= 50) and (N < 305)):
          N = (N - 50)

          values[h] = (2 * velocity)
          values[h+1] = int((N / 127) * velocity)
          values[h+2] = 0

        elif ((N >= 305) and (N < 360)):
          N = (N - 305)

          values[h] = int(((255 - N) / 127) * velocity)
          values[h+1] = (2 * velocity)
          values[h+2] = 0
        
  elif COLOR_MODE == 2:
    if (N < 0):
      N = 560 + N
    elif (N > 360):
      N = N - 560

    if ((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)):

      if ((N >= 0) and (N < 255)):

        values[((L*3)-2)] = int(((255-N) / 127) * velocity)
        values[((L*3)-1)] = 0
        values[(L*3)] = (2 * velocity)

      elif ((N >= 255) and (N < 510)):
        N = (N - 255)

        values[((L*3)-2)] = 0
        values[((L*3)-1)] = int((N / 127) * velocity)
        values[(L*3)] = (2 * velocity)

      elif ((N >= 510) and (N < 560)):
        N = (N - 510)

        values[((L*3)-2)] = 0
        values[((L*3)-1)] = (2 * velocity)
        values[(L*3)] = int(((255 - N) / 127) * velocity)

    #For second synth setting and Octo-Pad
    elif ((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)):

      for h in range(1,(CHAN + 1),3):
    
        if ((N >= 0) and (N < 255)):

          values[h] = int(((255-N) / 127) * velocity)
          values[h+1] = 0
          values[h+2] = (2 * velocity)

        elif ((N >= 255) and (N < 510)):
          N = (N - 255)

          values[h] = 0
          values[h+1] = int((N / 127) * velocity)
          values[h+2] = (2 * velocity)

        elif ((N >= 510) and (N < 560)):
          N = (N - 510)

          values[h] = 0
          values[h+1] = (2 * velocity)
          values[h+2] = int(((255 - N) / 127) * velocity)

		
    del i
    pygame.midi.quit()
                
def main():

      print_device_info()
      device_id = int(input("Enter the device ID to use: "))
      mainProgram(device_id)

main()
