import 'dart:async';

import 'package:car_security/camera_utils.dart';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

class CameraFeed extends StatefulWidget {
  final String url;
  const CameraFeed(this.url, {super.key});
  @override
  _CameraFeedState createState() => _CameraFeedState();
}

class _CameraFeedState extends State<CameraFeed> {
  CameraController? _camera;
  CameraImage? currentImage;
  late ImageUtils imageUtils;

  int imageCount = 0;
  int uploadedCount = 0;
  // bool _isDetecting = false;
  bool useImageStream = true;
  bool canSend = true;
  Image? image;
  CameraLensDirection _direction = CameraLensDirection.back;

  @override
  void initState() {
    super.initState();
    imageUtils = ImageUtils(widget.url, true);
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
    print("__ Controller");
    _camera = CameraController(
      await _getCamera(_direction),
      defaultTargetPlatform == TargetPlatform.iOS
          ? ResolutionPreset.low
          : ResolutionPreset.medium,
      imageFormatGroup: ImageFormatGroup.bgra8888,
    );
    // _camera.takePicture();
    print("__ Initliting");
    await _camera!.initialize();

    print("__ setting stream");
    _camera!.startImageStream(imageUtils.onNewImage);
    if (useImageStream) {
    } else {
      imageUtils.runLoop(_camera!, 100);
    }
  }

  Future<String> get _localPath async {
    final directory = await getApplicationDocumentsDirectory();

    return directory.path;
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
}
