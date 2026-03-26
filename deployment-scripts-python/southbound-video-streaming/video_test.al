#-----------------------------------------------------------------------------------------------------------------------
# Video streaming from videostreams.txt. Format: name,url per line (e.g. bobross,https://www.twitch.tv/bobross)
# Parses Twitch/YouTube/etc from URL automatically. View at: http://localhost:8888/stream/{name}
# Set ENABLE_DETECTIONS=true for YOLO object detection (boxes overlay on live stream only, no DB storage).
# Run: process !local_scripts/videostreaming/video_test.al
# Docker: port 8888 must be exposed (-p 8888:8888)
#-----------------------------------------------------------------------------------------------------------------------
on error ignore

:set-paths:
if not $DEPLOYMENT_SCRIPTS then anylog_path = /app
if not !local_scripts then local_scripts = $DEPLOYMENT_SCRIPTS + "/deployment-scripts/node-deployment"

streams_txt = !local_scripts + "/videostreaming/videostreams.txt"
streams_generated = !local_scripts + "/videostreaming/video_streams_generated.al"

set enable_detections = true
if $ENABLE_DETECTIONS == true or $ENABLE_DETECTIONS == True or $ENABLE_DETECTIONS == TRUE then set enable_detections = true
print "ENABLE_DETECTIONS = " + !enable_detections

:generate-script:
on error goto generate-error
# Run shell script to generate video_streams_generated.al from videostreams.txt
script_path = !local_scripts + "/videostreaming/generate_video_streams.sh"
detect_arg = ""
if !enable_detections == true then detect_arg = " detections"
gen_cmd = "sh " + !script_path + " " + !streams_txt + " " + !streams_generated + !detect_arg
system !gen_cmd
goto setup-display

:setup-display:
on error goto setup-error
video_host = 0.0.0.0
video_port = 8888
set default_dbms = test

import function where import_name = imshow and lib = external_lib.video_processing.cv2_stream_imshow and method = init_class
set function params where import_name = imshow and param_name = port and param_type = int and param_value = !video_port
set function params where import_name = imshow and param_name = host and param_value = !video_host

if !enable_detections == false then goto load-streams

:enable-detections:
on error goto enable-detections-error
import function where import_name = initiate_yolo and lib = external_lib.frame_modeling.yolo_detection and method = init_class
set function params where import_name = initiate_yolo and param_name = module_type and param_value = darknet
set function params where import_name = initiate_yolo and param_name = classes and param_type = list and param_value = []
set function params where import_name = initiate_yolo and param_name = module_path1 and param_value = https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights
set function params where import_name = initiate_yolo and param_name = module_path2 and param_value = https://raw.githubusercontent.com/AlexeyAB/darknet/refs/heads/master/cfg/yolov4-tiny.cfg
set function params where import_name = initiate_yolo and param_name = coco_path and param_value = https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

:load-streams:
on error goto load-error
process !streams_generated
print "Streams loaded from videostreams.txt - view at http://localhost:8888/stream/{name}"
goto end-script

:end-script:
end script

:generate-error:
echo "Failed to generate video streams from videostreams.txt"
goto end-script

:enable-detections-error:
echo "Failed to define YOLO detection information"
goto end-script

:setup-error:
echo "Failed to setup video display (imshow)"
goto end-script

:load-error:
echo "Failed to load streams from generated script"
goto end-script
