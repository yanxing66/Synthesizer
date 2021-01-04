'''
author: Yan Xing, Ruijing Wang
finish time: 12/16/2020
subject: DJ KEYBOARD
'''

import logging
import threading
import time
import wave
import pyaudio
import struct
import tkinter as Tk
from math import sin, pi, cos
from collections import deque
from PIL import Image,ImageTk

#-------------------------------------------------Prevent Overflow--------------------------------------------------------#
def clip16( x ):    
    # Clipping for 16 bits
    if x > 32767:
        x = 32767
    elif x < -32768:
        x = -32768
    else:
        x = x        
    return (x)
#------------------------------------------------Thread Create and Keep----------------------------------------------------#
def thread_it(func, *args):
    t = threading.Thread(target=func, args=args) 
    t.setDaemon(True) 
    t.start()
#--------------------------------------------------Recording the Music from Microphone-------------------------------------#
def record_wav():
    global file_name
    WIDTH       = 2         # Number of bytes per sample
    CHANNELS    = 1         # mono
    RATE        = 16000     # Sampling rate (frames/second)
    DURATION    = 20        # duration of processing (seconds)
    f0          = 400       # unit in Hz

    N = DURATION * RATE     # N : Number of samples to process

    wf = wave.open(file_name+".wav",'w')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)

    p = pyaudio.PyAudio()

    # Open audio stream
    stream = p.open(
        format      = p.get_format_from_width(WIDTH),
        channels    = CHANNELS,
        rate        = RATE,
        input       = True,
        output      = True)

    print('* Start')

    for n in range(0, N):

        # Get one frame from audio input (microphone)
        input_bytes = stream.read(1)
        # If you get run-time time input overflow errors, try:
        # input_bytes = stream.read(1, exception_on_overflow = False)

        # Convert binary data to tuple of numbers
        input_tuple = struct.unpack('h', input_bytes)

        # Convert one-element tuple to number
        x0 = input_tuple[0]

        # Difference equation
        #y0 = b0*x0 + b2*x2 + b4*x4 - a1*y1 - a2*y2 - a3*y3 - a4*y4 

        y0 = x0*cos(2*pi*f0*n/RATE)

        

        # Compute output value
        output_value = int(clip16(y0))    # Number

        # output_value = int(clip16(x0))   # Bypass filter (listen to input directly)

        # Convert output value to binary data
        output_bytes = struct.pack('h', output_value)  

        # Write binary data to audio stream
        stream.write(output_bytes)
        wf.writeframes(output_bytes) 

    print('* Finished')

    wf.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
#------------------------------------------------Button Sound Convert and Save-------------------------------------------#
def open_file(x):
    gain =2
    soundbuffer = deque()
    wavefile = x+'.wav'
    wf = wave.open( wavefile, 'rb' )
    p = pyaudio.PyAudio()
    # Open audio stream
    stream = p.open(
        format      = pyaudio.paInt16,
        channels    = wf.getnchannels(),
        rate        = wf.getframerate(),
        input       = False,
        output      = True )
    input_bytes = wf.readframes(1)
    while len(input_bytes) > 0:
        # Convert binary data to number
        input_tuple = struct.unpack('h', input_bytes)  # One-element tuple (unpack produces a tuple)
        input_value = input_tuple[0]                    # Number

        output_value = int(clip16(gain* input_value))  # Integer in allowed range
        soundbuffer.append(output_value)

        input_bytes = wf.readframes(1)


    p.terminate()
    return soundbuffer
#------------------------------------------Play the Music and Wait for Sound Adding----------------------------------------#
#play the original song five times
def play_bgm():
    global cur_addbuffer
    global play_start_flag
    global file_name
    times=5
    gain =2

    while(times):
        wf = wave.open(file_name+".wav","rb")
        wf_out = wave.open(file_name+str(times)+".wav",'w')

        # Read the wave file properties
        CHANNELS   = wf.getnchannels()     # Number of channels
        RATE            = wf.getframerate()     # Sampling rate (frames/second)
        signal_length   = wf.getnframes()       # Signal length
        WIDTH           = wf.getsampwidth()     # Number of bytes per sample

        wf_out.setframerate(RATE)
        wf_out.setsampwidth(WIDTH)
        wf_out.setnchannels(CHANNELS)

        p = pyaudio.PyAudio()

        # Open audio stream
        stream = p.open(
            format      = pyaudio.paInt16,
            channels    = CHANNELS,
            rate        = RATE,
            input       = False,
            output      = True )

        # Get first frame
        #input_bytes = wf2.readframes(1)
        input_bytes = wf.readframes(1)

        while len(input_bytes) > 0:
            if play_start_flag:

                # Convert binary data to number
                input_tuple = struct.unpack('h', input_bytes)  # One-element tuple (unpack produces a tuple)
                input_value = input_tuple[0] 
                if len(cur_addbuffer)>0:
                    output_value = int(clip16(gain * (input_value + cur_addbuffer.popleft())))
                    print(output_value)
                else:

                    output_value = int(clip16(gain * input_value))
                    
                output_bytes = struct.pack('h', output_value)  

                # Write binary data to audio stream
                stream.write(output_bytes)
                                     
                # Write binary data to output wave file
                wf_out.writeframes(output_bytes)
                # Get next frame
                input_bytes = wf.readframes(1)
            else:
                continue
        
        print('* Finished *')
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf_out.close()
        wf.close()
        file_name = file_name+str(times)
        times-=1
              
#-----------------------------------------------Reaction of Sound Button Clicked--------------------------------------------------------#
#when pressing the instruments
def press_btn(event):
    global play_start_flag
    play_start_flag = False
    global cur_addbuffer
    cur_addbuffer = deque()
    global all_addbuffer
    if event == 1:
        label3.config(text='loading Drum1',fg = '#FF8C00')
        cur_addbuffer = all_addbuffer[0]  
    if event == 2:
        label3.config(text='loading Drum2',fg = '#3CB371')
        cur_addbuffer = all_addbuffer[1]
    if event == 3:
        label3.config(text='loading Drum3',fg = '#DB7093')
        cur_addbuffer = all_addbuffer[2]
    if event == 4:
        label3.config(text='loading Drum4',fg = '#00BFFF')
        cur_addbuffer = all_addbuffer[3]
    if event == 5:
        label3.config(text='loading Pipa',fg = '#B22222')
        cur_addbuffer = all_addbuffer[4]
    if event == 6:
        label3.config(text='loading Guitar',fg = '#CD853F')
        cur_addbuffer = all_addbuffer[5]  
    if event == 7:
        label3.config(text='loading Base1',fg = '#32CD32')
        cur_addbuffer = all_addbuffer[6]
    if event == 8:
        label3.config(text='loading Base2',fg = '#FFA500')
        cur_addbuffer = all_addbuffer[7]
    if event == 9:
        label3.config(text='loading Gong',fg = '#800000')
        cur_addbuffer = all_addbuffer[8]
    play_start_flag = True

#-----------------------------------------Detail Seting for the Music We Create-----------------------------------------------#
def slider_change():
    global file_name
    #wf = wave.open(file_name+str(5)+".wav", 'rb' )
    wf = wave.open(file_name+str(5)+"wav",'rb')
    wf_out = wave.open("final_output",'w')
    
   
    # Read the wave file properties
    CHANNELS   = wf.getnchannels()     # Number of channels
    RATE            = wf.getframerate()     # Sampling rate (frames/second)
    signal_length   = wf.getnframes()       # Signal length
    WIDTH           = wf.getsampwidth()     # Number of bytes per sample

    wf_out.setframerate(RATE)
    wf_out.setsampwidth(WIDTH)
    wf_out.setnchannels(CHANNELS)

    p = pyaudio.PyAudio()

    # Open audio stream
    stream = p.open(
        format = pyaudio.paInt16,  
        channels = CHANNELS, 
        rate = RATE,
        input = False, 
        output = True)   
    # Get first frame
    #input_bytes = wf2.readframes(1)
    input_bytes = wf.readframes(1)
    theta = 0

    while len(input_bytes) > 0:
 
        input_tuple = struct.unpack('h', input_bytes)  # One-element tuple (unpack produces a tuple)
        input_value = input_tuple[0] 

        om1 = 2.0 * pi * f1.get()/ RATE
 
        output_value = clip16(int(gain.get() * cos(theta)*int(input_value)))
        theta = theta + om1
        if theta > pi:
            theta = theta - 2.0 * pi 

        #output_value= clip16(int(gain.get()*input_value))    
        output_bytes = struct.pack('h', output_value)  

        # Write binary data to audio stream
        stream.write(output_bytes)
                             
        # Write binary data to output wave file
        wf_out.writeframes(output_bytes)
        # Get next frame
        input_bytes = wf.readframes(1)
        
    print('* Finished *')
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf_out.close()
    wf.close()

#------------------------------------------------Initialization------------------------------------------------------------#
#entry the file name by user in gui
global file_name 
#get all add sound buffer, cur_addbuffer will be assigned in press button
global cur_addbuffer
global all_addbuffer
cur_addbuffer = deque()
all_addbuffer = []
for i in range(1,10):
    addbuffer=deque()
    addbuffer = open_file("sound"+ str(i))
    all_addbuffer.append(addbuffer)
global play_start_flag
#set flag to stop play thread wait for keyboard button get the sound we want to add
play_start_flag = True

#----------------------------------------------GUI Painting------------------------------------------------------------------#
#gui painting
#determind which sound we want to add
global cur_addbuffer
global file_name 
#get all add sound buffer
global all_addbuffer
cur_addbuffer = deque()
all_addbuffer = []
for i in range(1,10):
    addbuffer=deque()
    addbuffer = open_file("sound"+ str(i))
    all_addbuffer.append(addbuffer)
global play_start_flag
play_start_flag = True

root = Tk.Tk()

root.title("DJ Keyboard")
root.geometry("760x900")

f1 = Tk.DoubleVar()
gain = Tk.DoubleVar()
# Initialize Tk variables
f1.set(200)   
gain.set(0.2 * 2**15)

img = Image.open('star1.jpg')
img = ImageTk.PhotoImage(img)

#label1
label1 = Tk.Label(root,text='Hello~ This is DJ Keyboard',font = ("Helvetica Bold",40),compound='center',image=img,width=1000,height=200)
label1.place(x = 0,y = 0)

#label2
var = Tk.StringVar()
label2 = Tk.Label(root,text='File name:',font = ("Arial Bold",20))
label2.place(x = 30,y = 300)

#Entry input file name
e = Tk.Entry(root, show = None)
e.place(x = 150, y = 300, width = 120)
file_name = e.get()
print(e.get())

#button
btn = Tk.Button(root, text='Record', font=('Helvetica 12 bold'),width=8, height=2, command=record_wav)
btn.place(x = 30, y = 350)

#button6
btn10 = Tk.Button(root, text='Begin creating', font=('Helvetica 12 bold'),width=16, height=2, command=lambda :thread_it(play_bgm, ))
btn10.place(x = 30, y = 400)

#frame
frm1 = Tk.Frame(root, bg = 'black',  height=180, width=340)
frm1.place(x = 330, y = 330)

frm2 = Tk.Frame(root, bg = 'black',  height=220, width=340)
frm2.place(x = 330, y = 500)

#button1-5
btn1 = Tk.Button(root, text='drum1', highlightbackground = '#FF4500',fg = '#FF8C00',  font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,1))
btn2 = Tk.Button(root, text='drum2', highlightbackground = '#00FF7F',fg = '#3CB371', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,2))
btn3 = Tk.Button(root, text='drum3', highlightbackground = '#FF1493',fg = '#DB7093', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,3))
btn4 = Tk.Button(root, text='Drum4', highlightbackground = '#1E90FF',fg = '#00BFFF', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,4))
btn5 = Tk.Button(root, text='Pipa', highlightbackground = '#A52A2A',fg = '#B22222', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,5))
btn6 = Tk.Button(root, text='Guitar', highlightbackground = '#CD853F',fg = '#CD853F', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,6))
btn7 = Tk.Button(root, text='Base1', highlightbackground = '#7FFF00',fg = '#32CD32', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,7))
btn8 = Tk.Button(root, text='Base2', highlightbackground = '#FFD700',fg = '#FFA500', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,8))
btn9 = Tk.Button(root, text='Gong', highlightbackground = '#CD5C5C',fg = '#800000', font=('Helvetica 12 bold'),width=8, height=2, command=lambda:thread_it(press_btn,9))

btn1.place(x = 350, y = 350)
btn2.place(x = 350, y = 400)
btn3.place(x = 350, y = 450)
btn4.place(x = 450, y = 350)
btn5.place(x = 450, y = 400)
btn6.place(x = 450, y = 450)
btn7.place(x = 550, y = 350)
btn8.place(x = 550, y = 400)
btn9.place(x = 550, y = 450)

#button7
btn11 = Tk.Button(root, text='Detail Change', font=('Helvetica 12 bold'),width=8, height=2,  command=slider_change)
btn11.place(x = 30, y = 450)


#label3 show status
label3 = Tk.Label(root,text='',font = ("Helvetica Bold",20))
label3.place(x = 100, y = 550)


#label4
label4 = Tk.Label(root,text='Status:',font = ("Helvetica Bold",20))
label4.place(x = 30, y = 550)

#slider label
label5 = Tk.Label(root,text='Frequency',bg = 'black',font = ("Helvetica Bold",20), fg = '#00FA9A')
label5.place(x = 350, y = 530)
label6 = Tk.Label(root,text='Gain',bg = 'black',font = ("Helvetica Bold",20), fg = '#00FA9A')
label5.place(x = 350, y = 530)
label6.place(x = 350, y = 630)

#slider change
f1 = Tk.DoubleVar()
gain = Tk.DoubleVar()
f1.set(200)   # f1 : frequency of sinusoid (Hz)
gain.set(2)
S1 = Tk.Scale(root, variable = f1,bg = 'black', fg = '#00FA9A',orient=Tk.HORIZONTAL, from_=100, to=400)
S2 = Tk.Scale(root, variable = gain,bg = 'black', fg = '#00FA9A', orient=Tk.HORIZONTAL, from_=1, to=2**15-1)
S1.place(x = 450, y = 560)
S2.place(x = 450, y = 660)

root.mainloop()
