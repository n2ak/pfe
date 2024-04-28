package com.fsm.roadviz.ml.runners

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.Typeface

typealias Point = Pair<Float, Float>
typealias Line = List<Point>

fun drawResultOnBitmap(
    bitmap: Bitmap,
    confs: FloatArray,
    indices: FloatArray,
    nLines: Int,
    nPointsPerLine: Int,
    colors: Array<Int> = arrayOf(Color.RED, Color.GREEN, Color.BLUE)
): Bitmap {
    assert(confs.size == nLines)
    assert(colors.size == nLines)
    assert(indices.size == (nLines * nPointsPerLine * 2))

    val canvas = Canvas(bitmap)
    val linePaint = Paint().apply {
        strokeWidth = 5f
    }
    val textPaint = Paint().apply {
        textSize = 25f
        strokeWidth = 10f
        typeface = Typeface.create("serif", Typeface.BOLD_ITALIC)
    }
    val lanePaint = Paint().apply {
        color = Color.argb(100, 0, 255, 0)
        style = Paint.Style.FILL
    }
    val size = Pair(bitmap.height, bitmap.width)
    val lines = mutableListOf<Line>()
    for (line in 0..<nLines) {
        val currentColor = colors[line]
        textPaint.color = currentColor
        linePaint.color = currentColor

        val conf = (confs[line] * 100).toInt()
        canvas.drawText(
            "Line $line:   $conf%",
            10f,
            30f + (line * 30),
            textPaint,
        )
        val xs = line * (nPointsPerLine * 2)
        val ys = xs + nPointsPerLine

        lines.add(
            lineToPoints(
                indices, xs, ys, nPointsPerLine, size
            )
        )
        drawLine(canvas, lines.last(), linePaint)
    }
    drawCurrentLane(canvas, lines[1], lines[2], lanePaint)
    return bitmap
}


fun Path.lineToPoint(p: Point) = this.lineTo(p.first, p.second)
fun Path.moveToPoint(p: Point) = this.moveTo(p.first, p.second)
fun drawCurrentLane(
    canvas: Canvas, line1: Line, line2: Line, lanePaint: Paint, s: Int = 5
) {
    assert(s >= 1)
    val path = Path()
    path.reset()
    path.moveToPoint(line1.first())
    for (p in line1) path.lineToPoint(p)
    for (p in line2.reversed()) path.lineToPoint(p)
    path.moveToPoint(line1.first())
    canvas.drawPath(path, lanePaint)
    path.close()
}

fun drawCircleAt(canvas: Canvas, p: Point) {
    val paint = Paint().apply {
        strokeWidth = 10f
        style = Paint.Style.FILL
        color=Color.BLACK
    }
    canvas.drawCircle(p.first, p.second, 10f, paint)
}

private fun drawLine(
    canvas: Canvas,
    points: Line,
    paint: Paint,
) {
    var previous = points.first()
    for (p in 1..<points.size) {
        val current = points[p]
        canvas.drawLine(
            current.first, current.second, previous.first, previous.second, paint
        )
        previous = current
    }
}

private fun lineToPoints(
    indices: FloatArray,
    offsetX: Int,
    offsetY: Int,
    nPointsPerLine: Int,
    size: Pair<Int, Int>,
) = mutableListOf<Point>().apply {
    for (p in 0..<nPointsPerLine) {
        val point = indices.at(p, offsetX, offsetY, size)
        add(point)
    }
}

fun FloatArray.at(
    p: Int, offsetX: Int, offsetY: Int,
    size: Pair<Int, Int>,
) = Pair(this[p + offsetY] * size.second, this[p + offsetX] * size.first)

