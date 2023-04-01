import numpy as np
import cv2 as cv
import glob
import pickle


################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################


def calibrate(
    size_of_chessboard_squares_mm,
    images_path,
    chessboardSize,
    frameSize=None,
    criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001),
    show_chessboard=True
):

    objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboardSize[0],
                           0:chessboardSize[1]].T.reshape(-1, 2)

    objp = objp * size_of_chessboard_squares_mm

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    images = glob.glob(images_path)
    for image in images:
        img = cv.imread(image)
        if frameSize is None:
            h, w = img.shape[:2]
            frameSize = w, h

        print("Image shape:", img.shape)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

        # If found, add object points, image points (after refining them)
        if ret == True:

            objpoints.append(objp)
            corners2 = cv.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)

            # Draw and display the corners
            if show_chessboard:
                cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
                cv.imshow('img', cv.resize(
                    img, (img.shape[1]//2, img.shape[0]//2)))

                cv.waitKey()
    ret = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)
    cv.destroyAllWindows()
    return ret


if __name__ == "__main__":
    images_path = 'calibration/*.png'
    chessboardSize = (9, 6)
    frameSize = (640, 480)
    size_of_chessboard_squares_mm = 20
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)

    ret, cameraMatrix, dist, rvecs, tvecs = calibrate(
        size_of_chessboard_squares_mm,
        images_path,
        chessboardSize,
        frameSize=frameSize,
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
