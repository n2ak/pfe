import 'package:car_security/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:car_security/player_tab.dart';
import 'package:car_security/params_controller_tab.dart';

class App extends StatefulWidget {
  const App({super.key});

  @override
  _AppState createState() => _AppState();
}

class _AppState extends State<App> {
  static const _tabCount = 2;

  final String playerUrl = "https://media.w3.org/2010/05/sintel/trailer.mp4";
  final String carParamsUrl = "http://192.168.1.20:9999/params/car";
  final String drawParamsUrl = "http://192.168.1.20:9999/params/draw";
  final String imageFeedUrl = "http://192.168.1.20:9999/image_feed";

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
        // correctBars(fullScreen);
        // var player = PlayerTab(playerUrl, toggleFullScreen);

        // var g = DefaultTabController(
        //   length: _tabCount,
        //   child: Scaffold(
        //     appBar: fullScreen
        //         ? null
        //         : AppBar(
        //             centerTitle: true,
        //             title: const Text('Car Security'),
        //             bottom: const TabBar(
        //               tabs: [
        //                 Tab(text: 'Video stream'),
        //                 Tab(text: 'Params'),
        //               ],
        //             ),
        //           ),
        //     body: TabBarView(
        //       physics: const NeverScrollableScrollPhysics(),
        //       children: [
        //         player,
        //         ParamsControllerTab(
        //           drawParamsUrl,
        //           carParamsUrl,
        //         ),
        //       ],
        //     ),
        //   ),
        // );

        return Scaffold(
            appBar: AppBar(title: const Text("Yoo")),
            body: CameraFeed(imageFeedUrl));
      },
    );
  }
}
