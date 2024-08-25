# AnnyLog-API 

The AnyLog API examples section, contains a data generator that can be used as a test bed for inserting data into 
AnyLog/EdgeLake.

**Sample Data**: 
```json
{
  "timestamp": "2024-03-12 10:32:54.238491",
  "value": 3.141587
}
```
 ### Requirements
* A running AnyLog / EdgeLake instance to accept data
* A running AnyLog / EdgeLake instance with `system_query` to run queries (could be the same instance as above)
* Install [requirements](requirements.txt)
```shell
python3 -m pip install --upgrade -r requirements.txt
```

## Publishing Data

* Insert data via [PUT](examples/insert_data_put.py)
```shell
python3 examples/insert_data_put.py [Operator IP:PORT] \
  --db-name [DB_NAME] \
  --table-name [TABLE_NAME] \
  --total-rows [TOTAL_ROWS]
```

* Insert Data via [POST](examples/insert_data_post.py)
  * Generate MQTT client based on expected data to come in 
  * Publish data via _POST_
```shell
python3 examples/insert_data_put.py [Operator IP:PORT] \
  --db-name [DB_NAME] \
  --table-name [TABLE_NAME] \
  --total-rows [TOTAL_ROWS] \
  --topic [TOPIC_NAME] \
```

## Query data 
For querying purposes, the examples use an active AnyLog / EdgeLake setup, in order to demonstrate working use cases for
both _increments_ and _period_ functions. Note, that while naming of user-input might be similar, the actual user-input 
may be different.

* [Increment Function](examples/sample_query_increments.py)
```shell
python3 examples/sample_query_increments.py 23.239.12.151:32349 edgex rand_data \
  --output-format table \
  --time-column timestamp \
  --where-conditions "timestamp >= NOW() - 2 hours and timestamp <= NOW() - 1 hour" \
  --limit 10 \
  --return-cmd \
  --order-by
```
**Output**: 
```output
sql edgex format=table  SELECT increments(minute, 1, timestamp), MIN(timestamp) AS min_ts, MIN(timestamp) AS max_ts, MIN(value) AS min_value, MAX(value) AS max_value, AVG(value) AS avg_value,  COUNT(*) AS row_count  FROM rand_data WHERE timestamp >= NOW() - 2 hours and timestamp <= NOW() - 1 hour  ORDER BY min_ts limit 10 

min_ts                     max_ts                     min_value max_value avg_value          row_count
-------------------------- -------------------------- --------- --------- ------------------ --------- 
2024-08-24 22:55:18.637061 2024-08-24 22:55:18.637061     4.014   760.291 255.41164444444442        90 
2024-08-24 22:56:04.670541 2024-08-24 22:56:04.670541      3.19   790.123 246.85996363636366       110 
2024-08-24 22:57:00.952800 2024-08-24 22:57:00.952800     0.534    952.88           252.1716       120 
2024-08-24 22:58:02.336577 2024-08-24 22:58:02.336577     0.075   750.192         228.443625       120 
2024-08-24 22:59:03.722973 2024-08-24 22:59:03.722973     2.233   833.586 257.39289655172416       116 
2024-08-24 23:00:00.000012 2024-08-24 23:00:00.000012     1.567   831.919 254.34968421052633       114 
2024-08-24 23:01:01.393553 2024-08-24 23:01:01.393553     0.957   877.293  258.5495833333333       120 
2024-08-24 23:02:02.778916 2024-08-24 23:02:02.778916     0.456   896.794  275.2477083333333       120 
2024-08-24 23:03:04.170461 2024-08-24 23:03:04.170461     0.072   922.591  275.4125272727273       110 
2024-08-24 23:04:00.559784 2024-08-24 23:04:00.559784     1.464   899.864 254.89586666666668       120 

{"Statistics":[{"Count": 10,
                "Time":"00:00:00",
                "Nodes": 2}]}
```

* [Period Function](examples/sample_query_period.py)
```shell
python3 examples/sample_query_period.py 23.239.12.151:32349 litsanleandro ping_sensor \
  --time-column insert_timestamp \
  --interval day \
  --time-units 1 \
  --values device_name,min(timestamp),max(timestamp),count(*) \
  --group-by device_name \
  --output-format table \
  --return-cmd
```

**Output**:
```output
sql litsanleandro format=table  select device_name,min(timestamp),max(timestamp),count(*) FROM ping_sensor WHERE period(day, 1, NOW(),insert_timestamp) GROUP BY device_name 


device_name     min(timestamp)             max(timestamp)             count(*)
--------------- -------------------------- -------------------------- -------- 
ADVA FSP3000R7  2024-08-24 01:05:55.025758 2024-08-25 01:05:44.853925     7731 
Catalyst 3500XL 2024-08-24 01:05:55.526476 2024-08-25 01:05:43.351979     7841 
GOOGLE_PING     2024-08-24 01:06:08.314810 2024-08-25 01:05:42.851271     7725 
Ubiquiti OLT    2024-08-24 01:05:54.024306 2024-08-25 01:05:31.626811     7636 
VM Lit SL NMS   2024-08-24 01:05:54.525032 2024-08-25 01:05:44.353399     7753 

{"Statistics":[{"Count": 5,
                "Time":"00:00:01",
                "Nodes": 3}]}
```

