from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter import Frame, StringVar, OptionMenu, TOP, BOTTOM, LEFT, RIGHT, Entry, Button
import threading
import datetime
import imutils
import cv2
import os
import serial
import time
from imutils.video import VideoStream
import csv

# Set the correct port for the arduino
ser = serial.Serial(port="COM6")


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

        # initialize the root window and image panel
        self.root = tki.Tk()
        # retrieve screen size and set to variables
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        # setting tkinter window size to size of screen
        self.root.geometry("%dx%d" % (self.width, self.height))
        self.panel = None

        # create a selection bar for the user to select the study
        self.selection_frame = Frame(self.root)
        self.selection_frame.pack(side=TOP, ipady=10)
        self.options = ["Improve",
                        "CSN",
                        "Special Studies",
                        "Custom"]
        self.selected_study = StringVar(self.selection_frame)
        self.selected_study.set("Select a Study")
        self.study_selection = OptionMenu(self.selection_frame, self.selected_study, *self.options, command=self.selected_options)
        self.study_selection.pack()

        # create an input area for the user to enter the Study Tray ID number
        self.study_tray_ID_frame = Frame(self.root)
        self.study_tray_ID_frame.pack(side=TOP, ipady=5)
        self.study_tray_ID_entry = StringVar(self.study_tray_ID_frame)
        self.study_tray_ID_entry.set("Enter a Study Tray ID")
        self.study_tray_ID = Entry(self.study_tray_ID_frame)
        self.study_tray_ID.pack()

        enter_button = Button(self.root, text="Enter", command=self.print_ID)
        enter_button.pack()

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
        self.tray_ID = int(self.study_tray_ID.get())
        print(self.tray_ID)

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
                    self.panel.pack(side="left", padx=10, pady=10)

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
            if decoded_bytes == "1" and avg <= 0.1:
                time.sleep(2)
                self.takeSnapshot()

    def takeSnapshot(self):
        # grab the current timestamp and use it to construct the output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        captured_image = self.frame.copy()
        # percent by which the image is resized
        scale_percent = 16

        # calculate the 50 percent of original dimensions
        scaled_width = int(captured_image.shape[1] * scale_percent / 100)
        scaled_height = int(captured_image.shape[0] * scale_percent / 100)

        # dsize
        scaled_size = (scaled_width, scaled_height)
        captured_image = cv2.resize(captured_image, scaled_size)
        # display the image to the user
        cv2.imshow("Image", captured_image)
        # waitkey displays the image to the screen until the user presses any key
        cv2.waitKey(0)
        # this closes the image that was being displayed
        cv2.destroyAllWindows()
        # save the file
        cv2.imwrite(p, captured_image)
        print("Image Saved {}".format(filename))

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
image_path = "C:/Users/hanna/PycharmProjects/microscopeImages"
# specify the video source, likely 0 or 1
vs = VideoStream(1).start()
time.sleep(1)

# create an instance of the MicroscopeImages class and start the main loop of the tkinter window
microscope_images_instance = MicroscopeImages(vs, image_path)
microscope_images_instance.root.mainloop()
