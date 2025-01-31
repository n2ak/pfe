import numpy as np
import cv2


def to_numpy(x) -> np.ndarray:
    import torch
    if isinstance(x, torch.Tensor):
        return x.cpu().numpy()
    elif isinstance(x, np.ndarray):
        return x
    elif isinstance(x, (list, tuple)):
        return np.array(x)
    else:
        raise Exception(f"Invalid type {type(x)}")


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


def put_text(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(100, 255, 0), **kwargs):
    cv2.putText(frame, text, org, font, scale, color, **kwargs)


def polynome(coeffs, y, ret_curv_radius=False):
    A, B, C = coeffs
    res = A * y**2 + B * y + C
    if ret_curv_radius:
        curvature = abs((2 * A) / (1 + (2 * A * y + B) ** 2) ** (3/2))
        radius = 1 / curvature
        radius = np.mean(radius)
        return radius, res
    return res


def draw_lane_zone(image, xs, ys, step=1, color=(0, 255, 0), alpha=1, beta=0.5, gama=1.0, draw_lines=False):
    if len(xs[0]) != len(xs[1]) != len(ys):
        return image
    right, left = xs[0][::step], xs[1][::step]
    ys = ys[::step]
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    pointsl = np.column_stack((left, ys))
    pointsr = np.column_stack((right, ys))
    pointsr = pointsr[::-1]
    points = np.row_stack((pointsl, pointsr)).astype(np.int32)
    image = cv2.fillPoly(image, [points], color)
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


def scale_img(frame, ratio=1, size=None):
    if size is None:
        size = (int(frame.shape[1]//ratio), int(frame.shape[0]//ratio))
    return cv2.resize(frame, size)


def show_window(name, image, ratio=1):
    image = scale_img(image, ratio)
    cv2.imshow(name, image)
    return cv2.waitKey(1) & 0xFF == ord('q')


def is_window_closed(window_name):
    return cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1
