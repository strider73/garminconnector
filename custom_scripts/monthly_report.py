#!/usr/bin/env python3
"""
Monthly Report - Last 4 Weeks Summary
Shows weekly breakdown with trends and progress
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

    # Calculate 4 weeks (28 days)
    weeks = []
    for week_num in range(4, 0, -1):  # Week 4 (oldest) to Week 1 (most recent)
        week_end = today - timedelta(days=(week_num - 1) * 7)
        week_start = week_end - timedelta(days=6)
        weeks.append({
            'num': 5 - week_num,  # 1, 2, 3, 4
            'start': week_start,
            'end': week_end,
            'days': [(week_start + timedelta(days=i)) for i in range(7)]
        })

    print("=" * 95)
    print(f"📊 4-WEEK MONTHLY REPORT - {full_name}")
    print(f"   {weeks[0]['start'].strftime('%Y-%m-%d')} to {weeks[3]['end'].strftime('%Y-%m-%d')}")
    print("=" * 95)

    # Process each week
    weekly_data = []

    for week in weeks:
        week_totals = {
            'sleep': 0, 'sleep_count': 0,
            'steps': 0, 'calories': 0, 'active_cal': 0, 'distance': 0,
            'moderate_mins': 0, 'vigorous_mins': 0,
            'resting_hrs': [], 'days_with_data': 0
        }

        for day in week['days']:
            day_str = day.isoformat()
            has_data = False

            # Sleep
            try:
                sleep_data = garmin.get_sleep_data(day_str)
                if sleep_data:
                    daily_sleep = sleep_data.get('dailySleepDTO', {})
                    if daily_sleep:
                        sleep_sec = safe_get(daily_sleep, 'sleepTimeSeconds', 0)
                        if sleep_sec and sleep_sec > 0:
                            week_totals['sleep'] += sleep_sec / 3600
                            week_totals['sleep_count'] += 1
            except:
                pass

            # Heart Rate
            try:
                hr_data = garmin.get_heart_rates(day_str)
                if hr_data:
                    rhr = safe_get(hr_data, 'restingHeartRate')
                    if rhr:
                        week_totals['resting_hrs'].append(rhr)
            except:
                pass

            # Stats
            try:
                stats = garmin.get_stats(day_str)
                if stats:
                    steps = safe_get(stats, 'totalSteps')
                    if steps:
                        week_totals['steps'] += steps
                        has_data = True

                    cal = safe_get(stats, 'totalKilocalories')
                    if cal:
                        week_totals['calories'] += cal

                    active = safe_get(stats, 'activeKilocalories')
                    if active:
                        week_totals['active_cal'] += active

                    dist = safe_get(stats, 'totalDistanceMeters')
                    if dist:
                        week_totals['distance'] += dist / 1000

                    mod = safe_get(stats, 'moderateIntensityMinutes')
                    if mod:
                        week_totals['moderate_mins'] += mod

                    vig = safe_get(stats, 'vigorousIntensityMinutes')
                    if vig:
                        week_totals['vigorous_mins'] += vig
            except:
                pass

            if has_data:
                week_totals['days_with_data'] += 1

        # Calculate averages
        days_count = max(week_totals['days_with_data'], 1)
        sleep_count = max(week_totals['sleep_count'], 1)

        weekly_data.append({
            'week_num': week['num'],
            'date_range': f"{week['start'].strftime('%m/%d')}-{week['end'].strftime('%m/%d')}",
            'sleep_avg': round(week_totals['sleep'] / sleep_count, 1) if week_totals['sleep_count'] > 0 else 0,
            'sleep_total': round(week_totals['sleep'], 1),
            'rhr_avg': round(sum(week_totals['resting_hrs']) / len(week_totals['resting_hrs'])) if week_totals['resting_hrs'] else 0,
            'steps_total': week_totals['steps'],
            'steps_avg': week_totals['steps'] // days_count,
            'calories_total': int(week_totals['calories']),
            'calories_avg': int(week_totals['calories'] / days_count),
            'active_cal': int(week_totals['active_cal']),
            'distance_total': round(week_totals['distance'], 1),
            'distance_avg': round(week_totals['distance'] / days_count, 1),
            'moderate_mins': week_totals['moderate_mins'],
            'vigorous_mins': week_totals['vigorous_mins'],
            'intensity_total': week_totals['moderate_mins'] + week_totals['vigorous_mins'],
            'days_with_data': week_totals['days_with_data']
        })

        print(f"   Week {week['num']} processed...")

    # ===== WEEKLY COMPARISON TABLE =====
    print("\n" + "─" * 95)
    print("📅 WEEKLY BREAKDOWN")
    print("─" * 95)
    print(f"{'Week':<12} │ {'Sleep':^10} │ {'Resting':^8} │ {'Steps':^12} │ {'Calories':^10} │ {'Distance':^10} │ {'Intensity':^12}")
    print(f"{'':12} │ {'(avg hrs)':^10} │ {'HR':^8} │ {'(total)':^12} │ {'(total)':^10} │ {'(total)':^10} │ {'Mod + Vig':^12}")
    print("─" * 95)

    for w in weekly_data:
        sleep = f"{w['sleep_avg']:.1f}" if w['sleep_avg'] > 0 else "-"
        rhr = str(w['rhr_avg']) if w['rhr_avg'] > 0 else "-"
        steps = f"{w['steps_total']:,}" if w['steps_total'] > 0 else "-"
        cal = f"{w['calories_total']:,}" if w['calories_total'] > 0 else "-"
        dist = f"{w['distance_total']:.1f}km" if w['distance_total'] > 0 else "-"
        intensity = f"{w['moderate_mins']}+{w['vigorous_mins']}m"

        print(f"Wk{w['week_num']} {w['date_range']:<7} │ {sleep:^10} │ {rhr:^8} │ {steps:>12} │ {cal:>10} │ {dist:>10} │ {intensity:^12}")

    print("─" * 95)

    # ===== TREND ANALYSIS =====
    print("\n" + "=" * 95)
    print("📈 4-WEEK TRENDS")
    print("=" * 95)

    # Calculate trends (compare week 4 to week 1)
    if len(weekly_data) >= 2:
        w1 = weekly_data[0]  # Oldest week
        w4 = weekly_data[3]  # Most recent week

        def trend_arrow(old, new):
            if old == 0 or new == 0:
                return "─"
            diff = ((new - old) / old) * 100
            if diff > 5:
                return f"↑ +{diff:.0f}%"
            elif diff < -5:
                return f"↓ {diff:.0f}%"
            else:
                return f"→ {diff:.0f}%"

        print(f"""
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│      Metric         │    Week 1    │    Week 4    │    Trend     │
│                     │   (oldest)   │   (latest)   │              │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ 😴 Sleep (avg hrs)  │ {w1['sleep_avg']:>10.1f}   │ {w4['sleep_avg']:>10.1f}   │ {trend_arrow(w1['sleep_avg'], w4['sleep_avg']):^12} │
│ ❤️ Resting HR       │ {w1['rhr_avg']:>10}   │ {w4['rhr_avg']:>10}   │ {trend_arrow(w1['rhr_avg'], w4['rhr_avg']):^12} │
│ 👣 Steps (total)    │ {w1['steps_total']:>10,}   │ {w4['steps_total']:>10,}   │ {trend_arrow(w1['steps_total'], w4['steps_total']):^12} │
│ 🔥 Calories         │ {w1['calories_total']:>10,}   │ {w4['calories_total']:>10,}   │ {trend_arrow(w1['calories_total'], w4['calories_total']):^12} │
│ 📏 Distance (km)    │ {w1['distance_total']:>10.1f}   │ {w4['distance_total']:>10.1f}   │ {trend_arrow(w1['distance_total'], w4['distance_total']):^12} │
│ 💪 Intensity (mins) │ {w1['intensity_total']:>10}   │ {w4['intensity_total']:>10}   │ {trend_arrow(w1['intensity_total'], w4['intensity_total']):^12} │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
""")

    # ===== 4-WEEK TOTALS =====
    print("=" * 95)
    print("📊 4-WEEK TOTALS")
    print("=" * 95)

    total_sleep = sum(w['sleep_total'] for w in weekly_data)
    total_steps = sum(w['steps_total'] for w in weekly_data)
    total_calories = sum(w['calories_total'] for w in weekly_data)
    total_distance = sum(w['distance_total'] for w in weekly_data)
    total_moderate = sum(w['moderate_mins'] for w in weekly_data)
    total_vigorous = sum(w['vigorous_mins'] for w in weekly_data)
    total_intensity = total_moderate + total_vigorous

    print(f"""
   😴 Total Sleep:      {total_sleep:.1f} hours
   👣 Total Steps:      {total_steps:,}
   🔥 Total Calories:   {total_calories:,} kcal
   📏 Total Distance:   {total_distance:.1f} km
   💪 Total Intensity:  {total_intensity} mins ({total_moderate}m moderate + {total_vigorous}m vigorous)
""")

    # ===== SUGGESTIONS =====
    print("=" * 95)
    print("💡 MONTHLY INSIGHTS & SUGGESTIONS")
    print("=" * 95)

    suggestions = []

    # Sleep trend
    if weekly_data[3]['sleep_avg'] == 0:
        suggestions.append("😴 No recent sleep data. Sync your watch to track recovery!")
    elif weekly_data[3]['sleep_avg'] < weekly_data[0]['sleep_avg'] and weekly_data[0]['sleep_avg'] > 0:
        suggestions.append(f"😴 Sleep declining: {weekly_data[0]['sleep_avg']:.1f}h → {weekly_data[3]['sleep_avg']:.1f}h. Prioritize rest for performance.")
    elif weekly_data[3]['sleep_avg'] >= 8:
        suggestions.append(f"😴 Excellent sleep! {weekly_data[3]['sleep_avg']:.1f}h average supports peak athletic performance.")

    # Steps trend
    if weekly_data[3]['steps_total'] > weekly_data[0]['steps_total'] * 1.1:
        suggestions.append(f"👣 Great progress! Steps increased from Week 1 to Week 4.")
    elif weekly_data[3]['steps_total'] < weekly_data[0]['steps_total'] * 0.9:
        suggestions.append(f"👣 Steps decreased. Try to maintain consistent daily activity.")

    # Intensity
    avg_weekly_intensity = total_intensity / 4
    if avg_weekly_intensity < 150:
        suggestions.append(f"💪 Avg {avg_weekly_intensity:.0f} mins/week intensity. WHO recommends 150+ mins for health benefits.")
    else:
        suggestions.append(f"💪 Avg {avg_weekly_intensity:.0f} mins/week exceeds WHO guidelines. Great training volume!")

    # Vigorous for tennis
    vigorous_ratio = (total_vigorous / total_intensity * 100) if total_intensity > 0 else 0
    if vigorous_ratio < 25:
        suggestions.append(f"🎾 Only {vigorous_ratio:.0f}% vigorous training. Tennis demands more high-intensity work (sprints, HIIT).")
    else:
        suggestions.append(f"🎾 {vigorous_ratio:.0f}% vigorous training - good balance for tennis performance.")

    # Heart rate trend
    rhr_trend = [w['rhr_avg'] for w in weekly_data if w['rhr_avg'] > 0]
    if len(rhr_trend) >= 2:
        if rhr_trend[-1] < rhr_trend[0]:
            suggestions.append(f"❤️ Resting HR improving: {rhr_trend[0]} → {rhr_trend[-1]} bpm. Fitness is building!")
        elif rhr_trend[-1] > rhr_trend[0] + 5:
            suggestions.append(f"❤️ Resting HR elevated. Could indicate fatigue, stress, or need for recovery.")

    for i, s in enumerate(suggestions, 1):
        print(f"\n{i}. {s}")

    # ===== NEXT MONTH GOALS =====
    print("\n" + "─" * 95)
    print("🎯 NEXT MONTH GOALS")
    print("─" * 95)

    avg_weekly_steps = total_steps // 4
    avg_weekly_distance = total_distance / 4

    print(f"""
   Target Weekly Steps:     {max(35000, int(avg_weekly_steps * 1.1)):,} (current avg: {avg_weekly_steps:,})
   Target Weekly Distance:  {max(20, round(avg_weekly_distance * 1.1, 1))} km (current avg: {avg_weekly_distance:.1f} km)
   Target Weekly Intensity: {max(150, int(avg_weekly_intensity * 1.1))} mins (current avg: {avg_weekly_intensity:.0f})
   Target Sleep:            8+ hours/night
   Target Vigorous Ratio:   30%+ of total intensity
""")

    print("=" * 95)
    print("✅ 4-week monthly report complete!")
    print("=" * 95)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
