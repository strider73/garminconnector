import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date
from config import email, password

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

    today = date.today().isoformat()

    # ===== TRAINING READINESS =====
    readiness = garmin.get_training_readiness(today)

    print("=" * 55)
    print(f"  TRAINING READINESS - {today}")
    print("=" * 55)

    if readiness:
        score = readiness.get("score")
        level = readiness.get("levelKey", readiness.get("level"))
        sleep_score = readiness.get("sleepScore")
        recovery_time = readiness.get("recoveryTimeInMinutes")
        hrv_status = readiness.get("hrvStatus")
        acute_load = readiness.get("acuteTrainingLoad")
        sleep_history = readiness.get("sleepHistoryScore")
        stress_history = readiness.get("stressHistoryScore")

        if score is not None:
            print(f"\n  Readiness Score:  {score}/100")
        if level:
            print(f"  Level:            {level}")

        has_factors = any(v is not None for v in [sleep_score, sleep_history, hrv_status, stress_history, acute_load, recovery_time])
        if has_factors:
            print(f"\n  --- Contributing Factors ---")
            if sleep_score is not None:
                print(f"  Sleep Score:      {sleep_score}")
            if sleep_history is not None:
                print(f"  Sleep History:    {sleep_history}")
            if hrv_status is not None:
                print(f"  HRV Status:       {hrv_status}")
            if stress_history is not None:
                print(f"  Stress History:   {stress_history}")
            if acute_load is not None:
                print(f"  Acute Load:       {acute_load}")
            if recovery_time is not None:
                hours = recovery_time // 60
                mins = recovery_time % 60
                print(f"  Recovery Time:    {hours}h {mins}m")
    else:
        print("\n  No training readiness data available for today.")

    # ===== TRAINING STATUS =====
    status = garmin.get_training_status(today)

    if status:
        print(f"\n{'=' * 55}")
        print(f"  TRAINING STATUS - {today}")
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

    print()

except Exception as e:
    print(f"\nError: {e}")
    print("You may need to login first")
