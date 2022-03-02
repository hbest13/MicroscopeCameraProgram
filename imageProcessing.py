import cv2
import numpy
from PIL import Image
import seaborn
import matplotlib.pyplot as plt
import pandas


def process_image(image_path, xmin = 500, xmax = 1200, ymin=600, ymax = 1300):
    gray_image = cv2.imread(image_path, 0)
    # cropped_image = gray_image[xmin:xmax, ymin:ymax]
    # cv2.imshow("Cropped", cropped_image)
    # cv2.waitKey(0)

    pixel_values = []

    for i in range(gray_image.shape[0]):
        for j in range(gray_image.shape[1]):
            pixel_values.append(int(gray_image[i][j]))

    # print(pixel_values)

    pixel_data_frame = pandas.DataFrame(pixel_values, columns=['pixels'])

    pixel_data_frame.pixels.plot.density(color='black')
    plt.title('Density Plot for Pixels')
    plt.show()

def find_peaks(image_data_frame):
