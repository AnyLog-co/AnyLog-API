#!/bin/sh
# Read stream list from videostreams.txt (format: name,url per line) and generate
# video_streams_generated.al with video connect + run video stream blocks.
# Optional 3rd arg: detections or true = enable YOLO object detection (boxes overlay on live stream only, no DB storage)
#
# Usage: ./generate_video_streams.sh <input_txt> <output_al> [detections]

if [ $# -lt 2 ]; then
  echo "Usage: generate_video_streams.sh <input_txt> <output_al> [detections]" >&2
  exit 1
fi

INPUT="$1"
OUTPUT="$2"
DETECTIONS="${3:-false}"
[ "$DETECTIONS" = "true" ] || [ "$DETECTIONS" = "True" ] || [ "$DETECTIONS" = "TRUE" ] || [ "$DETECTIONS" = "detections" ] && ENABLE_DETECT=1 || ENABLE_DETECT=0

{
  echo "on error ignore"
  echo ""
  while IFS= read -r line || [ -n "$line" ]; do
    line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    [ -z "$line" ] && continue
    name=$(echo "$line" | cut -d',' -f1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    url=$(echo "$line" | cut -d',' -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    [ -z "$name" ] || [ -z "$url" ] && continue
    url_escaped=$(echo "$url" | sed 's/"/\\"/g')
    echo "# $name"
    echo "<video connect where"
    echo "    name = $name and"
    echo "    protocol = https and"
    echo "    interface = url and"
    echo "    address = \"$url_escaped\" and"
    echo "    video_dbms = !default_dbms and"
    echo "    video_table = video_table"
    echo ">"
    if [ "$ENABLE_DETECT" = "1" ]; then
      echo "run video stream where name = $name and import_detect = initiate_yolo and import_display = imshow"
    else
      echo "run video stream where name = $name and import_display = imshow"
    fi
    echo ""
  done < "$INPUT"
  echo "end script"
} > "$OUTPUT"

count=$(grep -c "^# " "$OUTPUT" 2>/dev/null || echo 0)
echo "Generated $count stream(s) -> $OUTPUT"
