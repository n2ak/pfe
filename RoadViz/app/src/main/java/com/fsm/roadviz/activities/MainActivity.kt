package com.fsm.roadviz.activities

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.Spinner
import androidx.appcompat.app.AppCompatActivity
import com.fsm.roadviz.R
import com.fsm.roadviz.ml.runners.ModelRunners
import java.util.Arrays


class MainActivity : AppCompatActivity() {
    lateinit var button: Button
    lateinit var modelRunnersDropdown: Spinner
    lateinit var modelPathDropdown: Spinner

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        button = findViewById(R.id.start_camera)
        modelRunnersDropdown = findViewById(R.id.model_runners_dropdown)
        modelPathDropdown = findViewById(R.id.models_dropdown)

        button.setOnClickListener(::startCameraActivity)
        val availableRunners = ModelRunners.getAll()
        val adapter =
            ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, availableRunners)
        modelRunnersDropdown.adapter = adapter
        modelRunnersDropdown.setSelection(adapter.getPosition(ModelRunners.getDefaultRunner().name))
        modelRunnersDropdown.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(
                parent: AdapterView<*>?, view: View?, position: Int, id: Long
            ) {
                resetAdapter(availableRunners.get(id.toInt()))
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {
                TODO("Not yet implemented")
            }
        }
        resetAdapter(ModelRunners.getDefaultRunner().name)

    }

    fun resetAdapter(selected: String) {
        Log.i(
            "",
            "getAvailableModels($selected) ${Arrays.toString(getAvailableModels(selected).toTypedArray())}"
        )
        modelPathDropdown.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item, getAvailableModels(selected)
        )
        modelPathDropdown.setSelection(0)
    }

    private fun getAvailableModels(selectedRunner: String): List<String> {
        val runner = ModelRunners.valueOf(selectedRunner)
        val list = assets.list("")!!
        return runner.getAvailableModels(list)

    }

    private fun startCameraActivity(b: View) {
        val selectedRunner = modelRunnersDropdown.selectedItem as String
        val selectedPath = modelPathDropdown.selectedItem as String
        Intent(this, CameraActivity::class.java).apply {
            putExtra(CameraActivity.MODEL_RUNNER, selectedRunner)
            putExtra(CameraActivity.MODEL_PATH, selectedPath)
        }.also(::startActivity)
    }

}/*

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    RoadVizTheme {
        Greeting("Android")
    }
}
 */
