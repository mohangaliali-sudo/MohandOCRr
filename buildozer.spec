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

requirements =
    python3,
    kivy==2.3.1,
    numpy,
    pillow,
    opencv,
    plyer

android.api = 33
android.minapi = 24
android.archs = arm64-v8a

android.accept_sdk_license = True
android.private_storage = True

android.permissions =
    CAMERA,
    READ_MEDIA_IMAGES

android.entrypoint = org.kivy.android.PythonActivity

log_level = 2
warn_on_root = 1


[buildozer]

log_level = 2
warn_on_root = 1
