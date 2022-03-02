import cv2
import numpy
from PIL import Image
import seaborn
import matplotlib.pyplot as plt
import pandas
from scipy.signal import argrelextrema, savgol_filter, find_peaks
from scipy.stats import gaussian_kde

image_path = 'C:/Users/hanna/OneDrive/Pictures/filterExample.jpg'
xmin = 500
xmax = 1000
ymin=600
ymax = 1000

gray_image = cv2.imread(image_path, 0)
# cv2.imshow('image', gray_image)
# cv2.waitKey(0)

gray_image = gray_image[xmin:xmax, ymin:ymax]
# cv2.imshow("Cropped", gray_image)
# cv2.waitKey(0)

pixel_values = []

for i in range(gray_image.shape[0]):
    for j in range(gray_image.shape[1]):
        pixel_values.append(int(gray_image[i][j]))

# print(pixel_values)

pixel_data_frame = pandas.DataFrame(pixel_values, columns=['pixels'])
sorted_pixel_data_frame = pixel_data_frame.sort_values('pixels')
pixel_array = numpy.array(pixel_values)
count = sorted_pixel_data_frame['pixels'].value_counts(sort=False)
sorted_array = numpy.sort(pixel_array)
#print(sorted_array)
smoothed = savgol_filter(sorted_array, 7, 0)
#print(smoothed)
new_df = pandas.DataFrame(smoothed)
new_df.plot()
plt.show()

# print(pixel_array)

pixel_data_frame.pixels.plot.density(color='black')
plt.title('Density Plot for Pixels')
plt.show()
print(pixel_data_frame.pixels.density)

# peaks = find_peaks(smoothed)
# print(peaks)
# density = gaussian_kde(pixel_data_frame)
# ys = density(xs)
# index = np.argmax(ys)
# max_y = ys[index]
# max_x = xs[index]

# count.plot()
# plt.show()

