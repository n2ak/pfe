plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.fsm.roadviz"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.fsm.roadviz"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources.pickFirsts.add("lib/arm64-v8a/libfbjni.so")
        resources.pickFirsts.add("lib/armeabi-v7a/libfbjni.so")
        resources.pickFirsts.add("lib/x86/libfbjni.so")
        resources.pickFirsts.add("lib/x86_64/libfbjni.so")
        resources.pickFirsts.add("lib/arm64-v8a/libpytorch_jni_lite.so")
        resources.pickFirsts.add("lib/armeabi-v7a/libpytorch_jni_lite.so")
        resources.pickFirsts.add("lib/x86/libpytorch_jni_lite.so")
        resources.pickFirsts.add("lib/x86_64/libpytorch_jni_lite.so")

        jniLibs.pickFirsts.add("lib/arm64-v8a/libfbjni.so")
        jniLibs.pickFirsts.add("lib/armeabi-v7a/libfbjni.so")
        jniLibs.pickFirsts.add("lib/x86/libfbjni.so")
        jniLibs.pickFirsts.add("lib/x86_64/libfbjni.so")
        jniLibs.pickFirsts.add("lib/arm64-v8a/libpytorch_jni_lite.so")
        jniLibs.pickFirsts.add("lib/armeabi-v7a/libpytorch_jni_lite.so")
        jniLibs.pickFirsts.add("lib/x86/libpytorch_jni_lite.so")
        jniLibs.pickFirsts.add("lib/x86_64/libpytorch_jni_lite.so")
        resources.excludes.add("META-INF/*")
        resources {
            excludes += "META-INF/native-image/**"
            excludes += "/META-INF/{AL2.0,LGPL2.1}"

        }
    }
}
object Versions {
    const val camerax = "1.4.0-alpha04"
    const val pytorch = "2.1.0"
}
dependencies {

    implementation("org.pytorch:pytorch_android_lite:${Versions.pytorch}") {
        exclude(group = "org.pytorch", module = "pytorch_android")
    }
    implementation("org.pytorch:pytorch_android_torchvision_lite:${Versions.pytorch}") {
        exclude(group = "org.pytorch", module = "pytorch_android")
    }

    implementation("com.microsoft.onnxruntime:onnxruntime-android:latest.release")
    implementation("com.microsoft.onnxruntime:onnxruntime-extensions-android:latest.release")

//    implementation("org.pytorch:pytorch_android_torchvision:${Versions.pytorch}") {
//        exclude(group = "org.pytorch", module = "pytorch_android")
//    }
    implementation("org.pytorch:torchvision_ops:0.14.0")


    implementation("androidx.core:core-ktx:1.10.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.1")
    implementation("androidx.activity:activity-compose:1.7.0")
    implementation(platform("androidx.compose:compose-bom:2023.08.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.9.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2023.08.00"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
    // The following line is optional, as the core library is included indirectly by camera-camera2
    implementation("androidx.camera:camera-core:${Versions.camerax}")
    implementation("androidx.camera:camera-camera2:${Versions.camerax}")
    implementation("androidx.camera:camera-lifecycle:${Versions.camerax}")
    implementation("androidx.camera:camera-video:${Versions.camerax}")
    implementation("androidx.camera:camera-view:${Versions.camerax}")
//    implementation ("androidx.camera:camera-mlkit-vision:${Versions.camerax_version}")
//    implementation ("androidx.camera:camera-extensions:${Versions.camerax_version}")
}
