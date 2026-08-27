[app]

# ------------------------------------------------------------
# Basic information
# ------------------------------------------------------------

title = Mohand Sanskrit OCR
package.name = mohandsanskritocr
package.domain = org.mohand

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,tflite,ttf

version = 1.0.0

orientation = portrait

fullscreen = 0


# ------------------------------------------------------------
# Python requirements
# ------------------------------------------------------------

requirements =
    python3,
    kivy==2.3.1,
    pillow,
    numpy,
    opencv,
    tflite-runtime,
    plyer


# ------------------------------------------------------------
# Android
# ------------------------------------------------------------

android.api = 33
android.minapi = 24

android.archs = arm64-v8a

android.ndk = 25b

android.accept_sdk_license = True

android.private_storage = True


# ------------------------------------------------------------
# Permissions
# ------------------------------------------------------------

android.permissions =
    CAMERA,
    READ_MEDIA_IMAGES


# ------------------------------------------------------------
# Android application
# ------------------------------------------------------------

android.entrypoint = org.kivy.android.PythonActivity


# ------------------------------------------------------------
# Assets
# ------------------------------------------------------------

source.include_patterns =
    assets/*.tflite,
    assets/*.ttf,
    classes.txt


# ------------------------------------------------------------
# Java
# ------------------------------------------------------------

android.add_src = %(source.dir)s/android_src


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

log_level = 2


# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

warn_on_root = 1


[buildozer]

log_level = 2

warn_on_root = 1
