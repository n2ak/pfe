import 'package:car_security/camera.dart';
import 'package:car_security/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:car_security/main_app.dart';

class FirstPage extends StatefulWidget {
  const FirstPage({super.key});

  @override
  FirstPageState createState() => FirstPageState();
}

class FirstPageState extends State<FirstPage> {
  late TextEditingController textEditController;
  // late String baseUrl;
  @override
  void initState() {
    super.initState();
    textEditController = TextEditingController(text: "http://127.0.0.1:9999/");
    // baseUrl = "";
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
    return Scaffold(
        appBar: AppBar(title: const Text("Yoo")),
        body: Center(
          child: Column(
            children: [
              TextField(
                controller: textEditController,
              ),
              const SizedBox(height: 30),
              gradientButton(() {
                push((baseUrl) {
                  var viodeFeedUrl = Utils.joinURL(baseUrl, "ws");
                  viodeFeedUrl = viodeFeedUrl.replaceFirst("http", "ws");
                  return CameraFeed(viodeFeedUrl);
                });
              }, "Camera feed"),
              const SizedBox(height: 30),
              gradientButton(() {
                push((baseUrl) {
                  String paramsUrl = Utils.joinURL(baseUrl, "all_params");
                  String paramsBaseUrl = Utils.joinURL(baseUrl, "params/");
                  String imageFeedUrl =
                      Utils.joinURL(baseUrl, "params/image_feed");
                  return MainApp(paramsUrl, paramsBaseUrl, imageFeedUrl);
                });
              }, "Main App"),
            ],
          ),
        ));
  }

  void push(Function func) {
    Navigator.push(context, MaterialPageRoute(builder: (context) {
      var baseUrl = textEditController.text;
      return func(baseUrl);
    }));
  }

  Widget gradientButton(onPressed, String title) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: Stack(
        children: <Widget>[
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: <Color>[
                    Color(0xFF0D47A1),
                    Color(0xFF1976D2),
                    Color(0xFF42A5F5),
                  ],
                ),
              ),
            ),
          ),
          TextButton(
            style: TextButton.styleFrom(
              foregroundColor: Colors.white,
              padding: const EdgeInsets.all(16.0),
              textStyle: const TextStyle(fontSize: 20),
            ),
            onPressed: onPressed,
            child: Text(title),
          ),
        ],
      ),
    );
  }
}
