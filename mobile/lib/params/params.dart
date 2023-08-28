import 'package:car_security/params/base.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// ignore: must_be_immutable
class P extends StatefulWidget with Params {
  @override
  State<P> createState() => _PState();
  Map<String, String> data;
  P(String url, this.data) {
    this.url = url;
  }
}

class _PState extends State<P> {
  Future<Map<String, String>> getData() {
    var url = widget.url!;
    return http.get(Uri.parse(url)).then((resp) {
      if (resp.statusCode == 200) {
        Map<String, String> body = jsonDecode(resp.body);
        return body;
      }
      throw "";
    });
  }

  bool wasInit = true;

  @override
  void initState() {
    super.initState();
  }

  Widget getWidget(String key, String value) {
    if (["true", "false"].contains(value.toLowerCase())) {
      return CheckboxListTile(
        title: Text(key),
        checkColor: Colors.black,
        value: value.toLowerCase() == "true",
        onChanged: (value) {
          setState(() {
            widget.data[key] = value! ? "True" : "False";
          });
        },
      );
    }
    var controller = TextEditingController(
      text: key,
    );
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: key),
      // keyboardType: type,
      // inputFormatters: inputFormatters,
      onChanged: (v) {
        setState(() {
          widget.data[key] = v;
        });
        // print("changing state $v");
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!wasInit) return CircularProgressIndicator();

    List<Widget> children = [];
    widget.data.forEach((key, value) {
      var element = getWidget(key, value);
      children.add(element);
    });
    children.add(ElevatedButton(
      child: const Text("Send"),
      onPressed: () {
        widget.onSavePressed(widget.data, context);
      },
    ));
    return Column(
      children: children,
    );
  }
}
