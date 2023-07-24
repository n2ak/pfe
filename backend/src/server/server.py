from car import CarParams
from drawer import DrawParams
import cv2
import threading
import time
import base64
import websockets
import asyncio
from flask import Flask, Response, render_template_string, request, render_template

source = "./video2.mp4"

_frame_count = 30
_outputFrame = None
_frame_lock = threading.Lock()
car_params = CarParams()
draw_params = DrawParams()
app = Flask(__name__)


_dummy_page = """
<html>
  <head>
    <title>RTSP web streaming</title>
  </head>
  <body>
    <h1>RTSP web streaming</h1>
    <img src="{{ url_for('video_feed') }}">
  </body>
</html>
"""


@app.route("/")
def index():
    # return the rendered template
    return render_template("./index.html")
    return render_template_string(_dummy_page)


async def transmit(websocket, path):
    global _outputFrame, _frame_lock, video
    print("Client Connected !")
    try:
        while True:
            if _outputFrame is None:
                continue
            start = time.time()
            print("Starting to send")
            (flag, encodedImage) = cv2.imencode(".jpg", _outputFrame)
            if not flag:
                continue

            data = str(base64.b64encode(encodedImage))
            data = data[2:len(data)-1]

            await websocket.send(data)
            delta = time.time() - start
            print(f"{delta}")
            print("Fps", int(1/delta))
    except Exception as e:
        print("Someting went Wrong !", e)


def stream(frameCount, video):
    if video.isOpened():
        while True:
            ret_val, frame = video.read()
            if ret_val is False:
                video = cv2.VideoCapture(source)
                continue
            frame = cv2.resize(frame, (640, 360))
            set_frame(frame)
            time.sleep(1/frameCount)
    else:
        print('camera open failed')


def generate_frame_response():
    global _outputFrame, _frame_lock
    while True:
        with _frame_lock:
            if _outputFrame is None:
                continue
            flag, encodedImage = cv2.imencode(".jpg", _outputFrame)
            if not flag:
                continue
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) +
            b'\r\n'
        )


def update(type, data):
    global car_params
    # print(type == "car", type, data)
    if type == "car":
        car_params.update_from_json(data)
    elif type == "draw":
        draw_params.update_from_json(data)
    else:
        raise TypeError(type)
    print(f"Params for {type} are updated.")


@app.get("/params/<type>")
def get_params(type: str):
    type = type.lower()
    import json
    resp = Response()
    if type not in ["car", "draw"]:
        resp.status_code = 400
        resp.response = f"Invalid params type: {str(type)}"
        return resp
    params = {
        "car": car_params.PARAMS,
        "draw": draw_params.PARAMS
    }[type]
    resp.response = json.dumps(params)
    resp.status_code = 200
    return resp


@app.post("/params/<type>")
def set_params(type: str):
    type = type.lower()
    data = request.json
    resp = Response()
    try:
        update(type, data)
        resp.status_code = 200
    except KeyError as e:
        resp.status_code = 400
        resp.response = f"Key {str(e)} does not exist on the request."
    except TypeError:
        resp.status_code = 400
        resp.response = f"Invalid params type: {str(type)}"

    return resp


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frame_response(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def set_frame(frame):
    global _outputFrame, _frame_lock
    with _frame_lock:
        _outputFrame = frame


def run_server(host, port):
    app.run(
        host=host,
        port=port,
        debug=True,
    )


def run_vlc(*args):
    t = threading.Thread(target=stream, args=args)
    t.daemon = True
    t.start()


def run_socket():
    def run():
        start_server = websockets.serve(transmit, host, port=port)
        print("Started server on port : ", port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    stream(_frame_count)


if __name__ == '__main__':
    video = cv2.VideoCapture(source)
    host, port = "0.0.0.0:9999".split(":")
    run_vlc(_frame_count, video)
    run_server(host, port)
    video.release()
    cv2.destroyAllWindows()
