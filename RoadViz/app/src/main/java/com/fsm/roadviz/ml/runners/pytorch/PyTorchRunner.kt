package com.fsm.roadviz.ml.runners.pytorch

import android.graphics.Bitmap
import android.util.Log
import com.fsm.roadviz.activities.CameraActivity
import com.fsm.roadviz.ml.runners.IModelRunner
import org.pytorch.IValue
import org.pytorch.LiteModuleLoader
import org.pytorch.Module
import org.pytorch.Tensor
import java.util.concurrent.atomic.AtomicBoolean


class PyTorchLiteRunner : IModelRunner {
    //TODO add device
    private var module: Module? = null
    private var output: Tensor? = null
    private var model: Model? = null

    @Volatile
    private var inputImage: Bitmap? = null
    private var ready: AtomicBoolean = AtomicBoolean(true)


    override fun pushBitmap(input: Bitmap) {
        this.inputImage = input
    }

    override fun getName() = "PytorchModel"

    override fun isReady(): Boolean = ready.get()
    enum class ModelType {
        Segmentation, Detection
    }

    override fun setup(modelPath: String, type: ModelType) {
        Log.i(CameraActivity.TAG, "Loading model $modelPath $type")
        module = when {
            modelPath.endsWith(".ptl") -> LiteModuleLoader.load(modelPath)
            else -> Module.load(modelPath)
        }
        model = when (type) {
            ModelType.Segmentation -> SegmentationModel()
            ModelType.Detection -> throw Exception("")
        }
        Log.i(CameraActivity.TAG, "loaded model")

    }

    override fun execute(inputImage: Bitmap) {
        ready.set(false)
        val input = model!!.prepareInput(inputImage)
        output = module!!.forward(IValue.from(input)).toTensor()
        ready.set(true)
    }

    override fun drawResults(bitmap: Bitmap): Bitmap? {
        if (output == null) return null;
        return model!!.postProcessOutput(bitmap, output!!)
    }


    override fun close() {
    }

    override fun start() = (inputImage != null).also { if (it) (execute(inputImage!!)) }

    companion object {
        fun isCompatible(p: String) = p.endsWith(".pt").or(p.endsWith(".ptl"))
    }


}