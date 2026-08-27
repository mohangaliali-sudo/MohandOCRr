[app]

# ============================================================
# Basic
# ============================================================

title = Mohand Sanskrit OCR

package.name = mohandsanskritocr

package.domain = org.mohand

source.dir = .

version = 1.0.0


# ============================================================
# Files
# ============================================================

source.include_exts =
    py,
    txt,
    tflite,
    jpg,
    jpeg,
    png,
    kv,
    atlas,
    ttf


source.include_patterns =
    assets/*,
    assets/fonts/*


# ============================================================
# Requirements
# ============================================================

requirements =
    python3,
    kivy==2.3.1,
    pillow,
    numpy,
    opencv,
    tflite-runtime,
    plyer


# ============================================================
# Android
# ============================================================

orientation = portrait

fullscreen = 0

android.archs = arm64-v8a

android.api = 33

android.minapi = 24

android.ndk = 25b

android.accept_sdk_license = True


# ============================================================
# Permissions
# ============================================================

android.permissions =
    CAMERA,
    READ_MEDIA_IMAGES


# ============================================================
# Python-for-Android
# ============================================================

p4a.bootstrap = sdl2

p4a.local_recipes = ./p4a-recipes


# ============================================================
# AndroidX
# ============================================================

android.enable_androidx = True


# ============================================================
# Logging
# ============================================================

log_level = 2


[buildozer]

log_level = 2

warn_on_root = 1
