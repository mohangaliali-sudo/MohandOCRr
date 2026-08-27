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

requirements = python3,kivy==2.3.1,pillow,numpy,plyer,hostpython3

orientation = portrait

fullscreen = 0

# ============================================================
# ANDROID
# ============================================================
# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (string) Android NDK version to use
android.ndk = 25b

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
