package com.fsm.roadviz.ml.runners

import com.fsm.roadviz.ml.runners.onnx.OnnxModel
import com.fsm.roadviz.ml.runners.pytorch.PyTorchLiteRunner


enum class ModelRunners {
    PYTORCH_LITE, ONNX;

    fun toModelRunnerInstance(): IModelRunner = when (this) {
        PYTORCH_LITE -> PyTorchLiteRunner()
        ONNX -> OnnxModel()
    }

    fun getAvailableModels(list: Array<String>): List<String> {
        val filterFunc = when (this) {
            PYTORCH_LITE -> PyTorchLiteRunner::isCompatible
            ONNX -> OnnxModel::isCompatible
        }
        return list.toList().filter(filterFunc)
    }

    companion object {
        fun getAll() = entries.toTypedArray().map { it.name }
        fun getDefaultRunner() = ONNX
    }

}