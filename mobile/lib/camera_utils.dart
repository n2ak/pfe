import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:image/image.dart' as imglib;
import 'package:camera/camera.dart';
import 'dart:async';

import 'package:http/http.dart' as http;

import 'package:web_socket_channel/io.dart';

class ImageUtils {
  String url;
  IOWebSocketChannel? channel;
  bool useSockets;
  ImageUtils(this.url, this.useSockets) {
    if (useSockets) {
      resetSocket();
    }
    timer(fps);
  }

  bool canUpload = true;
  bool canProcess = true;
  //List<int>? image;
  Uint8List? image;

  String imageToString(CameraImage image) {
    return json.encode(
      image,
      toEncodable: (object) {
        CameraImage object_ = object;
        List<MapEntry> list = List.empty();
        for (var i = 0; i < object_.planes.length; i++) {
          var plane = object_.planes[i];
          list.add(MapEntry("plane$i", plane.bytes));
        }
        return Map.fromEntries(list);
      },
    );
  }

  Uint8List withouDecode(CameraImage image) {
    return convertCameraImage(image).getBytes(format: imglib.Format.rgb);
  }

  void timer(int fps) {
    Timer.periodic(Duration(milliseconds: ((1000 / fps).round())), (timer) {
      send();
    });
  }

  void send() {
    if (image == null) return;
    print("Uploading length: ${image!.length}");
    if (useSockets) {
      _sendFramesViaWebSocket(image);
    } else {
      _asyncSend(url, image!);
      // postRequest(image!);
    }
  }

  int last = DateTime.now().millisecondsSinceEpoch;
  int fps = 5;
  int fpss = (1000 / 5).round();
  void onNewImage(CameraImage image) {
    if (canProcess || this.image == null) {
      int current = DateTime.now().millisecondsSinceEpoch;
      if ((current - last) < fpss) return;
      canProcess = false;
      print("Processing");
      var list = withouDecode(image);
      this.image = list;
      canProcess = true;
      print("Processed");
      last = current;
    }
    // if (this.image != null && canUpload) {
    //   canUpload = false;
    //   send();
    // }
  }

  dispose() {
    channel?.sink.close();
  }

  void resetSocket() {
    channel = IOWebSocketChannel.connect('ws://192.168.1.20:9999/ws');
  }

  Future<void> _sendFramesViaWebSocket(dynamic frame) async {
    if (channel!.closeCode != null) {
      resetSocket();
      return;
    }
    channel!.sink.add(frame);
    print("Uploaded");
    canUpload = true;
  }

  postRequest(Uint8List data) {
    // var body = json.encode(data);
    print("url: $url");
    try {
      var resp = http.post(Uri.parse(url),
          headers: {"Content-Type": "application/octet-stream"}, body: data);
      resp.then((response) {
        String respText = "Params set successfully.";
        if (response.statusCode != 200) {
          String msg = response.body;
          respText = "Setting params was unsuccessful,Error: $msg";
        }
        print(respText);
        canUpload = true;
      });
    } catch (e) {
      print("***************Error**************");
      print("Error: $e");
    }
  }

  _asyncSend(String url, List<int> list) async {
    // canSend = false;
    try {
      await _asyncFileUpload(url, list);
      canUpload = true;
      print("Uploaded to $url");
    } catch (e) {
      print(e);
    }
    // canSend = true;
  }

  static imglib.Image convertCameraImage(CameraImage cameraImage) {
    if (cameraImage.format.group == ImageFormatGroup.yuv420) {
      return convertYUV420ToImage(cameraImage);
    } else if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
      return convertBGRA8888ToImage(cameraImage);
    } else {
      throw Exception('Undefined image type.');
    }
  }

  static imglib.Image convertBGRA8888ToImage(CameraImage cameraImage) {
    return imglib.Image.fromBytes(
      cameraImage.planes[0].width!,
      cameraImage.planes[0].height!,
      cameraImage.planes[0].bytes,
      format: imglib.Format.bgra,
    );
  }

  static imglib.Image convertYUV420ToImage(CameraImage cameraImage) {
    final imageWidth = cameraImage.width;
    final imageHeight = cameraImage.height;

    final yBuffer = cameraImage.planes[0].bytes;
    final uBuffer = cameraImage.planes[1].bytes;
    final vBuffer = cameraImage.planes[2].bytes;

    final int yRowStride = cameraImage.planes[0].bytesPerRow;
    final int yPixelStride = cameraImage.planes[0].bytesPerPixel!;

    final int uvRowStride = cameraImage.planes[1].bytesPerRow;
    final int uvPixelStride = cameraImage.planes[1].bytesPerPixel!;

    final image = imglib.Image(imageWidth, imageHeight);

    for (int h = 0; h < imageHeight; h++) {
      int uvh = (h / 2).floor();

      for (int w = 0; w < imageWidth; w++) {
        int uvw = (w / 2).floor();

        final yIndex = (h * yRowStride) + (w * yPixelStride);

        // Y plane should have positive values belonging to [0...255]
        final int y = yBuffer[yIndex];

        // U/V Values are subsampled i.e. each pixel in U/V chanel in a
        // YUV_420 image act as chroma value for 4 neighbouring pixels
        final int uvIndex = (uvh * uvRowStride) + (uvw * uvPixelStride);

        // U/V values ideally fall under [-0.5, 0.5] range. To fit them into
        // [0, 255] range they are scaled up and centered to 128.
        // Operation below brings U/V values to [-128, 127].
        final int u = uBuffer[uvIndex];
        final int v = vBuffer[uvIndex];

        // Compute RGB values per formula above.
        int r = (y + v * 1436 / 1024 - 179).round();
        int g = (y - u * 46549 / 131072 + 44 - v * 93604 / 131072 + 91).round();
        int b = (y + u * 1814 / 1024 - 227).round();

        r = r.clamp(0, 255);
        g = g.clamp(0, 255);
        b = b.clamp(0, 255);

        image.setPixelRgba(w, h, r, g, b);
      }
    }

    return image;
  }

  Future<bool> _asyncFileUpload(String url, List<int> list) async {
    var request = http.MultipartRequest("POST", Uri.parse(url));
    var pic = http.MultipartFile.fromBytes("file", list, filename: "file");
    request.files.add(pic);
    try {
      await request.send();
    } catch (e) {}
    return true;
  }

  runLoop(CameraController camera, int millis) {
    camera.setFlashMode(FlashMode.off);
    camera;
    var duration = Duration(milliseconds: millis);
    Timer.periodic(duration, (timer) async {
      if (!canUpload) return;
      canUpload = false;
      var xfile = await camera.takePicture();
      var frame = await xfile.readAsBytes();
      canUpload = false;
      if (useSockets) {
        _sendFramesViaWebSocket(frame);
      } else {
        _asyncSend(url, frame);
      }
    });
  }
}
