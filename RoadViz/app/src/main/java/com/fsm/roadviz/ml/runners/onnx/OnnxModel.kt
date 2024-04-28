package com.fsm.roadviz.ml.runners.onnx

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import ai.onnxruntime.extensions.OrtxPackage
import android.content.res.Resources
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.util.Log
import com.fsm.roadviz.ml.runners.IModelRunner
import com.fsm.roadviz.ml.runners.Point
import com.fsm.roadviz.ml.runners.drawCircleAt
import com.fsm.roadviz.ml.runners.pytorch.PyTorchLiteRunner
import org.pytorch.torchvision.TensorImageUtils
import java.nio.FloatBuffer
import java.util.Arrays
import java.util.Collections
import java.util.concurrent.atomic.AtomicReference


class OnnxModel : IModelRunner {

    private var ortEnv: OrtEnvironment = OrtEnvironment.getEnvironment()
    private lateinit var ortSession: OrtSession

    @Volatile
    private var inputImage: Bitmap? = null

    @Volatile
    private var output: AtomicReference<OrtSession.Result?> = AtomicReference(null)
    private var ready = true

//    fun detect(inputStream: InputStream, ortEnv: OrtEnvironment, ortSession: OrtSession): IntArray {
//        // Step 1: convert image into byte array (raw image bytes)
//        val rawImageBytes = inputStream.readBytes()
//
//        // Step 2: get the shape of the byte array and make ort tensor
//        val shape = longArrayOf(rawImageBytes.size.toLong())
//
//        val inputTensor = OnnxTensor.createTensor(
//            ortEnv, ByteBuffer.wrap(rawImageBytes), shape, OnnxJavaType.UINT8
//        )
//        inputTensor.use {
//            // Step 3: call ort inferenceSession run
//            val output = ortSession.run(
//                Collections.singletonMap("image", inputTensor),
//                setOf("image_out", "scaled_box_out_next")
//            )
//
//            // Step 4: output analysis
//            output.use {
//                return (output?.get(0)?.value) as IntArray
//            }
//        }
//    }

    private fun byteArrayToBitmap(data: ByteArray): Bitmap {
        return BitmapFactory.decodeByteArray(data, 0, data.size)
    }

    override fun pushBitmap(input: Bitmap) {
        this.inputImage = input
    }

    override fun getName() = "OnnxModel"

    override fun isReady() = ready

    //TODO
    override fun setup(modelPath: String, type: PyTorchLiteRunner.ModelType) {
        Log.i(getName(), "Loading onnx model, at '$modelPath'")
        val sessionOptions: OrtSession.SessionOptions = OrtSession.SessionOptions()
        sessionOptions.registerCustomOpLibrary(OrtxPackage.getLibraryPath())
        ortSession = ortEnv.createSession(modelPath, sessionOptions)
    }

    private fun readModel(): ByteArray {
        val modelID = com.fsm.roadviz.R.raw.sss
        return Resources.getSystem().openRawResource(modelID).readBytes()
    }

    fun throughPytorch(bitmap: Bitmap) = TensorImageUtils.bitmapToFloat32Tensor(
        bitmap,
        TensorImageUtils.TORCHVISION_NORM_MEAN_RGB,
        TensorImageUtils.TORCHVISION_NORM_STD_RGB
    ).also {
        Log.i("", "Input shape: ${Arrays.toString(it.shape())}")
    }.dataAsFloatArray

    fun preProcess(bitmap: Bitmap): FloatBuffer {

        val DIM_BATCH_SIZE = 1;
        val DIM_PIXEL_SIZE = 3;
        val IMAGE_SIZE_X = w;
        val IMAGE_SIZE_Y = h;
        val imgData = FloatBuffer.allocate(
            DIM_BATCH_SIZE * DIM_PIXEL_SIZE * IMAGE_SIZE_X * IMAGE_SIZE_Y
        )
        imgData.rewind()
        val stride = IMAGE_SIZE_X * IMAGE_SIZE_Y
        val bmpData = IntArray(stride)
        bitmap.getPixels(bmpData, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
        for (i in 0..IMAGE_SIZE_X - 1) {
            for (j in 0..IMAGE_SIZE_Y - 1) {
                val idx = IMAGE_SIZE_Y * i + j
                val pixelValue = bmpData[idx]
                imgData.put(idx, (((pixelValue shr 16 and 0xFF) / 255f - 0.485f) / 0.229f))
                imgData.put(idx + stride, (((pixelValue shr 8 and 0xFF) / 255f - 0.456f) / 0.224f))
                imgData.put(idx + stride * 2, (((pixelValue and 0xFF) / 255f - 0.406f) / 0.225f))
            }
        }

        imgData.rewind()
        return imgData
    }

    private fun toArray(bitmap: Bitmap): FloatBuffer {
        return preProcess(bitmap)
    }

    val w = 640
    val h = 384

    override fun execute(image: Bitmap) {
        ready = false

        val input = Bitmap.createScaledBitmap(image, w, h, false)
        println("Scaled from ${image.height}*${image.width} to $h*$w")
//        val rawImageBytes = toArray(input).array()
        val rawImageBytes = throughPytorch(input)
        val inputName = ortSession.inputNames?.iterator()?.next()
        val shape = longArrayOf(1, 3, h.toLong(), w.toLong())
        val inputTensor = OnnxTensor.createTensor(ortEnv, FloatBuffer.wrap(rawImageBytes), shape)
        output.set(
            ortSession.run(
                Collections.singletonMap(inputName, inputTensor), setOf("out")
            )
        )
        println("output ${output} ${android.os.Process.myTid()}")

        ready = true
    }

    override fun drawResults(bitmap: Bitmap): Bitmap? {
        val res = output.get()
        println("output ${output} ${res} ${android.os.Process.myTid()}")

        if (res == null) return null;
        val value = (res.get(0).value as List<Float>)
        val ret = (value[0] as OnnxTensor)
        return postProcessOutput(bitmap, ret.floatBuffer.array(), ret.info.shape)
    }

    private fun postProcessOutput(input: Bitmap, mask: FloatArray, shape: LongArray): Bitmap {
        Log.i(
            "",
            "mask len ${mask.size},found shape: ${Arrays.toString(shape)} ,image shape: ${input.height}*${input.width}"
        )
        val nLines = if (shape[0] > 3) 3 else shape[0]
        if (nLines.toInt() == 0) return input
        val mutableBitmap: Bitmap = input.copy(Bitmap.Config.ARGB_8888, true)
        val canvas = Canvas(mutableBitmap)
        for (i in 0..<nLines) {
            val len = shape[1] * shape[2]
            for (j in 0..<shape[1]) {
                for (k in 0..<shape[2]) {
                    val index = (j * shape[2] + k) + len * i
                    val isLane = mask.get(index.toInt()) > .5
                    if (isLane) {
                        val p =
                            Point((k.toFloat() / h * input.height), (j.toFloat() / w * input.width))
                        drawCircleAt(canvas, p)
                    }
                }
            }
        }

        return mutableBitmap
    }

    override fun close() {
        ortSession.close()
        ortEnv.close()
    }

    override fun start() = (inputImage != null).also { if (it) (execute(inputImage!!)) }

    companion object {
        fun isCompatible(p: String) = p.endsWith(".onnx")

    }
}