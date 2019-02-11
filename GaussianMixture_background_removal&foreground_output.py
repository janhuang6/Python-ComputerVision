import cv2
import argparse
import os
import glob
import re

def bg_removal(video_file, video_out):
    cap = cv2.VideoCapture(video_file)
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    ret, frame = cap.read()

    while (ret):
        fgmask = fgbg.apply(frame) #, learningRate=0.001)
        cv2.namedWindow("Original")
        cv2.imshow('Original',frame)
        mask_rgb = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2RGB)
        fg = cv2.bitwise_and(frame, mask_rgb)
        cv2.namedWindow("Background Removal")
        cv2.imshow('Background Removal', fg)
        video_out.write(fg)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()

def get_video_parameter(video_file):
    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()
    height, width = frame.shape[:2]

    print("Video width, height: {0}, {1}".format(width, height))

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    if int(major_ver) < 3:
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = cap.get(cv2.CAP_PROP_FPS)

#    print("Frames per second: {0}".format(fps))
    cap.release()
    return width, height, fps

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_one_frame(file, output_path):
    print("Processing video", file)
    width, height, fps = get_video_parameter(file)

    m = re.search("\d", file)
    part = file[m.start():]
    output_file = output_path + '/' + part
    ensure_dir(output_file)
    video_out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    bg_removal(file, video_out)
    video_out.release()   # We close out this after one video is done

def main():
    """ Main application to remove background on video frames and output to another video.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', help='Input path of video source.'
                                                            'If it is a filename it will process the file only.'
                                                            'If it is a folder it will process all the files with'
                                                            'the extension specified by the -e parameter',
                        required=True)
    parser.add_argument('-o', '--output', dest='output', help='Output folder to store extracted fg results',
                        required=True)
    parser.add_argument('-e', '--ext', dest='ext', help='File extension if input is a folder', default='mp4',
                        required=False)

    args = parser.parse_args()

    if os.path.isdir(args.input):
        if args.ext is None:
            raise ValueError("When processing folder as input source, file extension for video to be processed"
                             "has to be filled")
        for index, file in enumerate(list(glob.glob(os.path.join(args.input, "*." + args.ext)))):
            process_one_frame(file, args.output)
    else:
        file = args.input
        process_one_frame(file, args.output)


if __name__ == "__main__":
    main()
