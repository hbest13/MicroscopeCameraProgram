from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter import Frame, StringVar, OptionMenu, TOP, BOTTOM, LEFT, RIGHT, Entry, Button, Label, Text, Message, Toplevel, CENTER, font, Y
import threading
import datetime
import imutils
import cv2
import os
import serial
import time
from imutils.video import VideoStream
from CURRENTpandasFunction import *
import pygame
# from CURRENTimportedR import *

# Set the correct port for the arduino
ser = serial.Serial(port="COM4")

class MicroscopeImages:
    def __init__(self, vs, outputPath):
        # store the video stream object and output path, then initialize the most recently read frame, thread for
        # reading frames, and the thread stop event
        self.vs = vs  # video stream variable, instantiation of VideoStream
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.stopArduino = None
        self.study = None
        self.i = 0
        self.list_index = 0
        self.enter_button_pressed = False

        # initialize the root window and image panel
        self.root = tki.Tk()
        # retrieve screen size and set to variables
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        # setting tkinter window size to size of screen
        self.root.geometry("%dx%d" % (self.width, self.height))
        self.panel = None

        # create a selection bar for the user to select the study
        self.blank_frame = Frame(self.root)
        self.blank_frame.pack(side=TOP, ipady=5)
        self.selection_font=font.Font(family='Helvetica', size=20)
        self.selection_frame = Frame(self.root)
        self.selection_frame.pack(side=TOP, ipady=5)
        self.options = ["IMPROVE",
                        "CSN",
                        "Special Studies",
                        "Custom"]
        self.selected_study = StringVar(self.selection_frame)
        self.selected_study.set("Select a Study")
        self.study_selection = OptionMenu(self.selection_frame, self.selected_study, *self.options, command=self.selected_options)
        self.study_selection.config(font=self.selection_font)
        self.study_selection['menu'].config(font=self.selection_font)
        self.study_selection.pack()

        # create an input area for the user to enter the Study Tray ID number
        self.study_tray_ID_frame = Frame(self.root)
        self.study_tray_ID_frame.pack(side=TOP, ipady=5)
        self.study_tray_ID_entry = StringVar(self.study_tray_ID_frame)
        self.study_tray_ID_entry.set("Enter a Study Tray ID #")
        self.tray_label = Label(self.study_tray_ID_frame, textvariable=self.study_tray_ID_entry)
        self.tray_label.config(font=self.selection_font)
        self.tray_label.pack(ipady=5)
        self.study_tray_ID = Entry(self.study_tray_ID_frame, width=5)
        self.study_tray_ID.config(font=self.selection_font)
        self.study_tray_ID.pack()

        self.label = Label(self.study_tray_ID_frame)

        self.enter_frame = Frame(self.root)
        self.enter_frame.pack(side=TOP, ipady=5)
        enter_button = Button(self.enter_frame, text="Enter", command=lambda: [self.print_ID(), self.test_func(), self.display_selections()])
        enter_button.config(font=self.selection_font)
        enter_button.pack(ipady=5)

        # start a thread that constantly pools the video sensor for the most recently read frame
        # stop event is what will end the threading and thus end the pooling of the video stream
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("Microscope Images")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        # start a thread that constantly pools the information from the switch button to see if it is clicked
        # stop arduino is what will end the threading and thus end the pooling of the arduino information
        self.stopArduino = threading.Event()
        self.thread = threading.Thread(target=self.test_for_button_press, args=())
        self.thread.start()

        # max_bits is the number of bytes used in calculating the average
        self.max_bits = 10
        # Clicks is the list that stores the last 10 bits
        self.clicks = []

    # Function to retrieve the selected study
    def selected_options(self, study):
        self.study = study
        print(study)

    # Function to retrieve the entered study tray ID
    def print_ID(self):
        self.label.destroy()
        self.tray_ID = int(self.study_tray_ID.get())
        print(self.tray_ID)
        self.enter_button_pressed = True

    def test_func(self):
        self.filter_id = func(self.study, self.tray_ID)[0]
        self.filter_position = func(self.study, self.tray_ID)[1]
        self.filter_date = func(self.study, self.tray_ID)[2]

    def display_selections(self):
        # Create label
        self.label = Label(self.root)
        self.label.configure(text="Current Tray\n\n" + "Study :  " + self.study + "       Tray ID # :  " + str(self.tray_ID), font=self.selection_font)
        self.label.place(relx=0.07, rely=0.1, anchor="w")

    def videoLoop(self):
        # DISCLAIMER: This try/except statement is a pretty ugly hack to get around a RunTime error that Tkinter throws due to threading
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to have a maximum width of 300 pixels
                self.frame = self.vs.read()
                self.frame = imutils.resize(self.frame, width=500)

                # OpenCV represents images in BGR order; however PIL represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.place(relx=0.5, rely=0.5, anchor=CENTER)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError:
            print("[INFO] caught a RuntimeError")

    # The mean function finds the average of the values stored in clicks
    def mean(self, nums):
        return float(sum(nums)) / max(len(nums), 1)

    # Function to test whether the button has been pressed
    # If the button has been pressed the function will stop running
    def test_for_button_press(self):
        while not self.stopArduino.is_set():
            # Read the bytes from the arduino and decode them into bits
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes.decode('utf-8').strip()
            #print(decoded_bytes)

            # Append the bits into the clicks list and calculate the average of the last 10
            if decoded_bytes != '' and len(decoded_bytes) == 1:
                self.clicks.append(int(decoded_bytes))
            avg = float(self.mean(self.clicks))

            # If the length of the clicks list is longer than max_bits, the oldest bit is removed
            # This ensures that the list only stays at a length of 10
            if len(self.clicks) == self.max_bits:
                self.clicks.pop(0)

            # If the bit is 1 (meaning the button has been pressed) and the average of the last
            # ten bits is less than 0.1 (meaning the '1' is an actual click and not just 'bouncing'), then
            # an image will be taken
            if decoded_bytes == "0" and avg == 0.9:
                self.top = Toplevel(self.root)
                self.top.geometry("600x50")
                Message(self.top, text='CAPTURING IMAGE, PLEASE WAIT.', width=500, anchor='center',font=("Courier", 20)).pack()
                time.sleep(2.5)
                self.top.destroy()
                self.takeSnapshot()
                self.test_func()

    def takeSnapshot(self):
        if self.enter_button_pressed == False:
            self.i = 0
            self.second_top = Toplevel(self.root)
            self.second_top.geometry("800x50")
            Message(self.second_top, text='Tray Complete! Please Select New Tray.', width=800, anchor='center',
                    font=("Courier", 20)).pack()
            return

        if self.i < len(self.filter_id):
            self.current_filter_ID = str(self.filter_id[self.i])
            # grab the current timestamp and use it to construct the output path
            ts = datetime.datetime.now()
            filename = "{}.jpg".format(self.current_filter_ID + "_" + ts.strftime("%Y-%m-%d_%H-%M-%S"))
            csv_file_name = "{}.csv".format(self.current_filter_ID + "_" + ts.strftime("%Y-%m-%d_%H-%M-%S"))
            if self.study == 'IMPROVE':
                self.specific_path = self.outputPath + '/IMPROVE' + '/Study Tray ID ' + str(self.study_tray_ID.get())
                while not os.path.isdir(self.specific_path):
                    os.mkdir(self.specific_path)
                p = os.path.sep.join((self.specific_path, filename))
                p2 = os.path.sep.join((self.specific_path, csv_file_name))
            if self.study == 'CSN':
                self.specific_path = self.outputPath + '/CSN' + '/Study Tray ID ' + str(self.study_tray_ID.get())
                while not os.path.isdir(self.specific_path):
                    os.mkdir(self.specific_path)
                p = os.path.sep.join((self.specific_path, filename))
                p2 = os.path.sep.join((self.specific_path, csv_file_name))
            if self.study == 'Special Studies':
                self.specific_path = self.outputPath + '/Special Studies' + '/Study Tray ID ' + str(self.study_tray_ID.get())
                while not os.path.isdir(self.specific_path):
                    os.mkdir(self.specific_path)
                p = os.path.sep.join((self.specific_path, filename))
                p2 = os.path.sep.join((self.specific_path, csv_file_name))
            if self.study == 'Custom':
                self.specific_path = self.outputPath + '/Custom' + '/Study Tray ID ' + str(self.study_tray_ID.get())
                while not os.path.isdir(self.specific_path):
                    os.mkdir(self.specific_path)
                p = os.path.sep.join((self.specific_path, filename))
                p2 = os.path.sep.join((self.specific_path, csv_file_name))
            #captured_image = self.frame.copy()
            captured_image = self.vs.read()
            # percent by which the image is resized
            scale_percent = 75

            # calculate the 50 percent of original dimensions
            scaled_width = int(captured_image.shape[1] * scale_percent / 100)
            scaled_height = int(captured_image.shape[0] * scale_percent / 100)

            # dsize
            scaled_size = (scaled_width, scaled_height)
            captured_image = cv2.resize(captured_image, scaled_size)
            # display the image to the user
            # str(self.filter_position[self.i])\
            cv2.imshow("Filter ID: " + str(self.current_filter_ID) + "     Filter Position: " + str(self.list_index + 1)\
                    + "     Filter Date: " + str(self.filter_date[self.i]) + "       Press SPACE to save or ENTER to retake.", captured_image)
            # self.csv_filter_position = str(self.filter_position[self.i])
            self.csv_filter_position = str(self.i + 1)
            self.csv_filter_date = str(self.filter_date[self.i])
            # waitkey displays the image to the screen until the user presses any key
            self.key = cv2.waitKey(0)
            if self.key == 32:
                self.i += 1
                self.list_index += 1
                # this closes the image that was being displayed
                cv2.destroyAllWindows()
                # save the file
                cv2.imwrite(p, captured_image)
                csv_creation(p2, str(self.current_filter_ID), self.csv_filter_position, self.csv_filter_date)
                # process_image_function_r('C:/Users/hanna/OneDrive/Pictures/green.jpg')
                print("Image Saved {}".format(filename))
            if self.key == 13:
                cv2.destroyAllWindows()

        if self.i >= len(self.filter_id):
            self.i = 0
            self.second_top = Toplevel(self.root)
            self.second_top.geometry("800x50")
            Message(self.second_top, text='Tray Complete! Please Select New Tray.', width=800, anchor='center',
                    font=("Courier", 20)).pack()
            self.enter_button_pressed = False

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of the quit process to continue
        print("program closing...")
        self.stopEvent.set()
        self.stopArduino.set()
        self.vs.stream.release()
        self.vs.stop()
        self.root.destroy()
        # force exit program
        os._exit(0)


# specify the image path of where to save the captured images
image_path = "C:/Research/Microscope/Images"

# specify the video source, likely 0 or 1
vs = VideoStream(0).start()
time.sleep(1)

# create an instance of the MicroscopeImages class and start the main loop of the tkinter window
microscope_images_instance = MicroscopeImages(vs, image_path)
microscope_images_instance.root.mainloop()
