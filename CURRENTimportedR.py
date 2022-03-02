import cv2
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


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

# Defining the R script and loading the instance in Python
r = robjects.r
r['source']('ImageAnalysis.R')

process_image_function_r = robjects.globalenv['processImage']
integrate_peak_function_r = robjects.globalenv['integratePeak']
process_image_function_r = robjects.globalenv['processImage']
find_peaks_function_r = robjects.globalenv['findPeaks']

# process_image_function_r('C:/Users/hanna/OneDrive/Pictures/filterExample.jpg')




