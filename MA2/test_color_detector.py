from color_detector import *
from utils import show
import pytest


def test_wheel():
    img = cv2.imread('./img/color_wheel.jpg')
    output = img.copy()
    for c in MASKS.keys():
        print(" === " + c)
        bicol = apply_mask(img, MASKS[c])
        output = np.hstack((bicol, output))
    show(output)


def test_4color_image():
    output = []
    for c in MASKS.keys():
        # print(" === " + c)
        img = cv2.imread('./img/{}.jpg'.format(c))
        bicol = apply_mask(img, MASKS[c])
        # show( bicol,c)
        detected, el = circle_detector(bicol)
        # print("circle detected: ", detected)
        blob = cv2.ellipse(img.copy(), el, (120, 255, 0), 5)
        # show(blob, detected)
        row = np.hstack((bicol, blob))
        show(row)
        # if len(output) == 0:
        #     output= bicol.copy()
        #     output = np.hstack((output, blob))
        # output = np.concatenate((output, row), axis=0)
        # else:
        # output = np.hstack((output, bicol))
        # output = np.hstack((output, blob))
    # show(output)

def test_4color_find_colored_circle():
    colors = list(MASKS.keys())
    colors.extend(['black', 'white'])
    imgs = ['./img/{}.jpg'.format(c) for c in colors]
    for f in imgs:
        img = cv2.imread(f)
        res = find_colored_circle(img)
        res.sort(key=lambda x: x[1], reverse=True)
        colors = [x[0] for x in res]
        els = [x[2] for x in res]
        blob = img.copy()
        for el in els:
            blob = cv2.ellipse(blob, el, (120, 255, 0), 5)
        row = np.hstack((img, blob))
        show(row, str(colors))

def test_video(video_file='img/320x240.mp4'):
    video = cv2.VideoCapture(video_file)
    if (video.isOpened() == False):
        print('Error read video')
    rgb_color = {
        'blue': (255, 0, 0),
        'red': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (0, 255, 255),
    }
    paused = False
    while(video.isOpened()):
        # Capture frame-by-frame
        ret, frame = video.read()
        if ret == True:
            # Display the resulting frame
            # cv2.imshow('Frame',frame)
            current_col = ""
            output = frame.copy()

            bicol = {}
            for c, mask_fn in MASKS.items():
                bicol[c] = apply_mask(frame, mask_fn)
                detected, el = circle_detector(bicol[c])
                if detected:
                    current_col += c
                    cv2.ellipse(output, el, rgb_color[c], 5)
                current_col += '\t'

            for c, img in bicol.items():
                output = np.hstack((output, img))
            cv2.imshow('Frame', output)
            print(current_col)
            if not paused:
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                if key == ord('p'):
                    cv2.waitKey(-1)  # wait until any key is pressed
                    paused = True
            if paused:
                key = cv2.waitKey(0)
                if key == ord('q'):
                    break
                if key == ord('p'):
                    # cv2.waitKey(-1) #wait until any key is pressed
                    paused = False
        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    video.release()

    # Closes all the frames
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # test_video('img/raspi_320x240.h264')
    test_4color_find_colored_circle()
