from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint

from os.path import join
import os
import tarfile
import glob
import sh


class TFLiteRuntimeRecipe(Recipe):

    version = "2.19.0"

    url = None

    depends = [
        "python3",
        "numpy",
    ]

    def prebuild_arch(self, arch):
        pass

    def build_arch(self, arch):

        if arch.arch != "arm64-v8a":
            return

        build_dir = self.get_build_dir(arch.arch)

        archive = join(
            self.get_recipe_dir(),
            "tflite-runtime-android-arm64-2.19.0.tgz"
        )

        if not os.path.exists(archive):
            raise RuntimeError(
                "Missing local TFLite Runtime archive:\n"
                + archive
            )

        os.makedirs(build_dir, exist_ok=True)

        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(build_dir)

        # -------------------------------------------------
        # Find Python package
        # -------------------------------------------------

        candidates = []

        for root, dirs, files in os.walk(build_dir):

            for filename in files:

                if filename.endswith(".so"):

                    candidates.append(
                        join(root, filename)
                    )

        if not candidates:

            raise RuntimeError(
                "No .so file found in TFLite archive."
            )

        info = "\n".join(candidates)

        print(
            "TFLITE LIBRARIES:\n" + info
        )

        # -------------------------------------------------
        # Install native libraries
        # -------------------------------------------------

        libs_dir = self.ctx.get_libs_dir(
            arch.arch
        )

        os.makedirs(
            libs_dir,
            exist_ok=True
        )

        for lib in candidates:

            destination = join(
                libs_dir,
                os.path.basename(lib)
            )

            shprint(
                sh.cp,
                lib,
                destination
            )


recipe = TFLiteRuntimeRecipe()
