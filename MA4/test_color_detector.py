from color_detector import *
from utils import show
import pytest
import globals

def test_4color_image():
    output = []
    for i in range(1,8):
        img = cv2.imread('../greenscrot/{}.png'.format(i))
        bicol = apply_mask(img, green_mask)
        # show( bicol, str(i))
        # print("circle detected: ", detected)
        blob = find_blobs(bicol,show_im=True)
        # show(blob, detected)
        row = np.hstack((bicol, img))
        show(row, str(i))
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
    test_4color_image()
