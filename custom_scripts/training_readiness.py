import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date, datetime, timedelta
from config import email, password, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

TRAINING_STATUS_MAP = {
    0: "NOT_APPLICABLE",
    1: "DETRAINING",
    2: "RECOVERY",
    3: "MAINTAINING",
    4: "PRODUCTIVE",
    5: "PEAKING",
    6: "OVERREACHING",
    7: "UNPRODUCTIVE",
}

try:
    print("Connecting to Garmin...")

    garth_home = os.path.expanduser("~/.garth")
    os.makedirs(garth_home, exist_ok=True)

    try:
        garth.resume(garth_home)
    except:
        garth.login(email, password)
        garth.save(garth_home)

    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    print(f"Connected as: {garmin.get_full_name()}\n")

    if len(sys.argv) > 1:
        today = date.fromisoformat(sys.argv[1])
    else:
        today = date.today()
    today_str = today.isoformat()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.isoformat()

    # ==========================================================
    # 1) RECOVERY (yesterday's training + today's recovery data)
    # ==========================================================
    print("=" * 55)
    print(f"  1. RECOVERY - {today_str}")
    print("=" * 55)

    # --- Yesterday's Training Status ---
    status = garmin.get_training_status(yesterday_str)
    device_status = {}
    device_balance = {}

    if status:
        # VO2 Max
        vo2 = status.get("mostRecentVO2Max", {})
        generic = vo2.get("generic", {}) if vo2 else {}
        if generic:
            vo2_val = generic.get("vo2MaxPreciseValue") or generic.get("vo2MaxValue")
            vo2_date = generic.get("calendarDate", "")
            fitness_age = generic.get("fitnessAge")
            print(f"\n  VO2 Max:          {vo2_val}")
            if vo2_date:
                print(f"    Measured:       {vo2_date}")
            if fitness_age:
                print(f"    Fitness Age:    {fitness_age}")

        # Training Status
        latest = status.get("mostRecentTrainingStatus", {})
        latest_data = latest.get("latestTrainingStatusData", {}) if latest else {}
        device_status = next(iter(latest_data.values()), {}) if latest_data else {}

        if device_status:
            ts_code = device_status.get("trainingStatus")
            ts_label = TRAINING_STATUS_MAP.get(ts_code, str(ts_code))
            feedback = device_status.get("trainingStatusFeedbackPhrase", "")
            since_date = device_status.get("sinceDate", "")

            print(f"\n  Training Status:  {ts_label}")
            if feedback:
                print(f"    Feedback:       {feedback}")
            if since_date:
                print(f"    Since:          {since_date}")

            # Training Load
            acwr = device_status.get("acuteTrainingLoadDTO", {})
            if acwr:
                acute = acwr.get("dailyTrainingLoadAcute")
                chronic = acwr.get("dailyTrainingLoadChronic")
                ratio = acwr.get("dailyAcuteChronicWorkloadRatio")
                acwr_pct = acwr.get("acwrPercent")
                acwr_status = acwr.get("acwrStatus")

                print(f"\n  --- Training Load ---")
                if acute is not None:
                    print(f"  Acute Load:       {acute}")
                if chronic is not None:
                    print(f"  Chronic Load:     {chronic}")
                if ratio is not None:
                    print(f"  Acute/Chronic:    {ratio}")
                if acwr_status:
                    print(f"  Load Status:      {acwr_status} ({acwr_pct}%)")

        # Monthly Load Balance
        balance = status.get("mostRecentTrainingLoadBalance", {})
        balance_data = balance.get("metricsTrainingLoadBalanceDTOMap", {}) if balance else {}
        device_balance = next(iter(balance_data.values()), {}) if balance_data else {}

        if device_balance:
            aero_low = device_balance.get("monthlyLoadAerobicLow")
            aero_high = device_balance.get("monthlyLoadAerobicHigh")
            anaerobic = device_balance.get("monthlyLoadAnaerobic")
            aero_low_min = device_balance.get("monthlyLoadAerobicLowTargetMin")
            aero_low_max = device_balance.get("monthlyLoadAerobicLowTargetMax")
            aero_high_min = device_balance.get("monthlyLoadAerobicHighTargetMin")
            aero_high_max = device_balance.get("monthlyLoadAerobicHighTargetMax")
            anaerobic_min = device_balance.get("monthlyLoadAnaerobicTargetMin")
            anaerobic_max = device_balance.get("monthlyLoadAnaerobicTargetMax")
            feedback = device_balance.get("trainingBalanceFeedbackPhrase", "")

            print(f"\n  --- Monthly Load Balance ---")
            if aero_low is not None:
                target = f" (target: {aero_low_min}-{aero_low_max})" if aero_low_min is not None else ""
                print(f"  Aerobic Low:      {aero_low:.1f}{target}")
            if aero_high is not None:
                target = f" (target: {aero_high_min}-{aero_high_max})" if aero_high_min is not None else ""
                print(f"  Aerobic High:     {aero_high:.1f}{target}")
            if anaerobic is not None:
                target = f" (target: {anaerobic_min}-{anaerobic_max})" if anaerobic_min is not None else ""
                print(f"  Anaerobic:        {anaerobic:.1f}{target}")
            if feedback:
                print(f"  Feedback:         {feedback}")

    # --- Sleep Timing (last night) ---
    try:
        sleep_data = garmin.get_sleep_data(today_str)
        sleep_dto = None
        if sleep_data and "dailySleepDTO" in sleep_data:
            dto = sleep_data["dailySleepDTO"]
            start_local = dto.get("sleepStartTimestampLocal")
            start_gmt = dto.get("sleepStartTimestampGMT")
            end_local = dto.get("sleepEndTimestampLocal")
            end_gmt = dto.get("sleepEndTimestampGMT")
            start_ts = start_local if start_local is not None else start_gmt
            end_ts = end_local if end_local is not None else end_gmt
            if start_ts and end_ts:
                sleep_dto = dto

        if sleep_dto:
            bed_time = datetime.utcfromtimestamp(start_ts / 1000)
            wake_time = datetime.utcfromtimestamp(end_ts / 1000)
            sleep_dur = (end_ts - start_ts) / 1000 / 3600
            print(f"\n  --- Sleep Timing (last night) ---")
            print(f"  Bed Time:         {bed_time.strftime('%I:%M %p, %a %b %d')}")
            print(f"  Wake Time:        {wake_time.strftime('%I:%M %p, %a %b %d')}")
            print(f"  Duration:         {sleep_dur:.1f}h")
        else:
            print(f"\n  --- Sleep Timing (last night) ---")
            print(f"  No sleep data (watch not worn?)")
    except Exception as e:
        print(f"\n  (Could not fetch sleep timing: {e})")

    # ==========================================================
    # 2) TRAINING READINESS (computed from recovery data)
    # ==========================================================
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT report_date, acute_load, acwr_ratio,
                   sleep_hours, resting_hr, hrv_last_night,
                   body_battery_charged, sleep_score,
                   body_battery_drained, hrv_weekly_avg,
                   sleep_start, sleep_end
            FROM garmin_daily_metrics
            WHERE report_date >= %s AND report_date <= %s
            ORDER BY report_date
        """, ((today - timedelta(days=6)), today))
        rows = cur.fetchall()
        conn.close()

        if rows:
            def is_watch_worn(row):
                """Detect if watch was worn overnight based on HRV and Body Battery."""
                hrv, bb = row[5], row[6]
                return hrv is not None and (bb is None or bb > 0)

            worn_rows = [r for r in rows if is_watch_worn(r)]
            vals = lambda idx: [r[idx] for r in worn_rows if r[idx] is not None]
            avg_fn = lambda v: sum(v) / len(v) if v else None

            # Find today's row (last row should match, but be safe)
            t = next((r for r in reversed(rows) if r[0] == today), rows[-1])
            watch_worn = is_watch_worn(t)
            t_rhr, t_hrv, t_bb = t[4], t[5], t[6]
            t_sleep_h, t_sleep_score = t[3], t[7]
            t_bb_drained, t_hrv_weekly = t[8], t[9]

            # Get ACWR from the live API data (more current than DB)
            t_acwr = None
            if device_status:
                acwr_dto = device_status.get("acuteTrainingLoadDTO", {})
                t_acwr = acwr_dto.get("dailyAcuteChronicWorkloadRatio") if acwr_dto else None
            if t_acwr is None:
                t_acwr = t[2]

            scores = {}
            details = {}

            if not watch_worn:
                print(f"\n{'=' * 55}")
                print(f"  2. TRAINING READINESS - {today_str}")
                print("=" * 55)
                print(f"\n  *** WATCH NOT WORN OVERNIGHT ***")
                print(f"  HRV, RHR, and Body Battery data unavailable.")
                print(f"  Readiness score based on available data only.")

            # --- ACWR Score (25%) ---
            if t_acwr is not None:
                if 0.8 <= t_acwr <= 1.3:
                    scores["acwr"] = 100
                elif t_acwr < 0.8:
                    scores["acwr"] = max(0, t_acwr / 0.8 * 100)
                else:
                    scores["acwr"] = max(0, 100 - (t_acwr - 1.3) / 0.7 * 100)
                details["acwr"] = f"ACWR {t_acwr:.1f}"

            # --- Sleep Score (25%) ---
            if t_sleep_score is not None:
                scores["sleep"] = min(100, t_sleep_score)
                details["sleep"] = f"Sleep score {t_sleep_score}"
            elif t_sleep_h is not None:
                if t_sleep_h >= 8:
                    scores["sleep"] = 100
                elif t_sleep_h >= 7:
                    scores["sleep"] = 65 + (t_sleep_h - 7) * 35
                elif t_sleep_h >= 6:
                    scores["sleep"] = 40 + (t_sleep_h - 6) * 25
                else:
                    scores["sleep"] = max(10, t_sleep_h / 6 * 40)
                details["sleep"] = f"{t_sleep_h:.1f}h sleep"

            # --- HRV Score (20%) --- (skip if watch not worn)
            if watch_worn and t_hrv is not None:
                baseline = t_hrv_weekly if t_hrv_weekly else avg_fn(vals(5))
                if baseline and baseline > 0:
                    hrv_pct = t_hrv / baseline
                    if hrv_pct >= 1.1:
                        scores["hrv"] = 100
                    elif hrv_pct >= 0.9:
                        scores["hrv"] = 60 + (hrv_pct - 0.9) / 0.2 * 40
                    else:
                        scores["hrv"] = max(10, hrv_pct / 0.9 * 60)
                    details["hrv"] = f"HRV {t_hrv:.0f} (avg {baseline:.0f})"
                else:
                    scores["hrv"] = 60
                    details["hrv"] = f"HRV {t_hrv:.0f}"

            # --- RHR Score (15%) --- (skip if watch not worn)
            BASELINE_RHR = 44
            if watch_worn and t_rhr is not None:
                rhr_diff = t_rhr - BASELINE_RHR
                if rhr_diff <= 0:
                    scores["rhr"] = 100
                elif rhr_diff <= 4:
                    scores["rhr"] = 100 - rhr_diff * 5
                elif rhr_diff <= 8:
                    scores["rhr"] = 80 - (rhr_diff - 4) * 5
                elif rhr_diff <= 12:
                    scores["rhr"] = 60 - (rhr_diff - 8) * 5
                else:
                    scores["rhr"] = max(10, 40 - (rhr_diff - 12) * 5)
                details["rhr"] = f"RHR {t_rhr} (base {BASELINE_RHR})"

            # --- Body Battery Score (15%) --- (skip if watch not worn)
            if watch_worn and t_bb is not None:
                if t_bb >= 80:
                    scores["bb"] = 100
                elif t_bb >= 60:
                    scores["bb"] = 70 + (t_bb - 60) / 20 * 30
                elif t_bb >= 40:
                    scores["bb"] = 40 + (t_bb - 40) / 20 * 30
                else:
                    scores["bb"] = max(5, t_bb / 40 * 40)
                details["bb"] = f"BB charged {t_bb}"

            # --- Weighted total ---
            weights = {"acwr": 25, "sleep": 25, "hrv": 20, "rhr": 15, "bb": 15}
            total_weight = sum(weights[k] for k in scores)
            if total_weight > 0:
                readiness = sum(scores[k] * weights[k] for k in scores) / total_weight
                readiness = round(readiness)

                if readiness >= 80:
                    level = "PRIME"
                    msg = "Ready to train hard. Body is well recovered."
                elif readiness >= 60:
                    level = "MODERATE"
                    msg = "OK for normal training. Avoid max efforts."
                elif readiness >= 40:
                    level = "LOW"
                    msg = "Body is fatigued. Keep it light or rest."
                else:
                    level = "POOR"
                    msg = "Strongly consider a rest day."

                if watch_worn:
                    print(f"\n{'=' * 55}")
                    print(f"  2. TRAINING READINESS - {today_str}")
                    print("=" * 55)

                print(f"\n  Readiness Score:  {readiness}/100  [{level}]")
                if not watch_worn:
                    print(f"  (Based on ACWR + Sleep only — no watch data)")
                print(f"  -> {msg}")

                print(f"\n  --- Factor Breakdown ---")
                factor_labels = {
                    "acwr":  ("Load Balance", 25),
                    "sleep": ("Sleep",        25),
                    "hrv":   ("HRV Recovery", 20),
                    "rhr":   ("Resting HR",   15),
                    "bb":    ("Body Battery", 15),
                }
                for key in ["acwr", "sleep", "hrv", "rhr", "bb"]:
                    if key in scores:
                        label, w = factor_labels[key]
                        bar_len = int(scores[key] / 100 * 15)
                        bar = "#" * bar_len + "." * (15 - bar_len)
                        print(f"  {label:<14} {round(scores[key]):>3}/100  [{bar}]  ({details[key]})")
                    elif not watch_worn and key in ("hrv", "rhr", "bb"):
                        label, w = factor_labels[key]
                        print(f"  {label:<14}     -    [  no watch data ]")
            else:
                print(f"\n  (Not enough data to compute readiness)")

            # ==========================================================
            # 3) 7-DAY TRENDS
            # ==========================================================
            print(f"\n{'=' * 55}")
            print(f"  3. 7-DAY TRENDS")
            print("=" * 55)
            print(f"\n  {'Date':<12} {'Load':>6} {'ACWR':>5} {'Sleep':>5} {'Bed':>7} {'Wake':>7} {'RHR':>4} {'HRV':>5} {'BB+':>4}")
            print(f"  {'-'*12} {'-'*6} {'-'*5} {'-'*5} {'-'*7} {'-'*7} {'-'*4} {'-'*5} {'-'*4}")

            for row in rows:
                rd, load, acwr, slp_h, rhr, hrv, bb = row[:7]
                s_start, s_end = row[10], row[11]
                worn = is_watch_worn(row)
                bed_str = s_start.strftime('%I:%M%p').lstrip('0').lower() if s_start else '-'
                wake_str = s_end.strftime('%I:%M%p').lstrip('0').lower() if s_end else '-'
                mark = '' if worn else '  *'
                print(f"  {rd.isoformat():<12} "
                      f"{load if load is not None else '-':>6} "
                      f"{acwr if acwr is not None else '-':>5} "
                      f"{f'{slp_h:.1f}' if slp_h is not None else '-':>5} "
                      f"{bed_str:>7} "
                      f"{wake_str:>7} "
                      f"{rhr if rhr is not None and worn else '-':>4} "
                      f"{f'{hrv:.0f}' if hrv is not None and worn else '-':>5} "
                      f"{bb if bb is not None and worn else '-':>4}"
                      f"{mark}")

            load_avg = avg_fn(vals(1))
            acwr_avg = avg_fn(vals(2))
            sleep_avg = avg_fn(vals(3))
            rhr_avg = avg_fn(vals(4))
            hrv_avg = avg_fn(vals(5))

            unworn_count = len(rows) - len(worn_rows)

            print(f"\n  {'Averages:':<12} "
                  f"{f'{load_avg:.0f}' if load_avg else '-':>6} "
                  f"{f'{acwr_avg:.2f}' if acwr_avg else '-':>5} "
                  f"{f'{sleep_avg:.1f}' if sleep_avg else '-':>5} "
                  f"{'':>7} {'':>7} "
                  f"{f'{rhr_avg:.0f}' if rhr_avg else '-':>4} "
                  f"{f'{hrv_avg:.0f}' if hrv_avg else '-':>5}")

            if unworn_count:
                print(f"\n  * = watch not worn ({unworn_count} day{'s' if unworn_count > 1 else ''},"
                      f" excluded from RHR/HRV/BB averages)")

        else:
            print(f"\n  (No trend data in database. Run store_daily_metrics.py --backfill 7 first)")

    except ImportError:
        print(f"\n  (psycopg2 not installed - skipping DB trends)")
    except Exception as e:
        print(f"\n  (Could not load trends from DB: {e})")

    print()

except Exception as e:
    print(f"\nError: {e}")
    print("You may need to login first")
