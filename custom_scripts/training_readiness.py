import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date, timedelta
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

    today = date.today()
    today_str = today.isoformat()

    # ===== TRAINING STATUS =====
    status = garmin.get_training_status(today_str)

    if status:
        print(f"\n{'=' * 55}")
        print(f"  TRAINING STATUS - {today_str}")
        print("=" * 55)

        # --- VO2 Max ---
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

        # --- Training Status (from latest device data) ---
        latest = status.get("mostRecentTrainingStatus", {})
        latest_data = latest.get("latestTrainingStatusData", {}) if latest else {}
        # Get first device's data
        device_status = next(iter(latest_data.values()), {}) if latest_data else {}

        if device_status:
            ts_code = device_status.get("trainingStatus")
            ts_label = TRAINING_STATUS_MAP.get(ts_code, str(ts_code))
            feedback = device_status.get("trainingStatusFeedbackPhrase", "")
            since_date = device_status.get("sinceDate", "")
            paused = device_status.get("trainingPaused", False)

            print(f"\n  Training Status:  {ts_label}")
            if feedback:
                print(f"    Feedback:       {feedback}")
            if since_date:
                print(f"    Since:          {since_date}")
            if paused:
                print(f"    Paused:         Yes")

            # --- Acute/Chronic Workload ---
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

        # --- Training Load Balance ---
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

    # ===== 7-DAY TRENDS FROM DATABASE =====
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
                   body_battery_drained, hrv_weekly_avg
            FROM garmin_daily_metrics
            WHERE report_date >= %s
            ORDER BY report_date
        """, ((today - timedelta(days=6)),))
        rows = cur.fetchall()
        conn.close()

        if rows:
            print(f"\n{'=' * 55}")
            print(f"  7-DAY TRENDS (from database)")
            print("=" * 55)
            print(f"\n  {'Date':<12} {'Load':>6} {'ACWR':>5} {'Sleep':>5} {'RHR':>4} {'HRV':>5} {'BB+':>4}")
            print(f"  {'-'*12} {'-'*6} {'-'*5} {'-'*5} {'-'*4} {'-'*5} {'-'*4}")

            for row in rows:
                rd, load, acwr, slp_h, rhr, hrv, bb = row[:7]
                print(f"  {rd.isoformat():<12} "
                      f"{load if load is not None else '-':>6} "
                      f"{acwr if acwr is not None else '-':>5} "
                      f"{f'{slp_h:.1f}' if slp_h is not None else '-':>5} "
                      f"{rhr if rhr is not None else '-':>4} "
                      f"{f'{hrv:.0f}' if hrv is not None else '-':>5} "
                      f"{bb if bb is not None else '-':>4}")

            # Averages
            vals = lambda idx: [r[idx] for r in rows if r[idx] is not None]
            avg_fn = lambda v: sum(v) / len(v) if v else None

            load_avg = avg_fn(vals(1))
            acwr_avg = avg_fn(vals(2))
            sleep_avg = avg_fn(vals(3))
            rhr_avg = avg_fn(vals(4))
            hrv_avg = avg_fn(vals(5))

            print(f"\n  {'Averages:':<12} "
                  f"{f'{load_avg:.0f}' if load_avg else '-':>6} "
                  f"{f'{acwr_avg:.2f}' if acwr_avg else '-':>5} "
                  f"{f'{sleep_avg:.1f}' if sleep_avg else '-':>5} "
                  f"{f'{rhr_avg:.0f}' if rhr_avg else '-':>4} "
                  f"{f'{hrv_avg:.0f}' if hrv_avg else '-':>5}")

            # ===== COMPUTED TRAINING READINESS =====
            # Use today's row (last row) for readiness calculation
            # Scoring: each factor 0-100, weighted average
            #   ACWR:          25%  (most predictive of injury/overtraining)
            #   Sleep:         25%  (hours + quality)
            #   HRV:           20%  (autonomic recovery)
            #   RHR:           15%  (cardiovascular recovery)
            #   Body Battery:  15%  (Garmin's energy estimate)

            t = rows[-1]  # today's data
            t_rhr, t_hrv, t_bb = t[4], t[5], t[6]
            t_sleep_h, t_sleep_score = t[3], t[7]
            t_bb_drained, t_hrv_weekly = t[8], t[9]

            # Get ACWR from the live API data (more current than DB)
            t_acwr = None
            if device_status:
                acwr_dto = device_status.get("acuteTrainingLoadDTO", {})
                t_acwr = acwr_dto.get("dailyAcuteChronicWorkloadRatio") if acwr_dto else None
            if t_acwr is None:
                t_acwr = t[2]  # fallback to DB

            scores = {}
            details = {}

            # --- ACWR Score (25%) ---
            # Sweet spot: 0.8-1.3 = 100, degrades outside
            if t_acwr is not None:
                if 0.8 <= t_acwr <= 1.3:
                    scores["acwr"] = 100
                elif t_acwr < 0.8:
                    scores["acwr"] = max(0, t_acwr / 0.8 * 100)
                else:  # > 1.3
                    scores["acwr"] = max(0, 100 - (t_acwr - 1.3) / 0.7 * 100)
                details["acwr"] = f"ACWR {t_acwr:.1f}"

            # --- Sleep Score (25%) ---
            # Use sleep_score if available, otherwise estimate from hours
            # For 20yo athlete: 8h=100, 7h=75, 6h=50, <5h=20
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

            # --- HRV Score (20%) ---
            # Compare last night HRV to weekly average
            # Above avg = good recovery, below = stressed
            if t_hrv is not None:
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
                    scores["hrv"] = 60  # no baseline, assume neutral
                    details["hrv"] = f"HRV {t_hrv:.0f}"

            # --- RHR Score (15%) ---
            # Yehwan baseline ~44bpm. Lower=better recovered
            # 44=100, 48=80, 52=60, 56=40, 60+=20
            BASELINE_RHR = 44
            if t_rhr is not None:
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

            # --- Body Battery Score (15%) ---
            # BB charged amount: 80+=excellent, 60=good, 40=fair, <20=poor
            if t_bb is not None:
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

                print(f"\n{'=' * 55}")
                print(f"  TRAINING READINESS (computed)")
                print("=" * 55)
                print(f"\n  Readiness Score:  {readiness}/100  [{level}]")
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
            else:
                print(f"\n  (Not enough data to compute readiness)")

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
