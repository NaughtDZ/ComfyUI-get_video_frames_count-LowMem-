# ComfyUI-get_video_frames_count-LowMem-
---


# ComfyUI-StreamVideoTools

A collection of ultra-lightweight, memory-efficient video utilities for ComfyUI. Designed specifically for long video processing (e.g., Frame Interpolation, Upscaling) without blowing up your System RAM or VRAM.

Unlike default nodes (like `Load Video (VHS)`) which decode and cache the **entire** video into memory at once, this suite utilizes a **streaming pipeline** approach to decode and load video frames strictly on-demand.

---

## 🚀 Key Features

* **⚡ Ultra-Light Video Info (No Memory)**: Instantly reads video metadata (Total Frames, FPS, Width, Height) in less than 0.01s. It opens only the video header using OpenCV—**Zero frame decoding, Zero memory consumption.**
* **⚡ Stream Video Loader (FFmpeg No Memory)**: A pure streaming video loader. When combined with loop nodes, it uses FFmpeg under the hood to seek and decode *only* the specific chunk of frames requested for the current loop execution. Once the loop passes, the memory is immediately released.

---

## 📊 Memory Consumption: The Difference

When processing a 5-minute 1080p Anime video (~9,000 frames):

| Loader Type | Initial Memory Spike | Memory over Time (100+ Loops) | Risk of OOM (`Out of Memory`) |
| :--- | :--- | :--- | :--- |
| **Standard Load Video (VHS)** | 🛑 **20GB+ RAM / VRAM** (Crash) | 📈 Continuous Accumulation | 🔥 **Extremely High** |
| **Stream Video Loader (FFmpeg)** |   **~150MB** (30 frames chunk) | ➡️ **Constant & Flat** (Auto-GC) | 🟢 **Zero** |

---

## 🛠️ Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/

   ```

2. Clone this repository

Recommend Install:

opencv-python>=4.8.0,

numpy>=2.3.0,<2.4.0,

torch

4. Restart ComfyUI.
* *Note: Ensure `ffmpeg` is available in your system PATH (Standard for ComfyUI portable versions).*



---

## 🔄 Advanced Workflow: Pipelining with `comfyui-easy-use` For-Loop

This suite is best used to create a "conveyor belt" workflow using the For-Loop feature from the `comfyui-easy-use` extension.

---

## ⚙️ Nodes Specifications

### 1. Ultra-Light Video Info

* **Inputs:**
* `video_path` (STRING): Absolute path to the video file.


* **Outputs:**
* `total_frames` (INT)
* `fps` (FLOAT)
* `width` (INT)
* `height` (INT)



### 2. Stream Video Loader (FFmpeg)

* **Inputs:**
* `video_path` (STRING): Absolute path to the video file.
* `skip_first_frames` (INT): The frame index to start decoding from (driven by loop counter).
* `frame_load_cap` (INT): How many frames to decode in this single batch (Recommended: `30` - `128` depending on your GPU).


* **Outputs:**
* `images` (IMAGE): Standard ComfyUI image batch tensor `[B, H, W, C]`.
* `loaded_count` (INT): Actual number of frames loaded (useful for handling the final trailing chunk).



---

## 📄 License

MIT License. Feel free to use, modify, and distribute.

```

***

<img width="1539" height="619" alt="image" src="https://github.com/user-attachments/assets/39decbf5-e076-4858-8f57-a95062cb4e93" />
