from color_detector import *
from utils import show
import pytest

def test_4color_image():
    output = []
    for i in range(1,8)
        img = cv2.imread('../greenscrot/{}.png'.format(i))
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

if __name__ == '__main__':
    # test_video('img/raspi_320x240.h264')
    test_4color_find_colored_circle()
