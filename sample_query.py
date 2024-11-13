import json
import requests

query = "sql cos format=json  select am_pdb1_feedback, am_pdb2_feedback, am_sludgepump_rate, am_ta_do_ai, am_rasab2_on_display, am_tb_do_ai, am_was1_pause_remain, am_was1_settle_remain, hw_influent, am_wasa_on_remain, am_wasb_on_remain, am_pdb1_status, am_bp_rtm_hrs, am_pdb2_status, am_pdb3_status, am_pdb4_status, am_ras1_off_time, uv_signal1_ai, hw_influent_ttlzr_curday, hw_influent_ttlzr_yesday, uv_room_temp_ai, am_rasab1_off_display, am_rasab1_on_display, am_bp_rtm_mins, am_rasab2_off_display, am_was1_on_setpoint, am_was1_pause_setpoint, am_was1_settle_setpoint, am_pdb3_feedback, am_was1_start_hr, am_was1_start_min, am_ras1_on_time, am_seq1_off_total, am_seq1_on_total, uv_signal2_ai, am_seq2_off_total, am_seq2_on_total, am_seq1_off_setpoint, am_seq2_on_setpoint, am_seq2_off_setpoint, am_seq1_on_setpoint, am_hw_temp_ai, am_polymer_speed, am_pr_temp_ai, am_pdb4_feedback, am_sludgepress_daily from wwp_analog where period(minute, 1, now(), timestamp) limit 1"
conn = "23.239.12.151:32349"
headers = {
    "command": query,
    "User-Agent": "AnyLog/1.23",
    "destination": "network"
}
try:
    r = requests.get(url=f"http://{conn}", headers=headers)
except Exception as error:
    print(f"Failed to query data against {conn} (Error: {error})")
else:
    if not 200 <= int(r.status_code) <= 299:
        print(f"Failed to query data against {conn} (Error: {r.status_code})")
    print(json.dumps(r.json()['Query'][0], indent=2))
