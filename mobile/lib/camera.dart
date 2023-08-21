import 'dart:async';

import 'package:car_security/camera_utils.dart';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class CameraFeed extends StatefulWidget {
  final String url;
  const CameraFeed(this.url, {super.key});
  @override
  _CameraFeedState createState() => _CameraFeedState();
}

class _CameraFeedState extends State<CameraFeed> {
  CameraController? _camera;
  late ImageUtils imageUtils;

  // bool _isDetecting = false;
  bool useImageStream = true;
  Image? image;
  CameraLensDirection _direction = CameraLensDirection.back;
  bool useSockets = true;
  @override
  void initState() {
    super.initState();
    imageUtils = ImageUtils(widget.url, useSockets, setState);
    _initializeCamera();
  }

  Future<CameraDescription> _getCamera(CameraLensDirection dir) async {
    return await availableCameras().then(
      // print("*********ERROR***********");
      (List<CameraDescription> cameras) => cameras.firstWhere(
        (CameraDescription camera) => camera.lensDirection == dir,
      ),
    );
  }

  void _initializeCamera() async {
    print("__ Controller");
    try {
      _camera = CameraController(
        await _getCamera(_direction),
        defaultTargetPlatform == TargetPlatform.iOS
            ? ResolutionPreset.low
            : ResolutionPreset.medium,
        imageFormatGroup: ImageFormatGroup.bgra8888,
      );
    } catch (e) {
      print("*********ERROR***********");
      print("${e.toString()}");
    }
    // _camera.takePicture();
    print("__ Initliting");
    await _camera!.initialize();

    print("__ setting stream");
    if (useImageStream) {
      _camera!.startImageStream(imageUtils.onNewImage);
    } else {
      imageUtils.runLoop(_camera!, 100);
    }
    imageUtils.isOn = true;
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
  void dispose() {
    _camera?.dispose();
    imageUtils.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // var w = (image == null ? const Text("No image") : image!);
    if (image == null) {}
    var center = Center(
        child: Column(
      children: [
        Text("Status: ${imageUtils.isOn ? 'On' : 'Off'}"),
        Text("Images taken: ${imageUtils.imageProcessed}"),
        Text("Images uploaded: ${imageUtils.imageUploaded}"),
        IconButton(
            onPressed: () {
              _showToast("Re initializing");
              reset();
              imageUtils = ImageUtils(widget.url, useSockets, setState);
              Timer(const Duration(milliseconds: 100), _initializeCamera);
            },
            icon: const Icon(Icons.refresh)),
        IconButton(
            onPressed: () {
              reset();
              _showToast("Stopped");
            },
            icon: const Icon(Icons.stop)),
        (_camera != null ? CameraPreview(_camera!) : const Text("No Preview")),
      ],
    ));
    return Scaffold(
      appBar: AppBar(title: const Text("Yoo")),
      body: center,
    );
  }

  reset() {
    _camera!.stopImageStream();
    _camera!.dispose();
    imageUtils.dispose();
    setState(() {
      _camera = null;
    });
  }
}
