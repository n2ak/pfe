import 'package:car_security/params/hidable_param.dart';
import 'package:car_security/params/params.dart';
import 'package:car_security/utils.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class ParamsControllerTab extends StatefulWidget {
  //const ParamsControllerTab({super.key});
  final String paramsUrl;
  final String paramsBaseUrl;
  const ParamsControllerTab(this.paramsUrl, this.paramsBaseUrl, {super.key});

  @override
  State<ParamsControllerTab> createState() => _ParamsControllerTabState();
}

class _ParamsControllerTabState extends State<ParamsControllerTab> {
  Map<String, Map<String, String>>? data;
  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    http.get(Uri.parse(widget.paramsUrl)).then((resp) {
      if (resp.statusCode == 200) {
        Map<String, Map<String, String>> body = jsonDecode(resp.body);
        data = body;
      }
      throw "";
    });
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> children = [];
    data!.forEach((type, map) {
      String url = Utils.joinURL(widget.paramsBaseUrl, type);
      children.add(HidableParam("$type params:", P(url, map)));
    });
    return SingleChildScrollView(
      padding: EdgeInsets.only(
          top: 50, bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Column(
        children: children,
      ),
    );
  }
}
