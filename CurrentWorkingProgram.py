# Import important python packages and modules
import cv2
import os
import serial
from datetime import datetime

# Get current date and time in mm-dd-YY and H-M:- format
current_date_time = datetime.now()
date_time_string = current_date_time.strftime("%m-%d-%Y T%H-%M-%S")


# Initiate communication between the arduino and laptop
# Set the correct port for the arduino
ser = serial.Serial(port="COM6")


# Set initial variables
# max_bits is the number of bytes used in calculating the average
max_bits = 10
# Clicks is the list that stores the last 10 bits
clicks = []


# The mean function finds the average of the values stored in clicks
def mean(nums):
    return float(sum(nums)) / max(len(nums), 1)


# # Create a function to display the real-time video feed
# def begin_video_feed():
#     cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
#
#     # Capture the video frame
#     # by frame
#     ret, frame = cam.read()
#
#     # Display the resulting frame
#     cv2.imshow('frame', frame)
#
#     # the 'q' button is set as the
#     # quitting button you may use any
#     # desired button of your choice
#     if video_feed_state == False or cv2.waitKey(1) & 0xFF == ord('q'):
#         cam.release()
#         cv2.destroyAllWindows()


# The image_function is responsible for capturing, naming, and saving the image
def image_function():
    # Set up / initialize the camera with the correct port number (usually 0 or 1)
    # cv2.CAP_DSHOW specifies the video source on windows
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    # .read() returns a boolean and image content
    result, image = cam.read()

    # If the image was detected (i.e. the boolean (result) is True), then display and save the image
    if result:
        # Outputting and displaying the result
        # imshow takes in the image name and the image content
        cv2.imshow(date_time_string, image)

        # waitkey displays the image to the screen until the user presses any key
        cv2.waitKey(0)

        # Set variables for the file name and storage
        # The file_name is set to the date and time of the picture
        image_path = "C:/Users/hanna/PycharmProjects/microscopeImages"
        file_name = date_time_string

        # imwrite saves the image to local storage
        cv2.imwrite(os.path.join(image_path, file_name + ".png"), image)

    else:
        print("No image detected.")

    cv2.destroyAllWindows()


# The main operation function facilitates communication with the arduino and then executes the
# image function based on whether the button is pressed or not
def main_operation():
    while True:
        try:
            # Read the bytes from the arduino and decode them into bits
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes.decode('utf-8').strip()
            print(decoded_bytes)

            # Append the bits into the clicks list and calculate the average of the last 10
            if decoded_bytes != '' and len(decoded_bytes) == 1:
                clicks.append(int(decoded_bytes))
            avg = float(mean(clicks))

            # If the length of the clicks list is longer than max_bits, the oldest bit is removed
            # This ensures that the list only stays at a length of 10
            if len(clicks) == max_bits:
                clicks.pop(0)

            # If the bit is 1 (meaning the button has been pressed) and the average of the last
            # ten bits is less than 0.1 (meaning the '1' is an actual click and not just 'bouncing'
            if decoded_bytes == "1" and avg <= 0.1:
                image_function()

        # If you press stop, the program will stop running
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            break


main_operation()
