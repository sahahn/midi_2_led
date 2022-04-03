
from __future__ import print_function
import pygame
import pygame.midi
from pygame.locals import *
import sys
import os
from ola.ClientWrapper import ClientWrapper
import array
import random


c = open('configs/1.txt','r')
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
FADE_OUT = int(config[28])
FADE_OUT_SPEED = int(config[31])
FADE_OUT_RATE = int(config[34])
FADE_IN = int(config[37])
FADE_IN_DROP = float(config[40])
FADE_IN_SPEED = int(config[43])
FADE_IN_RATE = int(config[46])
device_id = int(config[49])
CHAOS = int(config[52])
MOD = int(config[55])

STROBE_SPEED = 200 #Value used to determine strobe speed w/ the mod effect, this value is a constant and chosen based on performance- no need for it to be able to change w/ config settings

CHAN = NUM_LIGHTS * 3

values=[0 for t in range(CHAN + 2)] #Array to store light values, slot 0 stays empty

CON = 1 #Value to hold which config is open
NUM_OF_CONFIGS = 8 #The numbers of configs to cycle through

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

  try:

    pygame.init()
    pygame.midi.init()

    input_id = device_id
    print ("using input_id %s" % input_id)


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

    if CHAOS == 0:
        stack.sort(reverse=True) #In this build, the stack is contantly sorted so that lights fill in a predictable way
    elif CHAOS == 1:
        random.shuffle(stack) #jumble the stack

    heap = [] #Heap used in LEFTIFY

    stickyCount = 1

    lights = [[0 for x in range(2)] for d in range(NUM_LIGHTS+2)]  #lights[x][0] = N Value lights[x][1] = initial velocity 
    light = [0 for x in range(5)]  #light[0] = latest N of pressed light[1] = velocity of latest pressed, light[2] = key, light[3] = fade out flag, light[4] = fade in flag

    fadeOut = [] #Holds a list of all the lights that need to fade out still
    fadeOutCounter = 0 #Counter used with fade out

    fadeIn = [] #Holds a list of all the lights fading in
    fadeInCounter = 0

    i = pygame.midi.Input( input_id )
    going = True
    
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
                  
                if ((DEVICE_TYPE == 1) or (CHAOS == 1)):

                  if ((SYNTH_MODE == 1) or (CHAOS == 1)):

                    if (((STICKY == 0) and (LEFTIFY == 0)) or ((CHAOS == 1) and STICKY == 0)):

                      if (len(stack) != 0): #Make sure the lights are not full
                        L = stack.pop() #Assign a light number from the stack, and set the associated light in active to it

                        if ((SYNTH_MODE == 2) or (DEVICE_TYPE == 2)):#Ensure only one light is on
                          if FADE_OUT == 0:
                            for z in range(1,(NUM_LIGHTS + 1)):
                              if (lights[z][1] != 0):
                                
                                lights[z][1] = 0 
                                lights[z][0] = 0

                                assignColor(0,0,z)

                                stack.append(z) #Return the light number to the stack, and resort

                                if (CHAOS == 0):
                                    stack.sort(reverse=True)
         
                                elif (CHAOS == 1):
                                    random.shuffle(stack) #jumble the stack

                          elif FADE_OUT == 1:
                            for z in range(1,(NUM_LIGHTS + 1)):
                              if (lights[z][1] != 0):

                                fadeOut.append(z) #Set a value to be faded
                                stack.append(z) #Return the light number to the stack, and resort

                                if (CHAOS == 0):
                                    stack.sort(reverse=True)
         
                                elif (CHAOS == 1):
                                    random.shuffle(stack) #jumble the stack

                    elif ((STICKY == 1) and (LEFTIFY == 0) and (CHAOS == 1)):  #For compaitability with chaos and sticky mode
                      L = random.randint(1,NUM_LIGHTS)
                      

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
                    
                    lights[L][0] = N
                    lights[L][1] = velocity #Set the velocity, and store it in the lights multiarray

                    if (L in fadeOut):
                        fadeOut.remove(L) #Take the item off the list if this light is being re-assigned

                    if (FADE_IN == 1):  #If fade in set
                        fadeIn.append(L) #Append the light number to the fade in list
                        lights[L][1] = int(lights[L][1] * FADE_IN_DROP) #Change the initial velocity

                  elif SYNTH_MODE == 2:
            
                    light[0] = N
                    light[1] = velocity
                    light[2] = key
                    light[3] = 0 #Set fade out flag to 0

                    if (FADE_IN == 1):
                        light[4] = 1 #Set the fade in flag
                        light[1] = int(light[1] * FADE_IN_DROP) #Change the initial velocity

                  N = N + bend #Add bend if already set

                elif DEVICE_TYPE == 2:

                    light[0] = N
                    light[1] = velocity
                    light[3] = 0 #Set the fade out flag to 0

                assignColor(N,velocity,L)

                dmxSend()

            elif midi_events[0][0][0] == keyRelease: #Key/hit released
  
		key = (midi_events[0][0][1])

                if STICKY == 0:

                  if ((DEVICE_TYPE == 1) or (CHAOS == 1)):
                    if ((SYNTH_MODE == 1) or (CHAOS == 1)):
                      if ((LEFTIFY == 0) or (CHAOS == 1)):

                          if FADE_IN == 1:

                              if (active[key] in fadeIn):
                                fadeIn.remove(active[key]) #Remove the key from being faded in

                          if FADE_OUT == 0:
                          
                            #Set all three active channels to 0, the key is released
                            values[((active[key]*3)-2)] = 0
                            values[((active[key]*3)-1)] = 0
                            values[(active[key]*3)] = 0

                            stack.append(active[key]) #Return the light number to the stack, and resort

                            if (CHAOS == 0):
                                stack.sort(reverse=True)

                            elif (CHAOS == 1):
                                random.shuffle(stack) #jumble the stack
                            
                            #Set the appropriate values back to 0
                            lights[active[key]][0] = 0
                            lights[active[key]][1] = 0

                            active[key] = 0

                          elif FADE_OUT == 1:

                            fadeOut.append(active[key]) #Set a value to be faded
                            stack.append(active[key]) #Return the light number to the stack, and resort

                            if (CHAOS == 0):
                                stack.sort(reverse=True)
       
                            elif (CHAOS == 1):
                                random.shuffle(stack) #jumble the stack

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

                      if FADE_IN == 1:

                          if (light[2] == key):
                            light[4] = 0 #Set the fade in flag off

                      if FADE_OUT == 0:

                          if (light[2] == key):   #Only go to blackout if the note being released is the latest played
                              for h in range(1,(CHAN + 1),3):
                                  values[h] = 0
                                  values[h+1] = 0
                                  values[h+2] = 0

                              light[0] = 0
                              light[1] = 0
                              light[2] = 0

                      elif FADE_OUT == 1:

                          light[3] = 1 #Fade out flag on

                  elif DEVICE_TYPE == 2:

                    if FADE_OUT == 0:
                        for h in range(1,(CHAN + 1),3):
                           values[h] = 0
                           values[h+1] = 0
                           values[h+2] = 0

                        light[0] = 0
                        light[1] = 0

                    elif FADE_OUT == 1:

                        light[3] = 1
                        
                    
                  dmxSend()

            if FADE_OUT == 1:

                if ((midi_events[0][0][0] == 248) and ((light[3] == 1) or (len(fadeOut) > 0))):
                  

                  fadeOutCounter = fadeOutCounter + 1

                  #Fade out logic for chord mode
                  if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):
                      
                      if (fadeOutCounter > FADE_OUT_SPEED):

                          for b in fadeOut: #For each light w/ a fade out
                              lights[b][1] = (lights[b][1] - FADE_OUT_RATE)

                              if (lights[b][1] <= 0): #If the fade is done, remove the light from the list
                                  fadeOut.remove(b)

                                  lights[b][0] = 0  #Reset the lights values
                                  lights[b][1] = 0

                              assignColor((lights[b][0]),(lights[b][1]),b)
                              dmxSend()

                              fadeOutCounter = 0

                  #Fade out logic for single key and octa pad
                  elif (((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)) and (light[4] == 0)):

                      if (fadeOutCounter > FADE_OUT_SPEED):

                          light[1] = (light[1] - FADE_OUT_RATE)

                          if (light[1] <= 0): #If the fade is done... set the flag off
                              light[3] = 0
                              light[2] = 0
                              light[1] = 0
                              light[0] = 0
                              
                              
                          assignColor(light[0],light[1],L)
                          dmxSend()

                          fadeOutCounter = 0

            if DEVICE_TYPE == 1:

              if ((midi_events[0][0][0] == modWheel) and (MOD == 1)): #Mod Wheel

                if (mod != midi_events[0][0][2]):
                  mod = midi_events[0][0][2]    #If the value is new for mod, set it to the new value
                if (mod == 0):
                  dmxSend() #If the mod is set back to 0, re-send dmx, as error handling
                

              elif ((midi_events[0][0][0] == 248) and (mod > 0) and (MOD == 1)):  #248 is the tick's from the MIDI, used if mod wheel is active
                modCounter = modCounter + mod #modCounter use's the mod value to determine strobe speed

                if (modCounter > STROBE_SPEED) and (modCounter < (STROBE_SPEED + 200)): #Blackout portion of strobe
                  dmxSendBlack()
                  modCounter = modCounter + 200 
                  
                elif (modCounter > (STROBE_SPEED + STROBE_SPEED + 200)): #Light portion of strobe
                  dmxSend()
                  modCounter = 0


##              elif ((midi_events[0][0][0] == 248) and (mod > 0) and (MOD == 2) and ((SYNTH_MODE == 1) or (CHAOS == 1))):
##                modCounter = modCounter + mod
##
##                if (modCounter > STROBE_SPEED) and (modCounter < (STROBE_SPEED + 200)):
##
##                  for z in range(1,(NUM_LIGHTS + 1)):
##                    if (lights[z][1] != 0):
##
##                      assignColor((lights[z][0] + mod),lights[z][1],z)
##
##
##                  modCounter = modCounter + 200
##                  dmxSend()
##
##                elif (modCounter > (STROBE_SPEED + STROBE_SPEED + 200)):
##
##                  for z in range(1,(NUM_LIGHTS + 1)):
##                    if (lights[z][1] != 0):
##
##                      assignColor((lights[z][0]),lights[z][1],z)
##
##                  modCounter = 0
##                  dmxSend()
                  
              elif (midi_events[0][0][0] == pitchWheel):   #Pitch Wheel

                bend = ((midi_events[0][0][2] - 64) * SEMI_TONE) #Set the bend value

                if SYNTH_MODE == 1:

                  #Update all lights that are on with there new values
                  for z in range(1,(NUM_LIGHTS + 1)):
                    if (lights[z][1] != 0):

                      velocity = lights[z][1] #Get the lights initial velocity
                      N = lights[z][0] + bend #Get the N value, and add the new bend

                      assignColor(N,velocity,z)  #z was L if for some reason this breaks

                elif SYNTH_MODE == 2:

                  #Update the lights with new values
                  if light[2] != 0:
                      velocity = light[1]
                      N = light[0] + bend

                      assignColor(N,velocity,L)
    

                dmxSend() #Send out the new DMX information

              
              if FADE_IN == 1:
                  
                  if ((midi_events[0][0][0] == 248) and ((light[4] == 1) or (len(fadeIn) > 0))):  #If fade in flag set

                    fadeInCounter = fadeInCounter + 1

                    #Fade in logic for chord mode
                    if ((SYNTH_MODE == 1) or (CHAOS == 1)):
                        
                        if (fadeInCounter > FADE_IN_SPEED):

                            for c in fadeIn: #For each light w/ a fade in
                                lights[c][1] = (lights[c][1] + FADE_IN_RATE)

                                if (lights[c][1] >= 127): #If the fade is done, remove the light from the list
                                    fadeIn.remove(c)

                                    lights[c][1] = 127 #Cap the fade at 127

                                assignColor((lights[c][0]),(lights[c][1]),c) #Assign the new light values 
                                dmxSend()

                                fadeInCounter = 0 #reset the counter

                    #Fade in logic for single key mode
                    elif SYNTH_MODE == 2:

                        if (fadeInCounter > FADE_IN_SPEED):

                            light[1] = (light[1] + FADE_IN_RATE)

                            if (light[1] >= 127): #If the fade is done... 
                                light[4] = 0 #Flag for fade in off
                                light[1] = 127 #Cap the fade at 127
                                
                            assignColor(light[0],light[1],L) #Note L is just a placeholder, it isn't actually used in single key mode
                            dmxSend() 

                            fadeInCounter = 0 #reset the counter
                      

  #If user presses ctrl-c
  except KeyboardInterrupt:
    pygame.midi.quit()
    changeConfig()
    mainProgram(device_id)

    
                 
def assignColor(N, velocity, L):

  N = N * 1.0
  velocity = velocity

  if COLOR_MODE == 0:

    if (N < 0):
      N = 765 + N
    elif (N > 764):
      N = N - 765


    if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):
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
          G = (N - 255)

          values[h] = 0
          values[h+1] = int((G / 127) * velocity)
          values[h+2] = int(((255 - G) / 127) * velocity)

        elif ((N >= 510) and (N < 765)):
          G = (N - 510)

          values[h] = int((G / 127) * velocity)
          values[h+1] = int(((255 - G) / 127) * velocity)
          values[h+2] = 0

        
 

  elif COLOR_MODE == 1:

    if (N < 0):
      N = 360 + N
    elif (N > 360):
      N = N - 360

    if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):

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
          G = (N - 50)

          values[h] = (2 * velocity)
          values[h+1] = int((G / 127) * velocity)
          values[h+2] = 0

        elif ((N >= 305) and (N < 360)):
          G = (N - 305)

          values[h] = int(((255 - G) / 127) * velocity)
          values[h+1] = (2 * velocity)
          values[h+2] = 0
        
  elif COLOR_MODE == 2:
    if (N < 0):
      N = 560 + N
    elif (N > 560):
      N = N - 560

    if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):

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
          G = (N - 255)

          values[h] = 0
          values[h+1] = int((G / 127) * velocity)
          values[h+2] = (2 * velocity)

        elif ((N >= 510) and (N < 560)):
          G = (N - 510)

          values[h] = 0
          values[h+1] = (2 * velocity)
          values[h+2] = int(((255 - G) / 127) * velocity)

def changeConfig():

  global CON

  if CON == NUM_OF_CONFIGS:
    CON = 1
  else:
    CON = CON + 1

  filename = ("configs/" + str(CON) +".txt")
    
  c = open(filename,'r')
  config = c.readlines()
  config = [x.strip() for x in config]

  c.close()

  global DEVICE_TYPE
  global MIDI_CHANNEL
  global NUM_LIGHTS
  global COLOR_MODE
  global STICKY
  global SYNTH_MODE
  global COLOR_RANGE
  global SEMI_TONE
  global LEFTIFY
  global FADE_OUT
  global FADE_OUT_SPEED
  global FADE_OUT_RATE
  global FADE_IN
  global FADE_IN_DROP
  global FADE_IN_SPEED
  global FADE_IN_RATE
  global CHAN 
  global values
  global device_id
  global CHAOS
  global MOD

  DEVICE_TYPE = int(config[1])
  MIDI_CHANNEL = int(config[4])
  NUM_LIGHTS = int(config[7])
  COLOR_MODE = int(config[10])
  STICKY = int(config[13])
  SYNTH_MODE = int(config[16])
  COLOR_RANGE = int(config[19])
  SEMI_TONE = int(config[22])
  LEFTIFY = int(config[25])
  FADE_OUT = int(config[28])
  FADE_OUT_SPEED = int(config[31])
  FADE_OUT_RATE = int(config[34])
  FADE_IN = int(config[37])
  FADE_IN_DROP = float(config[40])
  FADE_IN_SPEED = int(config[43])
  FADE_IN_RATE = int(config[46])
  device_id = int(config[49])
  CHAOS = int(config[52])
  MOD = int(config[55])

  CHAN = NUM_LIGHTS * 3 
  values=[0 for t in range(CHAN + 2)] #Array to store light values, slot 0 stays empty
                
def main():

      #global device_id
      #print_device_info()
      #device_id = int(input("Enter the device ID to use: "))
      mainProgram(device_id)

main()
