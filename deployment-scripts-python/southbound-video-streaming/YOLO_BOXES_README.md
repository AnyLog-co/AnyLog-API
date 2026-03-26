# How YOLO Boxes Work

This doc explains how the YOLO bounding boxes work in the video streaming setup and how to ensure they work correctly.

---

## End-to-end flow

```
Video URL (Twitch/YouTube) → PyAV decode → frame (numpy/BGR)
       → generic_client.get_video_frames()
       → process_ai(): ai_module.detect(frame) → ai_module.draw_bounding_box(detections, frame)
       → frame with boxes put in queue → _display_loop → imshow(frame)
       → FastAPI / WebSocket → browser at http://localhost:8888/stream/{name}
```

---

## How the code matches

### 1. Your scripts (`video_test.al` + `generate_video_streams.sh`)

| Step | File | What it does |
|------|------|--------------|
| Enable detection | `video_test.al` | Sets `ENABLE_DETECTIONS=true` → generator gets 3rd arg `detections` |
| Init YOLO | `video_test.al` | `import function ... initiate_yolo` + `set function params` |
| Pass detection to stream | `generate_video_streams.sh` | Produces `run video stream ... import_detect = initiate_yolo and import_display = imshow` |

### 2. AnyLog runtime (`video_calls.py`)

- Parses `run video stream where name=X and import_detect = initiate_yolo and import_display = imshow`
- Looks up `initiate_yolo` in the function registry (loaded by `import function` in `video_test.al`)
- Instantiates the module with params (`module_type=darknet`, weights URL, cfg URL, coco.names URL)
- Passes the module to `GenericVideoStreaming.start_stream_video(external_func={"import_detect": [module], "import_display": [...]})`

### 3. Video pipeline (`generic_client.py`)

- `get_video_frames()` reads frames from the stream
- If `import_detect` is provided, it calls `process_ai(status, ai_module, img)` for each frame
- `process_ai()`:
  1. `detect_status, detections = ai_module.detect(frame=img)` → YOLO inference
  2. `ai_module.draw_bounding_box(detections=detections, frame=img)` → draws boxes on the frame in place
- The modified frame goes into the display queue, then to `imshow()`, which publishes to the web UI

### 4. YOLO module (`yolo_detection.py`)

- `init_class()` loads YOLOv4-tiny (weights, cfg, coco.names)
- First run: downloads from URLs into `external_lib/frame_modeling/models/`
- `detect(frame)` → `preprocess` → `infer` → `postprocess` → returns list of `{class, confidence, bbox}`
- `draw_bounding_box(detections, frame)` → draws green rectangles and labels on frame

---

## Parameters that drive YOLO

| Param | Value | Purpose |
|-------|-------|---------|
| `module_type` | darknet | Use OpenCV DNN with Darknet weights |
| `module_path1` | URL to yolov4-tiny.weights | Model weights |
| `module_path2` | URL to yolov4-tiny.cfg | Model config |
| `coco_path` | URL to coco.names | 80 COCO class names |
| `classes` | `[]` | Empty = detect all classes; or e.g. `["person","car","truck","bus"]` |

---

## How to ensure boxes work

### 1. Enable detection

```bash
# Before running the script:
export ENABLE_DETECTIONS=true
```

Or set it in your environment (Docker, etc.).

### 2. Docker image requirements

The `anylogco/anylog-network` image should include:

- `cv2` (OpenCV)
- `numpy`
- `av` (PyAV)

### 3. Network access on first run

On first run, YOLO downloads:

- `yolov4-tiny.weights`
- `yolov4-tiny.cfg`
- `coco.names`

Ensure the container can reach these URLs. If downloads fail, copy the files into  
`/app/AnyLog-Network/external_lib/frame_modeling/models/` and point the params to those paths.

### 4. Port 8888 exposed

```bash
docker run ... -p 8888:8888 ...
```

### 5. Quick checks

1. Run: `process !local_scripts/videostreaming/video_test.al`
2. Confirm: `ENABLE_DETECTIONS = true` is printed
3. Open: `http://localhost:8888/stream/{stream_name}` (e.g. `bobross`)
4. If the stream shows but no boxes: check AnyLog logs for `detect`, `draw_bounding_box`, or `initiate_yolo` errors

### 6. Troubleshooting

| Symptom | Possible cause |
|---------|----------------|
| No stream at all | URL wrong, yt-dlp/ffmpeg not installed, network blocked |
| Stream shows, no boxes | `ENABLE_DETECTIONS` not true, or `import_detect` not passed to `run video stream` |
| Error "function 'initiate_yolo' does not exist" | `:enable-detections:` block not run before `:load-streams:` |
| Error downloading weights | No network or firewall blocking github.com |
| Slow/frozen UI | YOLO runs on CPU; expect ~5–15 FPS depending on hardware |

---

## Two YOLO modes

This setup uses the built-in darknet path (`import_detect = initiate_yolo`). There is also a gRPC path (see `test.al`):

- **Darknet (this setup):** Runs inside the node, downloads weights on first use.
- **gRPC (test.al):** External YOLOv5 server at `127.0.0.1:50051`; `run video stream ... grpc_name = yolov5`.

The `video_test.al` flow uses the darknet path; no gRPC server is required.
