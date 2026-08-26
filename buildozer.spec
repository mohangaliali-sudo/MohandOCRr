[app]

title = Mohand Sanskrit OCR

package.name = mohandsanskritocr

package.domain = org.mohand

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,tflite,ttf,txt

source.include_patterns = assets/*.tflite,assets/fonts/*.ttf,classes.txt

version = 1.0

# ============================================================
# PYTHON / KIVY / TFLITE
# ============================================================

requirements = python3,kivy==2.3.1,pillow,numpy,tflite-runtime,plyer
orientation = portrait

fullscreen = 0

# ============================================================
# ANDROID
# ============================================================

android.api = 31

android.minapi = 24

android.archs = arm64-v8a

android.accept_sdk_license = True

android.private_storage = True

# ============================================================
# PERMISSIONS
# ============================================================

android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# ============================================================
# BUILD
# ============================================================

[buildozer]

log_level = 2

warn_on_root = 1
