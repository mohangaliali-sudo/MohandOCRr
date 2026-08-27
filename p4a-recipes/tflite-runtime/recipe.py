from pythonforandroid.recipe import PythonRecipe


class TFLiteRuntimeRecipe(PythonRecipe):

    name = "tflite-runtime"

    version = "2.14.0"

    url = (
        "https://github.com/tensorflow/tensorflow/"
        "archive/refs/tags/v{version}.tar.gz"
    )

    depends = [
        "python3",
        "setuptools",
        "numpy",
    ]

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        env["TFLITE_ENABLE_XNNPACK"] = "0"

        return env

    def build_arch(self, arch):

        import os

        from pythonforandroid.logger import shprint
        from sh import python

        build_dir = self.get_build_dir(arch.arch)

        tensorflow_dir = os.path.join(
            build_dir,
            "tensorflow"
        )

        pip_dir = os.path.join(
            tensorflow_dir,
            "lite",
            "tools",
            "pip_package"
        )

        setup_py = os.path.join(
            pip_dir,
            "setup.py"
        )

        if not os.path.exists(setup_py):
            raise RuntimeError(
                "TensorFlow Lite setup.py not found:\n"
                + setup_py
            )

        env = self.get_recipe_env(arch)

        env["PYTHONPATH"] = (
            tensorflow_dir
            + os.pathsep
            + env.get("PYTHONPATH", "")
        )

        with self.chdir(tensorflow_dir):

            shprint(
                python,
                "-m",
                "pip",
                "install",
                ".",
                "--no-deps",
                "--no-build-isolation",
                _env=env,
            )


recipe = TFLiteRuntimeRecipe()
