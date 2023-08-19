import 'package:flutter/material.dart';
import 'package:flutter_vlc_player/flutter_vlc_player.dart';
import 'package:car_security/vlc_player_with_controls.dart';

class PlayerTab extends StatefulWidget {
  final String url;
  final Function toggleFullScreen;
  const PlayerTab(this.url, this.toggleFullScreen, {super.key});

  @override
  _PlayerTabState createState() => _PlayerTabState();
}

class _PlayerTabState extends State<PlayerTab> {
  static const _networkCachingMs = 2000;
  // static const _subtitlesFontSize = 30;
  static const _height = 400.0;

  late VlcPlayerController _controller;
  late int selectedVideoIndex;

  void fillVideos() {}

  @override
  void initState() {
    super.initState();
    fillVideos();
    selectedVideoIndex = 0;
    _controller = VlcPlayerController.network(
      widget.url,
      hwAcc: HwAcc.full,
      options: VlcPlayerOptions(
        advanced: VlcAdvancedOptions([
          VlcAdvancedOptions.networkCaching(_networkCachingMs),
        ]),
        // subtitle: VlcSubtitleOptions([
        //   VlcSubtitleOptions.boldStyle(true),
        //   VlcSubtitleOptions.fontSize(_subtitlesFontSize),
        //   VlcSubtitleOptions.outlineColor(VlcSubtitleColor.yellow),
        //   VlcSubtitleOptions.outlineThickness(VlcSubtitleThickness.normal),
        //   // works only on externally added subtitles
        //   VlcSubtitleOptions.color(VlcSubtitleColor.navy),
        // ]),
        http: VlcHttpOptions([
          VlcHttpOptions.httpReconnect(true),
        ]),
        rtp: VlcRtpOptions([
          VlcRtpOptions.rtpOverRtsp(true),
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        SizedBox(
          height: _height,
          child: VlcPlayerWithControls(
            _controller,
            widget.toggleFullScreen,
          ),
        ),
      ],
    );
  }

  @override
  Future<void> dispose() async {
    super.dispose();
    // await _controller.stopRecording();
    await _controller.stopRendererScanning();
    await _controller.dispose();
  }
}
