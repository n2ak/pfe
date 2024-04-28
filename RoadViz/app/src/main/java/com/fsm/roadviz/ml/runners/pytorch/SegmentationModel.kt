package com.fsm.roadviz.ml.runners.pytorch

import android.graphics.Bitmap
import android.util.Log
import com.fsm.roadviz.activities.CameraActivity
import org.pytorch.Tensor
import org.pytorch.torchvision.TensorImageUtils
import java.util.Arrays

class SegmentationModel() : Model {
    override fun prepareInput(bitmap: Bitmap) = imageToTensor(bitmap)
    override fun postProcessOutput(bitmap: Bitmap, tensor: Tensor): Bitmap {
        Log.i(CameraActivity.TAG, "OUTPUT: ${Arrays.toString(tensor.shape())}")
        return bitmap
    }

    private fun imageToTensor(bitmap: Bitmap): Tensor = TensorImageUtils.bitmapToFloat32Tensor(
        bitmap,
        TensorImageUtils.TORCHVISION_NORM_MEAN_RGB,
        TensorImageUtils.TORCHVISION_NORM_STD_RGB
    )
}