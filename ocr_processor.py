# ============================================================
# ocr_processor.py
# Mohand Sanskrit OCR
#
# TFLite YOLO OCR Engine
#
# Model:
#   best.tflite
#
# Input:
#   [1, 3, 640, 640]
#
# Output:
#   [1, 50, 8400]
#
# 46 Classes
#   4 bbox + 46 classes = 50
#
# Letterbox preprocessing
# CPU inference
# ============================================================
import os

import cv2
import numpy as np
try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        raise RuntimeError(
            "TFLite Interpreter is not available."
        )
class SanskritOCR:

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        model_path="best.tflite",
        classes_path="classes.txt",
        img_size=640,
        conf_threshold=0.15,
        iou_threshold=0.45,
        line_threshold_ratio=0.50
    ):

        self.model_path = model_path
        self.classes_path = classes_path

        self.img_size = int(img_size)

        self.conf_threshold = float(
            conf_threshold
        )

        self.iou_threshold = float(
            iou_threshold
        )

        self.line_threshold_ratio = float(
            line_threshold_ratio
        )

        # ----------------------------------------------------
        # Classes
        # ----------------------------------------------------

        self.classes = self._load_classes(
            classes_path
        )

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        self.interpreter = self._load_model(
            model_path
        )

        # ----------------------------------------------------
        # Input / Output
        # ----------------------------------------------------

        self.input_details = (
            self.interpreter.get_input_details()
        )

        self.output_details = (
            self.interpreter.get_output_details()
        )

        if not self.input_details:
            raise RuntimeError(
                "TFLite model لا يحتوي على Input."
            )

        if not self.output_details:
            raise RuntimeError(
                "TFLite model لا يحتوي على Output."
            )

        self.input_index = (
            self.input_details[0]["index"]
        )

        self.output_index = (
            self.output_details[0]["index"]
        )

        self.input_shape = tuple(
            self.input_details[0]["shape"]
        )

        self.output_shape = tuple(
            self.output_details[0]["shape"]
        )

        self.input_dtype = (
            self.input_details[0]["dtype"]
        )

        self.output_dtype = (
            self.output_details[0]["dtype"]
        )

        print("========================================")
        print("Mohand Sanskrit OCR - TFLite")
        print("========================================")

        print("Model:", self.model_path)
        print("Classes:", len(self.classes))
        print("Input:", self.input_shape)
        print("Input dtype:", self.input_dtype)
        print("Output:", self.output_shape)
        print("Output dtype:", self.output_dtype)

        print("========================================")

        # ----------------------------------------------------
        # Validate classes
        # ----------------------------------------------------

        if len(self.classes) != 46:

            raise RuntimeError(
                f"عدد classes = {len(self.classes)} "
                f"لكن المتوقع 46."
            )

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        expected_input = (
            1,
            3,
            self.img_size,
            self.img_size
        )

        if self.input_shape != expected_input:

            raise RuntimeError(
                "Input غير مطابق.\n"
                f"المتوقع: {expected_input}\n"
                f"الحالي: {self.input_shape}"
            )

        # ----------------------------------------------------
        # Validate output
        # ----------------------------------------------------

        expected_output = (
            1,
            50,
            8400
        )

        if self.output_shape != expected_output:

            raise RuntimeError(
                "Output غير مطابق.\n"
                f"المتوقع: {expected_output}\n"
                f"الحالي: {self.output_shape}"
            )

        print("✅ Input مطابق: [1,3,640,640]")
        print("✅ Output مطابق: [1,50,8400]")
        print("✅ Classes = 46")
        print("========================================")

    # ========================================================
    # LOAD CLASSES
    # ========================================================

    def _load_classes(self, path):

        if not os.path.exists(path):

            raise FileNotFoundError(
                "Classes file not found:\n"
                + path
            )

        classes = []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                name = line.strip()

                if not name:
                    continue

                # دعم:
                # 0: ङ
                # 1: च

                if ":" in name:

                    left, right = name.split(
                        ":",
                        1
                    )

                    if left.strip().isdigit():

                        name = right.strip()

                classes.append(name)

        return classes

    # ========================================================
    # LOAD MODEL
    # ========================================================

    def _load_model(self, path):

        if not os.path.exists(path):

            raise FileNotFoundError(
                "TFLite model not found:\n"
                + path
            )

        try:

            interpreter = Interpreter(
                model_path=path,
                num_threads=4
            )

        except TypeError:

            interpreter = Interpreter(
                model_path=path
            )

        interpreter.allocate_tensors()

        return interpreter

    # ========================================================
    # LETTERBOX
    # ========================================================

    def _letterbox(
        self,
        image
    ):

        original_h, original_w = (
            image.shape[:2]
        )

        target = self.img_size

        ratio = min(
            target / original_w,
            target / original_h
        )

        new_w = int(
            round(original_w * ratio)
        )

        new_h = int(
            round(original_h * ratio)
        )

        resized = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_LINEAR
        )

        pad_w = target - new_w
        pad_h = target - new_h

        pad_left = pad_w // 2
        pad_right = pad_w - pad_left

        pad_top = pad_h // 2
        pad_bottom = pad_h - pad_top

        letterboxed = cv2.copyMakeBorder(
            resized,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
            value=(114, 114, 114)
        )

        return (
            letterboxed,
            ratio,
            pad_left,
            pad_top,
            original_w,
            original_h
        )

    # ========================================================
    # PREPROCESS
    # ========================================================

    def _preprocess(
        self,
        image
    ):

        (
            letterboxed,
            ratio,
            pad_x,
            pad_y,
            original_w,
            original_h
        ) = self._letterbox(image)

        # ----------------------------------------------------
        # BGR -> RGB
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            letterboxed,
            cv2.COLOR_BGR2RGB
        )

        # ----------------------------------------------------
        # Float32
        # ----------------------------------------------------

        rgb = rgb.astype(
            np.float32
        )

        rgb /= 255.0

        # ----------------------------------------------------
        # HWC -> CHW
        # ----------------------------------------------------

        chw = np.transpose(
            rgb,
            (2, 0, 1)
        )

        # ----------------------------------------------------
        # Batch
        # ----------------------------------------------------

        blob = np.expand_dims(
            chw,
            axis=0
        )

        blob = np.ascontiguousarray(
            blob,
            dtype=np.float32
        )

        return (
            blob,
            ratio,
            pad_x,
            pad_y,
            original_w,
            original_h
        )

    # ========================================================
    # INFERENCE
    # ========================================================

    def _inference(
        self,
        blob
    ):

        # ----------------------------------------------------
        # FLOAT32
        # ----------------------------------------------------

        if self.input_dtype == np.float32:

            input_data = blob.astype(
                np.float32
            )

        else:

            scale, zero_point = (
                self.input_details[0][
                    "quantization"
                ]
            )

            if scale == 0:

                raise RuntimeError(
                    "Quantized input لديه scale = 0."
                )

            input_data = (
                blob / scale
                + zero_point
            )

            input_data = np.round(
                input_data
            ).astype(
                self.input_dtype
            )

        # ----------------------------------------------------
        # SET INPUT
        # ----------------------------------------------------

        self.interpreter.set_tensor(
            self.input_index,
            input_data
        )

        # ----------------------------------------------------
        # RUN
        # ----------------------------------------------------

        self.interpreter.invoke()

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output = self.interpreter.get_tensor(
            self.output_index
        )

        # ----------------------------------------------------
        # Dequantize if needed
        # ----------------------------------------------------

        if self.output_dtype != np.float32:

            scale, zero_point = (
                self.output_details[0][
                    "quantization"
                ]
            )

            if scale != 0:

                output = (
                    output.astype(np.float32)
                    - zero_point
                ) * scale

        return output

    # ========================================================
    # DECODE
    # ========================================================

    def _decode(
        self,
        output,
        ratio,
        pad_x,
        pad_y,
        original_w,
        original_h
    ):

        output = np.asarray(
            output
        )

        # ----------------------------------------------------
        # [1,50,8400]
        # ->
        # [50,8400]
        # ----------------------------------------------------

        if output.ndim == 3:

            output = output[0]

        if output.ndim != 2:

            raise ValueError(
                "Unexpected TFLite output: "
                + str(output.shape)
            )

        # ----------------------------------------------------
        # [50,8400]
        # ->
        # [8400,50]
        # ----------------------------------------------------

        if (
            output.shape[0] == 50
            and
            output.shape[1] == 8400
        ):

            output = output.T

        elif (
            output.shape[0] == 8400
            and
            output.shape[1] == 50
        ):

            pass

        else:

            raise ValueError(
                "Unexpected YOLO output shape: "
                + str(output.shape)
            )

        detections = []

        # ====================================================
        # PREDICTIONS
        # ====================================================

        for row in output:

            if len(row) != 50:
                continue

            cx, cy, w, h = (
                row[:4]
            )

            class_scores = row[4:]

            class_id = int(
                np.argmax(
                    class_scores
                )
            )

            confidence = float(
                class_scores[class_id]
            )

            if confidence < self.conf_threshold:
                continue

            # ------------------------------------------------
            # Model coordinates are normalized 0..1
            # relative to 640x640 letterbox image.
            # ------------------------------------------------

            x1 = (
                cx - w / 2
            ) * self.img_size

            y1 = (
                cy - h / 2
            ) * self.img_size

            x2 = (
                cx + w / 2
            ) * self.img_size

            y2 = (
                cy + h / 2
            ) * self.img_size

            # ------------------------------------------------
            # Remove letterbox padding
            # ------------------------------------------------

            x1 = (
                x1 - pad_x
            ) / ratio

            y1 = (
                y1 - pad_y
            ) / ratio

            x2 = (
                x2 - pad_x
            ) / ratio

            y2 = (
                y2 - pad_y
            ) / ratio

            # ------------------------------------------------
            # Clip
            # ------------------------------------------------

            x1 = max(
                0.0,
                min(
                    float(original_w - 1),
                    float(x1)
                )
            )

            y1 = max(
                0.0,
                min(
                    float(original_h - 1),
                    float(y1)
                )
            )

            x2 = max(
                0.0,
                min(
                    float(original_w - 1),
                    float(x2)
                )
            )

            y2 = max(
                0.0,
                min(
                    float(original_h - 1),
                    float(y2)
                )
            )

            box_w = x2 - x1
            box_h = y2 - y1

            if box_w <= 2:
                continue

            if box_h <= 2:
                continue

            detections.append({

                "class_id": class_id,

                "confidence": confidence,

                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),

                "x": float(x1),
                "y": float(y1),

                "w": float(box_w),
                "h": float(box_h),

                "center_x": float(
                    (x1 + x2) / 2
                ),

                "center_y": float(
                    (y1 + y2) / 2
                )
            })

        return detections

    # ========================================================
    # IOU
    # ========================================================

    @staticmethod
    def _iou(
        a,
        b
    ):

        ax1 = a["x1"]
        ay1 = a["y1"]
        ax2 = a["x2"]
        ay2 = a["y2"]

        bx1 = b["x1"]
        by1 = b["y1"]
        bx2 = b["x2"]
        by2 = b["y2"]

        ix1 = max(
            ax1,
            bx1
        )

        iy1 = max(
            ay1,
            by1
        )

        ix2 = min(
            ax2,
            bx2
        )

        iy2 = min(
            ay2,
            by2
        )

        iw = max(
            0.0,
            ix2 - ix1
        )

        ih = max(
            0.0,
            iy2 - iy1
        )

        intersection = (
            iw * ih
        )

        area_a = (
            max(
                0.0,
                ax2 - ax1
            )
            *
            max(
                0.0,
                ay2 - ay1
            )
        )

        area_b = (
            max(
                0.0,
                bx2 - bx1
            )
            *
            max(
                0.0,
                by2 - by1
            )
        )

        union = (
            area_a
            +
            area_b
            -
            intersection
        )

        if union <= 0:
            return 0.0

        return (
            intersection
            /
            union
        )

    # ========================================================
    # CLASS AWARE NMS
    # ========================================================

    def _nms(
        self,
        detections
    ):

        if not detections:
            return []

        final_detections = []

        class_ids = sorted(
            set(
                d["class_id"]
                for d in detections
            )
        )

        for class_id in class_ids:

            class_detections = [

                d
                for d in detections
                if d["class_id"] == class_id

            ]

            class_detections.sort(
                key=lambda d:
                d["confidence"],
                reverse=True
            )

            while class_detections:

                best = class_detections.pop(
                    0
                )

                final_detections.append(
                    best
                )

                remaining = []

                for candidate in class_detections:

                    overlap = self._iou(
                        best,
                        candidate
                    )

                    if (
                        overlap
                        <
                        self.iou_threshold
                    ):

                        remaining.append(
                            candidate
                        )

                class_detections = remaining

        # ----------------------------------------------------
        # Sort Y
        # ----------------------------------------------------

        final_detections.sort(
            key=lambda d:
            d["center_y"]
        )

        return final_detections

    # ========================================================
    # MAKE LINES
    # ========================================================

    def _make_lines(
        self,
        detections
    ):

        if not detections:
            return []

        avg_height = np.mean([
            d["h"]
            for d in detections
        ])

        line_threshold = max(
            avg_height
            *
            self.line_threshold_ratio,
            8.0
        )

        ordered = sorted(
            detections,
            key=lambda d:
            d["center_y"]
        )

        lines = []

        for detection in ordered:

            best_line = None

            best_distance = float(
                "inf"
            )

            for line in lines:

                line_y = np.mean([
                    d["center_y"]
                    for d in line
                ])

                distance = abs(
                    detection["center_y"]
                    -
                    line_y
                )

                if (
                    distance
                    <= line_threshold
                    and
                    distance
                    <
                    best_distance
                ):

                    best_line = line

                    best_distance = (
                        distance
                    )

            if best_line is None:

                lines.append([
                    detection
                ])

            else:

                best_line.append(
                    detection
                )

        # ----------------------------------------------------
        # Top -> Bottom
        # ----------------------------------------------------

        lines.sort(
            key=lambda line:
            np.mean([
                d["center_y"]
                for d in line
            ])
        )

        # ----------------------------------------------------
        # Left -> Right
        # ----------------------------------------------------

        for line_number, line in enumerate(
            lines
        ):

            line.sort(
                key=lambda d:
                d["center_x"]
            )

            for detection in line:

                detection["line"] = (
                    line_number
                )

        return lines

    # ========================================================
    # LINES TO TEXT
    # ========================================================

    def _lines_to_text(
        self,
        lines
    ):

        text_lines = []

        for line in lines:

            chars = []

            for detection in line:

                class_id = detection[
                    "class_id"
                ]

                if (
                    0
                    <= class_id
                    <
                    len(self.classes)
                ):

                    chars.append(
                        self.classes[
                            class_id
                        ]
                    )

            if chars:

                text_lines.append(
                    "".join(chars)
                )

        return "\n".join(
            text_lines
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw_detections(
        self,
        image,
        detections
    ):

        result = image.copy()

        for detection in detections:

            x1 = int(
                detection["x1"]
            )

            y1 = int(
                detection["y1"]
            )

            x2 = int(
                detection["x2"]
            )

            y2 = int(
                detection["y2"]
            )

            class_id = detection[
                "class_id"
            ]

            confidence = detection[
                "confidence"
            ]

            # ------------------------------------------------
            # Box
            # ------------------------------------------------

            cv2.rectangle(
                result,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # ------------------------------------------------
            # OpenCV لا يرسم Devanagari بشكل صحيح
            # لذلك نعرض class ID + confidence
            # ------------------------------------------------

            label = (
                f"{class_id} "
                f"{confidence:.2f}"
            )

            cv2.putText(
                result,
                label,
                (
                    x1,
                    max(
                        20,
                        y1 - 5
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

        return result

    # ========================================================
    # MAIN OCR
    # ========================================================

    def process_image(
        self,
        image,
        draw=False
    ):

        if image is None:

            raise ValueError(
                "الصورة فارغة."
            )

        # ----------------------------------------------------
        # PREPROCESS
        # ----------------------------------------------------

        (
            blob,
            ratio,
            pad_x,
            pad_y,
            original_w,
            original_h
        ) = self._preprocess(
            image
        )

        # ----------------------------------------------------
        # INFERENCE
        # ----------------------------------------------------

        output = self._inference(
            blob
        )

        # ----------------------------------------------------
        # DECODE
        # ----------------------------------------------------

        detections = self._decode(
            output,
            ratio,
            pad_x,
            pad_y,
            original_w,
            original_h
        )

        before_nms = len(
            detections
        )

        # ----------------------------------------------------
        # NMS
        # ----------------------------------------------------

        detections = self._nms(
            detections
        )

        after_nms = len(
            detections
        )

        # ----------------------------------------------------
        # LINES
        # ----------------------------------------------------

        lines = self._make_lines(
            detections
        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        text = self._lines_to_text(
            lines
        )

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        result_image = None

        if draw:

            result_image = (
                self.draw_detections(
                    image,
                    detections
                )
            )

        return {

            "text": text,

            "detections": detections,

            "lines": lines,

            "before_nms": before_nms,

            "after_nms": after_nms,

            "image": result_image
        }

    # ========================================================
    # PROCESS FILE
    # ========================================================

    def process_file(
        self,
        image_path,
        save_result=None
    ):

        if not os.path.exists(
            image_path
        ):

            raise FileNotFoundError(
                image_path
            )

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise ValueError(
                "تعذر قراءة الصورة."
            )

        result = self.process_image(
            image,
            draw=True
        )

        if (
            save_result
            and
            result["image"] is not None
        ):

            cv2.imwrite(
                save_result,
                result["image"]
            )

        return result
