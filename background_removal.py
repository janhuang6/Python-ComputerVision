import cv2


if __name__ == "__main__":
    """ Main application to remove background on video frames.
    """

    cap = cv2.VideoCapture(
        '/Users/janhuang/Projects/pi_shoppe_videos/Video/1-20181127-1400/1543358520000/b6c0074f5ae8fcea.mp4')
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    ret, frame = cap.read()

    while (ret):
        fgmask = fgbg.apply(frame)
#        cv2.imshow('frame',fgmask)
        mask_rgb = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2RGB)
        fg = cv2.bitwise_and(frame, mask_rgb)
        cv2.imshow('frame', fg)

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()
