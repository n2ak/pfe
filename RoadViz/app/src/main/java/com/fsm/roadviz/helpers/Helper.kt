package com.fsm.roadviz.helpers

import android.app.Activity
import android.content.Context
import android.widget.Toast
import java.io.File
import java.io.FileOutputStream
import java.io.IOException

class Helper {
    companion object {
        @Throws(IOException::class)
        fun assetFilePath(context: Context, assetName: String, parent: String = ""): String {
            val file = File(context.filesDir, assetName)
            if (file.exists() && file.length() > 0) {
                return file.absolutePath
            }
            context.assets.open(assetName).use { `is` ->
                FileOutputStream(file).use { os ->
                    val buffer = ByteArray(4 * 1024)
                    var read: Int
                    while (`is`.read(buffer).also { read = it } != -1) {
                        os.write(buffer, 0, read)
                    }
                    os.flush()
                }
                return file.absolutePath
            }
        }

        fun toast(
            context: Activity, text: String, dur: Int = Toast.LENGTH_SHORT, runOnUi: Boolean = false
        ) {
            if (runOnUi) {
                context.runOnUiThread {
                    Toast.makeText(context, text, dur).show()
                }
            } else {
                Toast.makeText(context, text, dur).show()
            }
        }
    }

}