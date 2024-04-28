package com.fsm.roadviz.ml.runners

import android.graphics.Bitmap
import com.fsm.roadviz.ml.runners.pytorch.PyTorchLiteRunner

interface IModelRunner {
    fun pushBitmap(input: Bitmap)
    fun getName(): String
    fun isReady(): Boolean
    fun setup(modelPath: String, type: PyTorchLiteRunner.ModelType)
    fun execute(inputImage: Bitmap)
    fun drawResults(bitmap: Bitmap): Bitmap?
    fun close()
    fun start(): Boolean
}