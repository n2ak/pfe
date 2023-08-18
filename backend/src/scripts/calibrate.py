import numpy as np
import cv2 as cv
import pickle
from src.utils import calibrate

################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################


if __name__ == "__main__":
    images_path = 'Cv/*.jpg'
    chessboardSize = (9, 6)
    frameSize = (640, 480)
    size_of_chessboard_squares_mm = 20
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)

    ret, cameraMatrix, dist, rvecs, tvecs = calibrate(
        images_path,
        chessboardSize,
        size_of_chessboard_squares_mm=size_of_chessboard_squares_mm,
        frameSize=frameSize,
        show_chessboard=False,
    )
    np.save("cameraMatrix.npy", cameraMatrix)
    print(cameraMatrix.shape)
    print(np.load("cameraMatrix.npy").shape)
    # Save the camera calibration result for later use (we won't worry about rvecs / tvecs)
    pickle.dump((cameraMatrix, dist), open("calibration.pkl", "wb"))
    pickle.dump(cameraMatrix, open("cameraMatrix.pkl", "wb"))
    pickle.dump(dist, open("dist.pkl", "wb"))
    print("Done")
    print("Camera matrix:")
    print(cameraMatrix)
