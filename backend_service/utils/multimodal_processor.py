"""多模态数据预处理工具

处理图像、音频、文本、视频等多模态数据。

设计目标:
- 默认依赖尽量轻量(如 opencv, pillow, pytesseract)
- 所有外部依赖通过 try/except 包裹,在依赖缺失或运行失败时
    自动降级为占位实现,保证服务稳定性
"""
from typing import Optional, Tuple, List, Dict
import base64
from io import BytesIO
import os
import tempfile


def _safe_import_cv2():
    """延迟导入 OpenCV,在依赖缺失时返回 None 而不是抛异常。"""
    try:
        import cv2  # type: ignore
        return cv2
    except Exception:
        return None


def _safe_import_pil_and_tesseract():
    """延迟导入 Pillow 和 pytesseract。"""
    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
        return Image, pytesseract
    except Exception:
        return None, None


class ImageProcessor:
    """图像处理器"""
    
    @staticmethod
    def resize_image(image_data: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """
        调整图片大小
        """
        Image, _ = _safe_import_pil_and_tesseract()
        if Image is None:
            # 无 Pillow 依赖时,直接返回原图
            return image_data

        try:
            img = Image.open(BytesIO(image_data))
            img.thumbnail((max_width, max_height))
            output = BytesIO()
            img.save(output, format="JPEG", quality=85)
            return output.getvalue()
        except Exception:
            # 任意异常都降级为返回原图,避免中断主流程
            return image_data
    
    @staticmethod
    def to_base64(image_data: bytes) -> str:
        """转换为base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    @staticmethod
    def from_base64(base64_str: str) -> bytes:
        """从base64解码"""
        return base64.b64decode(base64_str)
    
    @staticmethod
    def extract_text_from_image(image_data: bytes) -> str:
        """从图片中提取文字(OCR)。

        优先使用 Tesseract(OCR 引擎),在依赖缺失或识别失败时
        安全降级为占位文本,避免影响主流程。
        """

        Image, pytesseract = _safe_import_pil_and_tesseract()
        if Image is None or pytesseract is None:
            return "OCR提取的文本(占位,未安装 Pillow/pytesseract)"

        try:
            img = Image.open(BytesIO(image_data))
            # 对 PPT / 课件截图,可以适当增强对比度/灰度化,此处保持简单实现
            text = pytesseract.image_to_string(img, lang=os.getenv("OCR_LANG", "chi_sim+eng"))
            cleaned = text.strip()
            return cleaned or "(OCR 无有效结果)"
        except Exception:
            return "OCR提取的文本(运行时失败,已降级)"


class AudioProcessor:
    """音频处理器"""
    
    @staticmethod
    def transcribe_audio(audio_data: bytes, language: str = "zh") -> str:
        """语音转文字 (ASR)。

        可以按需接入 Whisper / faster-whisper 或云端 ASR 服务。

        环境变量约定（可选）：
        - ASR_PROVIDER: "whisper" | "faster-whisper" | 其他自定义标识
        - WHISPER_MODEL: Whisper 模型名，默认 "base"

        为了方便本地开发和部署，所有外部依赖都通过 try/except 保护，
        缺少依赖或调用失败时会返回占位文本而不是抛出异常。
        """
        provider = os.getenv("ASR_PROVIDER", "mock").lower()

        # 为第三方库准备一个临时文件（大多数 ASR 库都基于文件路径）
        def _write_temp_wav() -> Optional[str]:
            try:
                fd, path = tempfile.mkstemp(suffix=".wav")
                with os.fdopen(fd, "wb") as f:
                    f.write(audio_data)
                return path
            except Exception:
                return None

        # 1) 本地 Whisper
        if provider == "whisper":
            try:
                import whisper  # type: ignore

                model_name = os.getenv("WHISPER_MODEL", "base")
                model = whisper.load_model(model_name)

                temp_path = _write_temp_wav()
                if temp_path is None:
                    raise RuntimeError("无法创建临时音频文件")

                try:
                    result = model.transcribe(temp_path, language=language)
                    text = result.get("text") or ""
                    return text.strip() or "(ASR 无结果)"
                finally:
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
            except Exception:
                # 回退到后续分支
                pass

        # 2) faster-whisper（可选）
        if provider in {"faster-whisper", "faster_whisper"}:
            try:
                from faster_whisper import WhisperModel  # type: ignore

                model_name = os.getenv("WHISPER_MODEL", "base")
                model = WhisperModel(model_name, device="cpu", compute_type="int8")

                temp_path = _write_temp_wav()
                if temp_path is None:
                    raise RuntimeError("无法创建临时音频文件")

                try:
                    segments, _ = model.transcribe(temp_path, language=language)
                    parts = [seg.text for seg in segments]
                    text = " ".join(parts).strip()
                    return text or "(ASR 无结果)"
                finally:
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
            except Exception:
                # 回退到占位实现
                pass

        # 3) 默认占位实现（未配置或依赖不可用时）
        return "语音转文字结果（占位，未接入实际ASR）"
    
    @staticmethod
    def convert_audio_format(
        audio_data: bytes,
        from_format: str,
        to_format: str
    ) -> bytes:
        """
        转换音频格式
        TODO: 使用pydub或ffmpeg
        """
        return audio_data


class TextProcessor:
    """文本处理器"""
    
    @staticmethod
    def extract_math_expressions(text: str) -> list:
        """
        提取数学表达式
        """
        # TODO: 使用正则或NLP工具提取数学公式
        import re
        # 简单示例: 查找包含运算符的表达式
        patterns = [
            r'[0-9+\-*/()=x²³√]+',  # 基础数学表达式
            r'\$.*?\$',              # LaTeX公式
        ]
        expressions = []
        for pattern in patterns:
            expressions.extend(re.findall(pattern, text))
        return expressions
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 去除多余空格、特殊字符等
        text = ' '.join(text.split())
        return text.strip()
    
    @staticmethod
    def segment_text(text: str, max_length: int = 512) -> list:
        """
        分段文本（用于长文本处理）
        """
        # 简单按字符分段
        segments = []
        for i in range(0, len(text), max_length):
            segments.append(text[i:i+max_length])
        return segments


class StructuredDataExtractor:
    """结构化数据提取器"""
    
    @staticmethod
    def extract_problem_structure(text: str) -> dict:
        """
        从题目文本中提取结构化信息
        """
        # TODO: 使用NLP技术提取题目类型、知识点等
        return {
            "type": "math",  # math, physics, chemistry, etc.
            "difficulty": "medium",
            "topics": ["代数", "方程"],
            "keywords": TextProcessor.extract_math_expressions(text),
            "raw_text": text
        }
    
    @staticmethod
    def format_solution_steps(solution: str) -> list:
        """
        格式化解题步骤
        """
        # 按行分割，识别步骤
        lines = solution.split('\n')
        steps = []
        for i, line in enumerate(lines, 1):
            if line.strip():
                steps.append({
                    "step": i,
                    "content": line.strip(),
                    "type": "calculation"  # calculation, explanation, conclusion
                })
        return steps


class VideoProcessor:
    """视频处理器 - 用于长视频一键萃取"""
    
    @staticmethod
    def extract_key_frames(
        video_path: str,
        interval_seconds: int = 5,
        max_frames: int = 50
    ) -> List[Dict]:
        """从视频中提取关键帧(基于 OpenCV 的轻量实现)。

        逻辑:
        - 使用 `cv2.VideoCapture` 打开本地视频
        - 按给定时间间隔(interval_seconds)抽帧
        - 每一帧编码为 JPEG 字节流

        在 opencv-python 未安装或视频无法打开时,自动降级为
        伪造的占位帧列表,保证上层流程不崩溃。
        """

        cv2 = _safe_import_cv2()
        if cv2 is None:
            # 降级: 返回占位帧,但包含合理的时间戳,方便前端联调
            return [
                {
                    "timestamp": i * interval_seconds,
                    "image_data": b"",  # 无实际图像
                    "frame_number": i * interval_seconds * 30,
                }
                for i in range(min(10, max_frames))
            ]

        if not os.path.exists(video_path):
            # 文件不存在时同样返回空列表,由调用方决定如何降级
            return []

        frames: List[Dict] = []
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        try:
            fps = float(fps) if fps > 1e-6 else 25.0
        except Exception:
            fps = 25.0

        frame_interval = max(int(fps * interval_seconds), 1)
        frame_index = 0

        try:
            while len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % frame_interval == 0:
                    ok, buffer = cv2.imencode(".jpg", frame)
                    if not ok:
                        frame_index += 1
                        continue

                    timestamp = frame_index / fps
                    frames.append(
                        {
                            "timestamp": float(timestamp),
                            "image_data": buffer.tobytes(),
                            "frame_number": int(frame_index),
                        }
                    )

                frame_index += 1
        finally:
            cap.release()

        return frames
    
    @staticmethod
    def extract_audio_from_video(video_path: str, output_path: str = None) -> str:
        """
        从视频中提取音频
        
        TODO: 使用 moviepy 或 ffmpeg
        """
        # 示例实现
        # from moviepy.editor import VideoFileClip
        # 
        # if output_path is None:
        #     output_path = video_path.rsplit('.', 1)[0] + '.mp3'
        # 
        # video = VideoFileClip(video_path)
        # video.audio.write_audiofile(output_path)
        # video.close()
        # 
        # return output_path
        
        return output_path or "audio_output.mp3"
    
    @staticmethod
    def analyze_video_content(video_path: str) -> dict:
        """
        分析视频内容，提取关键信息
        
        流程：
        1. 提取关键帧
        2. 对每帧进行OCR识别
        3. 提取音频并转文字
        4. 合并多模态信息
        
        Returns:
            {
                "frames": [...],  # 关键帧信息
                "transcription": "...",  # 音频转文字
                "detected_topics": [...],  # 检测到的知识点
                "key_moments": [...]  # 重要时刻标记
            }
        """
        frames = VideoProcessor.extract_key_frames(video_path)

        # 1) 对每个关键帧执行 OCR,提取 PPT / 白板中的文字
        frame_texts: List[Dict] = []
        aggregated_text_parts: List[str] = []

        for frame in frames:
            image_bytes: bytes = frame.get("image_data") or b""
            if not image_bytes:
                continue

            text = ImageProcessor.extract_text_from_image(image_bytes)
            cleaned = TextProcessor.clean_text(text)
            if cleaned:
                frame_texts.append(
                    {
                        "timestamp": frame.get("timestamp", 0.0),
                        "text": cleaned,
                    }
                )
                aggregated_text_parts.append(cleaned)

        aggregated_text = "\n".join(aggregated_text_parts)

        # 2) (可选) 提取并转录音频 — 这里保持占位实现,方便后续接入 ASR
        transcription = "视频音频转文字（占位,待接入 ASR）"

        # 3) 简单基于文本抽取知识点关键词
        detected_topics: List[str] = []
        if aggregated_text:
            structure = StructuredDataExtractor.extract_problem_structure(aggregated_text)
            detected_topics = [str(t) for t in structure.get("topics", [])]

        return {
            "frames": frames,
            "frame_count": len(frames),
            "frame_texts": frame_texts,
            "aggregated_text": aggregated_text,
            "transcription": transcription,
            "detected_topics": detected_topics or ["待实现"],
            "key_moments": [],
        }
    
    @staticmethod
    def create_knowledge_cards_from_video(video_analysis: dict) -> list:
        """
        根据视频分析结果生成知识卡片数据
        
        Returns:
            知识卡片列表，可以直接传给前端的 knowledge_card_widget
        """
        cards: List[Dict] = []

        # 1) 从关键帧生成卡片: 每张卡片对应一个时间点,前端可用 timestamp 控制播放器跳转
        frame_texts_by_ts: Dict[float, str] = {}
        newton_second_law_ts: Optional[float] = None
        for ft in video_analysis.get("frame_texts", []):
            ts = float(ft.get("timestamp", 0.0))
            text = str(ft.get("text", ""))
            # 同一时间戳多次识别时简单拼接
            frame_texts_by_ts[ts] = (frame_texts_by_ts.get(ts, "") + " " + text).strip()

            # 简单规则: 如果帧文本中出现 "牛顿第二定律" 等关键词,记录一个候选时间点
            if ("牛顿第二定律" in text or "Newton" in text) and newton_second_law_ts is None:
                newton_second_law_ts = ts

        for i, frame in enumerate(video_analysis.get("frames", [])):
            ts = float(frame.get("timestamp", 0.0))
            raw_text = frame_texts_by_ts.get(ts, "")
            preview = (raw_text[:120] + "...") if len(raw_text) > 120 else raw_text

            cards.append(
                {
                    "id": f"frame_{i}",
                    "title": f"关键时刻 {i + 1}",
                    "timestamp": ts,
                    # 内容为该时刻附近 PPT 文本摘要,前端可直接展示
                    "content": preview or "从视频中提取的关键信息",
                    "type": "video_frame",
                    "thumbnail": frame.get("image_data"),
                }
            )

        # 2) 从整体文本/转录生成一张总览卡片(知识卡片大纲)
        aggregated_text = video_analysis.get("aggregated_text") or ""
        if aggregated_text:
            cards.append(
                {
                    "id": "outline",
                    "title": "本节知识结构大纲",
                    "content": aggregated_text,
                    "type": "outline",
                }
            )

        transcription = video_analysis.get("transcription")
        if transcription:
            cards.append(
                {
                    "id": "transcription",
                    "title": "视频讲解逐字稿",
                    "content": transcription,
                    "type": "text",
                }
            )

        # 3) 物理场景示例: 为 "牛顿第二定律/受力分析" 构造一张带 3D 模型的演示卡片
        if newton_second_law_ts is not None:
            cards.append(
                {
                    "id": "physics_newton_second_law",
                    "title": "牛顿第二定律: 受力分析模型",
                    "timestamp": newton_second_law_ts,
                    "content": "根据视频内容自动萃取的受力分析示意: 通过受力分解理解 F = ma。",
                    "type": "physics_concept",
                    # 前端 ThreeDVisualizationWidget 可使用的可视化配置
                    "visualization_type": "geometry",
                    "visualization_parameters": {
                        # 一个简化的受力分析模型: 水平桌面上的小车,竖直向下的重力和向上的支持力
                        "objects": [
                            # 小车所在的水平面(抽象为一块面)
                            {
                                "type": "face",
                                "coords": [
                                    [-1.0, -0.2, 0.0],
                                    [1.0, -0.2, 0.0],
                                    [1.0, -0.4, 0.0],
                                    [-1.0, -0.4, 0.0],
                                ],
                                "label": "桌面",
                            },
                            # 受力箭头(用线段近似)
                            {
                                "type": "line",
                                "coords": [[0.0, 0.0, 0.0], [0.0, -0.6, 0.0]],
                                "label": "重力 mg",
                            },
                            {
                                "type": "line",
                                "coords": [[0.0, -0.2, 0.0], [0.0, 0.4, 0.0]],
                                "label": "支持力 N",
                            },
                        ]
                    },
                    # 额外的可视化指令,可让前端按步骤动态展示受力分解
                    "visual_commands": [
                        {
                            "type": "draw_line",
                            "from": "A",
                            "to": "C",
                            "color": "red",
                            "animate": True,
                            "step_id": "1",
                            "label": "沿运动方向的合力",
                        }
                    ],
                }
            )

        return cards

