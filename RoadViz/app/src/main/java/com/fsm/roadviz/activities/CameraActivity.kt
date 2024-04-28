package com.fsm.roadviz.activities

import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.os.Bundle
import android.util.Log
import android.util.Size
import android.view.Surface
import android.view.View
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import com.fsm.roadviz.R
import com.fsm.roadviz.helpers.Helper
import com.fsm.roadviz.ml.runners.ModelRunnerHolder
import com.fsm.roadviz.ml.runners.ModelRunningService
import com.google.android.material.floatingactionbutton.FloatingActionButton
import java.util.concurrent.Executor
import java.util.concurrent.Executors


class CameraActivity : AppCompatActivity() {

    val nLines: Int = 3
    val nPointsPerLine: Int = 20

    lateinit var imagaView: ImageView


    companion object {
        const val MODEL_RUNNER = "MODEL_RUNNER"
        const val MODEL_PATH = "MODEL_PATH"
        const val TAG = "CAMERA"
    }

    var selectedRunner = ""
    var selectedPath = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_camera)
        val cameraExecutor = Executors.newSingleThreadExecutor()
        startCamera(
            cameraExecutor,
            ::onImage,
        )
        imagaView = findViewById(R.id.imageView)
        findViewById<FloatingActionButton>(R.id.close_preview).setOnClickListener(::closePreview)
        findViewById<FloatingActionButton>(R.id.stop_start_model).setOnClickListener(::toggleModel)
        Log.i(CameraActivity.TAG, "Starting camera")

        selectedRunner = intent.getStringExtra(MODEL_RUNNER)!!
        selectedPath = intent.getStringExtra(MODEL_PATH)!!

        startService()

    }

    var index = 0

    private fun loadDummyImage(p: String): Bitmap {
        val path = Helper.assetFilePath(this, p)
//        val bm = BitmapFactory.decodeResource(resources, R.drawable.roa )
        val bMap = BitmapFactory.decodeFile(path)
        Log.i(TAG, "Got image path $path , bitmap $bMap")
        return bMap
    }

    private fun closePreview(v: View) {
        stopService()
        finish()
    }

    private fun startService() {
        Log.i(
            "",
            "Starting service with selectedRunner=$selectedRunner and selectedPath=$selectedPath"
        )
        Intent(this, ModelRunningService::class.java).apply {
            putExtra(MODEL_RUNNER, selectedRunner)
            putExtra(MODEL_PATH, selectedPath)
        }.also(::startService)
    }

    private fun stopService() {
        stopService(Intent(this, ModelRunningService::class.java))

    }

    var runningModel = false
    fun toggleModel(v: View) {
        runningModel = !runningModel
        if (runningModel) {
            startService()
            findViewById<FloatingActionButton>(R.id.stop_start_model).setImageResource(android.R.drawable.ic_media_pause)
        } else {
            stopService()
            findViewById<FloatingActionButton>(R.id.stop_start_model).setImageResource(android.R.drawable.ic_media_play)
        }
    }

    fun RotateBitmap(source: Bitmap, angle: Float): Bitmap {
        val matrix = Matrix()
        matrix.postRotate(angle)
        return Bitmap.createBitmap(source, 0, 0, source.width, source.height, matrix, true)
    }

    val images = arrayOf("road_image1.jpg", "road_image2.jpg", "road_image3.jpg")
    private fun onImage(imageProxy: ImageProxy) {
        //TODO
        var original = imageProxy.toBitmap()
//        var original = loadDummyImage(images.get(((index++)) % images.size))
        if (runningModel) {
            println("Pushing ${original.height}*${original.width}")

            ModelRunnerHolder.getInstance().modelRunner?.also { modelRunner ->
                if (modelRunner.isReady()) modelRunner.pushBitmap(original)
                modelRunner.drawResults(original)?.let {
                    original = it
                }
            }
        }
        runOnUiThread {
            imagaView.setImageBitmap(RotateBitmap(original, 90f))
            println()
        }
        imageProxy.close()
    }

    fun getTargetResolution(): Size {
        return when (resources.configuration.orientation) {
            Configuration.ORIENTATION_PORTRAIT -> Size(1200, 1600)
            Configuration.ORIENTATION_LANDSCAPE -> Size(1600, 1200)
            else -> Size(1600, 1200)
        }
    }

    private fun startCamera(
//        viewFinder: PreviewView,
        cameraExecutor: Executor,
        processImage: (ImageProxy) -> Unit,
    ) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
//            val preview = Preview.Builder().build().also {
//                it.setSurfaceProvider(viewFinder.surfaceProvider)
//            }
            val imageAnalysis = ImageAnalysis.Builder().setTargetRotation(Surface.ROTATION_90)
                .setTargetResolution(Size(640 * 2, 360 * 2)).build()
            imageAnalysis.setAnalyzer(cameraExecutor, processImage)
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, imageAnalysis
                )
            } catch (exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(this))
    }
}