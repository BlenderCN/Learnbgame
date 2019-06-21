import sys 
sys.path.append("/usr/local/lib/python3.7/dist-packages/cv2/")
import cv2

cv2.DAISY_NRM_NONE = cv2.xfeatures2d.DAISY_NRM_NONE
cv2.DAISY_NRM_PARTIAL = cv2.xfeatures2d.DAISY_NRM_PARTIAL
cv2.DAISY_NRM_FULL = cv2.xfeatures2d.DAISY_NRM_FULL
cv2.DAISY_NRM_SIFT = cv2.xfeatures2d.DAISY_NRM_SIFT

# For OCVLPreviewNodeBase common texture cache
TEXTURE_CACHE = {}
# For OCVLNodeBase common data socket cache
SOCKET_DATA_CACHE = {}
# For draw_handler_add callback cache
CALLBACK_DICT = {}
# Video capture for default camera
CAMERA_DEVICE_DICT = {}
# Dict to keep initializations objects of Feature2D
FEATURE2D_INSTANCES_DICT = {}
# Dict to keep initialization objects of DescriptorMacher
DESCRIPTORMATCHER_INSTANCES_DICT = {}
