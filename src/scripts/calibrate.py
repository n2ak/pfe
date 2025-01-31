import numpy as np
import cv2 as cv
import pickle

################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################


def calibrate(
    images_path,
    chessboardSize,
    frameSize=None,
    size_of_chessboard_squares_mm=20,
    criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001),
    show_chessboard=False,
    window_ratio=2,
):

    objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboardSize[0],
                           0:chessboardSize[1]].T.reshape(-1, 2)

    objp = objp * size_of_chessboard_squares_mm

    objpoints = []
    imgpoints = []
    import glob
    images = glob.glob(images_path)
    print(f"Found {len(images)} images")
    import tqdm
    for image in tqdm.tqdm(images):
        img = cv.imread(image)
        if frameSize is None:
            h, w = img.shape[:2]
            frameSize = w, h

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

        if ret == True:

            objpoints.append(objp)
            corners2 = cv.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)

            if show_chessboard:
                cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
                cv.imshow('img', scale_img(img, window_ratio))

                cv.waitKey()
    print(f"Using {len(objpoints)} points to calibrate the camera.")
    ret = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)
    cv.destroyAllWindows()
    return ret


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
