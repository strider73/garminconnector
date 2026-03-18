#!/usr/bin/env python3
"""
Trainer Weekly Report - Quick 5-min read before session
Combines weekly activity + heart rate/recovery + training load
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from garminconnect import Garmin
import garth
from datetime import date, timedelta, datetime
from config import email, password
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

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
        'moderate_mins': 0, 'vigorous_mins': 0,
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
            'steps': None, 'calories': None, 'active_cal': None
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
                row['moderate_mins'] = safe_get(stats, 'moderateIntensityMinutes')
                row['vigorous_mins'] = safe_get(stats, 'vigorousIntensityMinutes')

                if row['steps']:
                    totals['steps'] += row['steps']
                    has_data = True
                if row['calories']:
                    totals['calories'] += row['calories']
                if row['active_cal']:
                    totals['active_cal'] += row['active_cal']
                if row['moderate_mins']:
                    totals['moderate_mins'] += row['moderate_mins']
                if row['vigorous_mins']:
                    totals['vigorous_mins'] += row['vigorous_mins']
        except:
            pass

        if has_data:
            counts['days_with_data'] += 1

        all_data.append(row)

    # ===== FETCH ACTIVITIES =====
    print("\n  Fetching activities...")
    activities_by_day = {}  # date_str -> list of activity dicts
    for day in days:
        day_str = day.isoformat()
        try:
            day_activities = garmin.get_activities_by_date(day_str, day_str)
            if day_activities:
                activities_by_day[day_str] = day_activities
        except:
            pass

    # ===== TABLE 1: ACTIVITIES =====
    print("\n" + "-" * 115)
    print("  ACTIVITIES")
    print("-" * 115)
    print(f"{'Date':<10} | {'Activity':<25} | {'Type':<15} | {'Duration':>8} | {'Cal':>6} | {'Avg HR':>6} | {'Max HR':>6}")
    print("-" * 115)

    for i, day in enumerate(days):
        day_str = day.isoformat()
        day_name = day.strftime('%a %m/%d')
        day_acts = activities_by_day.get(day_str, [])
        if day_acts:
            for j, act in enumerate(day_acts):
                name = act.get('activityName', 'Unnamed')[:25]
                atype = act.get('activityType', {}).get('typeKey', '-')[:15]
                dur = act.get('duration', 0) / 60
                cal = act.get('calories', 0)
                avg_hr = act.get('averageHR', 0)
                max_hr = act.get('maxHR', 0)
                date_col = day_name if j == 0 else ''
                print(f"{date_col:<10} | {name:<25} | {atype:<15} | {dur:>6.0f}m | {cal:>5} | {avg_hr:>6} | {max_hr:>6}")
        else:
            print(f"{day_name:<10} | {'Rest day':<25} | {'-':<15} | {'-':>8} | {'-':>6} | {'-':>6} | {'-':>6}")

    print("-" * 115)

    # ===== 2-WEEK AVERAGES (from Garmin API, prior 2 weeks) =====
    print("\n  Loading 2-week averages...")
    avg_2w = {}
    try:
        hist_days = [(today - timedelta(days=i)) for i in range(21, 7, -1)]  # day 21..8
        hist_acc = {'steps': [], 'calories': [], 'active_cal': [],
                    'resting_hr': [], 'max_hr': [], 'hrv': [], 'intensity_mins': []}
        for hday in hist_days:
            hday_str = hday.isoformat()
            try:
                hstats = garmin.get_stats(hday_str)
                if hstats:
                    s = safe_get(hstats, 'totalSteps')
                    if s and s > 0:
                        hist_acc['steps'].append(s)
                        c = safe_get(hstats, 'totalKilocalories')
                        if c: hist_acc['calories'].append(c)
                        ac = safe_get(hstats, 'activeKilocalories')
                        if ac: hist_acc['active_cal'].append(ac)
                        mod = safe_get(hstats, 'moderateIntensityMinutes', 0)
                        vig = safe_get(hstats, 'vigorousIntensityMinutes', 0)
                        hist_acc['intensity_mins'].append(mod + vig)
            except:
                pass
            try:
                hhr = garmin.get_heart_rates(hday_str)
                if hhr:
                    rhr = safe_get(hhr, 'restingHeartRate')
                    if rhr: hist_acc['resting_hr'].append(rhr)
                    mhr = safe_get(hhr, 'maxHeartRate')
                    if mhr: hist_acc['max_hr'].append(mhr)
            except:
                pass
            try:
                hhrv = garmin.get_hrv_data(hday_str)
                if hhrv:
                    hs = hhrv.get('hrvSummary', {})
                    if hs:
                        v = safe_get(hs, 'lastNightAvg')
                        if v: hist_acc['hrv'].append(v)
            except:
                pass

        for key in hist_acc:
            vals = hist_acc[key]
            if vals:
                avg_2w[key] = sum(vals) / len(vals)
        if avg_2w:
            print(f"  2-week avg loaded (steps: {avg_2w.get('steps',0):,.0f}, active cal: {avg_2w.get('active_cal',0):,.0f}, HRV: {avg_2w.get('hrv',0):.0f}ms)")
    except Exception as e:
        print(f"  Warning: Could not load 2-week averages: {e}")

    # ===== GENERATE PDF REPORT =====
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chart_dir = os.path.join(project_root, 'reports')
    os.makedirs(chart_dir, exist_ok=True)

    def val_or_zero(row, key):
        v = row.get(key)
        return int(v) if v else 0

    # Compute summary values
    avg_sleep = totals['sleep'] / max(counts['sleep'], 1)
    avg_rhr = sum(resting_hrs) / len(resting_hrs) if resting_hrs else 0
    avg_hrv = sum(hrvs) / len(hrvs) if hrvs else 0
    total_intensity = totals['moderate_mins'] + totals['vigorous_mins']
    # Only count days with meaningful active cal (>0) to avoid incomplete days dragging avg down
    days_with_active_cal = sum(1 for r in all_data if val_or_zero(r, 'active_cal') > 0)
    avg_act_cal = totals['active_cal'] / max(days_with_active_cal, 1)

    # --- Yearly goal calc (30% increase for both cal and steps) ---
    BASELINE_ACT_CAL = 1414
    BASELINE_STEPS = 12943
    TARGET_ACT_CAL = round(BASELINE_ACT_CAL * 1.30)
    TARGET_STEPS = round(BASELINE_STEPS * 1.30)
    weeks_in_year = 52
    cal_weekly_inc = (TARGET_ACT_CAL - BASELINE_ACT_CAL) / weeks_in_year
    steps_weekly_inc = (TARGET_STEPS - BASELINE_STEPS) / weeks_in_year
    # Weeks since baseline (Mar 2026)
    baseline_date = date(2026, 3, 1)
    weeks_elapsed = max((today - baseline_date).days / 7, 0)
    expected_cal_now = BASELINE_ACT_CAL + (cal_weekly_inc * weeks_elapsed)
    expected_steps_now = BASELINE_STEPS + (steps_weekly_inc * weeks_elapsed)
    # Steps avg (only days with data)
    days_with_steps = sum(1 for r in all_data if val_or_zero(r, 'steps') > 0)
    avg_steps = totals['steps'] / max(days_with_steps, 1)
    pct_cal = max(0, ((avg_act_cal - BASELINE_ACT_CAL) / (TARGET_ACT_CAL - BASELINE_ACT_CAL)) * 100) if TARGET_ACT_CAL != BASELINE_ACT_CAL else 0
    pct_steps = max(0, ((avg_steps - BASELINE_STEPS) / (TARGET_STEPS - BASELINE_STEPS)) * 100) if TARGET_STEPS != BASELINE_STEPS else 0

    pdf_path = os.path.join(chart_dir, f'trainer_report_{today.isoformat()}.pdf')

    next_week_cal_target = round(avg_act_cal * 1.007)
    next_week_steps_target = round(avg_steps * 1.007)

    with PdfPages(pdf_path) as pdf:

        # ==================== SINGLE A4 PAGE ====================
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
        fig.patch.set_facecolor('white')

        # --- HEADER ---
        fig.text(0.50, 0.975, f'WEEKLY TRAINER REPORT — {full_name}',
                 ha='center', fontsize=19, fontweight='bold')
        fig.text(0.50, 0.955, f'{days[0].strftime("%b %d")} to {days[-1].strftime("%b %d, %Y")}',
                 ha='center', fontsize=13, color='#444')

        # --- SECTION 1: ACTIVITIES TIMELINE (visual weekly schedule) ---
        from matplotlib.patches import FancyBboxPatch
        # Color map for activity types
        act_colors = {
            'tennis': '#2070C0', 'tennis_v2': '#2070C0',
            'running': '#D04020',
            'cycling': '#2E7D32',
            'strength_training': '#D08800', 'gym': '#D08800',
            'walking': '#6A9E3A', 'hiking': '#6A9E3A',
            'swimming': '#00A0C0',
        }
        default_act_color = '#888888'

        ax_timeline = fig.add_axes([0.10, 0.72, 0.85, 0.21])
        ax_timeline.set_title('ACTIVITIES', fontsize=13, fontweight='bold', loc='left', pad=8)

        # Y-axis: days (top to bottom)
        day_positions = list(range(len(days)))
        ax_timeline.set_yticks(day_positions)
        ax_timeline.set_yticklabels([d.strftime('%a') for d in days], fontsize=9, fontweight='bold')
        ax_timeline.set_ylim(len(days) - 0.5, -0.5)

        # X-axis: hours 7am to 11pm
        ax_timeline.set_xlim(7, 23)
        ax_timeline.set_xticks(range(7, 24, 2))
        ax_timeline.set_xticklabels([f'{h%12 or 12}{"am" if h < 12 else "pm"}' for h in range(7, 24, 2)], fontsize=7.5)
        ax_timeline.grid(axis='x', alpha=0.15, linestyle='-')
        ax_timeline.grid(axis='y', alpha=0.1, linestyle='-')
        ax_timeline.spines['top'].set_visible(False)
        ax_timeline.spines['right'].set_visible(False)

        total_activities = 0
        total_act_duration = 0
        total_act_cal = 0
        hardest_day = None
        hardest_cal = 0

        for i, day in enumerate(days):
            day_str = day.isoformat()
            day_acts = activities_by_day.get(day_str, [])
            day_cal = 0
            if day_acts:
                for act in day_acts:
                    start_str = act.get('startTimeLocal', '')
                    dur_sec = act.get('duration', 0)
                    dur_hrs = dur_sec / 3600
                    atype = act.get('activityType', {}).get('typeKey', '')
                    name = act.get('activityName', atype.replace('_', ' ').title())
                    cal = act.get('calories', 0) or 0
                    total_activities += 1
                    total_act_duration += dur_sec / 60
                    total_act_cal += cal
                    day_cal += cal

                    # Parse start hour
                    try:
                        start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                        start_hour = start_dt.hour + start_dt.minute / 60
                    except:
                        start_hour = 12
                    if start_hour < 7:
                        start_hour = 7

                    color = act_colors.get(atype.lower(), default_act_color)
                    bar_width = max(dur_hrs, 0.4)

                    rect = FancyBboxPatch((start_hour, i - 0.32), bar_width, 0.64,
                                          boxstyle="round,pad=0.05", facecolor=color,
                                          edgecolor='white', linewidth=1.5, alpha=0.85)
                    ax_timeline.add_patch(rect)

                    # Label: always to the right of the block
                    dur_min = int(dur_sec / 60)
                    label_text = f'{name} ({dur_min}m)'
                    ax_timeline.text(start_hour + bar_width + 0.15, i, label_text,
                                     ha='left', va='center', fontsize=7, fontweight='bold', color='#222')

                if day_cal > hardest_cal:
                    hardest_cal = day_cal
                    hardest_day = day
            else:
                ax_timeline.text(15, i, 'Rest day', ha='center', va='center',
                                 fontsize=8, color='#BBB', style='italic')

        # AI briefing under activity timeline
        avg_dur = total_act_duration / max(total_activities, 1)
        tennis_count = sum(1 for d in activities_by_day.values() for a in d if 'tennis' in a.get('activityType', {}).get('typeKey', '').lower())
        rest_days = sum(1 for d in days if d.isoformat() not in activities_by_day)
        hardest_label = hardest_day.strftime('%a %m/%d') if hardest_day else '-'
        consecutive_days = 0
        max_consecutive = 0
        for d in days:
            if d.isoformat() in activities_by_day:
                consecutive_days += 1
                max_consecutive = max(max_consecutive, consecutive_days)
            else:
                consecutive_days = 0

        # Consistent left margin (aligned with chart left edge)
        L = 0.10

        # Activity AI briefing
        brief_y = 0.690
        fig.text(L, brief_y,
                 f'{total_activities} sessions ({tennis_count} tennis, {total_activities - tennis_count} other) | '
                 f'{total_act_duration:.0f} min total | {total_act_cal:,} cal burned',
                 fontsize=8.5, color='#333', style='italic')
        fig.text(L, brief_y - 0.015,
                 f'Hardest day: {hardest_label} ({hardest_cal:,} cal) | Avg session: {avg_dur:.0f} min | '
                 f'Consecutive training days: {max_consecutive}',
                 fontsize=8.5, color='#333', style='italic')
        fig.text(L, brief_y - 0.030,
                 f'Rest days: {rest_days}/7 — {"good recovery balance" if rest_days >= 2 else "consider adding a rest day" if rest_days == 1 else "no rest days — high injury risk"}',
                 fontsize=8.5, color='#CC0000' if rest_days == 0 else '#333', style='italic')

        # --- SECTION 2: SLEEP & RECOVERY TABLE ---
        sleep_y = 0.61
        fig.text(L, sleep_y, 'SLEEP & RECOVERY', fontsize=13, fontweight='bold', color='#000')

        sleep_headers = ['Day', 'Bed', 'Wake', 'Hrs', 'Deep', 'REM', 'HRV', 'RHR']
        sleep_col_x = [L, L+0.08, L+0.19, L+0.30, L+0.38, L+0.47, L+0.56, L+0.65]
        sleep_y -= 0.025
        for j, h in enumerate(sleep_headers):
            fig.text(sleep_col_x[j], sleep_y, h, fontsize=9.5, fontweight='bold', color='#333')

        for i, row in enumerate(all_data):
            sleep_y -= 0.025
            bed = row['sleep_start'].replace(' ', '') if row['sleep_start'] else "-"
            wake = row['sleep_end'].replace(' ', '') if row['sleep_end'] else "-"
            hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
            deep = f"{row['deep_mins']}m" if row['deep_mins'] else "-"
            rem = f"{row['rem_mins']}m" if row['rem_mins'] else "-"
            hrv = str(row['hrv']) if row['hrv'] else "-"
            rhr = str(row['resting_hr']) if row['resting_hr'] else "-"
            vals = [days[i].strftime('%a'), bed, wake, hrs, deep, rem, hrv, rhr]
            for j, v in enumerate(vals):
                c = '#CC0000' if j == 3 and row['sleep_hours'] and row['sleep_hours'] < 5 else '#111'
                fig.text(sleep_col_x[j], sleep_y, str(v), fontsize=9, color=c, family='monospace', fontweight='medium')

        # Sleep AI briefing
        sleep_y -= 0.024
        nights_below_6 = sum(1 for r in all_data if r['sleep_hours'] and r['sleep_hours'] < 6)
        nights_above_7 = sum(1 for r in all_data if r['sleep_hours'] and r['sleep_hours'] >= 7)
        avg_deep = totals['deep'] / max(counts['sleep'], 1)
        avg_rem = totals['rem'] / max(counts['sleep'], 1)
        fig.text(L, sleep_y,
                 f'Avg {avg_sleep:.1f}h/night (target 7.5h) | Deep {avg_deep:.0f}m | REM {avg_rem:.0f}m avg/night',
                 fontsize=8.5, color='#333', style='italic')
        fig.text(L, sleep_y - 0.015,
                 f'{nights_above_7}/{counts["sleep"]} nights above 7h | {nights_below_6} nights below 6h | '
                 f'HRV avg {avg_hrv:.0f}ms | RHR avg {avg_rhr:.0f}bpm',
                 fontsize=8.5, color='#333', style='italic')
        sleep_status = 'sleep debt accumulating — prioritize earlier bedtimes' if avg_sleep < 7 else 'sleep on track'
        fig.text(L, sleep_y - 0.030,
                 sleep_status,
                 fontsize=8.5, color='#CC0000' if avg_sleep < 7 else '#333', style='italic')
        sleep_y -= 0.030

        # --- SECTION 3: NEXT WEEK / YEARLY GOAL (bottom band) ---
        plan_y = sleep_y - 0.045
        fig.text(L, plan_y, 'NEXT WEEK PLAN', fontsize=12, fontweight='bold', color='#000')

        plan_y -= 0.025
        fig.text(L, plan_y, f'Cal target: {next_week_cal_target:,}/day  |  Steps target: {next_week_steps_target:,}/day  |  Sleep: above 6.5h',
                 fontsize=9.5, color='#111')

        # Yearly goal strip — Active Cal
        plan_y -= 0.035
        cal_progress = min(max(pct_cal / 100, 0), 1)
        cal_bar = "█" * int(cal_progress * 15) + "░" * (15 - int(cal_progress * 15))
        cal_status = "on track" if avg_act_cal >= expected_cal_now else "below"
        cal_color = '#2E7D32' if avg_act_cal >= expected_cal_now else '#CC0000'

        fig.text(L, plan_y, '2026 GOAL (+30%)', fontsize=10, fontweight='bold', color='#222')
        plan_y -= 0.018
        fig.text(L + 0.02, plan_y,
                 f'Cal:   [{cal_bar}] {pct_cal:.0f}%   now {avg_act_cal:,.0f} / target {TARGET_ACT_CAL:,}  — {cal_status}',
                 fontsize=8.5, family='monospace', fontweight='bold', color=cal_color)

        # Steps
        steps_progress = min(max(pct_steps / 100, 0), 1)
        steps_bar = "█" * int(steps_progress * 15) + "░" * (15 - int(steps_progress * 15))
        steps_status = "on track" if avg_steps >= expected_steps_now else "below"
        steps_color = '#2E7D32' if avg_steps >= expected_steps_now else '#CC0000'

        plan_y -= 0.018
        fig.text(L + 0.02, plan_y,
                 f'Steps: [{steps_bar}] {pct_steps:.0f}%   now {avg_steps:,.0f} / target {TARGET_STEPS:,}  — {steps_status}',
                 fontsize=8.5, family='monospace', fontweight='bold', color=steps_color)

        # Footer
        fig.text(0.50, 0.010, f'Generated {today.strftime("%b %d, %Y")}  |  Garmin Connect  |  Baseline: {BASELINE_ACT_CAL:,} cal, {BASELINE_STEPS:,} steps',
                 ha='center', fontsize=8, color='#777')

        pdf.savefig(fig)
        plt.close()

    print(f"\n  [PDF] Report saved: {pdf_path}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
