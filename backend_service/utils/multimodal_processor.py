"""多模态数据预处理工具

处理图像、音频、文本等多模态数据。

注意：本模块中的 ASR/OCR 等能力可以按需接入第三方依赖，
默认实现会在依赖不存在或调用失败时安全降级为占位结果，
以保证整体服务稳定性。
"""
from typing import Optional, Tuple
import base64
from io import BytesIO
import os
import tempfile


class ImageProcessor:
    """图像处理器"""
    
    @staticmethod
    def resize_image(image_data: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """
        调整图片大小
        """
        # TODO: 使用Pillow进行图像处理
        # from PIL import Image
        # img = Image.open(BytesIO(image_data))
        # img.thumbnail((max_width, max_height))
        # output = BytesIO()
        # img.save(output, format='JPEG', quality=85)
        # return output.getvalue()
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
        """
        从图片中提取文字（OCR）
        TODO: 集成OCR引擎 (如 PaddleOCR, Tesseract)
        """
        # 示例: 使用PaddleOCR
        # from paddleocr import PaddleOCR
        # ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        # result = ocr.ocr(image_data)
        # return "\n".join([line[1][0] for line in result[0]])
        return "OCR提取的文本（待实现）"


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
    ) -> list:
        """
        从视频中提取关键帧
        
        Args:
            video_path: 视频文件路径
            interval_seconds: 抽帧间隔（秒）
            max_frames: 最大帧数
            
        Returns:
            关键帧列表，每个元素包含时间戳和图像数据
            
        TODO: 使用 opencv-python 或 moviepy 实现
        """
        # 示例实现（需要安装 opencv-python）
        # import cv2
        # 
        # frames = []
        # cap = cv2.VideoCapture(video_path)
        # fps = cap.get(cv2.CAP_PROP_FPS)
        # frame_interval = int(fps * interval_seconds)
        # 
        # frame_count = 0
        # while len(frames) < max_frames:
        #     ret, frame = cap.read()
        #     if not ret:
        #         break
        #     
        #     if frame_count % frame_interval == 0:
        #         # 编码为JPEG
        #         _, buffer = cv2.imencode('.jpg', frame)
        #         frames.append({
        #             "timestamp": frame_count / fps,
        #             "image_data": buffer.tobytes(),
        #             "frame_number": frame_count
        #         })
        #     
        #     frame_count += 1
        # 
        # cap.release()
        # return frames
        
        return [
            {
                "timestamp": i * interval_seconds,
                "image_data": b"",  # 占位
                "frame_number": i * interval_seconds * 30  # 假设30fps
            }
            for i in range(min(10, max_frames))
        ]
    
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
        
        # TODO: 对每帧进行OCR
        frame_texts = []
        for frame in frames:
            # text = ImageProcessor.extract_text_from_image(frame['image_data'])
            # frame_texts.append({
            #     "timestamp": frame['timestamp'],
            #     "text": text
            # })
            pass
        
        # TODO: 提取并转录音频
        # audio_path = VideoProcessor.extract_audio_from_video(video_path)
        # transcription = AudioProcessor.transcribe_audio(audio_path)
        
        return {
            "frames": frames,
            "frame_count": len(frames),
            "frame_texts": frame_texts,
            "transcription": "视频音频转文字（待实现）",
            "detected_topics": ["待实现"],
            "key_moments": []
        }
    
    @staticmethod
    def create_knowledge_cards_from_video(video_analysis: dict) -> list:
        """
        根据视频分析结果生成知识卡片数据
        
        Returns:
            知识卡片列表，可以直接传给前端的 knowledge_card_widget
        """
        cards = []
        
        # 从关键帧生成卡片
        for i, frame in enumerate(video_analysis.get('frames', [])):
            cards.append({
                "id": f"frame_{i}",
                "title": f"关键时刻 {i+1}",
                "timestamp": frame.get('timestamp', 0),
                "content": "从视频中提取的内容",
                "type": "video_frame",
                "thumbnail": frame.get('image_data'),
            })
        
        # 从转录文本生成卡片
        if video_analysis.get('transcription'):
            cards.append({
                "id": "transcription",
                "title": "视频讲解内容",
                "content": video_analysis['transcription'],
                "type": "text",
            })
        
        return cards

