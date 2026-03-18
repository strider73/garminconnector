import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from garminconnect import Garmin
import garth
from datetime import date, datetime, timedelta
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

    if len(sys.argv) > 1:
        today = date.fromisoformat(sys.argv[1])
    else:
        today = date.today()
    today_str = today.isoformat()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.isoformat()

    print("=" * 55)
    print(f"  MORNING READINESS - {today_str}")
    print("=" * 55)

    # ==========================================================
    # 1) SLEEP (first — most important for morning readiness)
    # ==========================================================
    COMPLETE_TYPES = {"enhanced_confirmed_final", "auto_final", "auto_manual", "manual", "device"}
    NOT_WORN_TYPES = {"unconfirmed", "off_wrist"}
    PENDING_TYPES = {"enhanced_tentative", "auto_tentative"}

    sleep_status = "NO_DATA"

    try:
        sleep_data = garmin.get_sleep_data(today_str)
        confirmation_type = None

        if sleep_data and "dailySleepDTO" in sleep_data:
            dto = sleep_data["dailySleepDTO"]
            confirmation_type = (dto.get("sleepWindowConfirmationType") or "").lower()

            if confirmation_type in COMPLETE_TYPES:
                sleep_status = "COMPLETE"
            elif confirmation_type in NOT_WORN_TYPES:
                sleep_status = "NOT_WORN"
            elif confirmation_type in PENDING_TYPES:
                sleep_status = "PENDING"

            start_local = dto.get("sleepStartTimestampLocal")
            start_gmt = dto.get("sleepStartTimestampGMT")
            end_local = dto.get("sleepEndTimestampLocal")
            end_gmt = dto.get("sleepEndTimestampGMT")
            start_ts = start_local if start_local is not None else start_gmt
            end_ts = end_local if end_local is not None else end_gmt

            print(f"\n💤 SLEEP (last night)")
            print("-" * 55)

            if start_ts and end_ts and sleep_status == "COMPLETE":
                bed_time = datetime.utcfromtimestamp(start_ts / 1000)
                wake_time = datetime.utcfromtimestamp(end_ts / 1000)
                sleep_dur = (end_ts - start_ts) / 1000 / 3600
                sleep_score = dto.get("sleepScores", {}).get("overall", {}).get("value")
                sleep_quality = dto.get("sleepScores", {}).get("overall", {}).get("qualifierKey")

                print(f"Bed Time:           {bed_time.strftime('%I:%M %p, %a %b %d')}")
                print(f"Wake Time:          {wake_time.strftime('%I:%M %p, %a %b %d')}")
                print(f"Duration:           {sleep_dur:.1f}h")
                if sleep_score:
                    print(f"Sleep Score:        {sleep_score}")
                if sleep_quality:
                    print(f"Sleep Quality:      {sleep_quality}")
            elif sleep_status == "NOT_WORN":
                print(f"Watch not worn overnight — no sleep data")
            elif sleep_status == "PENDING":
                print(f"Sleep data still processing...")
            else:
                print(f"No sleep data available")

            print(f"[SLEEP_STATUS:{sleep_status}]")
        else:
            print(f"\n💤 SLEEP (last night)")
            print("-" * 55)
            print(f"No sleep data available")
            print(f"[SLEEP_STATUS:NO_DATA]")

    except Exception as e:
        print(f"\n💤 SLEEP (last night)")
        print("-" * 55)
        print(f"Could not fetch sleep data: {e}")
        print(f"[SLEEP_STATUS:NO_DATA]")

    # ==========================================================
    # 2) BODY BATTERY (right after sleep)
    # ==========================================================
    print(f"\n🔋 BODY BATTERY")
    print("-" * 55)
    try:
        bb_data = garmin.get_body_battery(today_str)
        if bb_data and isinstance(bb_data, list) and len(bb_data) > 0:
            bb_charged = bb_data[0].get("charged")
            bb_drained = bb_data[0].get("drained")
            if bb_charged is not None:
                print(f"Charged:            {bb_charged}")
            if bb_drained is not None:
                print(f"Drained:            {bb_drained}")
            if bb_charged is None and bb_drained is None:
                print(f"No body battery data (watch not worn?)")
        else:
            print(f"No body battery data available")
    except Exception as e:
        print(f"Could not fetch body battery: {e}")

    # ==========================================================
    # 3) HEART RATE & HRV
    # ==========================================================
    print(f"\n❤️  HEART RATE & HRV")
    print("-" * 55)
    try:
        hr_data = garmin.get_heart_rates(today_str)
        if hr_data:
            rhr = hr_data.get("restingHeartRate")
            if rhr:
                print(f"Resting HR:         {rhr} bpm")
            else:
                print(f"Resting HR:         No data")
        else:
            print(f"Resting HR:         No data")
    except Exception as e:
        print(f"Could not fetch HR: {e}")

    try:
        hrv_data = garmin.get_hrv_data(today_str)
        if hrv_data:
            summary = hrv_data.get("hrvSummary", {})
            hrv_last = summary.get("lastNightAvg") if summary else None
            hrv_weekly = summary.get("weeklyAvg") if summary else None
            hrv_status = summary.get("status", "") if summary else ""
            if hrv_last:
                print(f"HRV Last Night:     {hrv_last} ms")
            if hrv_weekly:
                print(f"HRV Weekly Avg:     {hrv_weekly} ms")
            if hrv_status:
                print(f"HRV Status:         {hrv_status}")
            if not hrv_last and not hrv_weekly:
                print(f"HRV:                No data")
    except Exception as e:
        print(f"Could not fetch HRV: {e}")

    # ==========================================================
    # 4) TRAINING STATUS & LOAD
    # ==========================================================
    print(f"\n📊 TRAINING STATUS")
    print("-" * 55)
    try:
        status = garmin.get_training_status(yesterday_str)

        if status:
            # Training Status
            latest = status.get("mostRecentTrainingStatus", {})
            latest_data = latest.get("latestTrainingStatusData", {}) if latest else {}
            device_status = next(iter(latest_data.values()), {}) if latest_data else {}

            if device_status:
                ts_code = device_status.get("trainingStatus")
                ts_label = TRAINING_STATUS_MAP.get(ts_code, str(ts_code))
                print(f"Status:             {ts_label}")

                acwr_dto = device_status.get("acuteTrainingLoadDTO", {})
                if acwr_dto:
                    acute = acwr_dto.get("dailyTrainingLoadAcute")
                    chronic = acwr_dto.get("dailyTrainingLoadChronic")
                    ratio = acwr_dto.get("dailyAcuteChronicWorkloadRatio")
                    acwr_status = acwr_dto.get("acwrStatus")
                    if acute is not None:
                        print(f"Acute Load:         {acute}")
                    if chronic is not None:
                        print(f"Chronic Load:       {chronic}")
                    if ratio is not None:
                        print(f"ACWR:               {ratio}")
                    if acwr_status:
                        print(f"Load Status:        {acwr_status}")

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
                bal_feedback = device_balance.get("trainingBalanceFeedbackPhrase", "")

                print(f"\nMonthly Load Balance:")
                if aero_low is not None:
                    target = f" (target: {aero_low_min}-{aero_low_max})" if aero_low_min is not None else ""
                    print(f"  Aerobic Low:      {aero_low:.1f}{target}")
                if aero_high is not None:
                    target = f" (target: {aero_high_min}-{aero_high_max})" if aero_high_min is not None else ""
                    print(f"  Aerobic High:     {aero_high:.1f}{target}")
                if anaerobic is not None:
                    target = f" (target: {anaerobic_min}-{anaerobic_max})" if anaerobic_min is not None else ""
                    print(f"  Anaerobic:        {anaerobic:.1f}{target}")
                if bal_feedback:
                    print(f"  Balance:          {bal_feedback}")
        else:
            print(f"No training status available")
    except Exception as e:
        print(f"Could not fetch training status: {e}")

    print()

except Exception as e:
    print(f"\nError: {e}")
    print("You may need to login first")
