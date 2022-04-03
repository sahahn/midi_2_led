#GUI editor for making configs
#By Sage Hahn
import tkinter
import tkinter.messagebox
import os
import sys
DEVICE_TYPE = 0     #Type of device, 1 Synth, 2 Octapad
NUM_LIGHTS = 0      #Number of lights
COLOR_MODE = 0      #Color Mode, 0 Full Spectrum, 1 Hot, 2 Cold, 3 Fuller Spectrum, 4 Red Based, 5 Green Based, 6 Blue Based
COLOR_RANGE = 0     #Parameter to assign color
device_id = 0       #Id used with pygamemidi of input device
MOD =  0            #Mod Mode, either 0 off, 1 strobe, 2 color switch strobe, 3 light shift
SEMI_TONE =  0      #Pitch Wheel parameter
SYNTH_MODE =  0     #Synth Mode, either 1 chords, or 2 single note
LEFTIFY =  0        #Leftify mode, either on or off
FADE_OUT =  0       #Fade out mode, either on or off
FADE_OUT_SPEED = 0  #Fade out parameter
FADE_OUT_RATE = 0   #Fade out parameter
FADE_IN =  0        #Fade in mode, either on or off
FADE_IN_DROP = 0    #Fade in parameter
FADE_IN_SPEED =  0  #Fade in parameter
FADE_IN_RATE = 0    #Fade in parameter
CHAOS =  0          #Chaos mode, either on or off
STICKY =  0         #Sticky mode, either on or off
DOUBLE = 0          #Double mode, either on or off
NUM_OF_CONFIGS = 0  #The numbers of configs to cycle through
NAME = ""           #Name of build
CONFIG_FOLDER = ""  #Name of the config folder
CON = 1             #The number of the file to be incrimented



#Global temp variables
temp1 = 0
temp2 = 0
temp3 = 0

#Global text flag
TEXT = 0
text = ""

#Main GUI class
class GUI:

    #Variables to hold max and min values
    MIN1= 0
    MIN2= 0
    MAX1= 0
    MAX2= 0
    MIN3 = 0
    MAX3 = 0

    def __init__(self):
        r=6
        
    #GUI template for radio button questions
    def showButtons(self, option, choice1, choice2, choice3='', choice4='', choice5='', choice6='', choice7=''):

        self.main_window = tkinter.Tk()

        w = 600 # width 
        h = 300 # height

        # get screen width and height
        ws = self.main_window.winfo_screenwidth() # width of the screen
        hs = self.main_window.winfo_screenheight() # height of the screen

        # calculate x and y coordinates
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.main_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    
        self.title_frame = tkinter.Frame(self.main_window)
        self.top_frame = tkinter.Frame(self.main_window)
        self.bottom_frame = tkinter.Frame(self.main_window)

        self.label = tkinter.Label(self.title_frame, text=option)

        self.label.pack()

        self.radio_var = tkinter.IntVar()

        self.radio_var.set(1)

        self.rb1 = tkinter.Radiobutton(self.top_frame, text=choice1, \
                                       variable=self.radio_var, value=1)
        self.rb1.pack()

        self.rb2 = tkinter.Radiobutton(self.top_frame, text=choice2, \
                                       variable=self.radio_var, value=2)
        self.rb2.pack()

        if (choice3 != ''):
            self.rb3 = tkinter.Radiobutton(self.top_frame, text=choice3, \
                                           variable=self.radio_var, value=3)
            self.rb3.pack()

        if (choice4 != ''):

            self.rb4 = tkinter.Radiobutton(self.top_frame, text=choice4, \
                                           variable=self.radio_var, value=4)
            self.rb4.pack()

        if (choice5 != ''):
            self.rb5 = tkinter.Radiobutton(self.top_frame, text=choice5, \
                                           variable=self.radio_var, value=5)
            self.rb5.pack()

        if (choice6 != ''):
            self.rb6 = tkinter.Radiobutton(self.top_frame, text=choice6, \
                                           variable=self.radio_var, value=6)
            self.rb6.pack()

        if (choice7 != ''):
            self.rb7 = tkinter.Radiobutton(self.top_frame, text=choice7, \
                                           variable=self.radio_var, value=7)
            self.rb7.pack()


        self.ok_button = tkinter.Button(self.bottom_frame, \
                                        text='OK', command=self.end1)
        self.quit_button = tkinter.Button(self.bottom_frame, \
                                        text='Quit', command=self.END)
        
        self.ok_button.pack(side='left')
        self.quit_button.pack(side='left')
        
        self.title_frame.pack()
        self.top_frame.pack()
        self.bottom_frame.pack()

        tkinter.mainloop()

    #Internal end logic for radio button questions
    def end1(self):

        global temp1
        temp1 = self.radio_var.get()  #Set's result to temp1
        self.main_window.destroy()

    #GUI template for text box questions
    def showTextBoxes(self, option1, min1=0, max1=0, option2='', min2=0, max2=0, option3='', min3=0, max3=0):
        self.main_window = tkinter.Tk()

        w = 600 # width 
        h = 300 # height

        # get screen width and height
        ws = self.main_window.winfo_screenwidth() # width of the screen
        hs = self.main_window.winfo_screenheight() # height of the screen

        # calculate x and y coordinates
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.main_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.MIN1 = min1
        self.MAX1 = max1
        

        if option2 != '':
            
            self.MIN2 = min2
            self.MAX2 = max2

            self.frame_3 = tkinter.Frame(self.main_window)
            self.frame_4 = tkinter.Frame(self.main_window)

        else:

            self.MIN2 = 0
            self.MAX2 = 0

        if option3 != '':

            
            self.MIN3 = min3
            self.MAX3 = max3

            self.frame_6 = tkinter.Frame(self.main_window)
            self.frame_7 = tkinter.Frame(self.main_window)

        else:
            self.MIN3 = 0
            self.MAX3 = 0

        self.frame_1 = tkinter.Frame(self.main_window)
        self.frame_2 = tkinter.Frame(self.main_window)
        self.frame_5 = tkinter.Frame(self.main_window)

        #Spot for first prompt
        self.prompt_one = tkinter.Label(self.frame_1, \
                                        text=option1)
        self.space_one = tkinter.Entry(self.frame_1,width=10)

        self.prompt_one.pack(side='left')
        self.space_one.pack(side='left')

        #Spot to display if result of first is in acceptable range
        self.value1 = tkinter.StringVar()
        self.output_label1 = tkinter.Label(self.frame_2,textvariable=self.value1)

        self.output_label1.pack()

        
        if option2 != '':

            self.prompt_two = tkinter.Label(self.frame_3, \
                                            text=option2)
            self.space_two = tkinter.Entry(self.frame_3,width=10)

            self.prompt_two.pack(side='left')
            self.space_two.pack(side='left')

            self.value2 = tkinter.StringVar()
            self.output_label2 = tkinter.Label(self.frame_4,textvariable=self.value2)

            self.output_label2.pack()

        if option3 != '':

            self.prompt_three = tkinter.Label(self.frame_6, \
                                        text=option3)
            self.space_three = tkinter.Entry(self.frame_6,width=10)

            self.prompt_three.pack(side='left')
            self.space_three.pack(side='left')

            self.value3 = tkinter.StringVar()
            self.output_labe3 = tkinter.Label(self.frame_7,textvariable=self.value3)

            self.output_labe3.pack()
            
        

        #Frame 5, w/ buttons
        self.okay_button = tkinter.Button(self.frame_5, \
                                        text='OK', command=self.end2)
        self.quit_button = tkinter.Button(self.frame_5, \
                                      text='Quit', command=self.END)

        self.okay_button.pack(side='left')
        self.quit_button.pack(side='left')

        #Pack everything
        self.frame_1.pack(side='top')
        self.frame_2.pack(side='top')

        if option2 != '':
            self.frame_3.pack(side='top')
            self.frame_4.pack(side='top')

        if option3 != '':
            self.frame_6.pack(side='top')
            self.frame_7.pack(side='top')

        self.frame_5.pack(side='top')
        tkinter.mainloop()
                                          
    #Internal end logic for text box questions
    def end2(self):

        min1 = self.MIN1
        max1 = self.MAX1
       
        min2 = self.MIN2
        max2 = self.MAX2
  
        max3 = self.MAX3
        min3 = self.MIN3

        global temp1
        global temp2
        global temp3

        if TEXT == 1:       #Work around so this will accept text answers also

            global text
            text = self.space_one.get()
            self.main_window.destroy()

        else:
                   
            try:
                one = int(self.space_one.get())


                if (max3 != 0):
                    three = int(self.space_three.get())
                    two = int(self.space_two.get())

                    
                    if ((one < min1) or (one > max1)):
                        self.value1.set("Enter between " + str(min1) + " and " + str(max1) + ".")
                    
                    elif ((two < min2) or (two > max2)):
                        self.value2.set("Enter between " + str(min2) + " and " + str(max2) + ".")

                    elif ((three < min3) or (three > max3)):
                            self.value3.set("Enter between " + str(min3) + " and " + str(max3) + ".")

                    else:
                        temp1 = one
                        temp2 = two
                        temp3 = three

                        self.main_window.destroy()

                elif (max2 != 0):
                    two = int(self.space_two.get())


                    if ((one < min1) or (one > max1)):
                        self.value1.set("Enter between " + str(min1) + " and " + str(max1) + ".")
                    
                    elif ((two < min2) or (two > max2)):
                        self.value2.set("Enter between " + str(min2) + " and " + str(max2) + ".")

                    else:

                        temp1 = one
                        temp2 = two

                        self.main_window.destroy()
                
                else:

                    if ((one < min1) or (one > max1)):
                        self.value1.set("Enter between " + str(min1) + " and " + str(max1) + ".")

                    else:

                        temp1 = one

                        self.main_window.destroy()
               

            except:
                self.value1.set("Enter between " + str(min1) + " and " + str(max1) + ".")

                if (max2 != 0):
                    self.value2.set("Enter between " + str(min2) + " and " + str(max2) + ".")

                if (max3 != 0):
                    self.value3.set("Enter between " + str(min3) + " and " + str(max3) + ".")
    #GUI for confirming all the settings
    def confirmSettings(self, question):


        self.main_window = tkinter.Tk()

        w = 600 # width 
        h = 600 # height

        # get screen width and height
        ws = self.main_window.winfo_screenwidth() # width of the screen
        hs = self.main_window.winfo_screenheight() # height of the screen

        # calculate x and y coordinates
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen 
        # and where it is placed
        self.main_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    
        self.main_frame = tkinter.Frame(self.main_window)
        self.bottom_frame = tkinter.Frame(self.main_window)

        f1 = ("Device Type: ")
        if DEVICE_TYPE == 1:
            f1 = f1 + "Synth"
        else:
            f1 = f1 + "Octa-Pad"
            
        f2 = ("Number of lights: " + str(NUM_LIGHTS))

        f3 = ("Color Mode: ")
        if COLOR_MODE == 0:
            f3 = f3 + "Full Spectrum"
        elif COLOR_MODE == 1:
            f3 = f3 + "Hot Colors"
        elif COLOR_MODE == 2:
            f3 = f3 + "Cold Colors"
        elif COLOR_MODE == 3:
            f3 = f3 + "Fuller Spectrum"
        elif COLOR_MODE == 4:
            f3 = f3 + "Red Based"
        elif COLOR_MODE == 5:
            f3 = f3 + "Green Based"
        elif COLOR_MODE == 6:
            f3 = f3 + "Blue Based"

        f4 = ("Color Range: " + str(COLOR_RANGE))

        f5 = ("Device ID: " + str(device_id))

        f6 = ("Synth Mode: ")
        if SYNTH_MODE == 0:
            f6 = f6 + "Off"
        elif SYNTH_MODE == 1:
            f6 = f6 + "Chord"
        else:
            f6 = f6 + "Single Note"

        f7 = ("Pitch wheel semitones: " + str(SEMI_TONE))

        f8 = ("Mod Mode: ")
        if MOD == 0:
            f8 = f8 + "Off"
        elif MOD == 1:
            f8 = f8 + "Strobe"
        elif MOD == 2:
            f8 = f8 + "Color Strobe"
        elif MOD == 3:
            f8 = f8 + "Value Jumble"

        f9 = ("Chaos Mode: ")
        if CHAOS == 0:
            f9 = f9 + "Off"
        elif CHAOS == 1:
            f9 = f9 + "On"

        f10 = ("Fade Out: ")
        if FADE_OUT == 0:
            f10 = f10 + "Off"
        elif FADE_OUT == 1:
            f10 = f10 + "On"

        f11 = ("Fade Out Speed: " + str(FADE_OUT_SPEED))
        f12 = ("Fade Out Rate: " + str (FADE_OUT_RATE))

        f13 = ("Fade In: ")
        if FADE_IN == 0:
            f13 = f13 + "Off"
        elif FADE_IN == 1:
            f13 = f13 + "On"
        
        f14 = ("Fade In Drop: " + str(FADE_IN_DROP))
        f15 = ("Fade In Speed: " + str(FADE_IN_SPEED))
        f16 = ("Fade In Rate: " + str (FADE_IN_RATE))

        f17 = ("Sticky Mode: ")
        if STICKY == 0:
            f17 = f17 + "Off"
        elif STICKY == 1:
            f17 = f17 + "On"
               
        f18 = ("Leftify Mode: ")
        if LEFTIFY == 0:
            f18 = f18 + "Off"
        elif LEFTIFY == 1:
            f18 = f18 + "On"

        f19 = ("Double Mode: ")
        if DOUBLE == 0:
            f19 = f19 + "Off"
        elif DOUBLE == 1:
            f19 = f19 + "On"


        self.label = tkinter.Label(self.main_frame, text=question)
        self.p1 = tkinter.Label(self.main_frame, text=f1)
        self.p2 = tkinter.Label(self.main_frame, text=f2)
        self.p3 = tkinter.Label(self.main_frame, text=f3)
        self.p4 = tkinter.Label(self.main_frame, text=f4)
        self.p5 = tkinter.Label(self.main_frame, text=f5)
        self.p6 = tkinter.Label(self.main_frame, text=f6)
        self.p7 = tkinter.Label(self.main_frame, text=f7)
        self.p8 = tkinter.Label(self.main_frame, text=f8)
        self.p9 = tkinter.Label(self.main_frame, text=f9)
        self.p10 = tkinter.Label(self.main_frame, text=f10)
        self.p11 = tkinter.Label(self.main_frame, text=f11)
        self.p12 = tkinter.Label(self.main_frame, text=f12)
        self.p13 = tkinter.Label(self.main_frame, text=f13)
        self.p14 = tkinter.Label(self.main_frame, text=f14)
        self.p15 = tkinter.Label(self.main_frame, text=f15)
        self.p16 = tkinter.Label(self.main_frame, text=f16)
        self.p17 = tkinter.Label(self.main_frame, text=f17)
        self.p18 = tkinter.Label(self.main_frame, text=f18)
        self.p19 = tkinter.Label(self.main_frame, text=f19)

        self.label.pack(side='top')
        self.p1.pack(side='top')
        self.p2.pack(side='top')
        self.p3.pack(side='top')
        self.p4.pack(side='top')
        self.p5.pack(side='top')
        self.p6.pack(side='top')
        self.p7.pack(side='top')
        self.p8.pack(side='top')
        self.p9.pack(side='top')
        self.p10.pack(side='top')
        self.p11.pack(side='top')
        self.p12.pack(side='top')
        self.p13.pack(side='top')
        self.p14.pack(side='top')
        self.p15.pack(side='top')
        self.p16.pack(side='top')
        self.p17.pack(side='top')
        self.p18.pack(side='top')
        self.p19.pack(side='top')

        self.ok_button = tkinter.Button(self.bottom_frame, \
                                        text='YES/CONTINUE', command=self.main_window.destroy)
        self.quit_button = tkinter.Button(self.bottom_frame, \
                                        text='NO/REDO', command=self.end3)
        
        self.ok_button.pack(side='left')
        self.quit_button.pack(side='left')
        
        self.main_frame.pack(side='top')
        self.bottom_frame.pack(side='top')

        tkinter.mainloop()

    #Internal end logic for confirm settings
    def end3(self):

        global temp1
        temp1 = 666
        self.main_window.destroy()

    def END(self):
        self.main_window.destroy()
        sys.exit()

#Method for choosing the settings w/ conflict logic built in
def chooseSettings():
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
    global device_id
    global CHAOS
    global MOD
    global DOUBLE

    g.showButtons("Choose a device type","Synth","Octa-Pad")
    DEVICE_TYPE = temp1

    g.showButtons("Choose a color mode","Full Spectrum","Hot Colors","Cold Colors","Fuller Spectrum","Red Based","Green Based","Blue Based")
    COLOR_MODE = (temp1 - 1)

    if DEVICE_TYPE == 2:
        g.showTextBoxes("Enter the number of lights",1,40,"Enter the device ID",0,10)
        COLOR_RANGE = 8 #Default Octa-pad settings
    else:
        g.showTextBoxes("Enter the number of lights",1,40,"Enter the device ID",0,10,"Enter the color range",1,60)
        COLOR_RANGE = temp3

    NUM_LIGHTS = temp1
    device_id = temp2

    if DEVICE_TYPE == 1: #If Synth

        g.showButtons("Mod Mode","Off","Strobe","Color Strobe","Value Jumble")
        MOD = (temp1-1)
        g.showTextBoxes("Enter the amount of semitones the pitch wheel controls",1,COLOR_RANGE)
        SEMI_TONE = temp1

        g.showButtons("Choose the Synth Mode","Chord","Single Note")
        SYNTH_MODE = temp1

        if SYNTH_MODE == 1:

            g.showButtons("Chord Modes","None","Leftify Mode","Double Mode")
            if temp1 == 2:
                LEFTIFY = 1
                DOUBLE = 0
            elif temp1 == 3:
                DOUBLE = 1
                LEFTIFY = 0
            else:
                DOUBLE = 0
                LEFTIFY = 0

        if LEFTIFY == 0:

            g.showButtons("Release Setting","None","Fade Out","Sticky Mode")

            if temp1 == 3: #If Sticky
                STICKY = 1
            else: 
                FADE_OUT = (temp1-1)
                STICKY = 0

            if FADE_OUT == 1:
                g.showTextBoxes("Enter the fade out rate (greater than 1 = slow fade)",1,10,"Enter the fade out speed",1,10)
                FADE_OUT_RATE = temp1
                FADE_OUT_SPEED = temp2


            g.showButtons("Fade In Setting","Off","On")
            FADE_IN = (temp1-1)

            if FADE_IN == 1:

                g.showTextBoxes("Enter the fade drop (0=black, 5=half, 10=normal",0,10,"Enter the fade in rate (greater than 1 = slow fade)",1,10,"Enter the fade in speed",1,10)

                FADE_IN_DROP = temp1
                FADE_IN_SPEED = temp2
                FADE_IN_RATE = temp3


            if DOUBLE == 0: #Double and Chaos not compatible
                g.showButtons("Chaos Mode","Off","On")
                CHAOS = (temp1-1)

    else: #Octapad settings

        g.showButtons("Release Setting","None","Fade Out","Sticky Mode")

        if temp1 == 3: #If Sticky
            STICKY = 1
        else: 
            FADE_OUT = (temp1-1)
            STICKY = 0

        if FADE_OUT == 1:
            g.showTextBoxes("Enter the fade out rate (greater than 1 = slow fade)",1,10,"Enter the fade out speed",1,10)
            FADE_OUT_RATE = temp1
            FADE_OUT_SPEED = temp2

        g.showButtons("Chaos Mode","Off","On")
        CHAOS = (temp1-1)


    g.confirmSettings("Do these settings look correct?")
    if temp1 == 666:
        chooseSettings() #Recall the function

#Method to write a new config
def writeConfig():
    filename = ("configs/" + CONFIG_FOLDER + "/" + str(CON) + ".txt")
    directory = os.path.dirname(filename)

    try:
        os.stat(directory)
    except:
        os.mkdir(directory)

    c = open(filename,'w')
    
    #Below is config format the program is designed to work with
    c.write(NAME + "\n")

    c.write("Device Type" + "\n")
    c.write(str(DEVICE_TYPE) + "\n")
    c.write("\n")

    c.write("Number of Lights" + "\n")
    c.write(str(NUM_LIGHTS) + "\n")
    c.write("\n")

    c.write("Device Color Mode" + "\n")
    c.write(str(COLOR_MODE) + "\n")
    c.write("\n")

    c.write("Color Range" + "\n")
    c.write(str(COLOR_RANGE) + "\n")
    c.write("\n")

    c.write("Device ID" + "\n")
    c.write(str(device_id) + "\n")
    c.write("\n")

    c.write("Mod Mode" + "\n")
    c.write(str(MOD) + "\n")
    c.write("\n")

    c.write("Pitch Wheel Semitones" + "\n")
    c.write(str(SEMI_TONE) + "\n")
    c.write("\n")

    c.write("Synth Mode" + "\n")
    c.write(str(SYNTH_MODE) + "\n")
    c.write("\n")

    c.write("Leftify Mode" + "\n")
    c.write(str(LEFTIFY) + "\n")
    c.write("\n")

    c.write("Fade Out" + "\n")
    c.write(str(FADE_OUT) + "\n")
    c.write("\n")

    c.write("Fade Out Speed" + "\n")
    c.write(str(FADE_OUT_SPEED) + "\n")
    c.write("\n")

    c.write("Fade Out Rate" + "\n")
    c.write(str(FADE_OUT_RATE) + "\n")
    c.write("\n")

    c.write("Fade In" + "\n")
    c.write(str(FADE_IN) + "\n")
    c.write("\n")

    c.write("Fade In Drop " + "\n")
    c.write(str(FADE_IN_DROP) + "\n")
    c.write("\n")

    c.write("Fade In Speed" + "\n")
    c.write(str(FADE_IN_SPEED) + "\n")
    c.write("\n")

    c.write("Fade In RATE" + "\n")
    c.write(str(FADE_IN_RATE) + "\n")
    c.write("\n")

    c.write("Chaos Mode" + "\n")
    c.write(str(CHAOS) + "\n")
    c.write("\n")

    c.write("Sticky Mode" + "\n")
    c.write(str(STICKY) + "\n")
    c.write("\n")

    c.write("Double Mode" + "\n")
    c.write(str(DOUBLE) + "\n")
    c.write("\n")

    if CON == 1:  #If it's the first config in a package
        c.write("Number Of Configs" + "\n")
        c.write(str(NUM_OF_CONFIGS) + "\n")
        c.write("\n")

        c.write("Config Folder Name" + "\n")
        c.write(str(CONFIG_FOLDER) + "\n")
        c.write("\n")

         
    c.close()

#Update the first config file of the package with the new number of configs
def updateConfigNumber():

    filename = ("configs/" + CONFIG_FOLDER + "/1.txt") #Open the first text file

    c = open(filename,'r')
    config = c.readlines()
    config = [x.strip() for x in config]

    c.close()

    print(NUM_OF_CONFIGS)

    config[59] = NUM_OF_CONFIGS

    d = open(filename,'w')

    for x in config:
        d.write(str(x) + "\n")

    d.close()

#Function for updating the number of lights and device ID for every config in a package
def update(x):

    filename = ("configs/" + CONFIG_FOLDER + "/" + str(x) + ".txt") #Open the first text file

    c = open(filename,'r')
    config = c.readlines()
    config = [x.strip() for x in config]

    c.close()

    config[5] = NUM_LIGHTS 
    config[14] = device_id    
    
    d = open(filename,'w')

    for x in config:
        d.write(str(x) + "\n")

    d.close()
    
#Returns the name from a config file
def getName(conNum):

    filename = ("configs/" + CONFIG_FOLDER + "/" + str(conNum) + ".txt")

    c = open(filename,'r')
    config = c.readlines()
    config = [x.strip() for x in config]

    c.close()

    return config[0]

#Reads a config file into the global variables
def readConfig():

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
    global device_id
    global CHAOS
    global MOD
    global DOUBLE
    global NAME

    filename = ("configs/" + CONFIG_FOLDER + "/" + str(CON) + ".txt")

    c = open(filename,'r')
    config = c.readlines()
    config = [x.strip() for x in config]

    c.close()

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
    FADE_IN_DROP = int(config[41]) #Fade in parameter
    FADE_IN_SPEED = int(config[44])  #Fade in parameter
    FADE_IN_RATE = int(config[47])   #Fade in parameter
    CHAOS = int(config[50])          #Chaos mode, either on or off
    STICKY = int(config[53])         #Sticky mode, either on or off
    DOUBLE = int(config[56])         #Double mode, either on or off

#The main program
def main():

    global NAME
    global CONFIG_FOLDER 
    global TEXT #Flag
    global CON
    global NUM_OF_CONFIGS
    global device_id
    global NUM_LIGHTS

    package = 0  #Package flag
    addMore = 0  #Add more flag
    flag = 1

    g.showButtons("Would you like to build a new config package, or view/edit previous configs","New Package", "View/Edit")
    package = temp1

    TEXT = 1 #Set TEXT flag on
    if (package == 1):  #New config package
        g.showTextBoxes("Enter the config folder name (choose carefully, ie no weird symbols")
        CONFIG_FOLDER = text

        TEXT = 0  #Set text flag off
        chooseSettings() #Pick settings

        TEXT = 1 #Set back on
        g.showTextBoxes("What is this config called")
        NAME = text

        NUM_OF_CONFIGS = 1
        writeConfig()

        g.showButtons("Would you like to add more configs?","No","Yes")
        addMore = (temp1-1)

        while (addMore == 1): #Keep adding more configs
            
            NUM_OF_CONFIGS = NUM_OF_CONFIGS + 1  #Update the configs numbers
            CON = CON + 1

            TEXT = 0  #Set text flag off
            chooseSettings() #Pick settings

            TEXT = 1 #Set back on
            g.showTextBoxes("What is this config called")
            NAME = text

            writeConfig()

            g.showButtons("Would you like to add more configs?","No","Yes")
            addMore = (temp1-1)

        updateConfigNumber() #Update the config number

        main() #Recall the main function, aka back to main menu

    elif (package == 2): #Read/edit/update


        avaliable = "Choose a config folder from: \n"
        error = ""
        root = "./configs/"
        
	#Get all of the avaliable folders
        for dirpath, dirs, files in os.walk(root):
            for dir in dirs:
                avaliable = (avaliable + str(dir) + "\n")


        while (flag == 1):

            root = "./configs/"
            option = avaliable + error

            TEXT = 1
            g.showTextBoxes(option)
            CONFIG_FOLDER = text

            root = root + CONFIG_FOLDER + "/"

            try:
                os.stat(root)
                if (CONFIG_FOLDER != ''):
                    flag = 0
            except:
                error = "Conifg File typed wrong, please re-try"


        g.showButtons("Choose to read/edit, append or update:","Read/Edit","Append", "Update")
        flag = temp1

        if temp1 == 1:  #Read/Edit

            names = "Choose one of the following configs (by #): \n"
            fileLength = 0
	
            for dirpath, dirs, files in os.walk(root):	#Get each config file
                fileLength = len(files)
                for file in files:
                    if '~' in file:
                        fileLength = fileLength - 1

                NUM_OF_CONFIGS = fileLength

                files.sort()
                for x in range(1,(fileLength+1)):
                    names = (names + str(x) + ": " + getName(x) + '\n')

            TEXT = 0
            g.showTextBoxes(names,1,(fileLength+1))
            CON = temp1

            readConfig()

            g.confirmSettings(NAME)
            if temp1 == 666:  #Flag number 666
                chooseSettings() #Recall the function

                TEXT = 1 #Set back on
                g.showTextBoxes("Change config name? (Leave blank to keep the same)")
                if text:
                    NAME = text

                writeConfig()

            main()

        elif temp1 == 2: #Append a new config

            for dirpath, dirs, files in os.walk(root):
                fileLength = len(files)
                for file in files:
                    if '~' in file:
                        fileLength = fileLength - 1
                NUM_OF_CONFIGS = fileLength   #Get the number of files already there

            addMore = 1

            while (addMore == 1):
            
                NUM_OF_CONFIGS = NUM_OF_CONFIGS + 1  #Update the configs numbers
                CON = NUM_OF_CONFIGS

                TEXT = 0  #Set text flag off
                chooseSettings() #Pick settings

                TEXT = 1 #Set back on
                g.showTextBoxes("What is this config called")
                NAME = text

                writeConfig()

                g.showButtons("Would you like to add more configs?","No","Yes")
                addMore = (temp1-1)

            updateConfigNumber() #Update the config number

            main()

        elif temp1 == 3: #Update a package

            for dirpath, dirs, files in os.walk(root):
                fileLength = len(files)
                for file in files:
                    if '~' in file: #Get rid of problem with system made backup files
                        fileLength = fileLength - 1
                NUM_OF_CONFIGS = fileLength

                TEXT = 0
                g.showTextBoxes("Enter the number of lights",1,40,"Enter the device ID",0,10)
                NUM_LIGHTS = temp1
                device_id = temp2

                for x in range(1,(fileLength+1)):
                    update(x)

            main()

g = GUI() #Create instance of the GUI, g

main()#Call the main function





   
      
