package com.fsm.roadviz.ml.runners

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import com.fsm.roadviz.activities.CameraActivity
import com.fsm.roadviz.helpers.Helper
import com.fsm.roadviz.ml.runners.pytorch.PyTorchLiteRunner

class ModelRunningService : Service() {
    companion object {
        const val TAG = "ModelService"
    }

    private var backgroundThread: Thread? = null
    private var isRunning = false
    private var modelRunner: IModelRunner? = null

    override fun onCreate() {
        super.onCreate()
    }

    private fun createModelRunner(runner: ModelRunners, modelPath: String): IModelRunner {
        val path = Helper.assetFilePath(this, modelPath)
        return runner.toModelRunnerInstance().apply {
            Log.i("", "Setting up model,${this.getName()}")
            // TODO: ModelType
            setup(path, PyTorchLiteRunner.ModelType.Segmentation)
            ModelRunnerHolder.getInstance().modelRunner = this
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val runner = ModelRunners.valueOf(intent?.extras?.getString(CameraActivity.MODEL_RUNNER)!!)
        val modelPath = intent.extras?.getString(CameraActivity.MODEL_PATH)!!
        modelRunner = createModelRunner(runner, modelPath)
        if (!isRunning) {
            startBackgroundThread()
        }
        return START_STICKY
    }

    private fun startBackgroundThread() {
        backgroundThread = Thread {
            isRunning = true
            while (isRunning) {
                val start = System.currentTimeMillis()
                val run = modelRunner!!.start()
                if (run) {
                    val end = System.currentTimeMillis()
                    Log.i(TAG, "Model did run in ${end - start}ms")
                } else {
                    try {
                        Thread.sleep(10)
                    } catch (_: Exception) {
                    }
                }
            }
        }
        backgroundThread?.start()
    }

    override fun onDestroy() {
        isRunning = false
        super.onDestroy()
        stopBackgroundThread()
        Log.i(TAG, "Service stopped")
        ModelRunnerHolder.getInstance().modelRunner = null
    }

    private fun stopBackgroundThread() {
        isRunning = false
        backgroundThread?.interrupt()
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}