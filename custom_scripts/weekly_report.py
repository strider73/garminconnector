#!/usr/bin/env python3
"""
Weekly Report - Daily breakdown for Tennis Player
- Sleep (hours, score)
- Heart Rate (rest, moderate zone, vigorous zone)
- Steps, Calories, Distance
- Weekly summary with suggestions
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

    print("=" * 90)
    print(f"📊 WEEKLY REPORT - {full_name}")
    print(f"   {days[0].strftime('%Y-%m-%d (%a)')} to {days[-1].strftime('%Y-%m-%d (%a)')}")
    print("=" * 90)

    # Storage
    all_data = []
    totals = {
        'sleep': 0, 'steps': 0, 'calories': 0, 'active_cal': 0,
        'distance': 0, 'moderate_mins': 0, 'vigorous_mins': 0
    }
    counts = {'sleep': 0, 'days_with_data': 0}
    resting_hrs = []

    for day in days:
        day_str = day.isoformat()
        day_name = day.strftime('%a %m/%d')

        row = {
            'date': day_name,
            'sleep_hours': None, 'sleep_score': None,
            'resting_hr': None, 'moderate_mins': None, 'vigorous_mins': None,
            'steps': None, 'calories': None, 'active_cal': None, 'distance': None
        }

        has_data = False

        # ===== SLEEP DATA =====
        try:
            sleep_data = garmin.get_sleep_data(day_str)
            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                if daily_sleep:
                    sleep_sec = safe_get(daily_sleep, 'sleepTimeSeconds', 0)
                    if sleep_sec and sleep_sec > 0:
                        row['sleep_hours'] = round(sleep_sec / 3600, 1)
                        totals['sleep'] += row['sleep_hours']
                        counts['sleep'] += 1

                sleep_scores = sleep_data.get('sleepScores')
                if sleep_scores:
                    overall = sleep_scores.get('overall', {})
                    if overall:
                        row['sleep_score'] = safe_get(overall, 'value')
        except:
            pass

        # ===== HEART RATE =====
        try:
            hr_data = garmin.get_heart_rates(day_str)
            if hr_data:
                row['resting_hr'] = safe_get(hr_data, 'restingHeartRate')
                if row['resting_hr']:
                    resting_hrs.append(row['resting_hr'])
        except:
            pass

        # ===== STATS (Steps, Calories, Distance, Intensity) =====
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

    # ===== DAILY TABLE =====
    print("\n" + "─" * 90)
    print(f"{'Date':<10} │ {'Sleep':^12} │ {'Heart Rate (bpm)':^22} │ {'Activity':^35}")
    print(f"{'':10} │ {'Hrs':>5} {'Score':>5} │ {'Rest':>6} {'Mod':>7} {'Vig':>6} │ {'Steps':>8} {'Cal':>6} {'Dist':>6}")
    print("─" * 90)

    for row in all_data:
        sleep_hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
        sleep_score = str(row['sleep_score']) if row['sleep_score'] else "-"
        rest_hr = str(row['resting_hr']) if row['resting_hr'] else "-"
        mod = f"{row['moderate_mins']}m" if row['moderate_mins'] else "-"
        vig = f"{row['vigorous_mins']}m" if row['vigorous_mins'] else "-"
        steps = f"{row['steps']:,}" if row['steps'] else "-"
        cal = str(int(row['calories'])) if row['calories'] else "-"
        dist = f"{row['distance']:.1f}km" if row['distance'] else "-"

        print(f"{row['date']:<10} │ {sleep_hrs:>5} {sleep_score:>5} │ {rest_hr:>6} {mod:>7} {vig:>6} │ {steps:>8} {cal:>6} {dist:>6}")

    print("─" * 90)

    # ===== WEEKLY TOTALS =====
    print("\n" + "=" * 90)
    print("📈 WEEKLY TOTALS")
    print("=" * 90)

    days_with_data = counts['days_with_data'] if counts['days_with_data'] > 0 else 1

    print(f"""
┌─────────────────────┬─────────────────┬─────────────────┐
│      Metric         │      Total      │    Daily Avg    │
├─────────────────────┼─────────────────┼─────────────────┤
│ 😴 Sleep            │ {totals['sleep']:>6.1f} hrs      │ {totals['sleep']/max(counts['sleep'],1):>6.1f} hrs      │
│ 👣 Steps            │ {totals['steps']:>10,}     │ {totals['steps']//days_with_data:>10,}     │
│ 🔥 Calories         │ {totals['calories']:>10,.0f}     │ {totals['calories']/days_with_data:>10,.0f}     │
│ ⚡ Active Calories  │ {totals['active_cal']:>10,.0f}     │ {totals['active_cal']/days_with_data:>10,.0f}     │
│ 📏 Distance         │ {totals['distance']:>8.1f} km    │ {totals['distance']/days_with_data:>8.1f} km    │
│ 💪 Moderate Mins    │ {totals['moderate_mins']:>8} mins  │ {totals['moderate_mins']//days_with_data:>8} mins  │
│ 🏃 Vigorous Mins    │ {totals['vigorous_mins']:>8} mins  │ {totals['vigorous_mins']//days_with_data:>8} mins  │
└─────────────────────┴─────────────────┴─────────────────┘
""")

    # ===== HEART RATE SUMMARY =====
    if resting_hrs:
        avg_rhr = sum(resting_hrs) / len(resting_hrs)
        min_rhr = min(resting_hrs)
        max_rhr = max(resting_hrs)
        print(f"❤️ Resting Heart Rate: Avg {avg_rhr:.0f} bpm (Range: {min_rhr}-{max_rhr} bpm)")

    # ===== SUGGESTIONS =====
    print("\n" + "=" * 90)
    print("💡 SUGGESTIONS FOR NEXT WEEK")
    print("=" * 90)

    suggestions = []

    # Sleep suggestions
    if counts['sleep'] == 0:
        suggestions.append("😴 SLEEP: No sleep data recorded. Sync your watch to track sleep quality.")
    elif totals['sleep'] / counts['sleep'] < 7:
        suggestions.append(f"😴 SLEEP: Avg {totals['sleep']/counts['sleep']:.1f} hrs is below 7-8 hrs recommended for athletes. More sleep = better recovery & reaction time.")
    elif totals['sleep'] / counts['sleep'] >= 8:
        suggestions.append(f"😴 SLEEP: Excellent! {totals['sleep']/counts['sleep']:.1f} hrs average. Keep it up!")
    else:
        suggestions.append(f"😴 SLEEP: {totals['sleep']/counts['sleep']:.1f} hrs average is good. Aim for 8+ hrs for optimal tennis performance.")

    # Steps suggestions
    avg_steps = totals['steps'] // days_with_data if days_with_data > 0 else 0
    if avg_steps < 5000:
        suggestions.append(f"👣 STEPS: {avg_steps:,}/day is low. Aim for 7,000-10,000 steps for baseline fitness.")
    elif avg_steps < 8000:
        suggestions.append(f"👣 STEPS: {avg_steps:,}/day is moderate. Push toward 10,000 for better endurance.")
    else:
        suggestions.append(f"👣 STEPS: Great! {avg_steps:,}/day shows good daily activity.")

    # Intensity suggestions
    total_intensity = totals['moderate_mins'] + totals['vigorous_mins']
    vigorous_ratio = totals['vigorous_mins'] / total_intensity * 100 if total_intensity > 0 else 0

    if total_intensity < 150:
        suggestions.append(f"💪 INTENSITY: {total_intensity} mins/week is below WHO target (150 mins). Increase training frequency.")
    else:
        suggestions.append(f"💪 INTENSITY: {total_intensity} mins/week meets WHO guidelines. Great job!")

    if totals['vigorous_mins'] < 30:
        suggestions.append(f"🏃 VIGOROUS: Only {totals['vigorous_mins']} mins. Tennis needs explosive power - add sprints, HIIT, or match play.")
    elif vigorous_ratio < 30:
        suggestions.append(f"🏃 VIGOROUS: {vigorous_ratio:.0f}% of training is high-intensity. For tennis, aim for 30-40% vigorous work.")
    else:
        suggestions.append(f"🏃 VIGOROUS: Good balance! {vigorous_ratio:.0f}% high-intensity training suits tennis demands.")

    # Heart rate suggestions
    if resting_hrs:
        if avg_rhr > 70:
            suggestions.append(f"❤️ RESTING HR: {avg_rhr:.0f} bpm - room to improve. More cardio training will lower this over time.")
        elif avg_rhr < 60:
            suggestions.append(f"❤️ RESTING HR: Excellent {avg_rhr:.0f} bpm indicates strong cardiovascular fitness!")
        else:
            suggestions.append(f"❤️ RESTING HR: {avg_rhr:.0f} bpm is good. Consistent training will improve further.")

    # Distance suggestion
    avg_distance = totals['distance'] / days_with_data if days_with_data > 0 else 0
    if avg_distance < 3:
        suggestions.append(f"📏 DISTANCE: {avg_distance:.1f} km/day is low. Try adding a 20-30 min walk or jog daily.")

    # Print all suggestions
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion}")

    # Weekly targets
    print("\n" + "─" * 90)
    print("🎯 NEXT WEEK TARGETS (10% progression)")
    print("─" * 90)
    target_steps = max(7000, int(avg_steps * 1.1))
    target_moderate = max(20, int(totals['moderate_mins'] * 1.1 / 7))
    target_vigorous = max(10, int(totals['vigorous_mins'] * 1.1 / 7))
    target_distance = max(3.0, round(avg_distance * 1.1, 1))

    print(f"""
   • Daily Steps:     {target_steps:,}/day
   • Daily Distance:  {target_distance} km/day
   • Daily Moderate:  {target_moderate} mins/day
   • Daily Vigorous:  {target_vigorous} mins/day
   • Sleep Goal:      8 hours/night
""")

    print("=" * 90)
    print("✅ Weekly report complete!")
    print("=" * 90)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
