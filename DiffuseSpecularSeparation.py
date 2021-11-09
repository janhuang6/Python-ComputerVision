# This code decomposes gradient and complement input images into diffuse and specular components.

# importing OpenCV(cv2) module
import cv2
import statistics
import numpy as np
import sys

def Fresnel(specAlbedo, saturate):
#    print('saturate=', saturate)
    return specAlbedo/255. + (1.0 - specAlbedo/255.) * pow((1.0 - saturate/255.), 5.0);

def PrintImageRange(img):
    ma = -sys.maxsize
    mi = sys.maxsize 
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for idx in range(img.shape[2]):
                if ma <img[i,j,idx]:
                    ma = img[i,j,idx]
                if mi >img[i,j,idx]:
                    mi = img[i,j,idx]

    print(' Value ranges from ', mi, ' to ', ma)
 
def PrintDataRange(data):
    ma = -sys.maxsize
    mi = sys.maxsize 
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if ma <data[i,j]:
                ma = data[i,j]
            if mi >data[i,j]:
                mi = data[i,j]

    print(' Value ranges from ', mi, ' to ', ma)
 
if __name__ == '__main__':
    # Read images using OpenCV
    # First, load gradient images

    gradients = []
    gradients_hsv = []

    gradients.append(cv2.imread('X.jpg'))
    gradients.append(cv2.imread('Y.jpg'))
    gradients.append(cv2.imread('Z.jpg'))

    for idx in range(len(gradients)):
        print('gradients['+str(idx)+']')
        PrintImageRange(gradients[idx])

    # convert BGR to HSV
    for img in gradients:
        gradients_hsv.append(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
        print('gradients_hsv[.]')
        PrintImageRange(img)

   # Output gradient img with window name (All imshow() are disabled because this code is running on GPU box remotely)
    #for idx in range(len(gradients_hsv)):
        #cv2.imshow('gradients_hsv'+str(idx), gradients_hsv[idx])

    # Second, do the same for complement images

    complements = []
    complements_hsv = []

    complements.append(cv2.imread('X\'.jpg'))
    complements.append(cv2.imread('Y\'.jpg'))
    complements.append(cv2.imread('Z\'.jpg'))

    for idx in range(len(complements)):
        print('complements['+str(idx)+']')
        PrintImageRange(complements[idx])

        if gradients[idx].shape != complements[idx].shape:
            print('gradients['+str(idx)+'] and complements['+str(idx)+'] are not the same size')
            quit()

    # convert BGR to HSV
    for img in complements:
        complements_hsv.append(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
        print('complements_hsv[.]')
        PrintImageRange(img)

   # Output complement img with window name
    #for idx, img in complements_hsv:
        #cv2.imshow('complements_hsv'+str(idx), img)

    # Compute specular image from formula 2 of the paper
    # "Diffuse-Specular Separation using Binary Spherical Gradient Illumination"
    tol = 1e-09
    num_zeros=0;
    num_blk_outlier=0;
    blk_outlier_threshold=20
    delta = np.zeros((gradients_hsv[0].shape[0], gradients_hsv[0].shape[1]))
    for i in range(gradients_hsv[0].shape[0]):
        for j in range(gradients_hsv[0].shape[1]):
            blk_outlier_exclusion=0
            for idx in range(len(gradients_hsv)):
                if (gradients_hsv[idx][i,j,2] < blk_outlier_threshold) or \
                   (complements_hsv[idx][i,j,2] < blk_outlier_threshold):
                    blk_outlier_exclusion = blk_outlier_exclusion + 1
                    num_blk_outlier = num_blk_outlier + 1
            if blk_outlier_exclusion == 3:
                delta[i,j] = 0
                print('Threshold is so high that all 3 pairs are excluded')
                continue

            pix = np.zeros(len(gradients_hsv)-blk_outlier_exclusion)
            idx1 = 0
            for idx in range(len(gradients_hsv)):
                if (gradients_hsv[idx][i,j,2] < blk_outlier_threshold) or \
                   (complements_hsv[idx][i,j,2] < blk_outlier_threshold):
                    continue	 
                if abs(complements_hsv[idx][i,j,1]) < tol: # Formula 2 cannot be used in case of dividing by zero
                    num_zeros = num_zeros+1
                    if i==0 and j==0:
                        pix[idx1] = 0
                    elif j > 0:
                        pix[idx1] = delta[i, j-1] # From the pixel on its left
                    else:
                        pix[idx1] = delta[i-1, j] # From the pixel on its top
                else:
                    # Compute chroma
                    C = max(gradients[idx][i,j]) - min(gradients[idx][i,j])
                    # By Formula 2
                    pix[idx1] = gradients_hsv[idx][i,j,2] - C/complements_hsv[idx][i,j,1]
                idx1 = idx1 + 1
 
            delta[i, j] = statistics.median(pix)
    print('delta')
    PrintDataRange(delta)

    specular = np.zeros((delta.shape[0], delta.shape[1], 3))
    for i in range(delta.shape[0]):
        for j in range(delta.shape[1]):
            f = Fresnel(delta[i, j], gradients_hsv[2][i, j, 1])
            rho = delta[i, j] * f * 0.4

            specular[i, j] = [rho, rho, rho] # specular is grayscale image saved in BGR format, i.e, B = G = R

    print('specular')
    PrintImageRange(specular)

    print('num_zeros=', num_zeros)
    print('num_zeros%=', float(num_zeros)/float(gradients_hsv[0].shape[0]*gradients_hsv[0].shape[1]*gradients_hsv[0].shape[2]))
    print('num_blk_outlier=', num_blk_outlier)
    print('num_blk_outlier%=', float(num_blk_outlier)/float(gradients_hsv[0].shape[0]*gradients_hsv[0].shape[1]*gradients_hsv[0].shape[2]))

    mixed = np.zeros((delta.shape[0], delta.shape[1], 3))
    for i in range(delta.shape[0]):
        for j in range(delta.shape[1]):
	    if gradients_hsv[2][i, j, 2] > complements_hsv[2][i, j, 2]:
		mixed[i, j] = gradients[2][i, j]
	    else:
		mixed[i, j] = complements[2][i, j]
    print('mixed')
    PrintImageRange(mixed)

    diffuse = cv2.subtract(mixed, specular, dtype=cv2.CV_64FC3) # or convert it before subtraction: image = np.asarray(image, np.float64)
    print('diffuse')
    PrintImageRange(diffuse)
    cv2.imwrite('diffuse_bfe_normalize.jpg', diffuse)

    ma = -sys.maxsize
    mi = sys.maxsize 
    for i in range(diffuse.shape[0]):
        for j in range(diffuse.shape[1]):
            for idx in range(diffuse.shape[2]):
                if ma <diffuse[i,j,idx]:
                    ma = diffuse[i,j,idx]
                if mi >diffuse[i,j,idx]:
                    mi = diffuse[i,j,idx]

    span = ma - mi
    for i in range(diffuse.shape[0]):
        for j in range(diffuse.shape[1]):
            for idx in range(diffuse.shape[2]):
                diffuse[i,j,idx] = (diffuse[i,j,idx]-mi)*255./span	
    print('diffuse after normalization')
    PrintImageRange(diffuse)
 
    cv2.imwrite('mixed.jpg', mixed)
    cv2.imwrite('diffuse.jpg', diffuse)
    cv2.imwrite('specular.jpg', specular)

    #cv2.imshow('mixed', mixed)
    #cv2.imshow('specular albedo', specular)
    #cv2.imshow('diffuse albedo', diffuse)

    # Maintain output window until user presses a key
    #cv2.waitKey(0)

    # Destroy present windows on screen
    #cv2.destroyAllWindows()

# End of __main__
