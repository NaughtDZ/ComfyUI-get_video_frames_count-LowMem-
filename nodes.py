import cv2
import os
import subprocess
import numpy as np
import torch

# ─── 节点 1：轻量级信息获取（保持不变） ───
class UltraLightVideoInfo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("INT", "FLOAT", "INT", "INT")
    RETURN_NAMES = ("total_frames", "fps", "width", "height")
    FUNCTION = "get_info"
    CATEGORY = "VideoTools/A_Light"

    def get_info(self, video_path):
        clean_path = video_path.strip('"').strip("'")
        if not os.path.exists(clean_path):
            raise FileNotFoundError(f"找不到视频文件: {clean_path}")
            
        cap = cv2.VideoCapture(clean_path)
        if not cap.isOpened():
            raise IOError(f"无法打开视频文件: {clean_path}")
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        return (total_frames, fps, width, height)


# ─── 节点 2：全新的不吃内存流式视频切片加载器 ───
class StreamVideoLoaderFFmpeg:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
                "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1}),
                "frame_load_cap": ("INT", {"default": 30, "min": 1, "max": 10000, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "loaded_count")
    FUNCTION = "load_video_stream"
    CATEGORY = "VideoTools/A_Light"

    def load_video_stream(self, video_path, skip_first_frames, frame_load_cap):
        clean_path = video_path.strip('"').strip("'")
        if not os.path.exists(clean_path):
            raise FileNotFoundError(f"找不到视频文件: {clean_path}")

        # 1. 首先通过 OpenCV 快速获取视频基本参数和 FPS
        cap = cv2.VideoCapture(clean_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # 边界检查：如果跳过的帧数超过了总帧数，直接返回单张空帧防止报错死循环
        if skip_first_frames >= total_frames:
            empty_image = torch.zeros((1, height, width, 3), dtype=torch.float32)
            return (empty_image, 0)

        # 确保不会读取超过剩余总帧数的数据
        actual_load_cap = min(frame_load_cap, total_frames - skip_first_frames)

        # 2. 计算精准的时间戳偏移（FFmpeg 按时间切片最稳健）
        start_time = skip_first_frames / fps
        
        # 3. 构造完美的 FFmpeg 原生命令行（直接读取 ComfyUI 便携包自带的 ffmpeg）
        # 如果便携包没有全局 ffmpeg，这里默认调用系统 PATH 中的 ffmpeg
        ffmpeg_cmd = [
            'ffmpeg',
            '-ss', str(start_time),            # 精准定位到起始时间点（必须放在 -i 前面实现秒开）
            '-i', clean_path,                  # 输入文件路径
            '-vframes', str(actual_load_cap),   # 严格限制只读取 N 帧
            '-f', 'image2pipe',                # 以管道流形式输出图片
            '-pix_fmt', 'rgb24',               # 强制色彩空间为标准的 RGB24
            '-vcodec', 'rawvideo',             # 采用无压缩裸流格式，速度最快
            '-'                                # 输出到标准输出（stdout）
        ]

        # 4. 启动 FFmpeg 子进程读取数据流
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        frame_bytes_size = width * height * 3
        video_frames = []

        # 5. 循环读取管道，每次只拿一帧的字节，完全不产生历史堆积
        for _ in range(actual_load_cap):
            in_bytes = process.stdout.read(frame_bytes_size)
            if not in_bytes or len(in_bytes) != frame_bytes_size:
                break
            
            # 将二进制字节转换为标准 NumPy 矩阵
            frame_array = np.frombuffer(in_bytes, dtype=np.uint8).reshape((height, width, 3))
            # 归一化为 ComfyUI 接受的 0.0~1.0 之间的 float32 张量
            frame_tensor = torch.from_numpy(frame_array).float() / 255.0
            video_frames.append(frame_tensor)

        process.stdout.close()
        process.wait()

        if len(video_frames) == 0:
            # 防御性回退：万一没读到，返回个黑帧
            empty_image = torch.zeros((1, height, width, 3), dtype=torch.float32)
            return (empty_image, 0)

        # 6. 将帧列表堆叠成 ComfyUI 标准的四维张量 [B, H, W, C]
        out_images = torch.stack(video_frames, dim=0)
        
        # ─── 🔥 暴力强杀内存残留（新增的防赖账机制） ───
        # 显式销毁局部列表，切断变量引用链
        del video_frames 
        
        # 强行唤醒 Python 垃圾回收器和 PyTorch 显存释放机制
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        # ─────────────────────────────────────────────

        return (out_images, len(out_images))

# ─── 现代标准节点映射 ───
NODE_CLASS_MAPPINGS = {
    "UltraLightVideoInfo": UltraLightVideoInfo,
    "StreamVideoLoaderFFmpeg": StreamVideoLoaderFFmpeg
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UltraLightVideoInfo": "⚡ Ultra-Light Video Info (No Memory)",
    "StreamVideoLoaderFFmpeg": "⚡ Stream Video Loader (FFmpeg No Memory)"
}
