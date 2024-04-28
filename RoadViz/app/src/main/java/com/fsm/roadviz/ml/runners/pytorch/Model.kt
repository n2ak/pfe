package com.fsm.roadviz.ml.runners.pytorch

import android.graphics.Bitmap
import org.pytorch.Tensor

interface Model {
    fun prepareInput(bitmap: Bitmap): Tensor
    fun postProcessOutput(bitmap: Bitmap, tensor: Tensor): Bitmap
}