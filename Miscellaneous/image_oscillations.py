import os
import matplotlib.pyplot as plt
import numpy as np
import cv2

if __name__ == "__main__":
    im1 = cv2.imread("/Users/jasonyuan/Desktop/Pressure Test Trial 1/DSC07462.JPG") # Reference image
    n = 226
    files = sorted(os.listdir("/Users/jasonyuan/Desktop/Pressure Test Trial 1"))
    for i in range(109,len(files)):
        file = files[n]

        if file == ".DS_Store":
            continue

        print(file)
        # im2 = cv2.imread("/Users/jasonyuan/Desktop/Pressure Test Trial 1/DSC07578.JPG")
        im2 = cv2.imread("/Users/jasonyuan/Desktop/Pressure Test Trial 1/"+file)
        im1_g = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
        im2_g = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)
        # im_diff = np.abs(im1_g - im2_g)

        im_diff = im1_g.astype(np.float64) - im2_g.astype(np.float64)
        # im_diff = (im_diff + np.abs(np.min(im_diff)))/(np.max(im_diff) - np.min(im_diff)) * 255
        # im_diff = im_diff.astype(np.uint8)

        # np.savetxt("/Users/jasonyuan/Desktop/im_diff",im_diff)
        # print(np.mean(im_diff))
        # print(im2_g)
        # print(im1_g)
        # print(im_diff)
        # print(np.min(im_diff), np.max(im_diff))

        bounds = max(abs(np.min(im_diff)),np.max(im_diff))

        fig = plt.figure()
        # ax1 = fig.add_subplot(1,2,1)
        # ax2 = fig.add_subplot(1,2,2)
        ax2 = fig.add_subplot(1,1,1)

        # im_gray = ax1.imshow(im1_g,cmap='gray',vmin=0,vmax=255,interpolation='none')
        # cbar_1 = fig.colorbar(im_gray,ax=ax1,fraction=0.046,pad=0.04)
        # cbar_1.minorticks_on()
        # ax1.set_title("Grayscale original image")

        im_diff_gray = ax2.imshow(im_diff,cmap='RdBu',vmin=-10,vmax=10,interpolation='none')
        cbar_2 = fig.colorbar(im_diff_gray,ax=ax2,fraction=0.046,pad=0.04)
        cbar_2.minorticks_on()
        ax2.set_title("Grayscale difference image (mean: {})".format(np.mean(im_diff)))

        plt.savefig("/Users/jasonyuan/Desktop/Differentials/Pic_{}.png".format(n))
        plt.close('all')
        n+=1
        # plt.show()

  # cv2.imshow("Gray 1", im1_g)
  # cv2.imshow("Gray difference",im_diff)
  # # cv2.imwrite("/Users/jasonyuan/Desktop/Image_Diff.png",im_diff)
  #
  # cv2.waitKey(0)
