import 'package:car_security/params/base.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

typedef OnchangedFunc = VoidCallback Function(String);

class CarDetectorParams extends StatefulWidget with Params {
  @override
  State<CarDetectorParams> createState() => _CarDetectorParamsState();

  CarDetectorParams(
    String url,
  ) {
    this.url = url;
  }
}

class _CarDetectorParamsState extends State<CarDetectorParams> {
  int f = 2800;
  int frame_center_y = 300;
  String yolo_version = "yolov5";
  double car_min_distance = 30;
  double car_avg_width = 2.5;

  Map<String, dynamic> prepareData() {
    Map<String, dynamic> data = {
      "f": f,
      "frame_center_y": frame_center_y,
      "yolo_version": yolo_version,
      "car_min_distance": car_min_distance,
      "car_avg_width": car_avg_width,
    };
    return data;
  }

  Future getData() {
    var url = widget.url!;
    return http.get(Uri.parse(url)).then((resp) {
      print('body: ${resp.body}');
      if (resp.statusCode == 200) {
        Map<String, dynamic> body = jsonDecode(resp.body);
        f = body["f"].toInt();
        frame_center_y = body["frame_center_y"].toInt();
        yolo_version = body["yolo_version"].toString();
        car_min_distance = body["car_min_distance"].toDouble();
        car_avg_width = body["car_avg_width"].toDouble();
      }
    });
  }

  bool wasInit = false;

  void initState() {
    getData().then((q) {
      setState(() {
        wasInit = true;
      });
    }).catchError((e) {
      print("No result $e");
    });
    super.initState();
  }

  TextField get_field(String initial, String text, OnchangedFunc onChanged,
      {bool digitsOnly = true}) {
    var inputFormatters = null;
    var type = null;
    if (digitsOnly) {
      // inputFormatters = [FilteringTextInputFormatter.digitsOnly];
      type = TextInputType.number;
    }
    var controller = TextEditingController(
      text: initial,
    );
    controller.selection = TextSelection.fromPosition(
        TextPosition(offset: controller.text.length));
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: text),
      keyboardType: type,
      inputFormatters: inputFormatters,
      onChanged: (v) {
        setState(onChanged(v));
        print("changing state $v");
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!wasInit) return CircularProgressIndicator();

    Map<String, MapEntry<String, OnchangedFunc>> map = {
      "f": MapEntry(f.toString(), (v) {
        return () {
          f = int.parse(v);
          print("state ${f}");
        };
      }),
      "frame_center_y": MapEntry(frame_center_y.toString(), (v) {
        return () {
          frame_center_y = int.parse(v);
        };
      }),
      "car_min_distance": MapEntry(car_min_distance.toString(), (v) {
        return () {
          car_min_distance = double.parse(v);
        };
      }),
      "car_avg_width": MapEntry(car_avg_width.toString(), (v) {
        return () {
          car_avg_width = double.parse(v);
        };
      }),
    };
    var fields = map.entries
        .map(
            (entry) => get_field(entry.value.key, entry.key, entry.value.value))
        .toList();
    fields.add(get_field(
      yolo_version,
      "yolo_version",
      (v) {
        return () {
          yolo_version = v;
        };
      },
      digitsOnly: false,
    ));
    return Column(
      children: [
        Column(
          children: fields,
        ),
        ElevatedButton(
          child: const Text("Send"),
          onPressed: () {
            var data = prepareData();
            widget.onSavePressed(data, context);
          },
        ),
      ],
    );
  }
}
