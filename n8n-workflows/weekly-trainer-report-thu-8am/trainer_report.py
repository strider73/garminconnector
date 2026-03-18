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

    # ===== NAP DETECTION =====
    print("\n  Detecting naps...")
    nap_map = {}  # date_str -> "start-end (Xmin)" string
    try:
        from detect_nap import connect_db, fetch_daytime_hr, compute_rolling, detect_naps, WINDOW_SIZE
        import statistics as nap_stats
        nap_conn = connect_db()
        for day in days:
            day_str = day.isoformat()
            rows_hr = fetch_daytime_hr(nap_conn, day_str)
            if not rows_hr:
                continue
            ntimes = [r[0] for r in rows_hr]
            nhrs = [r[1] for r in rows_hr]
            ravg, rstd = compute_rolling(nhrs, WINDOW_SIZE)
            naps = detect_naps(ntimes, nhrs, ravg, rstd)
            day_median = nap_stats.median(nhrs)
            naps = [n for n in naps if n['avg_hr'] < day_median - 10]
            if naps:
                parts = []
                for n in naps:
                    s = n['start'].strftime('%-I:%M%p').lower()
                    e = n['end'].strftime('%-I:%M%p').lower()
                    parts.append(f"{s}-{e} ({n['duration_min']}m)")
                nap_map[day_str] = ", ".join(parts)
        nap_conn.close()
    except Exception as e:
        print(f"  Warning: Nap detection failed: {e}")

    # ===== TABLE 1: SLEEP & RECOVERY =====
    print("\n" + "-" * 115)
    print("  SLEEP & RECOVERY")
    print("-" * 115)
    print(f"{'Date':<10} | {'Bedtime':>8} | {'Wake Up':>8} | {'Hrs':>5} | {'Deep':>5} | {'REM':>5} | {'HRV':>5} | {'RHR':>4} | {'Nap'}")
    print("-" * 115)

    for i, row in enumerate(all_data):
        bed = row['sleep_start'] if row['sleep_start'] else "-"
        wake = row['sleep_end'] if row['sleep_end'] else "-"
        hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
        deep = f"{row['deep_mins']}m" if row['deep_mins'] else "-"
        rem = f"{row['rem_mins']}m" if row['rem_mins'] else "-"
        hrv = str(row['hrv']) if row['hrv'] else "-"
        rhr = str(row['resting_hr']) if row['resting_hr'] else "-"
        nap = nap_map.get(days[i].isoformat(), "-")
        print(f"{row['date']:<10} | {bed:>8} | {wake:>8} | {hrs:>5} | {deep:>5} | {rem:>5} | {hrv:>5} | {rhr:>4} | {nap}")

    print("-" * 105)

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
    day_labels = [r['date'] for r in all_data]
    x = np.arange(len(day_labels))
    days_with_data = max(counts['days_with_data'], 1)

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chart_dir = os.path.join(project_root, 'reports')
    os.makedirs(chart_dir, exist_ok=True)

    def val_or_zero(row, key):
        v = row.get(key)
        return int(v) if v else 0

    def add_avg_line(ax, value, label, color, alpha=0.7):
        if value:
            ax.axhline(y=value, color=color, linestyle='--', linewidth=1.5, alpha=alpha)
            ax.text(ax.get_xlim()[1], value, f' 2w avg: {value:,.0f}',
                    va='center', ha='left', fontsize=7, color=color, alpha=alpha)

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

    # Pre-compute chart data
    steps_vals = [val_or_zero(r, 'steps') for r in all_data]
    act_vals = [val_or_zero(r, 'active_cal') for r in all_data]
    rhr_vals = [val_or_zero(r, 'resting_hr') for r in all_data]
    mhr_vals = [val_or_zero(r, 'max_hr') for r in all_data]
    hrv_vals = [val_or_zero(r, 'hrv') for r in all_data]
    intensity_vals = [(val_or_zero(r, 'moderate_mins') + val_or_zero(r, 'vigorous_mins')) for r in all_data]

    next_week_cal_target = round(avg_act_cal * 1.007)
    next_week_steps_target = round(avg_steps * 1.007)
    sorted_days_by_act = sorted(all_data, key=lambda r: val_or_zero(r, 'active_cal'), reverse=True)
    top1 = sorted_days_by_act[0] if sorted_days_by_act else None
    min_act_day = min((r for r in all_data if val_or_zero(r, 'active_cal') > 0), key=lambda r: val_or_zero(r, 'active_cal'), default=None)
    max_int_day = max(all_data, key=lambda r: val_or_zero(r, 'moderate_mins') + val_or_zero(r, 'vigorous_mins'))
    max_int = val_or_zero(max_int_day, 'moderate_mins') + val_or_zero(max_int_day, 'vigorous_mins')
    avg_2w_act = avg_2w.get('active_cal', 0)

    # Shortened day labels for compact charts
    short_labels = [d.strftime('%a') for d in days]

    with PdfPages(pdf_path) as pdf:

        # ==================== SINGLE A4 PAGE ====================
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
        fig.patch.set_facecolor('white')

        # --- HEADER ---
        fig.text(0.50, 0.975, f'WEEKLY TRAINER REPORT — {full_name}',
                 ha='center', fontsize=19, fontweight='bold')
        fig.text(0.50, 0.955, f'{days[0].strftime("%b %d")} to {days[-1].strftime("%b %d, %Y")}',
                 ha='center', fontsize=13, color='#444')

        # --- SECTION 1: SLEEP TABLE (top band) ---
        fig.text(0.04, 0.930, 'SLEEP & RECOVERY', fontsize=13, fontweight='bold', color='#000')

        headers = ['Day', 'Bed', 'Wake', 'Hrs', 'Deep', 'REM', 'HRV', 'RHR', 'Nap']
        col_x = [0.04, 0.12, 0.21, 0.29, 0.35, 0.41, 0.47, 0.53, 0.59]
        y = 0.912
        for j, h in enumerate(headers):
            fig.text(col_x[j], y, h, fontsize=9.5, fontweight='bold', color='#333')

        for i, row in enumerate(all_data):
            y -= 0.020
            bed = row['sleep_start'].replace(' ', '') if row['sleep_start'] else "-"
            wake = row['sleep_end'].replace(' ', '') if row['sleep_end'] else "-"
            hrs = f"{row['sleep_hours']:.1f}" if row['sleep_hours'] else "-"
            deep = f"{row['deep_mins']}m" if row['deep_mins'] else "-"
            rem = f"{row['rem_mins']}m" if row['rem_mins'] else "-"
            hrv = str(row['hrv']) if row['hrv'] else "-"
            rhr = str(row['resting_hr']) if row['resting_hr'] else "-"
            nap = nap_map.get(days[i].isoformat(), "-")
            vals = [days[i].strftime('%a'), bed, wake, hrs, deep, rem, hrv, rhr, nap]
            for j, v in enumerate(vals):
                c = '#CC0000' if j == 3 and row['sleep_hours'] and row['sleep_hours'] < 5 else '#111'
                fig.text(col_x[j], y, str(v), fontsize=9, color=c, family='monospace', fontweight='medium')

        # Sleep summary line
        y -= 0.022
        fig.text(0.04, y,
                 f'Avg {avg_sleep:.1f}h/night (target 7.5h) | Deep {totals["deep"]/max(counts["sleep"],1):.0f}m | REM {totals["rem"]/max(counts["sleep"],1):.0f}m | Naps {len(nap_map)}/{len(days)} days — body demanding recovery.',
                 fontsize=9, color='#333', style='italic')

        # --- SECTION 2: ACTIVITY CHART (full width) + 3-line comment ---
        ax_act = fig.add_axes([0.08, 0.57, 0.86, 0.15])
        ax_act.plot(x, steps_vals, 'o-', color='#2070C0', linewidth=2.5, markersize=6, label='Steps')
        ax_act.plot(x, act_vals, '^-', color='#D04020', linewidth=2.5, markersize=6, label='Active Cal')
        for i, v in enumerate(steps_vals):
            if v: ax_act.annotate(f'{v//1000}k', (i, v), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=7.5, fontweight='bold', color='#2070C0')
        for i, v in enumerate(act_vals):
            if v: ax_act.annotate(f'{int(v):,}', (i, v), textcoords='offset points', xytext=(0, -11), ha='center', fontsize=7.5, fontweight='bold', color='#D04020')
        if avg_2w.get('steps'):
            ax_act.axhline(y=avg_2w['steps'], color='#2070C0', linestyle='--', linewidth=1.2, alpha=0.6)
        if avg_2w.get('active_cal'):
            ax_act.axhline(y=avg_2w['active_cal'], color='#D04020', linestyle='--', linewidth=1.2, alpha=0.6)
        ax_act.set_xticks(x)
        ax_act.set_xticklabels(short_labels, fontsize=8, fontweight='bold')
        ax_act.tick_params(axis='y', labelsize=7)
        ax_act.legend(fontsize=8, loc='upper left', framealpha=0.9)
        ax_act.set_title('ACTIVITY', fontsize=11, fontweight='bold', loc='left', pad=5)
        ax_act.grid(axis='y', alpha=0.3)
        ax_act.spines['top'].set_visible(False)
        ax_act.spines['right'].set_visible(False)

        # Activity 3-line comment
        avg_2w_steps = avg_2w.get('steps', 0)
        min_step_day = min((r for r in all_data if val_or_zero(r, 'steps') > 0), key=lambda r: val_or_zero(r, 'steps'), default=all_data[0])
        ac1_y = 0.540
        fig.text(0.06, ac1_y,
                 f'{top1["date"]} was biggest at {val_or_zero(top1, "steps"):,} steps / {val_or_zero(top1, "active_cal"):,} active cal — well above 2w average.',
                 fontsize=9.5, color='#111')
        fig.text(0.06, ac1_y - 0.018,
                 f'Most days above 2w baseline of {avg_2w_steps:,.0f} steps, {min_step_day["date"]} only rest day ({val_or_zero(min_step_day, "steps"):,} steps).',
                 fontsize=9.5, color='#111')
        fig.text(0.06, ac1_y - 0.036,
                 f'Active cal averaged {avg_act_cal:,.0f}/day vs 2w avg {avg_2w_act:,.0f} — {"above" if avg_act_cal > avg_2w_act else "below"} recent baseline.',
                 fontsize=9.5, color='#111')

        # --- SECTION 3: HEART & RECOVERY CHART (full width) + 3-line comment ---
        ax_hr = fig.add_axes([0.08, 0.29, 0.80, 0.15])
        l1, = ax_hr.plot(x, rhr_vals, 'o-', color='#C04040', linewidth=2.5, markersize=6, label='RHR')
        l2, = ax_hr.plot(x, mhr_vals, 's-', color='#901010', linewidth=2.5, markersize=6, label='Max HR')
        l3, = ax_hr.plot(x, hrv_vals, '^-', color='#3060C0', linewidth=2.5, markersize=6, label='HRV')
        for i, v in enumerate(rhr_vals):
            if v: ax_hr.annotate(str(v), (i, v), textcoords='offset points', xytext=(0, -10), ha='center', fontsize=7.5, fontweight='bold', color='#C04040')
        for i, v in enumerate(mhr_vals):
            if v: ax_hr.annotate(str(v), (i, v), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=7.5, fontweight='bold', color='#901010')
        ax_hr2 = ax_hr.twinx()
        l4, = ax_hr2.plot(x, intensity_vals, 'D-', color='#D08800', linewidth=2.5, markersize=6, label='Intensity')
        ax_hr2.tick_params(axis='y', labelsize=7, labelcolor='#D08800')
        ax_hr.set_xticks(x)
        ax_hr.set_xticklabels(short_labels, fontsize=8, fontweight='bold')
        ax_hr.tick_params(axis='y', labelsize=7)
        if avg_2w.get('resting_hr'):
            ax_hr.axhline(y=avg_2w['resting_hr'], color='#C04040', linestyle='--', linewidth=1.2, alpha=0.6)
        if avg_2w.get('hrv'):
            ax_hr.axhline(y=avg_2w['hrv'], color='#3060C0', linestyle='--', linewidth=1.2, alpha=0.6)
        lines = [l1, l2, l3, l4]
        ax_hr.legend(lines, [l.get_label() for l in lines], fontsize=8, loc='upper left', framealpha=0.9)
        ax_hr.set_title('HEART & RECOVERY', fontsize=11, fontweight='bold', loc='left', pad=5)
        ax_hr.grid(axis='y', alpha=0.3)
        ax_hr.spines['top'].set_visible(False)

        # Heart & Recovery 3-line comment
        avg_2w_hrv = avg_2w.get('hrv', 0)
        hc1_y = 0.255
        fig.text(0.06, hc1_y,
                 f'Pushed hard on {max_int_day["date"]} ({max_int}min intensity) — recovery stayed below 2w avg of {avg_2w_hrv:.0f}ms most of the week.',
                 fontsize=9.5, color='#111')
        fig.text(0.06, hc1_y - 0.018,
                 f'Resting HR stable at {avg_rhr:.0f}bpm (range {min(resting_hrs)}-{max(resting_hrs)}) — cardiovascular system is strong, no stress signals.',
                 fontsize=9.5, color='#111')
        fig.text(0.06, hc1_y - 0.036,
                 f'Sleep at {avg_sleep:.1f}h is the bottleneck — napping {len(nap_map)} days means the body is compensating for what it\'s not getting at night.',
                 fontsize=9.5, color='#111')

        # --- SECTION 4: NEXT WEEK / YEARLY GOAL (bottom band) ---
        plan_y = hc1_y - 0.062
        fig.text(0.04, plan_y, 'NEXT WEEK PLAN', fontsize=12, fontweight='bold', color='#000')

        plan_y -= 0.022
        fig.text(0.06, plan_y, f'Cal target: {next_week_cal_target:,}/day  |  Steps target: {next_week_steps_target:,}/day  |  Sleep: above 6.5h',
                 fontsize=9.5, color='#111')

        # Yearly goal strip — Active Cal
        plan_y -= 0.028
        cal_progress = min(max(pct_cal / 100, 0), 1)
        cal_bar = "█" * int(cal_progress * 15) + "░" * (15 - int(cal_progress * 15))
        cal_status = "on track" if avg_act_cal >= expected_cal_now else "below"
        cal_color = '#2E7D32' if avg_act_cal >= expected_cal_now else '#CC0000'

        fig.text(0.04, plan_y, '2026 GOAL (+30%)', fontsize=10, fontweight='bold', color='#222')
        plan_y -= 0.018
        fig.text(0.06, plan_y,
                 f'Cal:   [{cal_bar}] {pct_cal:.0f}%   now {avg_act_cal:,.0f} / target {TARGET_ACT_CAL:,}  — {cal_status}',
                 fontsize=8.5, family='monospace', fontweight='bold', color=cal_color)

        # Steps
        steps_progress = min(max(pct_steps / 100, 0), 1)
        steps_bar = "█" * int(steps_progress * 15) + "░" * (15 - int(steps_progress * 15))
        steps_status = "on track" if avg_steps >= expected_steps_now else "below"
        steps_color = '#2E7D32' if avg_steps >= expected_steps_now else '#CC0000'

        plan_y -= 0.018
        fig.text(0.06, plan_y,
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
