import cv2
import matplotlib.pyplot as plt
import numpy as np


def circle_at(ee, p): cv2.circle(ee, p, 30, (255, 255, 255))


def show_img(img, figsize=None, **kwargs):
    figsize = figsize or (15, 15)
    plt.figure(figsize=figsize)
    plt.imshow(img, **kwargs)
    # plt.axis('off')
    plt.show()


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


def polynome(coeffs, xs):
    return coeffs[0]*xs**2 + coeffs[1]*xs + coeffs[2]


def fit_poly_one_side(image, indices, ys, nonzero):
    nonzeroy, nonzerox = nonzero
    if indices.shape == (0,):
        return []
    leftx = nonzerox[indices]
    lefty = nonzeroy[indices]
    left_fit = np.polyfit(lefty, leftx, 2)
    left_fitx = polynome(left_fit, ys)
    return left_fitx


def fit_poly(image, left_indices, right_indices):

    nonzero = np.array(image.nonzero())
    ys = np.linspace(0, image.shape[0]-1, image.shape[0])
    left_fitx = fit_poly_one_side(image, left_indices, ys, nonzero)
    right_fitx = fit_poly_one_side(image, right_indices, ys, nonzero)

    return left_fitx, right_fitx, ys


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
    print(pixels_per_mm)
    pixels_per_mm = round(pixels_per_mm / ratio)
    print(pixels_per_mm)
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


def load_f_from_file(filepath="../cameraMatrix.npy"):
    matrix = np.load(filepath)
    print("found matrix:\n", matrix)
    f_x, f_y, _ = matrix.diagonal()
    f = np.mean([f_x, f_y])
    return f


def combine(image, original, use_bitwise=True):
    if use_bitwise:
        return cv2.bitwise_or(image, original)
    # image = image.copy()
    # image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    indices = (image == 0)
    indices = (image.sum(-1) == 0)
    image[indices] = original[indices]
    return image


def draw_lane_zone(image, xs, ys, step=1, color=(0, 255, 0), alpha=1, beta=0.5, gama=1.0):
    if len(xs[0]) != len(xs[1]) != len(ys):
        return image
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    for index in range(0, len(xs[0]) - 1, step):
        step_ = min(index+step, len(ys)-1)
        p1 = (int(xs[0][index]), int(ys[index]))
        p2 = (int(xs[1][index]), int(ys[index]))
        p3 = (int(xs[1][step_]), int(ys[step_]))
        p4 = (int(xs[0][step_]), int(ys[step_]))
        x, y, h, w = p1[0], p1[1], step, p2[0]-p1[0]
        x = max(x, 0)
        y = max(y, 0)
        w = max(w, 0)
        # print(x, y, h, w)
        sub_img = image[y:y+h, x:x+w]
        shape = *sub_img.shape[:-1], 1
        white_rect = np.tile(color, shape).astype(sub_img.dtype)
        res = cv2.addWeighted(sub_img,  alpha, white_rect, beta, gama)
        if res is not None:
            image[y:y+h, x:x+w] = res

        cv2.line(image, p1, p4, (0, 0, 255), 30)
        cv2.line(image, p2, p3, (0, 0, 255), 30)

    return image


def get_curvatures(image, RECENTER_MINPIX):
    hist = histogram(image)
    left_peak, right_peak = histogram_peaks(hist)
    left_lane_inds, right_lane_inds = get_lane_indices(
        image, left_peak, right_peak, 10, 50, RECENTER_MINPIX)
    left_fitx, right_fitx, ys = fit_poly(
        image, left_lane_inds, right_lane_inds)
    return (left_fitx, right_fitx), ys


def threshold(image, thresh=100, maxval=255, type=cv2.THRESH_BINARY):
    _, image = cv2.threshold(image, thresh, maxval, type)
    return image


def canny(image, t1, t2):
    return cv2.Canny(image, t1, t2)


def scale(frame, ratio=1, size=None):
    if size is None:
        size = (frame.shape[1]//ratio, frame.shape[0]//ratio)
    return cv2.resize(frame, size)


def show_window(name, image, ratio=1):
    image = scale(image, ratio)
    cv2.imshow(name, image)


def put_text(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(100, 255, 0), **kwargs):
    cv2.putText(frame, text, org, font, scale, color, **kwargs)
