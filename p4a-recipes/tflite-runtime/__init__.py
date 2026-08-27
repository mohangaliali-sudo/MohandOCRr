from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory
from os.path import join


class TFLiteRuntimeRecipe(PythonRecipe):
    """
    Local python-for-android recipe for tflite-runtime.

    The package is built from TensorFlow Lite source instead of downloading
    a Linux manylinux wheel from PyPI.
    """

    version = "2.14.0"

    url = (
        "https://github.com/tensorflow/tensorflow/archive/"
        "refs/tags/v2.14.0.tar.gz"
    )

    depends = [
        "setuptools",
        "numpy",
    ]

    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        """
        Build only the TensorFlow Lite runtime shared library.
        """

        with current_directory(self.get_build_dir(arch.arch)):
            self.run_commands(
                [
                    [
                        "bash",
                        "-c",
                        """
set -e

echo "================================"
echo "Building TensorFlow Lite Runtime"
echo "================================"

echo "Architecture:"
echo "$ANDROID_ARCH"

echo "NDK:"
echo "$ANDROIDNDK"

echo "API:"
echo "$ANDROIDAPI"

echo "================================"
echo "Checking TensorFlow Lite source"
echo "================================"

test -d tensorflow/lite

echo "TensorFlow Lite source found"

echo "================================"
echo "Building TensorFlow Lite"
echo "================================"

mkdir -p build
cd build

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DTFLITE_ENABLE_XNNPACK=ON \
    -DTFLITE_ENABLE_RUY=ON \
    -DTFLITE_ENABLE_RESOURCE_VARIABLES=OFF \
    -DTFLITE_ENABLE_NNAPI=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON

cmake --build . --target tensorflow-lite -j2

echo "================================"
echo "TensorFlow Lite build finished"
echo "================================"
"""
                    ]
                ]
            )

    def install_libs(self, arch):
        """
        Install the TensorFlow Lite shared library.
        """

        build_dir = self.get_build_dir(arch.arch)

        lib_dir = join(
            build_dir,
            "build"
        )

        self.copy_libs(
            lib_dir,
            arch.lib_dir
        )

    def postbuild_arch(self, arch):
        """
        Verify the native library exists.
        """

        import os

        candidates = [
            join(arch.lib_dir, "libtensorflow-lite.so"),
            join(arch.lib_dir, "libtensorflow-lite.so.0"),
        ]

        if not any(os.path.exists(x) for x in candidates):
            raise RuntimeError(
                "TensorFlow Lite shared library was not produced."
            )


recipe = TFLiteRuntimeRecipe()
