package com.fsm.roadviz.ml.runners

class ModelRunnerHolder private constructor() {
    var modelRunner: IModelRunner? = null

    companion object {
        private var instance: ModelRunnerHolder? = null

        fun getInstance(): ModelRunnerHolder {
            if (instance == null) {
                instance = ModelRunnerHolder()
            }
            return instance!!
        }
    }
}
