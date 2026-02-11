#!/usr/bin/env python3
"""
Weekly Tennis Player Health Report
- Sleep (hours, score, deep/REM)
- Heart Rate (resting, avg, max, HRV)
- Calories & Training Load
- Body Battery & Stress
- VO2 Max & Fitness Age
- Training Recommendations
"""

from garminconnect import Garmin
import garth
import os
from datetime import date, timedelta

def safe_get(data, key, default=None):
    """Safely get value, returning default if None"""
    if data is None:
        return default
    val = data.get(key, default)
    return default if val is None else val

def safe_nested_get(data, *keys, default=None):
    """Safely get nested value"""
    for key in keys:
        if data is None:
            return default
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
    return default if data is None else data

try:
    print("Connecting to Garmin...")

    garth_home = os.path.expanduser("~/.garth")
    garth.resume(garth_home)

    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    full_name = garmin.get_full_name()
    print(f"✅ Connected as: {full_name}\n")

    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    print("=" * 80)
    print(f"🎾 WEEKLY TENNIS PLAYER REPORT - {full_name}")
    print(f"   {days[0].strftime('%Y-%m-%d (%a)')} to {days[-1].strftime('%Y-%m-%d (%a)')}")
    print("=" * 80)

    # Storage
    all_data = []
    totals = {
        'sleep': 0, 'deep': 0, 'rem': 0, 'light': 0,
        'calories': 0, 'active_cal': 0, 'steps': 0,
        'moderate_mins': 0, 'vigorous_mins': 0,
        'stress_avg': 0, 'body_battery_avg': 0
    }
    counts = {
        'sleep': 0, 'calories': 0, 'stress': 0, 'body_battery': 0, 'resting_hr': 0
    }
    resting_hrs = []
    hrvs = []

    for day in days:
        day_str = day.isoformat()
        day_name = day.strftime('%a %m/%d')

        row = {
            'date': day_name,
            'sleep_hours': None, 'sleep_score': None,
            'deep_mins': None, 'rem_mins': None, 'light_mins': None,
            'resting_hr': None, 'max_hr': None, 'hrv': None,
            'calories': None, 'active_cal': None,
            'body_battery': None, 'stress': None,
            'moderate_mins': None, 'vigorous_mins': None,
            'steps': None
        }

        # ===== SLEEP DATA =====
        try:
            sleep_data = garmin.get_sleep_data(day_str)
            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                if daily_sleep:
                    sleep_sec = safe_get(daily_sleep, 'sleepTimeSeconds', 0)
                    deep_sec = safe_get(daily_sleep, 'deepSleepSeconds', 0)
                    rem_sec = safe_get(daily_sleep, 'remSleepSeconds', 0)
                    light_sec = safe_get(daily_sleep, 'lightSleepSeconds', 0)

                    if sleep_sec and sleep_sec > 0:
                        row['sleep_hours'] = round(sleep_sec / 3600, 1)
                        row['deep_mins'] = round(deep_sec / 60) if deep_sec else 0
                        row['rem_mins'] = round(rem_sec / 60) if rem_sec else 0
                        row['light_mins'] = round(light_sec / 60) if light_sec else 0

                        totals['sleep'] += row['sleep_hours']
                        totals['deep'] += row['deep_mins']
                        totals['rem'] += row['rem_mins']
                        totals['light'] += row['light_mins']
                        counts['sleep'] += 1

                # Sleep score
                sleep_scores = sleep_data.get('sleepScores')
                if sleep_scores:
                    row['sleep_score'] = safe_nested_get(sleep_scores, 'overall', 'value')
        except:
            pass

        # ===== HEART RATE & HRV =====
        try:
            hr_data = garmin.get_heart_rates(day_str)
            if hr_data:
                row['resting_hr'] = safe_get(hr_data, 'restingHeartRate')
                row['max_hr'] = safe_get(hr_data, 'maxHeartRate')
                if row['resting_hr']:
                    resting_hrs.append(row['resting_hr'])
                    counts['resting_hr'] += 1
        except:
            pass

        # HRV (separate endpoint)
        try:
            hrv_data = garmin.get_hrv_data(day_str)
            if hrv_data:
                hrv_summary = hrv_data.get('hrvSummary', {})
                if hrv_summary:
                    row['hrv'] = safe_get(hrv_summary, 'lastNightAvg')
                    if row['hrv']:
                        hrvs.append(row['hrv'])
        except:
            pass

        # ===== STRESS & BODY BATTERY =====
        try:
            stress_data = garmin.get_stress_data(day_str)
            if stress_data:
                row['stress'] = safe_get(stress_data, 'overallStressLevel')
                if row['stress']:
                    totals['stress_avg'] += row['stress']
                    counts['stress'] += 1
        except:
            pass

        try:
            bb_data = garmin.get_body_battery(day_str)
            if bb_data and isinstance(bb_data, list) and len(bb_data) > 0:
                # Get highest body battery of the day
                bb_values = [safe_get(b, 'bodyBatteryLevel') for b in bb_data if safe_get(b, 'bodyBatteryLevel')]
                if bb_values:
                    row['body_battery'] = max(bb_values)
                    totals['body_battery_avg'] += row['body_battery']
                    counts['body_battery'] += 1
        except:
            pass

        # ===== STATS (Calories, Steps, Intensity) =====
        try:
            stats = garmin.get_stats(day_str)
            if stats:
                row['calories'] = safe_get(stats, 'totalKilocalories')
                row['active_cal'] = safe_get(stats, 'activeKilocalories')
                row['steps'] = safe_get(stats, 'totalSteps')
                row['moderate_mins'] = safe_get(stats, 'moderateIntensityMinutes')
                row['vigorous_mins'] = safe_get(stats, 'vigorousIntensityMinutes')

                if row['calories'] and row['calories'] > 0:
                    totals['calories'] += row['calories']
                    totals['active_cal'] += row['active_cal'] or 0
                    counts['calories'] += 1
                if row['steps']:
                    totals['steps'] += row['steps']
                if row['moderate_mins']:
                    totals['moderate_mins'] += row['moderate_mins']
                if row['vigorous_mins']:
                    totals['vigorous_mins'] += row['vigorous_mins']
        except:
            pass

        all_data.append(row)

    # ===== TABLE 1: SLEEP =====
    print("\n" + "─" * 80)
    print("😴 SLEEP")
    print("─" * 80)
    print(f"{'Date':<10} │ {'Hours':>6} │ {'Score':>6} │ {'Deep':>6} │ {'REM':>6} │ {'Light':>6}")
    print("─" * 80)

    for row in all_data:
        hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
        score = str(row['sleep_score']) if row['sleep_score'] else "-"
        deep = f"{row['deep_mins']}m" if row['deep_mins'] else "-"
        rem = f"{row['rem_mins']}m" if row['rem_mins'] else "-"
        light = f"{row['light_mins']}m" if row['light_mins'] else "-"
        print(f"{row['date']:<10} │ {hrs:>6} │ {score:>6} │ {deep:>6} │ {rem:>6} │ {light:>6}")

    # ===== TABLE 2: HEART & RECOVERY =====
    print("\n" + "─" * 80)
    print("❤️ HEART RATE & RECOVERY")
    print("─" * 80)
    print(f"{'Date':<10} │ {'Rest HR':>8} │ {'Max HR':>8} │ {'HRV':>6} │ {'Battery':>8} │ {'Stress':>7}")
    print("─" * 80)

    for row in all_data:
        rest = str(row['resting_hr']) if row['resting_hr'] else "-"
        max_hr = str(row['max_hr']) if row['max_hr'] else "-"
        hrv = str(row['hrv']) if row['hrv'] else "-"
        bb = str(row['body_battery']) if row['body_battery'] else "-"
        stress = str(row['stress']) if row['stress'] else "-"
        print(f"{row['date']:<10} │ {rest:>8} │ {max_hr:>8} │ {hrv:>6} │ {bb:>8} │ {stress:>7}")

    # ===== TABLE 3: TRAINING =====
    print("\n" + "─" * 80)
    print("🏃 TRAINING & CALORIES")
    print("─" * 80)
    print(f"{'Date':<10} │ {'Steps':>8} │ {'Calories':>9} │ {'Active':>8} │ {'Moderate':>9} │ {'Vigorous':>9}")
    print("─" * 80)

    for row in all_data:
        steps = f"{row['steps']:,}" if row['steps'] else "-"
        cal = str(int(row['calories'])) if row['calories'] else "-"
        active = str(int(row['active_cal'])) if row['active_cal'] else "-"
        mod = f"{row['moderate_mins']}m" if row['moderate_mins'] else "-"
        vig = f"{row['vigorous_mins']}m" if row['vigorous_mins'] else "-"
        print(f"{row['date']:<10} │ {steps:>8} │ {cal:>9} │ {active:>8} │ {mod:>9} │ {vig:>9}")

    # ===== WEEKLY SUMMARY =====
    print("\n" + "=" * 80)
    print("📈 WEEKLY SUMMARY")
    print("=" * 80)

    # Sleep Summary
    print("\n😴 SLEEP:")
    if counts['sleep'] > 0:
        avg_sleep = totals['sleep'] / counts['sleep']
        avg_deep = totals['deep'] / counts['sleep']
        avg_rem = totals['rem'] / counts['sleep']
        print(f"   Average: {avg_sleep:.1f} hrs/night (Deep: {avg_deep:.0f}m, REM: {avg_rem:.0f}m)")

        # Tennis-specific sleep advice
        if avg_sleep < 7:
            print(f"   ⚠️  Below 7 hours - impacts reaction time & recovery")
        elif avg_sleep >= 8:
            print(f"   ✅ Excellent for athletic recovery")
        else:
            print(f"   👍 Good - aim for 8+ hours for peak performance")

        if avg_deep < 60:
            print(f"   ⚠️  Low deep sleep - affects muscle recovery")
        if avg_rem < 60:
            print(f"   ⚠️  Low REM sleep - affects skill memory & learning")
    else:
        print(f"   No sleep data available")

    # Heart Rate Summary
    print("\n❤️ HEART RATE:")
    if resting_hrs:
        avg_rhr = sum(resting_hrs) / len(resting_hrs)
        print(f"   Avg Resting HR: {avg_rhr:.0f} bpm")
        if avg_rhr < 60:
            print(f"   ✅ Excellent cardiovascular fitness")
        elif avg_rhr < 70:
            print(f"   👍 Good fitness level")
        else:
            print(f"   📈 Room for improvement with cardio training")

    if hrvs:
        avg_hrv = sum(hrvs) / len(hrvs)
        print(f"   Avg HRV: {avg_hrv:.0f} ms")
        if avg_hrv > 50:
            print(f"   ✅ Good recovery capacity")
        else:
            print(f"   ⚠️  Consider more recovery time")

    # Training Summary
    print("\n🏃 TRAINING:")
    print(f"   Total Steps: {totals['steps']:,} ({totals['steps']//7:,}/day avg)")
    print(f"   Total Calories: {totals['calories']:,.0f} kcal")
    print(f"   Intensity Minutes: {totals['moderate_mins']}m moderate + {totals['vigorous_mins']}m vigorous")

    total_intensity = totals['moderate_mins'] + (totals['vigorous_mins'] * 2)  # Vigorous counts double
    print(f"   WHO Target Progress: {total_intensity}/150 minutes ({total_intensity*100//150}%)")

    if totals['vigorous_mins'] < 75:
        print(f"   ⚠️  Need more high-intensity training for tennis")
    else:
        print(f"   ✅ Good intensity level for tennis performance")

    # Body Battery & Stress
    print("\n⚡ RECOVERY STATUS:")
    if counts['body_battery'] > 0:
        avg_bb = totals['body_battery_avg'] / counts['body_battery']
        print(f"   Avg Peak Body Battery: {avg_bb:.0f}%")
        if avg_bb > 70:
            print(f"   ✅ Well recovered - can train hard")
        elif avg_bb > 50:
            print(f"   👍 Moderate energy - balance intensity")
        else:
            print(f"   ⚠️  Low energy - prioritize recovery")

    if counts['stress'] > 0:
        avg_stress = totals['stress_avg'] / counts['stress']
        print(f"   Avg Stress Level: {avg_stress:.0f}")
        if avg_stress < 30:
            print(f"   ✅ Low stress - optimal for training")
        elif avg_stress < 50:
            print(f"   👍 Moderate stress - monitor closely")
        else:
            print(f"   ⚠️  High stress - may impact performance")

    # ===== TENNIS RECOMMENDATIONS =====
    print("\n" + "=" * 80)
    print("🎾 TENNIS TRAINING RECOMMENDATIONS")
    print("=" * 80)

    # Determine training readiness
    ready_score = 0
    if counts['body_battery'] > 0 and totals['body_battery_avg'] / counts['body_battery'] > 60:
        ready_score += 1
    if counts['stress'] > 0 and totals['stress_avg'] / counts['stress'] < 40:
        ready_score += 1
    if counts['sleep'] > 0 and totals['sleep'] / counts['sleep'] >= 7:
        ready_score += 1
    if hrvs and sum(hrvs) / len(hrvs) > 40:
        ready_score += 1

    if ready_score >= 3:
        print("\n✅ READY FOR INTENSE TRAINING")
        print("   → High-intensity drills, match practice")
        print("   → Sprint & agility training")
        print("   → Focus on explosive power")
    elif ready_score >= 2:
        print("\n👍 MODERATE TRAINING DAY")
        print("   → Technical skill work")
        print("   → Moderate rally practice")
        print("   → Avoid exhaustive sessions")
    else:
        print("\n⚠️ RECOVERY DAY RECOMMENDED")
        print("   → Light stretching & mobility")
        print("   → Easy hitting or serve practice")
        print("   → Focus on sleep & nutrition")

    # Weekly intensity targets
    print("\n📊 NEXT WEEK TARGETS:")
    target_vigorous = max(15, int(totals['vigorous_mins'] * 1.1))  # 10% increase
    target_moderate = max(30, int(totals['moderate_mins'] * 1.1))
    print(f"   Vigorous: {target_vigorous} mins (current: {totals['vigorous_mins']})")
    print(f"   Moderate: {target_moderate} mins (current: {totals['moderate_mins']})")

    print("\n" + "=" * 80)
    print("✅ Weekly tennis player report complete!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
