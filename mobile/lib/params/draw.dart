import 'package:car_security/params/base.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// ignore: must_be_immutable
class DrawParams extends StatefulWidget with Params {
  @override
  State<DrawParams> createState() => _DrawParamsState();

  DrawParams(
    String url,
  ) {
    this.url = url;
  }
}

class _DrawParamsState extends State<DrawParams> {
  bool renderLines = false;
  bool renderLane = false;
  bool renderCarBox = false;
  Map<String, dynamic> prepareData() {
    Map<String, dynamic> data = {
      "renderLines": renderLines,
      "renderLane": renderLane,
      "renderCarBox": renderCarBox,
    };
    return data;
  }

  Future getData() {
    var url = widget.url!;
    return http.get(Uri.parse(url)).then((resp) {
      if (resp.statusCode == 200) {
        Map<String, dynamic> body = jsonDecode(resp.body);
        renderLines = body["renderLines"];
        renderLane = body["renderLane"];
        renderCarBox = body["renderCarBox"];
      }
    });
  }

  bool wasInit = false;

  @override
  void initState() {
    getData().then((q) {
      setState(() {
        wasInit = true;
      });
    });
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    if (!wasInit) return CircularProgressIndicator();

    return Column(
      children: [
        // new Placeholder(),
        CheckboxListTile(
          title: const Text("Render Lines"),
          checkColor: Colors.black,
          value: renderLines,
          onChanged: (value) {
            setState(() {
              renderLines = value!;
            });
          },
        ),
        CheckboxListTile(
          title: const Text("Render Lane"),
          checkColor: Colors.black,
          value: renderLane,
          onChanged: (value) {
            setState(() {
              renderLane = value!;
            });
          },
        ),
        CheckboxListTile(
          title: const Text("Render car box"),
          checkColor: Colors.black,
          value: renderCarBox,
          onChanged: (value) {
            setState(() {
              renderCarBox = value!;
            });
          },
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
