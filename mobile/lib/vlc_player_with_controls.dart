import 'package:flutter/material.dart';
import 'package:flutter_vlc_player/flutter_vlc_player.dart';
import 'package:car_security/controls_overlay.dart';

typedef OnStopRecordingCallback = void Function(String);

class VlcPlayerWithControls extends StatefulWidget {
  final Function toggleFullScreen;
  final VlcPlayerController controller;
  final bool showControls;

  const VlcPlayerWithControls(
    this.controller,
    this.toggleFullScreen, {
    this.showControls = true,
    super.key,
  });

  @override
  VlcPlayerWithControlsState createState() => VlcPlayerWithControlsState();
}

class VlcPlayerWithControlsState extends State<VlcPlayerWithControls>
    with AutomaticKeepAliveClientMixin {
  static const _playerControlsBgColor = Colors.black87;
  static const _recordingPositionOffset = 10.0;
  static const _aspectRatio = 16 / 9;

  final double initSnapshotRightPosition = 10;
  final double initSnapshotBottomPosition = 10;

  late VlcPlayerController _controller;

  //

  //
  double sliderValue = 0.0;
  double volumeValue = 50;
  String position = '';
  String duration = '';
  int numberOfCaptions = 0;
  int numberOfAudioTracks = 0;
  bool validPosition = false;

  double recordingTextOpacity = 0;
  DateTime lastRecordingShowTime = DateTime.now();

  //
  List<double> playbackSpeeds = [0.5, 1.0, 2.0];
  int playbackSpeedIndex = 1;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _controller = widget.controller;
    _controller.addListener(listener);
  }

  @override
  void dispose() {
    _controller.removeListener(listener);
    super.dispose();
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

  void listener() {
    if (!mounted) return;
    //
    if (_controller.value.isInitialized) {
      final oPosition = _controller.value.position;
      final oDuration = _controller.value.duration;
      // if (oPosition != null && oDuration != null) {
      if (oDuration.inHours == 0) {
        final strPosition = oPosition.toString().split('.').first;
        final strDuration = oDuration.toString().split('.').first;
        setState(() {
          position =
              "${strPosition.split(':')[1]}:${strPosition.split(':')[2]}";
          duration =
              "${strDuration.split(':')[1]}:${strDuration.split(':')[2]}";
        });
      } else {
        setState(() {
          position = oPosition.toString().split('.').first;
          duration = oDuration.toString().split('.').first;
        });
      }
      setState(() {
        validPosition = oDuration.compareTo(oPosition) >= 0;
        sliderValue = validPosition ? oPosition.inSeconds.toDouble() : 0;
      });
      // }
      setState(() {
        numberOfCaptions = _controller.value.spuTracksCount;
        numberOfAudioTracks = _controller.value.audioTracksCount;
      });
      // update recording blink widget
      if (_controller.value.isRecording && _controller.value.isPlaying) {
        if (DateTime.now().difference(lastRecordingShowTime).inSeconds >= 1) {
          setState(() {
            lastRecordingShowTime = DateTime.now();
            recordingTextOpacity = 1 - recordingTextOpacity;
          });
        }
      } else {
        setState(() => recordingTextOpacity = 0);
      }
      // check for change in recording state
    }
    if (_controller.value.hasError) {
      _showToast("Video not found.");
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    var vlcPlayer = VlcPlayer(
      controller: _controller,
      aspectRatio: _aspectRatio,
      placeholder: const Center(child: CircularProgressIndicator()),
    );

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Expanded(
          child: ColoredBox(
            color: Colors.black,
            child: Stack(
              alignment: Alignment.bottomCenter,
              children: <Widget>[
                Center(
                  child: vlcPlayer,
                ),
                Positioned(
                  top: _recordingPositionOffset,
                  left: _recordingPositionOffset,
                  child: AnimatedOpacity(
                    opacity: recordingTextOpacity,
                    duration: const Duration(seconds: 1),
                    child: const Wrap(
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Icon(Icons.circle, color: Colors.red),
                        SizedBox(width: 5),
                        Text(
                          'REC',
                          style: TextStyle(
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                ControlsOverlay(_controller),
              ],
            ),
          ),
        ),
        Visibility(
          visible: widget.showControls,
          child: ColoredBox(
            color: _playerControlsBgColor,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                IconButton(
                  color: Colors.white,
                  icon: _controller.value.isPlaying
                      ? const Icon(Icons.pause_circle_outline)
                      : const Icon(Icons.play_circle_outline),
                  onPressed: _togglePlaying,
                ),
                Expanded(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    mainAxisSize: MainAxisSize.max,
                    children: [
                      Text(
                        position,
                        style: const TextStyle(color: Colors.white),
                      ),
                      Expanded(
                        child: Slider(
                          activeColor: Colors.redAccent,
                          inactiveColor: Colors.white70,
                          value: sliderValue,
                          min: 0.0,
                          max: (!validPosition)
                              ? 1.0
                              : _controller.value.duration.inSeconds.toDouble(),
                          onChanged:
                              validPosition ? _onSliderPositionChanged : null,
                        ),
                      ),
                      Text(
                        duration,
                        style: const TextStyle(color: Colors.white),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.fullscreen),
                  color: Colors.white,
                  // ignore: no-empty-block
                  onPressed: () {
                    widget.toggleFullScreen();
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _togglePlaying() async {
    _controller.value.isPlaying
        ? await _controller.pause()
        : await _controller.play();
  }

  void _onSliderPositionChanged(double progress) {
    setState(() {
      sliderValue = progress.floor().toDouble();
    });
    //convert to Milliseconds since VLC requires MS to set time
    _controller.setTime(sliderValue.toInt() * Duration.millisecondsPerSecond);
  }
}
