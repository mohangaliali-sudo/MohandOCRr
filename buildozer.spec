[app]

title = Mohand Sanskrit OCR

package.name = mohandsanskritocr
package.domain = org.mohand

source.dir = .

source.include_exts =
    py,
    png,
    jpg,
    jpeg,
    kv,
    atlas,
    txt,
    tflite,
    ttf

source.include_patterns =
    assets/*.tflite,
    assets/fonts/*.ttf,
    classes.txt

version = 1.0.0

orientation = portrait
fullscreen = 0


# ============================================================
# REQUIREMENTS
# ============================================================

requirements =
    python3==3.11.9,
    kivy==2.3.1,
    numpy,
    pillow,
    opencv,
    plyer,
    tflite-runtime


# ============================================================
# ANDROID
# ============================================================

android.api = 33

android.minapi = 24

android.archs = arm64-v8a

android.ndk = 25b

android.accept_sdk_license = True

android.private_storage = True


# ============================================================
# PERMISSIONS
# ============================================================

android.permissions =
    CAMERA,
    READ_MEDIA_IMAGES


# ============================================================
# ENTRY POINT
# ============================================================

android.entrypoint = org.kivy.android.PythonActivity


# ============================================================
# LOGGING
# ============================================================

log_level = 2

warn_on_root = 1


[buildozer]

log_level = 2

warn_on_root = 1
