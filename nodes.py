import cv2
import os

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

# 符合你发我的现代标准映射
NODE_CLASS_MAPPINGS = {
    "UltraLightVideoInfo": UltraLightVideoInfo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UltraLightVideoInfo": "⚡ Ultra-Light Video Info (No Memory)"
}