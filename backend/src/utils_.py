import pickle
import glob
import numpy as np
import matplotlib.pyplot as plt
import cv2
# from lane import LaneDetectorBase
# from car import CarDetector
cv = cv2


def circle_at(ee, p): cv2.circle(ee, p, 30, (255, 255, 255))


def read_rgb(path):
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)


def draw_text_with_backgraound(frame, texts: str, x, y, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=.8, font_thickness=2, offset=20):
    texts = texts.split("\n")
    for text in texts:
        (text_width, text_height), _ = cv2.getTextSize(
            text, font, font_scale, font_thickness)
        cv2.rectangle(frame, (x, y), (x + text_width, y + text_height + 5),
                      (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, text, (x, y + offset),
                    font, font_scale, (0, 255, 0), font_thickness)
        y = y+text_height+5


def draw_main_window(frame, fr):
    show_window("Main window", frame, fr)


def put_text(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(100, 255, 0), **kwargs):
    cv2.putText(frame, text, org, font, scale, color, **kwargs)


def lane_detect_one_frame(detector, frame):
    detector.pipeline(frame)
    if detector.detected_lines:
        is_in_lane = detector.is_in_lane()
        put_text(frame, f"In lane: {bool(is_in_lane)}", (7, 50), thickness=2)
    return frame


def car_detect_one_frame(detector, frame):
    detector.detect(frame)
    return frame


def init_polygon(config: dict, H: int):
    polygon_height = config.get("polygon_height", 300)
    lane_center1 = config.get("lane_center1", 585), H - polygon_height
    lane_width1 = config.get("lane_width1", 250)
    lane_center2 = config.get("lane_center2", 638), H
    lane_width2 = config.get("lane_width2", 800)
    offset = config["offset"]
    top_left = lane_center1[0]-lane_width1//2, lane_center1[1]
    top_right = lane_center1[0]+lane_width1//2, lane_center1[1]
    bottom_right = lane_center2[0]+lane_width2//2, lane_center2[1] - offset
    bottom_left = lane_center2[0]-lane_width2//2, lane_center2[1] - offset

    polygon = [top_left, top_right, bottom_right, bottom_left]
    polygon = np.array(polygon)
    return np.array([polygon], dtype=np.int32)


def getOptimalNewCameraMatrix(shape, cameraMatrix, distortion, alpha=1):
    h,  w = shape
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        cameraMatrix, distortion, (w, h), alpha, (w, h))
    return newcameramtx, roi


def undistort(img, cameraMatrix, distortion, alpha=1, crop=False, use_optimal=True):
    h,  w = img.shape[:2]
    kwargs = {}
    if use_optimal:
        newcameramtx, roi = getOptimalNewCameraMatrix(
            (h,  w), cameraMatrix, distortion)
        kwargs["newCameraMatrix"] = newcameramtx
    dst = cv2.undistort(img, cameraMatrix, distortion, **kwargs)
    if use_optimal and crop:
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
    return dst


def equalize_hist(gray, thresh=150, type=cv2.THRESH_BINARY):
    # https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
    gray = cv2.equalizeHist(gray)
    _, th = cv2.threshold(gray, thresh, maxval=255, type=type)
    return th


def show_img(img, figsize=None, **kwargs):
    figsize = figsize or (5, 5)
    plt.figure(figsize=figsize)
    plt.imshow(img, **kwargs)
    plt.axis('off')
    plt.show()


def show_gray_img(img, **kwargs):
    show_img(img, cmap='gray', **kwargs)


def grad(im, ddepth, delta, scale, vert=False):
    dx, dy = 1, 0
    if vert:
        dx, dy = dy, dx
    grad_x = cv.Sobel(im, ddepth, dx, dy, ksize=3, scale=scale,
                      delta=delta, borderType=cv.BORDER_DEFAULT)
    return cv.convertScaleAbs(grad_x)


def sobel(gray, scale=1, delta=0, ddepth=cv.CV_16S, both=False):
    gray_x = grad(gray, ddepth, delta, scale)
    if not both:
        return gray_x
    gray_y = grad(gray, ddepth, delta, scale, True)
    out = cv.addWeighted(gray_x, 0.5, gray_y, 0.5, 0)
    return out


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

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    images = glob.glob(images_path)
    print(f"Found {len(images)} images")
    import tqdm
    for image in tqdm.tqdm(images):
        img = cv.imread(image)
        if frameSize is None:
            h, w = img.shape[:2]
            frameSize = w, h

        # print("Image shape:", img.shape)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)
        # print("Ret", ret)
        # If found, add object points, image points (after refining them)
        if ret == True:

            objpoints.append(objp)
            corners2 = cv.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)

            # Draw and display the corners
            if show_chessboard:
                cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
                cv.imshow('img', scale(img, window_ratio))

                cv.waitKey()
    print(f"Using {len(objpoints)} points to calibrate the camera.")
    ret = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)
    cv.destroyAllWindows()
    return ret


def dilate(gray, kernel=(50, 50), iterations=10):
    return cv2.dilate(gray, kernel, iterations)


class CameraInfo:
    def __init__(self, info) -> None:
        self.ret, self.cameraMatrix, self.dist, self.rvecs, self.tvecs = info


def save_camera_info(camInfo, path="../cameraInfo.pkl"):
    with open(path, "wb") as f:
        pickle.dump(camInfo, f)
        print("Saved")


def load_camera_info(path="../cameraInfo.pkl") -> CameraInfo:
    with open(path, "rb") as f:
        return pickle.load(f)


def mask_road(image, polygon):
    mask = np.zeros_like(image)
    mask = cv2.fillPoly(mask, polygon, (255, 255, 255))
    return cv2.bitwise_and(image, mask)


def lines_HTP(edges_img, threshold=100, thickness=2):
    ret_img = np.zeros_like(edges_img)
    lines = cv2.HoughLinesP(edges_img, 1, np.pi/180, threshold)
    if lines is not None:
        print("found", len(lines), "lines")
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(ret_img, (x1, y1), (x2, y2), (255, 0, 255), thickness)
    return lines, ret_img


def draw_line_to_object(im, object_box, color=(0, 255, 0)):
    h, w = im.shape[:2]
    x, y, ow, oh = object_box
    p1, p2 = (w//2, h), (x+ow//2, y+oh)
    cv2.circle(im, p2, 30, color, 10)
    cv2.arrowedLine(im, p1, p2, color, 40)
    return im


def draw_distance_to_object(
    im,
    object_box,
    distance,
    line_color=(0, 255, 0),
    text_color=(255, 0, 0),
    back_color=(0, 0, 0),
    font=cv2.FONT_HERSHEY_COMPLEX,
    unit="cm",
    rect_width=700,
    rect_hieght=200
):
    h, w = im.shape[:2]
    x, y, ow, oh = object_box
    p1, p2 = (w//2, h), (x+ow//2, y+oh)
    text_x, text_y = ((p1[0]+p2[0])//2 + 100, (p1[1]+p2[1])//2)
    # cv2.circle(im, (text_x, text_y),100,(255,0,0),10)
    rect_x, rect_y, rect_w, rect_h, offset = text_x, text_y, rect_width, rect_hieght, 50
    im = draw_line_to_object(im, object_box, color=line_color)
    cv2.rectangle(
        im,
        (max(0, text_x-20), max(0, text_y - rect_h//2-offset)),
        (text_x + rect_w+20, max(0, text_y + rect_h//2-offset)),
        back_color,
        -1
    )
    cv2.putText(im, f"{distance:.1f} {unit}",
                (text_x, text_y), font, 5, text_color, 10)
    return im


def lines_HT(edges_img, threshold):
    ret_img = np.zeros_like(edges_img)
    lines = cv2.HoughLines(edges_img, 1, np.pi/180, threshold)
    if lines is not None:
        print("found", len(lines), "lines")
        for line in lines:
            line = line[0]
            rho, theta = line
            import math
            a, b = math.cos(theta), math.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(ret_img, (x1, y1), (x2, y2), (255, 0, 255), 2)
    return lines, ret_img


def get_exif(fn):
    import PIL
    img = PIL.Image.open(fn)
    return img._getexif()


def warp_perspective(image, size, external_poly, flip=False, dst=None):
    size = list(size)
    h, w = size
    output_pts = np.float32([[0, 0],
                            [w - 1, 0],
                            [w - 1, h - 1],
                            [0, h - 1]])
    input_pts = np.float32(external_poly[0])

    args = input_pts, output_pts
    if flip:
        args = output_pts, input_pts
    matrice = cv2.getPerspectiveTransform(*args)
    return cv2.warpPerspective(image, matrice, (w, h), dst=dst)


def longest_lines(lines):
    lines = np.array(lines).squeeze()
    assert len(lines.shape) == 2 and lines.shape[-1] == 4
    pts1, pts2 = lines[:, :2], lines[:, 2:]
    lengths = (np.abs(pts1-pts2)**2).sum(axis=1)
    index = lengths.argmax()
    return lines[index]


def black_and_white(image):
    im = image.copy()
    # image[np.where(image != 0)] = 255
    print("same image:", (im-image).sum())
    return image


def draw_polygon(image, poly, color1=(0, 0, 255), color2=(255, 0, 0)):
    p1, p2, p3, p4 = poly
    cv2.line(image, p1, p2, color1, thickness=10)
    cv2.line(image, p2, p3, color1, thickness=10)
    cv2.line(image, p3, p4, color1, thickness=10)
    cv2.line(image, p4, p1, color1, thickness=10)

    cv2.circle(image, p1, 15, color2, -1)
    cv2.circle(image, p2, 15, color2, -1)
    cv2.circle(image, p3, 15, color2, -1)
    cv2.circle(image, p4, 15, color2, -1)

    # cv2.circle(image, lane_center1, 15, color2, -1)
    # cv2.circle(image, lane_center2, 15, color2, -1)

    return image


def get_lane_indices(image, leftx_base, rightx_base, n_windows, margin, recenter_minpix):
    window_height = image.shape[0]//n_windows
    nonzeroy, nonzerox = np.array(image.nonzero())
    left_lane_inds = []
    right_lane_inds = []
    leftx_current = leftx_base
    rightx_current = rightx_base
    for window in range(n_windows):
        win_y_low = image.shape[0] - (window + 1) * window_height
        win_y_high = image.shape[0] - window * window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        if len(good_left_inds) > recenter_minpix:
            leftx_current = int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > recenter_minpix:
            rightx_current = int(np.mean(nonzerox[good_right_inds]))
    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)
    return left_lane_inds, right_lane_inds


def histogram(image):
    hist = image.sum(axis=0)
    return hist


def histogram_peaks(hist):
    midpoint = hist.shape[0]//2
    a = np.argmax(hist[:midpoint])
    b = np.argmax(hist[midpoint:]) + midpoint
    return a, b


def polynome(coeffs, y):
    A, B, C = coeffs
    res = A * y**2 + B * y + C
    curvature = abs((2 * A) / (1 + (2 * A * y + B) ** 2) ** (3/2))
    radius = 1 / curvature
    radius = np.mean(radius)
    return radius, res


def fit_poly_one_side(image, indices, ys, nonzero):
    nonzeroy, nonzerox = nonzero
    if indices.shape == (0,):
        return []
    x = nonzerox[indices]
    y = nonzeroy[indices]
    fit = np.polyfit(y, x, 2)
    radius, fitx = polynome(fit, ys)
    return radius, fitx


def fit_poly(image, left_indices, right_indices):

    nonzero = np.array(image.nonzero())
    ys = np.linspace(0, image.shape[0]-1, image.shape[0])
    radius_left, left_fitx = fit_poly_one_side(
        image, left_indices, ys, nonzero)
    radius_right, right_fitx = fit_poly_one_side(
        image, right_indices, ys, nonzero)

    return radius_left, radius_right, left_fitx, right_fitx, ys


def get_object_distance2(f, object_size_in_image, object_size_in_real_world):
    """
    f: focal distance in pixels
    """
    return object_size_in_real_world * f / object_size_in_image


def get_object_distance(
    f,
    focal_length,
    object_size_in_image,
    object_size_in_real_world,
    ratio=1,
):
    """
    from : https://stackoverflow.com/questions/14038002/opencv-how-to-calculate-distance-between-camera-and-object-using-image
    - object_real_world in "mm"
    - object_size_in_image in "px"
    - object_size_in_real_world in "mm"
    """
    pixels_per_mm = f / focal_length
    # print(pixels_per_mm)
    pixels_per_mm = round(pixels_per_mm / ratio)
    # print(pixels_per_mm)
    object_image_sensor = object_size_in_image / pixels_per_mm
    distance = object_size_in_real_world * focal_length / object_image_sensor
    return distance  # in "mm"


def draw_curvatures(image, xs, ys, figsize=(10, 10), cmap=None, linewidth=2):
    plt.figure(figsize=figsize)
    plt.imshow(image, cmap)
    plt.axis("off")
    plt.plot(xs[0], ys, color='red', linewidth=linewidth)
    plt.plot(xs[1], ys, color='red', linewidth=linewidth)
    plt.show()
    return image


def load_f_from_file(filepath="../cameraInfo.pkl"):
    info = load_camera_info(filepath)
    print(info)
    print("found matrix:\n", info.cameraMatrix)
    return info.cameraMatrix.diagonal()[:2].mean()


def combine(image, original, use_bitwise=True):
    if use_bitwise:
        return cv2.bitwise_or(image, original)
    # image = image.copy()
    # image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    indices = (image == 0)
    indices = (image.sum(-1) == 0)
    image[indices] = original[indices]
    return image


def draw_lane_zone(image, xs, ys, step=1, color=(0, 255, 0), alpha=1, beta=0.5, gama=1.0, draw_lines=False):
    if len(xs[0]) != len(xs[1]) != len(ys):
        return image
    right, left = xs
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # show_img(image)
    prev = None
    for r, l, y in list(zip(right, left, ys))[::step]:
        curr = [l, y], [r, y]
        if prev is not None:
            points = [np.array([*curr, *prev], dtype=np.int32)]
            cv2.fillPoly(image, points, color)
            # cv2.drawContours(image, points, -1, color, thickness=cv2.FILLED)
        prev = [r, y], [l, y]
    return image


def get_curvatures(image, RECENTER_MINPIX, n_windows=10, margin=50):
    hist = histogram(image)
    left_peak, right_peak = histogram_peaks(hist)
    left_lane_inds, right_lane_inds = get_lane_indices(
        image, left_peak, right_peak, n_windows, margin, RECENTER_MINPIX)
    if left_lane_inds.size == 0 or right_lane_inds.size == 0:
        return None
    radius_left, radius_right, left_fitx, right_fitx, ys = fit_poly(
        image, left_lane_inds, right_lane_inds)
    return (radius_left, radius_right), (left_fitx, right_fitx), ys


def threshold(image, thresh, maxval=255, type=cv2.THRESH_BINARY):
    _, image = cv2.threshold(image, thresh.get_value(), maxval, type)
    return image


def seek_video(video, seconds):
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_to_seek_to = seconds * fps
    assert frame_to_seek_to < total_frames, f"{frame_to_seek_to} < {total_frames}?"
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_to_seek_to)


def read_video(video: cv2.VideoCapture, cvt=None, size=None, rotate=None):
    on, frame = video.read()
    if on:
        if rotate is not None:
            frame = cv2.rotate(frame, rotate)
        if size is not None:
            frame = cv2.resize(frame, size)
        if cvt is not None:
            frame = cv2.cvtColor(frame, cvt)

    return on, frame


def canny(image, t1, t2):
    return cv2.Canny(image, t1, t2)


def scale(frame, ratio=1, size=None):
    if size is None:
        size = (int(frame.shape[1]//ratio), int(frame.shape[0]//ratio))
    return cv2.resize(frame, size)


def show_window(name, image, ratio=1):
    image = scale(image, ratio)
    cv2.imshow(name, image)


# def put_text(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(100, 255, 0), **kwargs):
#     cv2.putText(frame, text, org, font, scale, color, **kwargs)


def timed_function(func):
    import time
    import functools
    name = func.__name__

    @functools.wraps(func)
    def func_w(*args):
        start = time.time()
        res = func(*args)
        end = time.time()
        print(f"Function ran: {name} in {end - start:.2} sec")
        return res
    return func_w
