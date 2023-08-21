import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

abstract class Params {
  String? url;
  // Params(this.url);

  Future<String> postRequest(Map<String, dynamic> data) {
    var body = json.encode(data);
    var resp = http.post(Uri.parse(url!),
        headers: {"Content-Type": "application/json"}, body: body);
    var text = resp.then((response) {
      String respText = "Params set successfully.";
      if (response.statusCode != 200) {
        String msg = response.body;
        respText = "Setting params was unsuccessful,Error: $msg";
      }
      return respText;
    });
    return text;
  }

  void _showToast(BuildContext context, String text) {
    final scaffold = ScaffoldMessenger.of(context);
    scaffold.showSnackBar(
      SnackBar(
        content: Text(text),
        action: SnackBarAction(
            label: 'UNDO', onPressed: scaffold.hideCurrentSnackBar),
      ),
    );
  }

  void onSavePressed(Map<String, dynamic> data, BuildContext context) {
    print('Sending');
    postRequest(data).then((text) {
      _showToast(context, text);
    });
  }

  //  prepareData();
}
