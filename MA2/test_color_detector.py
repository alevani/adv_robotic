from color_detector import *
import pytest


def test_wheel():
    for c in MASKS.keys():
        print(" === " + c)
        img = imread('./img/color_wheel.jpg')
        bicol = apply_mask(img, MASKS[c])
        imshow(c, bicol)
        waitKey(0)
        destroyWindow(c)


def test_4color_image():
    for c in MASKS.keys():
        print(" === " + c)
        img = imread('./img/{}.jpg'.format(c))
        bicol = apply_mask(img, MASKS[c])
        show( bicol,c)
        detected, el = circle_detector(bicol)
        print("circle detected: ", detected)
        blob = cv2.ellipse(img.copy(),el, (120, 255, 0), 5)
        show(blob, detected)


def test_video():
    video = VideoCapture('img/320x240.mp4')
    if (video.isOpened()== False):
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
                current_col += c + ' '
                cv2.ellipse(output,el, rgb_color[c], 5)

        for c, img in bicol.items():
            output = np.hstack((output, img))
        cv2.imshow('Frame',output)
        print(current_col)
        if not paused:
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('p'):
                cv2.waitKey(-1) #wait until any key is pressed
                paused = True
        if paused:
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
            if key == ord('n'):
                # cv2.waitKey(0) #wait until any key is pressed
                pass
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
    DEBUG = False
    test_video()
