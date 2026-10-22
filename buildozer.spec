[app]

# (str) Title of your application
title = Rocket Boots

# (str) Package name
package.name = rocketboots

# (str) Package domain (needed for android/ios packaging)
package.domain = com.ocjono

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,wav,ttf,gif,json

# (list) List of directory to exclude
source.exclude_dirs = bin,.buildozer,.git,build,dist,.idea

# (str) Application versioning
version = 0.5.0

# (list) Application requirements
# Modern Python 3 and Kivy 2.3+
requirements = python3,kivy,pillow

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# (int) Android API to use (34 for Android 14 / modern phones)
android.api = 34

# (int) Minimum API required (21 = Android 5.0 Lollipop+)
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for (arm64-v8a is REQUIRED for modern phones)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Automatically accept SDK licenses
android.accept_sdk_license = True

# (bool) Enable AndroidX
android.enable_androidx = True

# (bool) Allow backup
android.allow_backup = True

# (str) Android entry point
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
