[app]

title = Mohand Sanskrit OCR

package.name = mohandsanskritocr

package.domain = org.mohand

source.dir = .

version = 1.0.0

orientation = portrait

fullscreen = 0


# ============================================================
# SOURCE FILES
# ============================================================

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


# ============================================================
# ASSETS
# ============================================================

source.include_patterns =
    assets/*.tflite,
    assets/fonts/*.ttf,
    classes.txt


# ============================================================
# PYTHON REQUIREMENTS
# ============================================================

requirements =
    python3,
    kivy==2.3.1,
    pillow,
    numpy,
    opencv,
    plyer


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
# ANDROID PERMISSIONS
# ============================================================

android.permissions =
    CAMERA,
    READ_MEDIA_IMAGES


# ============================================================
# ANDROID ENTRY POINT
# ============================================================

android.entrypoint = org.kivy.android.PythonActivity


# ============================================================
# LOGGING
# ============================================================

log_level = 2

warn_on_root = 1


# ============================================================
# BUILDOZER
# ============================================================

[buildozer]

log_level = 2

warn_on_root = 1
