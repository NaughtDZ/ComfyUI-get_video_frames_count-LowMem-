# ComfyUI-get_video_frames_count-LowMem-
---

```markdown
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

2. Clone this repository:


3. Restart ComfyUI.
* *Note: Ensure `ffmpeg` is available in your system PATH (Standard for ComfyUI portable versions).*



---

## 🔄 Advanced Workflow: Pipelining with `comfyui-easy-use` For-Loop

This suite is best used to create a "conveyor belt" workflow using the For-Loop feature from the `comfyui-easy-use` extension.

### Workflow Architecture:

1. **Get Metadata**: Pass the video path to `⚡ Ultra-Light Video Info` to get the `total_frames`.
2. **Calculate Loop End**: Use a math node to calculate total loop iterations: `ceil(total_frames / frame_load_cap)`. Feed this into `For Loop Open -> end`.
3. **Calculate Frame Offset**: Inside the loop, multiply the current loop `index` by your chunk size (e.g., `index * 30`).
4. **Stream Load**: Pass the video path and the calculated offset into `⚡ Stream Video Loader (FFmpeg)` with `frame_load_cap` set to `30`.
5. **Inference & Export**: Pipe the images into your AI models (e.g., GMFSS, APISR) and save chunks iteratively.

```text
[Video Path String] 
       │
       ├──> [⚡ Ultra-Light Video Info] ──(total_frames)──> [Math: Ceil(Total/Cap)] ──> [For Loop Open (end)]
       │                                                                                      │
       └──> [⚡ Stream Video Loader] <──(skip_first_frames) <── [Math: Index * Cap] <─────────┘
                   │
                   └──(IMAGE)──> [Your AI Model / Frame Interpolation] ──> [Video Combine]

```

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

```
<img width="1539" height="619" alt="image" src="https://github.com/user-attachments/assets/39decbf5-e076-4858-8f57-a95062cb4e93" />
