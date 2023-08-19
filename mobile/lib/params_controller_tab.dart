import 'package:car_security/params/car_detector.dart';
import 'package:car_security/params/draw.dart';
import 'package:car_security/params/hidable_param.dart';
import 'package:flutter/material.dart';

class ParamsControllerTab extends StatefulWidget {
  //const ParamsControllerTab({super.key});
  final String drawParamsUrl;
  final String carParamsUrl;
  const ParamsControllerTab(this.drawParamsUrl, this.carParamsUrl, {super.key});

  @override
  State<ParamsControllerTab> createState() => _ParamsControllerTabState();
}

class _ParamsControllerTabState extends State<ParamsControllerTab> {
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: EdgeInsets.only(
          top: 50, bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Column(
        children: [
          HidableParam(
            "Draw params:",
            DrawParams(
              widget.drawParamsUrl,
            ),
          ),
          HidableParam(
            "Car detector params:",
            CarDetectorParams(
              widget.carParamsUrl,
            ),
          ),
          // SizedBox(height: MediaQuery.of(context).viewInsets.bottom),
        ],
      ),
    );
  }
}
