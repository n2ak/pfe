import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:car_security/params_controller_tab.dart';
import 'package:car_security/player_tab.dart';

class MainApp extends StatefulWidget {
  final String paramsBaseUrl; // = "http://192.168.1.20:9999/params/car";
  final String paramsUrl; // = "http://192.168.1.20:9999/params/draw";
  final String imageFeedUrl; // = "http://192.168.1.20:9999/image_feed";
  const MainApp(this.paramsUrl, this.paramsBaseUrl, this.imageFeedUrl,
      {super.key});

  @override
  MainAppState createState() => MainAppState();
}

class MainAppState extends State<MainApp> {
  final String playerUrl = "https://media.w3.org/2010/05/sintel/trailer.mp4";

  @override
  void initState() {
    super.initState();
  }

  Future<void> _forceLandscape() async {
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeRight,
      DeviceOrientation.landscapeLeft,
    ]);
    await SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  }

  Future<void> _forcePortrait() async {
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
    ]);
    await SystemChrome.setEnabledSystemUIMode(SystemUiMode.manual,
        overlays: SystemUiOverlay.values); // to re-show bars
  }

  toggleFullScreen() {
    var orientation = MediaQuery.of(context).orientation;
    var fullScreen = orientation == Orientation.landscape;
    print("fullScreen: $fullScreen");
    if (fullScreen)
      _forcePortrait();
    else
      _forceLandscape();
  }

  correctBars(bool fullScreen) {
    if (fullScreen) {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky)
          .then((value) {
        setState(() {});
      });
    } else {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.manual,
              overlays: SystemUiOverlay.values)
          .then((value) {
        setState(() {});
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // return Scaffold(
    //   body: ParamsControllerTab(
    //     drawParamsUrl,
    //     carParamsUrl,
    //   ),
    // );

    return OrientationBuilder(
      builder: (context, orientation) {
        var fullScreen = orientation == Orientation.landscape;
        // var func = fullScreen ? _forcePortrait : _forceLandscape;
        correctBars(fullScreen);
        var player = PlayerTab(playerUrl, toggleFullScreen);
        return DefaultTabController(
          length: 2,
          child: Scaffold(
            appBar: fullScreen
                ? null
                : AppBar(
                    centerTitle: true,
                    title: const Text('Car Security'),
                    bottom: const TabBar(
                      tabs: [
                        Tab(text: 'Video stream'),
                        Tab(text: 'Params'),
                      ],
                    ),
                  ),
            body: TabBarView(
              physics: const NeverScrollableScrollPhysics(),
              children: [
                player,
                ParamsControllerTab(
                  widget.paramsUrl,
                  widget.paramsBaseUrl,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
