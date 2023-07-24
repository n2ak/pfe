// ignore_for_file: curly_braces_in_flow_control_structures

import 'package:flutter/material.dart';
import 'package:flutter_vlc_player/flutter_vlc_player.dart';

class ControlsOverlay extends StatefulWidget {
  static const double _playButtonIconSize = 80;
  static const double _replayButtonIconSize = 100;
  static const double _seekButtonIconSize = 48;

  static const Duration _seekStepForward = Duration(seconds: 10);
  static const Duration _seekStepBackward = Duration(seconds: -10);

  static const Color _iconColor = Colors.white;
  final VlcPlayerController controller;

  const ControlsOverlay(this.controller, {super.key});

  @override
  State<ControlsOverlay> createState() => _ControlsOverlayState();
}

class _ControlsOverlayState extends State<ControlsOverlay> {
  bool showControls = false;
  Widget playWidget() {
    return SizedBox.expand(
      child: ColoredBox(
        color: Colors.black45,
        child: FittedBox(
          child: IconButton(
            onPressed: _play,
            color: ControlsOverlay._iconColor,
            iconSize: ControlsOverlay._playButtonIconSize,
            icon: const Icon(
              Icons.play_arrow,
              size: 50,
            ),
          ),
        ),
      ),
    );
  }

  Widget replayWidget() {
    return Center(
      child: FittedBox(
        child: IconButton(
          onPressed: _replay,
          color: ControlsOverlay._iconColor,
          iconSize: ControlsOverlay._replayButtonIconSize,
          icon: const Icon(Icons.replay),
        ),
      ),
    );
  }

  _builder(BuildContext ctx) {
    if (widget.controller.value.isEnded || widget.controller.value.hasError)
      return replayWidget();
    var state = widget.controller.value.playingState;
    if (state == PlayingState.initialized ||
        state == PlayingState.stopped ||
        state == PlayingState.paused) return playWidget();

    if (state == PlayingState.buffering || state == PlayingState.playing)
      return GestureDetector(
        child: Container(
          color: Colors.transparent,
        ),
      );

    if (state == PlayingState.ended || state == PlayingState.error)
      return replayWidget();
    return const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 50),
      reverseDuration: const Duration(milliseconds: 200),
      child: Builder(
        builder: (ctx) => _builder(ctx),
      ),
    );
  }

  Future<void> _play() {
    return widget.controller.play();
  }

  Future<void> _replay() async {
    await widget.controller.stop();
    await widget.controller.play();
  }
}
