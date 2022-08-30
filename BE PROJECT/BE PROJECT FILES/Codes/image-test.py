#testing for displaying an image
import cv2
 
image = cv2.imread('21.jpg')

 
cv2.imshow('Test image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()