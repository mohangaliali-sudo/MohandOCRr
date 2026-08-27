# ============================================================
# main.py
# Mohand Sanskrit OCR
#
# Kivy Android Application
#
# TFLite Float32
# Camera + Gallery
# ============================================================

import os
import threading

import cv2

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivy.graphics import Color, RoundedRectangle

from plyer import camera

from ocr_processor import SanskritOCR


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)

FONTS_DIR = os.path.join(
    ASSETS_DIR,
    "fonts"
)

MODEL_PATH = os.path.join(
    ASSETS_DIR,
    "best.tflite"
)

CLASSES_PATH = os.path.join(
    BASE_DIR,
    "classes.txt"
)


# ============================================================
# FONTS
# ============================================================

DEVANAGARI_FONT = os.path.join(
    FONTS_DIR,
    "NotoSansDevanagari-Regular.ttf"
)

ARABIC_FONT = os.path.join(
    FONTS_DIR,
    "Cairo-Regular.ttf"
)

ROBOTO_FONT = os.path.join(
    FONTS_DIR,
    "Roboto-Regular.ttf"
)


# ============================================================
# DESKTOP WINDOW
# ============================================================

try:

    Window.size = (
        420,
        800
    )

except Exception:

    pass


# ============================================================
# ROUNDED BUTTON
# ============================================================

class RoundedButton(Button):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            **kwargs
        )

        self.background_normal = ""
        self.background_down = ""

        with self.canvas.before:

            Color(
                0.12,
                0.38,
                0.65,
                1
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    dp(12)
                ]
            )

        self.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

    def _update_bg(
        self,
        *args
    ):

        self.bg.pos = self.pos
        self.bg.size = self.size


# ============================================================
# APPLICATION
# ============================================================

class SanskritOCRApp(App):

    # ========================================================
    # BUILD
    # ========================================================

    def build(self):

        self.title = (
            "Mohand Sanskrit OCR"
        )

        self.current_image_path = None
        self.current_image = None

        self.processing = False
        self.ocr = None

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = Label(
            text="Mohand Sanskrit OCR",
            font_name=self._english_font(),
            font_size=dp(22),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )

        root.add_widget(
            title
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = Label(
            text="جاري بدء التطبيق...",
            font_name=self._arabic_font(),
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40)
        )

        root.add_widget(
            self.status_label
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        self.image_widget = Image(
            source="",
            allow_stretch=True,
            keep_ratio=True
        )

        root.add_widget(
            self.image_widget
        )

        # ----------------------------------------------------
        # IMAGE BUTTONS
        # ----------------------------------------------------

        image_buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(55)
        )

        camera_button = RoundedButton(
            text="الكاميرا",
            font_name=self._arabic_font(),
            font_size=dp(15)
        )

        camera_button.bind(
            on_release=self.open_camera
        )

        image_buttons.add_widget(
            camera_button
        )

        gallery_button = RoundedButton(
            text="المعرض",
            font_name=self._arabic_font(),
            font_size=dp(15)
        )

        gallery_button.bind(
            on_release=self.open_gallery
        )

        image_buttons.add_widget(
            gallery_button
        )

        root.add_widget(
            image_buttons
        )

        # ----------------------------------------------------
        # OCR BUTTON
        # ----------------------------------------------------

        self.ocr_button = RoundedButton(
            text="تشغيل OCR",
            font_name=self._arabic_font(),
            font_size=dp(17),
            size_hint_y=None,
            height=dp(60),
            disabled=True
        )

        self.ocr_button.bind(
            on_release=self.start_ocr
        )

        root.add_widget(
            self.ocr_button
        )

        # ----------------------------------------------------
        # RESULT TITLE
        # ----------------------------------------------------

        text_title = Label(
            text="النص المستخرج",
            font_name=self._arabic_font(),
            font_size=dp(18),
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(
            text_title
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        self.result_text = TextInput(
            text="",
            multiline=True,
            font_name=self._devanagari_font(),
            font_size=dp(24),
            halign="right",
            valign="top",
            padding=[
                dp(10),
                dp(10),
                dp(10),
                dp(10)
            ],
            readonly=False
        )

        root.add_widget(
            self.result_text
        )

        # ----------------------------------------------------
        # TEXT BUTTONS
        # ----------------------------------------------------

        text_buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(55)
        )

        copy_button = RoundedButton(
            text="نسخ",
            font_name=self._arabic_font(),
            font_size=dp(15)
        )

        copy_button.bind(
            on_release=self.copy_text
        )

        text_buttons.add_widget(
            copy_button
        )

        clear_button = RoundedButton(
            text="مسح",
            font_name=self._arabic_font(),
            font_size=dp(15)
        )

        clear_button.bind(
            on_release=self.clear_text
        )

        text_buttons.add_widget(
            clear_button
        )

        root.add_widget(
            text_buttons
        )

        # ----------------------------------------------------
        # OCR INITIALIZATION
        # ----------------------------------------------------

        Clock.schedule_once(
            self.initialize_ocr,
            0.5
        )

        return root

    # ========================================================
    # FONTS
    # ========================================================

    def _devanagari_font(self):

        if os.path.exists(
            DEVANAGARI_FONT
        ):

            return DEVANAGARI_FONT

        return "Roboto"

    def _arabic_font(self):

        if os.path.exists(
            ARABIC_FONT
        ):

            return ARABIC_FONT

        return "Roboto"

    def _english_font(self):

        if os.path.exists(
            ROBOTO_FONT
        ):

            return ROBOTO_FONT

        return "Roboto"

    # ========================================================
    # CHECK FILES
    # ========================================================

    def check_files(self):

        missing = []

        required_files = [

            (
                MODEL_PATH,
                "assets/best.tflite"
            ),

            (
                CLASSES_PATH,
                "classes.txt"
            ),

            (
                DEVANAGARI_FONT,
                "assets/fonts/"
                "NotoSansDevanagari-Regular.ttf"
            ),

            (
                ARABIC_FONT,
                "assets/fonts/"
                "Cairo-Regular.ttf"
            ),

            (
                ROBOTO_FONT,
                "assets/fonts/"
                "Roboto-Regular.ttf"
            )

        ]

        for path, name in required_files:

            if not os.path.exists(path):

                missing.append(name)

        return missing

    # ========================================================
    # INITIALIZE OCR
    # ========================================================

    def initialize_ocr(
        self,
        *args
    ):

        self.status_label.text = (
            "جاري تحميل نموذج OCR..."
        )

        def load():

            try:

                missing = self.check_files()

                if missing:

                    raise FileNotFoundError(
                        "الملفات التالية مفقودة:\n\n"
                        +
                        "\n".join(
                            missing
                        )
                    )

                ocr = SanskritOCR(

                    model_path=MODEL_PATH,

                    classes_path=CLASSES_PATH,

                    img_size=640,

                    conf_threshold=0.15,

                    iou_threshold=0.45,

                    line_threshold_ratio=0.50

                )

                Clock.schedule_once(
                    lambda dt:
                    self.ocr_ready(
                        ocr
                    )
                )

            except Exception as e:

                error = str(e)

                Clock.schedule_once(
                    lambda dt:
                    self.ocr_error(
                        error
                    )
                )

        threading.Thread(
            target=load,
            daemon=True
        ).start()

    # ========================================================
    # OCR READY
    # ========================================================

    def ocr_ready(
        self,
        ocr
    ):

        self.ocr = ocr

        self.status_label.text = (
            "جاهز — اختر صورة"
        )

        self.ocr_button.disabled = False

    # ========================================================
    # OCR ERROR
    # ========================================================

    def ocr_error(
        self,
        error
    ):

        self.status_label.text = (
            "خطأ في تحميل OCR"
        )

        self.ocr_button.disabled = True

        self.show_error(
            "خطأ OCR",
            error
        )

    # ========================================================
    # CAMERA
    # ========================================================

    def open_camera(
        self,
        *args
    ):

        self.status_label.text = (
            "فتح الكاميرا..."
        )

        try:

            filename = os.path.join(
                self.user_data_dir,
                "ocr_camera.jpg"
            )

            camera.take_picture(
                filename=filename,
                on_complete=self.camera_complete
            )

        except Exception as e:

            self.status_label.text = (
                "تعذر فتح الكاميرا"
            )

            self.show_error(
                "الكاميرا",
                str(e)
            )

    # ========================================================
    # CAMERA COMPLETE
    # ========================================================

    def camera_complete(
        self,
        filename
    ):

        if not filename:
            return

        Clock.schedule_once(
            lambda dt:
            self.load_image_file(
                filename
            )
        )

    # ========================================================
    # GALLERY
    # ========================================================

    def open_gallery(
        self,
        *args
    ):

        content = BoxLayout(
            orientation="vertical"
        )

        chooser = FileChooserListView(
            path="/",
            filters=[
                "*.jpg",
                "*.jpeg",
                "*.png",
                "*.JPG",
                "*.JPEG",
                "*.PNG"
            ]
        )

        content.add_widget(
            chooser
        )

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(5)
        )

        select_button = RoundedButton(
            text="اختيار",
            font_name=self._arabic_font()
        )

        cancel_button = RoundedButton(
            text="إلغاء",
            font_name=self._arabic_font()
        )

        buttons.add_widget(
            select_button
        )

        buttons.add_widget(
            cancel_button
        )

        content.add_widget(
            buttons
        )

        popup = Popup(
            title="اختر صورة",
            content=content,
            size_hint=(
                0.95,
                0.9
            )
        )

        def select_file(
            *args
        ):

            selection = chooser.selection

            if not selection:
                return

            filename = selection[0]

            popup.dismiss()

            self.load_image_file(
                filename
            )

        select_button.bind(
            on_release=select_file
        )

        cancel_button.bind(
            on_release=popup.dismiss
        )

        popup.open()

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    def load_image_file(
        self,
        filename
    ):

        if not filename:
            return

        if not os.path.exists(
            filename
        ):

            self.show_error(
                "الصورة",
                "الملف غير موجود"
            )

            return

        image = cv2.imread(
            filename
        )

        if image is None:

            self.show_error(
                "الصورة",
                "تعذر قراءة الصورة"
            )

            return

        self.current_image_path = filename

        self.current_image = image

        self.image_widget.source = filename

        self.image_widget.reload()

        self.status_label.text = (
            "تم اختيار الصورة"
        )

    # ========================================================
    # START OCR
    # ========================================================

    def start_ocr(
        self,
        *args
    ):

        if self.processing:
            return

        if self.ocr is None:

            self.show_error(
                "OCR",
                "النموذج لم يتم تحميله بعد."
            )

            return

        if self.current_image is None:

            self.show_error(
                "OCR",
                "اختر صورة أولًا."
            )

            return

        self.processing = True

        self.ocr_button.disabled = True

        self.status_label.text = (
            "جاري تحليل الصورة..."
        )

        image = (
            self.current_image.copy()
        )

        def process():

            try:

                result = (
                    self.ocr.process_image(
                        image,
                        draw=True
                    )
                )

                Clock.schedule_once(
                    lambda dt:
                    self.show_ocr_result(
                        result
                    )
                )

            except Exception as e:

                error = str(e)

                Clock.schedule_once(
                    lambda dt:
                    self.ocr_failed(
                        error
                    )
                )

        threading.Thread(
            target=process,
            daemon=True
        ).start()

    # ========================================================
    # RESULT
    # ========================================================

    def show_ocr_result(
        self,
        result
    ):

        self.processing = False

        self.ocr_button.disabled = False

        text = result.get(
            "text",
            ""
        )

        self.result_text.text = text

        before_nms = result.get(
            "before_nms",
            0
        )

        after_nms = result.get(
            "after_nms",
            0
        )

        lines = result.get(
            "lines",
            []
        )

        self.status_label.text = (
            f"تم الانتهاء | "
            f"الكشوف: {before_nms} | "
            f"بعد NMS: {after_nms} | "
            f"الأسطر: {len(lines)}"
        )

        result_image = result.get(
            "image"
        )

        if result_image is not None:

            result_path = os.path.join(
                self.user_data_dir,
                "ocr_result.jpg"
            )

            try:

                cv2.imwrite(
                    result_path,
                    result_image
                )

                self.image_widget.source = (
                    result_path
                )

                self.image_widget.reload()

            except Exception:

                pass

    # ========================================================
    # FAILED
    # ========================================================

    def ocr_failed(
        self,
        error
    ):

        self.processing = False

        self.ocr_button.disabled = False

        self.status_label.text = (
            "حدث خطأ أثناء OCR"
        )

        self.show_error(
            "خطأ OCR",
            error
        )

    # ========================================================
    # COPY
    # ========================================================

    def copy_text(
        self,
        *args
    ):

        text = self.result_text.text

        if not text.strip():

            self.status_label.text = (
                "لا يوجد نص لنسخه"
            )

            return

        try:

            Clipboard.copy(
                text
            )

            self.status_label.text = (
                "تم نسخ النص"
            )

        except Exception as e:

            self.show_error(
                "نسخ",
                str(e)
            )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_text(
        self,
        *args
    ):

        self.result_text.text = ""

        self.status_label.text = (
            "تم مسح النص"
        )

    # ========================================================
    # ERROR POPUP
    # ========================================================

    def show_error(
        self,
        title,
        message
    ):

        content = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )

        scroll = ScrollView()

        label = Label(
            text=str(message),
            font_name=self._english_font(),
            font_size=dp(14),
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        label.bind(
            texture_size=lambda instance,
            value:
            setattr(
                instance,
                "height",
                value[1]
            )
        )

        scroll.add_widget(
            label
        )

        content.add_widget(
            scroll
        )

        close_button = RoundedButton(
            text="إغلاق",
            font_name=self._arabic_font(),
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(
            close_button
        )

        popup = Popup(
            title=title,
            content=content,
            size_hint=(
                0.9,
                0.7
            )
        )

        close_button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    SanskritOCRApp().run()
