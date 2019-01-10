import cv2


vidcap = cv2.VideoCapture('0f23af6f77bfd1c8.mp4')
success,image = vidcap.read()
count = 1 

while success:
    cv2.imwrite("%03d.jpg" % count, image)     # save frame as JPEG file      
    success,image = vidcap.read()
    count += 1
