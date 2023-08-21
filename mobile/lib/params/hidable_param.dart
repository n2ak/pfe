// import 'package:car_security/params/base.dart';
import 'package:flutter/material.dart';

// ignore: must_be_immutable
class HidableParam extends StatefulWidget {
  String label;
  Widget child;
  HidableParam(this.label, this.child, {super.key});

  @override
  State<HidableParam> createState() => HidableParamState();
}

class HidableParamState extends State<HidableParam> {
  late bool visible = false;

  @override
  void initState() {
    visible = false;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    var button = IconButton(
      onPressed: () {
        setState(() {
          visible = !visible;
        });
      },
      icon: Icon(visible
          ? Icons.keyboard_arrow_up_sharp
          : Icons.keyboard_arrow_down_sharp),
    );
    // var inner = (widget.child as Params);
    return Column(
      children: [
        Center(
          child: Row(
            mainAxisAlignment:
                MainAxisAlignment.center, //Center Row contents horizontally,
            crossAxisAlignment:
                CrossAxisAlignment.center, //Center Row contents vertically,
            children: [
              Text(widget.label),
              button,
            ],
          ),
        ),
        Visibility(
          visible: visible,
          child: widget.child,
        ),
      ],
    );
  }
}
