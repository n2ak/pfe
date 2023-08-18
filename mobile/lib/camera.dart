import 'dart:async';
import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';

import 'package:car_security/camera_utils.dart';
import 'package:http_parser/http_parser.dart';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image/image.dart' as imglib;
import 'package:http/http.dart' as http;

import 'package:web_socket_channel/io.dart';

// void main() => runApp(MaterialApp(home: CameraFeed()));

class CameraFeed extends StatefulWidget {
  String url;
  CameraFeed(this.url, {super.key});
  @override
  _CameraFeedState createState() => _CameraFeedState();
}

class _CameraFeedState extends State<CameraFeed> {
  dynamic _scanResults;
  CameraController? _camera;
  CameraImage? currentImage;

  int imageCount = 0;
  int uploadedCount = 0;
  bool _isDetecting = false;
  bool _cameraInitialized = false;
  bool canSend = true;
  Image? image;
  CameraLensDirection _direction = CameraLensDirection.back;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<CameraDescription> _getCamera(CameraLensDirection dir) async {
    return await availableCameras().then(
      (List<CameraDescription> cameras) => cameras.firstWhere(
        (CameraDescription camera) => camera.lensDirection == dir,
      ),
    );
  }

  void _initializeCamera() async {
    _camera = CameraController(
      await _getCamera(_direction),
      defaultTargetPlatform == TargetPlatform.iOS
          ? ResolutionPreset.low
          : ResolutionPreset.medium,
      imageFormatGroup: ImageFormatGroup.bgra8888,
    );
    // _camera.takePicture();
    await _camera!.initialize();
    setState(() {
      _cameraInitialized = true;
    });

    // _camera!.startImageStream(onNewImage);
    runLoop(100);
  }

  final channel = IOWebSocketChannel.connect('ws://192.168.1.20:9999/ws');
  Future<void> _sendFramesViaWebSocket(dynamic frame) async {
    channel.sink.add(frame);
  }

  runLoop(int millis) {
    _camera!.setFlashMode(FlashMode.off);
    _camera!;
    var duration = Duration(milliseconds: millis);
    Timer.periodic(duration, (timer) async {
      if (!canSend) return;
      canSend = false;
      var xfile = await _camera!.takePicture();
      canSend = true;
      var frame = await xfile.readAsBytes();
      // _sendFramesViaWebSocket(frame);
      _asyncSend(frame);
    });
  }

  Future<String> get _localPath async {
    final directory = await getApplicationDocumentsDirectory();

    return directory.path;
  }

  int fps = 10;
  int last = DateTime.now().millisecondsSinceEpoch;
  void onNewImage(CameraImage image) {
    var current = DateTime.now().millisecondsSinceEpoch;
    // image.
    if (canSend == false) return;
    var delta = (current - last);
    if (delta < (1000 / fps)) return;
    last = current;
    setState(() {
      this.imageCount = imageCount + 1;
    });
    var img = ImageUtils.convertCameraImage(image);
    var list = imglib.encodePng(img);
    print("length ${list.length}");
    // _sendFramesViaWebSocket(list);
    _asyncSend(list);
    // print("Length ${im.length}");
  }

  _asyncSend(List<int> list) async {
    // canSend = false;
    try {
      print("uploading");
      var start = DateTime.now().millisecondsSinceEpoch;
      await _asyncFileUpload(widget.url, list);
      var end = DateTime.now().millisecondsSinceEpoch;
      print("uploaded in ${(end - start) / 1000} seconds");
      setState(() {
        uploadedCount = uploadedCount + 1;
      });
    } catch (e) {
      print(e);
    }
    // canSend = true;
  }

  void _showToast(String text) {
    final scaffold = ScaffoldMessenger.of(context);
    scaffold.showSnackBar(
      SnackBar(
        content: Text(text),
        action: SnackBarAction(
            label: 'UNDO', onPressed: scaffold.hideCurrentSnackBar),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    var w = (image == null ? const Text("No image") : image!);
    if (image == null) {}
    return Center(
        child: Column(
      children: [
        Text("Images taken: $imageCount"),
        Text("Images uploaded: $uploadedCount"),
        IconButton(
            onPressed: () {
              _showToast("Re initializing");
              _camera!.dispose();
              setState(() {
                _cameraInitialized = false;
                imageCount = 0;
                uploadedCount = 0;
                currentImage = null;
                _camera = null;
                canSend = true;
              });
              Timer(const Duration(milliseconds: 100), _initializeCamera);
            },
            icon: const Icon(Icons.refresh)),
        w,
      ],
    ));
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
}
