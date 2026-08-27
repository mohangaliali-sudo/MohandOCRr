from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info_main
from pythonforandroid.util import current_directory

from os.path import join
import os
import tarfile
import sh


class TFLiteRuntimeRecipe(Recipe):

    version = "2.19.0"

    url = (
        "https://github.com/DeNA/tflite-runtime-builder/"
        "releases/download/2.19.0/"
        "tflite-runtime-android-arm64-2.19.0.tgz"
    )

    depends = ["python3", "numpy"]

    def build_arch(self, arch):

        if arch.arch != "arm64-v8a":
            info_main(
                "tflite-runtime: skipping unsupported architecture "
                + arch.arch
            )
            return

        info_main("==============================================")
        info_main("Building custom tflite-runtime")
        info_main("Architecture: " + arch.arch)
        info_main("Version: " + self.version)
        info_main("==============================================")

        build_dir = self.get_build_dir(arch.arch)

        package_dir = join(
            self.ctx.packages_path,
            self.name
        )

        archive = join(
            package_dir,
            "tflite-runtime-android-arm64-2.19.0.tgz"
        )

        if not os.path.exists(archive):
            raise RuntimeError(
                "tflite-runtime archive was not downloaded: "
                + archive
            )

        os.makedirs(build_dir, exist_ok=True)

        info_main("Extracting tflite-runtime archive...")

        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(build_dir)

        info_main("Archive extracted.")

        # Find the shared library
        so_file = None

        for root, dirs, files in os.walk(build_dir):
            for filename in files:
                if filename.endswith(".so"):
                    candidate = join(root, filename)

                    if "tflite" in filename.lower():
                        so_file = candidate
                        break

            if so_file:
                break

        if so_file is None:
            raise RuntimeError(
                "Could not find tflite-runtime shared library "
                "inside downloaded archive."
            )

        info_main("Found library:")
        info_main(so_file)

        # Python installation directory
        site_packages = self.ctx.get_site_packages_dir(
            arch.arch
        )

        target_dir = join(
            site_packages,
            "tflite_runtime"
        )

        os.makedirs(target_dir, exist_ok=True)

        target_so = join(
            target_dir,
            "_pywrap_tensorflow_interpreter_wrapper.so"
        )

        info_main(
            "Installing shared library to:"
        )
        info_main(target_so)

        shprint(
            sh.cp,
            so_file,
            target_so
        )

        # Create the Python package
        init_file = join(
            target_dir,
            "__init__.py"
        )

        with open(init_file, "w", encoding="utf-8") as f:
            f.write(
                """
from .interpreter import Interpreter
from .interpreter import load_delegate

__all__ = [
    "Interpreter",
    "load_delegate",
]
"""
            )

        # interpreter.py
        interpreter_file = join(
            target_dir,
            "interpreter.py"
        )

        with open(
            interpreter_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                r'''
import ctypes
import os


_LIB_NAME = "_pywrap_tensorflow_interpreter_wrapper.so"


def _load_library():

    package_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    library_path = os.path.join(
        package_dir,
        _LIB_NAME
    )

    return ctypes.CDLL(library_path)


class Interpreter:

    def __init__(
        self,
        model_path=None,
        model_content=None,
        num_threads=None,
        experimental_delegates=None,
        experimental_op_resolver_type=None,
        **kwargs
    ):

        # The actual TensorFlow Lite Python API is
        # normally supplied by the native runtime.
        #
        # This wrapper is intentionally minimal.
        #
        # If the packaged runtime exposes the normal
        # interpreter module, use it.

        try:

            from tflite_runtime.interpreter_wrapper import (
                Interpreter as NativeInterpreter
            )

            self._interpreter = NativeInterpreter(
                model_path=model_path,
                model_content=model_content,
                num_threads=num_threads
            )

        except ImportError as exc:

            raise ImportError(
                "The packaged tflite-runtime native "
                "interpreter is unavailable."
            ) from exc

    def allocate_tensors(self):

        return self._interpreter.allocate_tensors()

    def get_input_details(self):

        return self._interpreter.get_input_details()

    def get_output_details(self):

        return self._interpreter.get_output_details()

    def set_tensor(self, index, value):

        return self._interpreter.set_tensor(
            index,
            value
        )

    def get_tensor(self, index):

        return self._interpreter.get_tensor(index)

    def invoke(self):

        return self._interpreter.invoke()


def load_delegate(
    library,
    options=None
):

    raise RuntimeError(
        "Delegates are not enabled in this Android build."
    )
'''
            )


recipe = TFLiteRuntimeRecipe()
