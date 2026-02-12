#!/usr/bin/env python3
"""
Trainer Weekly Report - Quick 5-min read before session
Combines weekly activity + heart rate/recovery + training load
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date, timedelta, datetime
from config import email, password

def safe_get(data, key, default=None):
    if data is None:
        return default
    val = data.get(key, default)
    return default if val is None else val

def safe_nested_get(data, *keys, default=None):
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
    os.makedirs(garth_home, exist_ok=True)

    try:
        garth.resume(garth_home)
    except:
        garth.login(email, password)
        garth.save(garth_home)

    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    full_name = garmin.get_full_name()
    print(f"Connected as: {full_name}\n")

    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    print("=" * 90)
    print(f"  WEEKLY TRAINER REPORT - {full_name}")
    print(f"  {days[0].strftime('%Y-%m-%d (%a)')} to {days[-1].strftime('%Y-%m-%d (%a)')}")
    print("=" * 90)

    # Storage
    all_data = []
    totals = {
        'sleep': 0, 'steps': 0, 'calories': 0, 'active_cal': 0,
        'distance': 0, 'moderate_mins': 0, 'vigorous_mins': 0,
        'deep': 0, 'rem': 0,
    }
    counts = {'sleep': 0, 'days_with_data': 0, 'stress': 0, 'body_battery': 0}
    resting_hrs = []
    hrvs = []
    stress_total = 0
    bb_total = 0

    for day in days:
        day_str = day.isoformat()
        day_name = day.strftime('%a %m/%d')

        row = {
            'date': day_name,
            'sleep_hours': None, 'sleep_score': None,
            'sleep_start': None, 'sleep_end': None,
            'deep_mins': None, 'rem_mins': None,
            'resting_hr': None, 'max_hr': None, 'hrv': None,
            'body_battery': None, 'stress': None,
            'moderate_mins': None, 'vigorous_mins': None,
            'steps': None, 'calories': None, 'active_cal': None, 'distance': None
        }

        has_data = False

        # ===== SLEEP =====
        try:
            sleep_data = garmin.get_sleep_data(day_str)
            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                if daily_sleep:
                    sleep_sec = safe_get(daily_sleep, 'sleepTimeSeconds', 0)
                    deep_sec = safe_get(daily_sleep, 'deepSleepSeconds', 0)
                    rem_sec = safe_get(daily_sleep, 'remSleepSeconds', 0)
                    if sleep_sec and sleep_sec > 0:
                        row['sleep_hours'] = round(sleep_sec / 3600, 1)
                        row['deep_mins'] = round(deep_sec / 60) if deep_sec else 0
                        row['rem_mins'] = round(rem_sec / 60) if rem_sec else 0
                        totals['sleep'] += row['sleep_hours']
                        totals['deep'] += row['deep_mins']
                        totals['rem'] += row['rem_mins']
                        counts['sleep'] += 1

                    start_ts = safe_get(daily_sleep, 'sleepStartTimestampGMT')
                    end_ts = safe_get(daily_sleep, 'sleepEndTimestampGMT')
                    if start_ts:
                        row['sleep_start'] = datetime.fromtimestamp(start_ts / 1000).strftime('%I:%M %p')
                    if end_ts:
                        row['sleep_end'] = datetime.fromtimestamp(end_ts / 1000).strftime('%I:%M %p')

                sleep_scores = sleep_data.get('sleepScores')
                if sleep_scores:
                    row['sleep_score'] = safe_nested_get(sleep_scores, 'overall', 'value')
        except:
            pass

        # ===== HEART RATE =====
        try:
            hr_data = garmin.get_heart_rates(day_str)
            if hr_data:
                row['resting_hr'] = safe_get(hr_data, 'restingHeartRate')
                row['max_hr'] = safe_get(hr_data, 'maxHeartRate')
                if row['resting_hr']:
                    resting_hrs.append(row['resting_hr'])
        except:
            pass

        # ===== HRV =====
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

        # ===== STRESS =====
        try:
            stress_data = garmin.get_stress_data(day_str)
            if stress_data:
                row['stress'] = safe_get(stress_data, 'overallStressLevel')
                if row['stress']:
                    stress_total += row['stress']
                    counts['stress'] += 1
        except:
            pass

        # ===== BODY BATTERY =====
        try:
            bb_data = garmin.get_body_battery(day_str)
            if bb_data and isinstance(bb_data, list) and len(bb_data) > 0:
                bb_values = [safe_get(b, 'bodyBatteryLevel') for b in bb_data if safe_get(b, 'bodyBatteryLevel')]
                if bb_values:
                    row['body_battery'] = max(bb_values)
                    bb_total += row['body_battery']
                    counts['body_battery'] += 1
        except:
            pass

        # ===== STATS =====
        try:
            stats = garmin.get_stats(day_str)
            if stats:
                row['steps'] = safe_get(stats, 'totalSteps')
                row['calories'] = safe_get(stats, 'totalKilocalories')
                row['active_cal'] = safe_get(stats, 'activeKilocalories')
                distance_m = safe_get(stats, 'totalDistanceMeters')
                row['distance'] = round(distance_m / 1000, 2) if distance_m else None
                row['moderate_mins'] = safe_get(stats, 'moderateIntensityMinutes')
                row['vigorous_mins'] = safe_get(stats, 'vigorousIntensityMinutes')

                if row['steps']:
                    totals['steps'] += row['steps']
                    has_data = True
                if row['calories']:
                    totals['calories'] += row['calories']
                if row['active_cal']:
                    totals['active_cal'] += row['active_cal']
                if row['distance']:
                    totals['distance'] += row['distance']
                if row['moderate_mins']:
                    totals['moderate_mins'] += row['moderate_mins']
                if row['vigorous_mins']:
                    totals['vigorous_mins'] += row['vigorous_mins']
        except:
            pass

        if has_data:
            counts['days_with_data'] += 1

        all_data.append(row)

    # ===== TABLE 1: SLEEP & RECOVERY =====
    print("\n" + "-" * 90)
    print("  SLEEP & RECOVERY")
    print("-" * 90)
    print(f"{'Date':<10} | {'Bedtime':>8} | {'Wake Up':>8} | {'Hrs':>5} | {'Score':>5} | {'Deep':>5} | {'REM':>5} | {'HRV':>5} | {'Rest HR':>7}")
    print("-" * 90)

    for row in all_data:
        bed = row['sleep_start'] if row['sleep_start'] else "-"
        wake = row['sleep_end'] if row['sleep_end'] else "-"
        hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
        score = str(row['sleep_score']) if row['sleep_score'] else "-"
        deep = f"{row['deep_mins']}m" if row['deep_mins'] else "-"
        rem = f"{row['rem_mins']}m" if row['rem_mins'] else "-"
        hrv = str(row['hrv']) if row['hrv'] else "-"
        rhr = str(row['resting_hr']) if row['resting_hr'] else "-"
        print(f"{row['date']:<10} | {bed:>8} | {wake:>8} | {hrs:>5} | {score:>5} | {deep:>5} | {rem:>5} | {hrv:>5} | {rhr:>7}")

    print("-" * 90)

    # ===== TABLE 2: ACTIVITY & HEART RATE =====
    print("\n" + "-" * 95)
    print(f"{'Date':<10} | {'Steps':>8} {'Cal':>6} {'Dist':>6} | {'Rest':>5} {'Max':>5} {'Mod':>5} {'Vig':>5} | {'Batt':>5} {'Stress':>6}")
    print("-" * 95)

    for row in all_data:
        steps = f"{row['steps']:,}" if row['steps'] else "-"
        cal = str(int(row['calories'])) if row['calories'] else "-"
        dist = f"{row['distance']:.1f}km" if row['distance'] else "-"
        rest_hr = str(row['resting_hr']) if row['resting_hr'] else "-"
        max_hr = str(row['max_hr']) if row['max_hr'] else "-"
        mod = f"{row['moderate_mins']}m" if row['moderate_mins'] else "-"
        vig = f"{row['vigorous_mins']}m" if row['vigorous_mins'] else "-"
        bb = str(row['body_battery']) if row['body_battery'] else "-"
        stress = str(row['stress']) if row['stress'] else "-"
        print(f"{row['date']:<10} | {steps:>8} {cal:>6} {dist:>6} | {rest_hr:>5} {max_hr:>5} {mod:>5} {vig:>5} | {bb:>5} {stress:>6}")

    print("-" * 95)

    # ===== TABLE 4: TRAINING & CALORIES =====
    print("\n" + "-" * 80)
    print("  TRAINING & CALORIES")
    print("-" * 80)
    print(f"{'Date':<10} | {'Steps':>8} | {'Calories':>9} | {'Active':>8} | {'Moderate':>9} | {'Vigorous':>9}")
    print("-" * 80)

    for row in all_data:
        steps = f"{row['steps']:,}" if row['steps'] else "-"
        cal = str(int(row['calories'])) if row['calories'] else "-"
        active = str(int(row['active_cal'])) if row['active_cal'] else "-"
        mod = f"{row['moderate_mins']}m" if row['moderate_mins'] else "-"
        vig = f"{row['vigorous_mins']}m" if row['vigorous_mins'] else "-"
        print(f"{row['date']:<10} | {steps:>8} | {cal:>9} | {active:>8} | {mod:>9} | {vig:>9}")

    print("-" * 80)

    # ===== WEEKLY SUMMARY =====
    days_with_data = max(counts['days_with_data'], 1)

    print("\n" + "=" * 90)
    print("  WEEKLY SUMMARY")
    print("=" * 90)

    print(f"""
  Metric              Total           Daily Avg
  -------             -----           ---------
  Sleep               {totals['sleep']:.1f} hrs         {totals['sleep']/max(counts['sleep'],1):.1f} hrs
  Steps               {totals['steps']:,}        {totals['steps']//days_with_data:,}
  Calories            {totals['calories']:,.0f}          {totals['calories']/days_with_data:,.0f}
  Active Calories     {totals['active_cal']:,.0f}          {totals['active_cal']/days_with_data:,.0f}
  Distance            {totals['distance']:.1f} km        {totals['distance']/days_with_data:.1f} km
  Moderate Mins       {totals['moderate_mins']} mins        {totals['moderate_mins']//days_with_data} mins
  Vigorous Mins       {totals['vigorous_mins']} mins        {totals['vigorous_mins']//days_with_data} mins""")

    # Recovery summary
    print(f"\n  Recovery")
    print(f"  --------")
    if resting_hrs:
        avg_rhr = sum(resting_hrs) / len(resting_hrs)
        print(f"  Resting HR:       Avg {avg_rhr:.0f} bpm (range {min(resting_hrs)}-{max(resting_hrs)})")
    if hrvs:
        avg_hrv = sum(hrvs) / len(hrvs)
        print(f"  HRV:              Avg {avg_hrv:.0f} ms (range {min(hrvs)}-{max(hrvs)})")
    if counts['body_battery'] > 0:
        print(f"  Body Battery:     Avg {bb_total/counts['body_battery']:.0f}%")
    if counts['stress'] > 0:
        print(f"  Stress Level:     Avg {stress_total/counts['stress']:.0f}")

    # Sleep quality
    if counts['sleep'] > 0:
        avg_sleep = totals['sleep'] / counts['sleep']
        avg_deep = totals['deep'] / counts['sleep']
        avg_rem = totals['rem'] / counts['sleep']
        print(f"\n  Sleep Quality")
        print(f"  -------------")
        print(f"  Average:          {avg_sleep:.1f} hrs/night")
        print(f"  Deep Sleep:       {avg_deep:.0f} min/night")
        print(f"  REM Sleep:        {avg_rem:.0f} min/night")

    # ===== TRAINER NOTES =====
    print(f"\n{'=' * 90}")
    print("  NOTES FOR TODAY'S SESSION")
    print("=" * 90)

    notes = []

    # Sleep assessment
    if counts['sleep'] > 0:
        avg_sleep = totals['sleep'] / counts['sleep']
        if avg_sleep < 7:
            notes.append(f"  Sleep avg {avg_sleep:.1f}h - below 7h, expect slower recovery between sets")
        elif avg_sleep >= 8:
            notes.append(f"  Sleep avg {avg_sleep:.1f}h - well rested, can push intensity")

    # Recovery assessment
    if counts['body_battery'] > 0:
        avg_bb = bb_total / counts['body_battery']
        if avg_bb > 70:
            notes.append(f"  Body battery avg {avg_bb:.0f}% - good energy, ready for high intensity")
        elif avg_bb > 50:
            notes.append(f"  Body battery avg {avg_bb:.0f}% - moderate energy, balance work/rest")
        else:
            notes.append(f"  Body battery avg {avg_bb:.0f}% - low energy, keep session lighter")

    if counts['stress'] > 0:
        avg_stress = stress_total / counts['stress']
        if avg_stress > 50:
            notes.append(f"  Stress avg {avg_stress:.0f} - elevated, watch for fatigue signs")

    # HRV trend
    if hrvs:
        avg_hrv = sum(hrvs) / len(hrvs)
        if avg_hrv < 40:
            notes.append(f"  HRV avg {avg_hrv:.0f}ms - low, autonomic recovery is lagging")
        elif avg_hrv > 60:
            notes.append(f"  HRV avg {avg_hrv:.0f}ms - strong recovery capacity")

    # Resting HR
    if resting_hrs:
        avg_rhr = sum(resting_hrs) / len(resting_hrs)
        if avg_rhr > 55:
            notes.append(f"  Resting HR avg {avg_rhr:.0f} bpm - slightly elevated for athlete baseline")

    # Training load
    total_intensity = totals['moderate_mins'] + totals['vigorous_mins']
    if total_intensity < 60:
        notes.append(f"  Light training week ({total_intensity} mins) - can increase load today")
    elif total_intensity > 300:
        notes.append(f"  Heavy training week ({total_intensity} mins) - consider active recovery")

    if not notes:
        notes.append("  All metrics look normal - proceed with planned session")

    for note in notes:
        print(note)

    print(f"\n{'=' * 90}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
