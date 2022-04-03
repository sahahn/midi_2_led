#pibuild10.py, the latest build of the Snake Box main program
#By Sage Hahn, designed for python2.7
#Convert incoming MIDI siginal to DMX
from __future__ import print_function
import pygame
import pygame.midi
from pygame.locals import *
import sys
import os
from ola.ClientWrapper import ClientWrapper
import array
import random

#Use default config package if no system arguments specified
if (len(sys.argv) == 1):

  filen = 'configs/default/1.txt'

#If a package name specified, used that config package
else:
  filen = 'configs/' + sys.argv[1] + '/1.txt'

#Open the first config file, and read in the values
c = open(filen,'r') 
config = c.readlines()
config = [x.strip() for x in config]

c.close()

#Default Values read from config
NAME = config[0]                 #Config name
DEVICE_TYPE = int(config[2])     #Type of device, 1 Synth, 2 Octapad
NUM_LIGHTS = int(config[5])      #Number of lights
COLOR_MODE = int(config[8])      #Color Mode, 0 Full Spectrum, 1 Hot, 2 Cold, 3 Fuller Spectrum, 4 Red Based, 5 Green Based, 6 Blue Based
COLOR_RANGE = int(config[11])    #Parameter to assign color
device_id = int(config[14])      #Id used with pygamemidi of input device
MOD = int(config[17])            #Mod Mode, either 0 off, 1 strobe, 2 color switch strobe, 3 light shift
SEMI_TONE = int(config[20])      #Pitch Wheel parameter
SYNTH_MODE = int(config[23])     #Synth Mode, either 1 chords, or 2 single note
LEFTIFY = int(config[26])        #Leftify mode, either on or off
FADE_OUT = int(config[29])       #Fade out mode, either on or off
FADE_OUT_SPEED = int(config[32]) #Fade out parameter
FADE_OUT_RATE = int(config[35])  #Fade out parameter
FADE_IN = int(config[38])        #Fade in mode, either on or off
FADE_IN_DROP = int(config[41])   #Fade in parameter
FADE_IN_SPEED = int(config[44])  #Fade in parameter
FADE_IN_RATE = int(config[47])   #Fade in parameter
CHAOS = int(config[50])          #Chaos mode, either on or off
STICKY = int(config[53])         #Sticky mode, either on or off
DOUBLE = int(config[56])         #Double mode, either on or off
NUM_OF_CONFIGS = int(config[59]) #The numbers of configs to cycle through
CONFIG_FOLDER = config[62]       #Name of the config folder

STROBE_SPEED = 200               #Value used to determine strobe speed w/ the mod effect, this value is a constant and was chosen based on performance
CHAN = NUM_LIGHTS * 3            #3 Channels for each light
values=[0 for t in range(CHAN + 2)] #Array to store light values,note slot 0 stays empty
CON = 1                          #Value to hold which config is open

FADE_IN_DROP = FADE_IN_DROP * .1

#Set up wrapper information for OLA
global wrapper
wrapper = ClientWrapper()
client = wrapper.Client()

#Used for error handling with sending DMX, code by Simon Newton
def DmxSent(status):
  if status.Succeeded():
    r = 7  
  else:
    print('Error: %s' % status.message, file=sys.stderr)

  global wrapper
  if wrapper:
    wrapper.Stop()

#Used to send out DMX information to OLA, code based off example from Simon Newton
def dmxSend():
  universe = 1
  data = array.array('B')
  for x in range(1,(CHAN+1)):
    data.append(values[x])
  
  client.SendDmx(universe, data, DmxSent)
  wrapper.Run()

#Used to send a black out, based off code by Simon Newton
def dmxSendBlack():
  universe = 1
  data = array.array('B')
  for x in range(1,(CHAN+1)):
    data.append(0)
  
  client.SendDmx(universe, data, DmxSent)
  wrapper.Run()
  
#Used to print avaliable ports for MIDI input
def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()

#Prints the input and outut ports that pygamemidi can work with
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
        
#The main program
def mainProgram(device_id):

  try:

    #Note: All the variables used in every mode are initialized, for lack of hassle, and for ease of switching modes
    pygame.init()
    pygame.midi.init()

    print ("Using: " + NAME) #Print which config is being used


    keyPress = 144 #Default value for key press
    keyRelease = 128 #Default value for key release

    N = 0 #Initialize light value
    L = 0 #Intialize light number

    modWheel = 176 #Default value for mod wheel
    pitchWheel = 224 #Default value for pitch wheel
    
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

    dLight = 0 #Variable used with DOUBLE for holding the alternate L value

    mod3Flag = 0#Flag used for single note mod 3 mode

    midiInput = pygame.midi.Input(device_id) #Set midiInput to the device_id
    going = True
    
    while going:

        if midiInput.poll(): #Call the pygamemidi poll function
            midi_events = midiInput.read(10) 

            #For testing MIDI input
            #if midi_events[0][0][0] != 248:
                #print (midi_events[0][0][0])

            if ((midi_events[0][0][0] >= keyPress) and (midi_events[0][0][0] <= (keyPress + 10))):  #Key pressed

		key = midi_events[0][0][1] #Set the key value (different range for different devices)
                velocity = midi_events[0][0][2]

                #Depending on the color mode, set the pre-bend N value based on what note is played
                if COLOR_MODE == 0:
                  N = ((key % COLOR_RANGE) * (765 / COLOR_RANGE)) 

                elif COLOR_MODE == 1:
                  N = ((key % COLOR_RANGE) * (360 / COLOR_RANGE)) 

                elif COLOR_MODE == 2:
                  N = ((key % COLOR_RANGE) * (560 / COLOR_RANGE))

                elif COLOR_MODE == 3:
                  N = ((key % COLOR_RANGE) * (1530 / COLOR_RANGE))

                elif ((COLOR_MODE == 4) or (COLOR_MODE == 5) or (COLOR_MODE == 6)):
                  N = ((key % COLOR_RANGE) * (510 / COLOR_RANGE)) 
                  

                if ((DEVICE_TYPE == 1) or (CHAOS == 1)): #If Synth/Chaos 
                  if ((SYNTH_MODE == 1) or (CHAOS == 1)): #If Chord/Chaos
                    if (((STICKY == 0) and (LEFTIFY == 0)) or ((CHAOS == 1) and STICKY == 0)): #If Sticky and Leftify off

                      if (DOUBLE == 1): #If double mode is on, only use half the stack
                        if ((len(stack) > (NUM_LIGHTS / 2))):
                          L = stack.pop()
                        
                      elif (len(stack) != 0): #Make sure all lights are not currently assigned
                        L = stack.pop() #Assign a light number from the stack

                        if ((SYNTH_MODE == 2) or (DEVICE_TYPE == 2)): #If single note or octapad mode
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

                          elif FADE_OUT == 1: #If Fade out mode,
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

                      if DOUBLE == 0:

                        if stickyCount == NUM_LIGHTS:
                          stickyCount = 1
                        else:
                          stickyCount = stickyCount + 1

                      elif DOUBLE == 1: #If double mode is on

                        if stickyCount == (NUM_LIGHTS / 2):
                          stickyCount = 1
                        else:
                          stickyCount = stickyCount + 1

                    elif (LEFTIFY == 1):

                      
                      if (len(heap) < NUM_LIGHTS): #Error handling so too many lights arn't assigned
		        
			heap.append(key)
                        heap.sort()

                        L = (heap.index(key) + 1) #Assign light number based on 

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
                        lights[L][1] = 1 #Change the initial velocity

                    if DOUBLE == 1: #If double mode is set, add an additional light at the other end
                      dLight = (NUM_LIGHTS - L) + 1 #The doubled light is set as the comprable light from the right

                      lights[dLight][0] = N
                      lights[dLight][1] = velocity

                      if (L in fadeOut):
                          fadeOut.remove(dLight) 

                      if (FADE_IN == 1):  
                          fadeIn.append(dLight)

                      assignColor(N,velocity,dLight)

                  elif SYNTH_MODE == 2:
            
                    light[0] = N
                    light[1] = velocity
                    light[2] = key
                    light[3] = 0 #Set fade out flag to 0

                    if (FADE_IN == 1):
                        light[4] = 1 #Set the fade in flag
                        light[1] = 1 #Change the initial velocity

                  N = N + bend #Add bend if already set

                elif DEVICE_TYPE == 2:

                    light[0] = N
                    light[1] = velocity
                    light[3] = 0 #Set the fade out flag to 0

                assignColor(N,velocity,L) #Assign the light based on the provided parameters

                dmxSend() #Send out the DMX command w/ the current stored values

            elif ((midi_events[0][0][0] >= keyRelease) and (midi_events[0][0][0] <= (keyRelease + 10))): #Key/hit released
  
		key = (midi_events[0][0][1])

                if STICKY == 0:

                  if ((DEVICE_TYPE == 1) or (CHAOS == 1)):    #If Synth 
                    if ((SYNTH_MODE == 1) or (CHAOS == 1)):   #If Chord Mode/Chaos
                      if ((LEFTIFY == 0) or (CHAOS == 1)):    #If Leftify off...

                          dLight = (NUM_LIGHTS - active[key])+1    #Value used with Double Mode

                          if FADE_IN == 1:
                            
                              if (active[key] in fadeIn):
                                fadeIn.remove(active[key]) #Remove the key from being faded in

                              if DOUBLE == 1:
                                if (dLight in fadeIn):
                                  fadeIn.remove(active[key]) #Remove the key from being faded in
                            
                          if FADE_OUT == 0:
                          
                            #Set all three active channels to 0, the key is released
                            values[((active[key]*3)-2)] = 0
                            values[((active[key]*3)-1)] = 0
                            values[(active[key]*3)] = 0

                            stack.append(active[key]) #Return the light number to the stack, and resort

                            if (DOUBLE == 1):  #If double mode on
                              values[((dLight*3)-2)] = 0
                              values[((dLight*3)-1)] = 0
                              values[(dLight*3)] = 0

                              lights[dLight][0] = 0
                              lights[dLight][1] = 0  #reset values
                  
                            if (CHAOS == 0):
                                stack.sort(reverse=True)

                            elif (CHAOS == 1):
                                random.shuffle(stack) #jumble the stack
                            
                            #Set the appropriate values back to 0
                            lights[active[key]][0] = 0
                            lights[active[key]][1] = 0

                          elif FADE_OUT == 1:

                            fadeOut.append(active[key]) #Set a value to be faded
                            stack.append(active[key]) #Return the light number to the stack, and resort

                            if (DOUBLE == 1):
                              fadeOut.append(dLight) #Set the double value to be faded

                            if (CHAOS == 0):
                                stack.sort(reverse=True)
       
                            elif (CHAOS == 1):
                                random.shuffle(stack) #jumble the stack

                          active[key] = 0 #Reset the active key

                      elif LEFTIFY == 1: #Key release logic for Leftify Mode

                        hole = heap.index(key)

                        del(heap[hole]) #Get rid of light from the heap
                        heap.sort()

                        for x in range((hole+1),(len(heap)+1)):  #Re-assign all lights that need to change, based on the light removed... if any

                          lights[x][0] = lights[x+1][0]
                          lights[x][1] = lights[x+1][1]

                          velocity = lights[x][1] 
                          N = lights[x][0]

                          assignColor(N,velocity,x)

                        lights[(len(heap)+1)][0] = 0	#Reset the lights values
                        lights[(len(heap)+1)][1] = 0

                        values[((len(heap)+1) * 3) -2] = 0	#Set the light to blackout
                        values[((len(heap)+1) * 3) -1] = 0
                        values[(len(heap)+1) * 3] = 0

                        active[key] = 0

                    elif SYNTH_MODE == 2: #Chord Mode

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

                  elif DEVICE_TYPE == 2: #If OctaPad

                    if FADE_OUT == 0:
                        for h in range(1,(CHAN + 1),3):
                           values[h] = 0
                           values[h+1] = 0
                           values[h+2] = 0

                        light[0] = 0
                        light[1] = 0

                    elif FADE_OUT == 1:

                        light[3] = 1

                  dmxSend() #Send new dmx values

            if FADE_OUT == 1:

                if ((midi_events[0][0][0] == 248) and ((light[3] == 1) or (len(fadeOut) > 0))): #If any lights are set to fade out
                  
                  fadeOutCounter = fadeOutCounter + 1

                  #Fade out logic for chord mode
                  if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):
                      
                      if (fadeOutCounter > FADE_OUT_SPEED):

                          for b in fadeOut: #For each light w/ a fade out                              
			      
			      lights[b][1] = (lights[b][1] - FADE_OUT_RATE) #Reduce each light by the fadeout rate

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

            if DEVICE_TYPE == 1: #If Synth,

              if ((midi_events[0][0][0] >= modWheel) and (midi_events[0][0][0] <= (modWheel + 10)) and (MOD > 0)): #If Mod Wheel signal...

                if (mod != midi_events[0][0][2]): #If the value is new for mod, set it to the new value
                  mod = midi_events[0][0][2]    

                if (mod == 0):#Reset the lights based on MOD mode
                  if ((MOD == 2) or (MOD == 3)):

                    if ((SYNTH_MODE == 1) or (CHAOS == 1)): #reset for synth/chaos mode

                      for z in range(1,(NUM_LIGHTS + 1)):
                        assignColor((lights[z][0]),lights[z][1],z)

                    elif SYNTH_MODE == 2: #reset for single note
                      assignColor(light[0],light[1],L)

                  dmxSend() #If the mod is set back to 0, re-send dmx, as error handling
                

              elif ((midi_events[0][0][0] == 248) and (mod > 0) and (MOD == 1)):  #248 is the tick's from the MIDI, used if mod wheel is active
                modCounter = modCounter + mod #modCounter use's the mod value to determine strobe speed

                if (modCounter > STROBE_SPEED) and (modCounter < (STROBE_SPEED * 2)): #Blackout portion of strobe
                  dmxSendBlack()
                  modCounter = modCounter + STROBE_SPEED
                  
                elif (modCounter > (STROBE_SPEED * 3)): #Light portion of strobe
                  dmxSend()
                  modCounter = 0


              elif ((midi_events[0][0][0] == 248) and (mod > 0) and (MOD == 2)): #Alternate Mod Mode 2, color strobe, same as above except dif color vs. blackout

                modCounter = modCounter + mod

                if (modCounter > STROBE_SPEED) and (modCounter < (STROBE_SPEED * 2)):

                  if ((SYNTH_MODE == 1) or (CHAOS == 1)): 
                    for z in range(1,(NUM_LIGHTS + 1)):
                      if (lights[z][1] != 0):

                        assignColor((lights[z][0] + mod),lights[z][1],z)

                  elif SYNTH_MODE == 2:
                    assignColor((light[0]+mod),light[1],L)

                  modCounter = modCounter + STROBE_SPEED
                  dmxSend()

                elif (modCounter > (STROBE_SPEED * 3)):
                  if ((SYNTH_MODE == 1) or (CHAOS == 1)): 

                    for z in range(1,(NUM_LIGHTS + 1)):
                      if (lights[z][1] != 0):

                        assignColor((lights[z][0]),lights[z][1],z)

                  elif SYNTH_MODE == 2:
                    
                    assignColor(light[0],light[1],L)

                  modCounter = 0
                  dmxSend()

              elif ((midi_events[0][0][0] == 248) and (mod > 0) and (MOD == 3)): #Alternate mod mode 3, value shift

                modCounter = modCounter + mod

                if (modCounter > STROBE_SPEED):

                  if ((SYNTH_MODE == 1) or (CHAOS == 1)):
		    #Hold temp values
                    temp1 = values[1]
                    temp2 = values[2]
                    temp3 = values[3]
                    
                    for z in range(1,(NUM_LIGHTS + 1)): #For each light,

                      if (z == NUM_LIGHTS):  #If z is the last light, set to temp values aka the first lights value

                        values[((z*3)-2)] = temp1
                        values[((z*3)-1)] = temp2
                        values[(z*3)] = temp3

                      else:	#Otherwise, all other lights move over one to the left in value

                        values[((z*3)-2)] = values[(((z+1)*3)-2)]
                        values[((z*3)-1)] = values[(((z+1)*3)-1)]
                        values[(z*3)] = values[((z+1)*3)]


                    modCounter = 0
                    dmxSend()

                  elif SYNTH_MODE == 2:     #For single note mode, turn off lights one by one from the right, then back on each tick

                    if mod3Flag == 0: #Reduce the lights until one is on
                      

                      if ((values[4] == 0) and (values[5] == 0) and (values[6] == 0)): #If this next decrement would go to blackout...
                        dmxSendBlack() 
                        mod3Flag = 1 #Set flag to on


                      else:

                        for z in range(1,(NUM_LIGHTS + 1)):

                          if (z == NUM_LIGHTS):  #If z is the last light

                            values[((z*3)-2)] = 0
                            values[((z*3)-1)] = 0
                            values[(z*3)] = 0
			  
                          else:
                            values[((z*3)-2)] = values[(((z+1)*3)-2)]
                            values[((z*3)-1)] = values[(((z+1)*3)-1)]
                            values[(z*3)] = values[((z+1)*3)]

                      if mod3Flag == 0:
                        dmxSend()

                    elif mod3Flag == 1:

                      if ((values[4] == 0) and (values[5] == 0) and (values[6] == 0)): #If this is the first time through after the flag was tripped
                        dmxSend()
                        values[4] = 1

                      elif((values[(CHAN)] != 0) or (values[(CHAN-1)] != 0) or (values[(CHAN-2)] != 0)): #If lights full again
                        mod3Flag = 0

                      else:
                        for z in range(2,(NUM_LIGHTS + 1)):
                          values[((z*3)-2)] = values[(((z-1)*3)-2)]
                          values[((z*3)-1)] = values[(((z-1)*3)-1)]
                          values[(z*3)] = values[((z-1)*3)]

                        dmxSend()
                        
            

                    modCounter = 0
                  

              if ((midi_events[0][0][0] >= pitchWheel) and (midi_events[0][0][0] <= (pitchWheel + 10))):  #Pitch Wheel

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
                      
  #If user presses ctrl-c, switch to next config file
  except KeyboardInterrupt:
    pygame.midi.quit()
    changeConfig()
    mainProgram(device_id)

#Function used to assign color based on N value, and velocity and L- light number                 
def assignColor(N, velocity, L):

  N = N * 1.0
  velocity = velocity

  if COLOR_MODE == 0: #Full Spectrum

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

  elif COLOR_MODE == 1: #Hot Colors

    if (N < 0):
      N = 360 + N
    elif (N > 359):
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
        
  elif COLOR_MODE == 2: #Cold Colors
    if (N < 0):
      N = 560 + N
    elif (N > 559):
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

  elif COLOR_MODE == 3:  #Fuller Spectrum
    if (N < 0):
      N = 1530 + N
    elif (N > 1529):
      N = N - 1530

    if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):

      if ((N >= 0) and (N < 255)):

        values[((L*3)-2)] = (2 * velocity)
        values[((L*3)-1)] = int((N / 127) * velocity)
        values[(L*3)] = 0

      elif ((N >= 255) and (N < 510)):
        N = (N - 255)

        values[((L*3)-2)] = int(((255-N) / 127) * velocity)
        values[((L*3)-1)] = (2 * velocity)
        values[(L*3)] = 0

      elif ((N >= 510) and (N < 765)):
        N = (N - 510)

        values[((L*3)-2)] = 0
        values[((L*3)-1)] = (2 * velocity)
        values[(L*3)] = int((N / 127) * velocity)

      elif ((N >= 765) and (N < 1020)):
        N = (N - 765)

        values[((L*3)-2)] = 0
        values[((L*3)-1)] = int(((255-N) / 127) * velocity)
        values[(L*3)] = (2 * velocity)

      elif ((N >= 1020) and (N < 1275)):
        N = (N - 1020)

        values[((L*3)-2)] = int((N / 127) * velocity)
        values[((L*3)-1)] = 0
        values[(L*3)] = (2 * velocity)

      elif ((N >= 1275) and (N < 1530)):
        N = (N - 1275)

        values[((L*3)-2)] = (2 * velocity)
        values[((L*3)-1)] = 0
        values[(L*3)] = int(((255-N) / 127) * velocity)

    #For second synth setting and Octa-Pad
    elif ((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)):

      for h in range(1,(CHAN + 1),3):
    
        if ((N >= 0) and (N < 255)):

          values[h] = (2 * velocity)
          values[h+1] = int((N / 127) * velocity)
          values[h+2] = 0

        elif ((N >= 255) and (N < 510)):
          G = (N - 255)

          values[h] = int(((255-G) / 127) * velocity)
          values[h+1] = (2 * velocity)
          values[h+2] = 0

        elif ((N >= 510) and (N < 765)):
          G = (N - 510)

          values[h] = 0
          values[h+1] = (2 * velocity)
          values[h+2] = int((G / 127) * velocity)

        elif ((N >= 765) and (N < 1020)):
          G = (N - 765)

          values[h] = 0
          values[h+1] = int(((255-G) / 127) * velocity)
          values[h+2] = (2 * velocity)

        elif ((N >= 1020) and (N < 1275)):
          G = (N - 1020)

          values[h] = int((G / 127) * velocity)
          values[h+1] = 0
          values[h+2] = (2 * velocity)

        elif ((N >= 1275) and (N < 1530)):
          G = (N - 1275)

          values[h] = (2 * velocity)
          values[h+1] = 0
          values[h+2] = int(((255 - G) / 127) * velocity)

  elif ((COLOR_MODE == 4) or (COLOR_MODE == 5) or (COLOR_MODE == 6)):  #4 = Red based, 5 = Green based, 6 = Blue based
    if (N < 0):
      N = 510 + N
    elif (N > 509):
      N = N - 510

    if (((DEVICE_TYPE == 1) and (SYNTH_MODE == 1)) or (CHAOS == 1)):

      if ((N >= 0) and (N < 255)):

        if COLOR_MODE == 4:
          values[((L*3)-2)] = (2 * velocity)
          values[((L*3)-1)] = int(((255-N) / 127) * velocity)
          values[(L*3)] = 0

        elif COLOR_MODE == 5:
          values[((L*3)-2)] = 0
          values[((L*3)-1)] = (2 * velocity)
          values[(L*3)] = int(((255-N) / 127) * velocity)

        elif COLOR_MODE == 6:
          values[((L*3)-2)] = int(((255-N) / 127) * velocity)
          values[((L*3)-1)] = 0
          values[(L*3)] = (2 * velocity)

      elif ((N >= 255) and (N < 510)):
        N = (N - 255)

        if COLOR_MODE == 4:
          values[((L*3)-2)] = (2 * velocity)
          values[((L*3)-1)] = 0
          values[(L*3)] = int((N / 127) * velocity)

        elif COLOR_MODE == 5:
          values[((L*3)-2)] = int((N / 127) * velocity)
          values[((L*3)-1)] = (2 * velocity)
          values[(L*3)] = 0

        elif COLOR_MODE == 6:
          values[((L*3)-2)] = 0
          values[((L*3)-1)] = int((N / 127) * velocity)
          values[(L*3)] = (2 * velocity)

    #For second synth setting and Octa-Pad
    elif ((DEVICE_TYPE == 2) or (SYNTH_MODE == 2)):

      for h in range(1,(CHAN + 1),3):
    
        if ((N >= 0) and (N < 255)):

          if COLOR_MODE == 4:

             values[h] = (2 * velocity)
             values[h+1] = int(((255-N) / 127) * velocity)
             values[h+2] = 0

          elif COLOR_MODE == 5:

             values[h] = 0
             values[h+1] = (2 * velocity)
             values[h+2] = int(((255-N) / 127) * velocity)
     
          elif COLOR_MODE == 6:

             values[h] = int(((255-N) / 127) * velocity)
             values[h+1] = 0
             values[h+2] = (2 * velocity)
       
        elif ((N >= 255) and (N < 510)):
          G = (N - 255)

          if COLOR_MODE == 4:

             values[h] = (2 * velocity)
             values[h+1] = 0
             values[h+2] = int((G / 127) * velocity)

          elif COLOR_MODE == 5:

             values[h] = int((G / 127) * velocity)
             values[h+1] = (2 * velocity)
             values[h+2] = 0
     
          elif COLOR_MODE == 6:

             values[h] = 0
             values[h+1] = int((G / 127) * velocity)
             values[h+2] = (2 * velocity)

#Function to change config files
def changeConfig():

  global CON

  if CON == NUM_OF_CONFIGS:
    CON = 1
  else:
    CON = CON + 1

  filename = ("configs/" + CONFIG_FOLDER + "/" + str(CON) + ".txt")

  print(filename)
    
  c = open(filename,'r')
  config = c.readlines()
  config = [x.strip() for x in config]

  c.close()
#Refer to the global variables
  global NAME
  global DEVICE_TYPE
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
  global DOUBLE

  NAME = config[0]                 
  DEVICE_TYPE = int(config[2])
  NUM_LIGHTS = int(config[5])
  COLOR_MODE = int(config[8])
  COLOR_RANGE = int(config[11])
  device_id = int(config[14])
  MOD = int(config[17])
  SEMI_TONE = int(config[20])
  SYNTH_MODE = int(config[23])
  LEFTIFY = int(config[26])
  FADE_OUT = int(config[29])
  FADE_OUT_SPEED = int(config[32])
  FADE_OUT_RATE = int(config[35])
  FADE_IN = int(config[38])
  FADE_IN_DROP = float(config[41])
  FADE_IN_SPEED = int(config[44])
  FADE_IN_RATE = int(config[47])
  CHAOS = int(config[50])
  STICKY = int(config[53])
  DOUBLE = int(config[56])

  CHAN = NUM_LIGHTS * 3 
  values=[0 for t in range(CHAN + 2)] #Array to store light values, slot 0 stays empty
                
def main():
      mainProgram(device_id) #Call the main program

main()
