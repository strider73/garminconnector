#!/usr/bin/env python3
"""
Monthly Workload Report - Database-Driven
Generates comprehensive training load and recovery metrics for each month
Uses PostgreSQL data for fast, historical analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from datetime import datetime, date
from calendar import month_name

# Database connection from .mcp.json
DB_CONFIG = {
    'host': 'travel-tube.com',
    'port': 5432,
    'database': 'adventuretube',
    'user': 'postgres',
    'password': '5785Ch00'
}

def get_monthly_summary(year, month):
    """Get aggregated metrics for a specific month"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
    SELECT
        COUNT(*) as days_tracked,

        -- Training Load
        AVG(acute_load) as avg_acute_load,
        AVG(chronic_load) as avg_chronic_load,
        AVG(acwr_ratio) as avg_acwr,

        -- Readiness
        AVG(readiness_score) as avg_readiness,
        COUNT(CASE WHEN readiness_score >= 80 THEN 1 END) as prime_days,
        COUNT(CASE WHEN readiness_score BETWEEN 60 AND 79 THEN 1 END) as moderate_days,
        COUNT(CASE WHEN readiness_score < 60 THEN 1 END) as low_days,

        -- Sleep
        AVG(sleep_hours) as avg_sleep,
        AVG(sleep_score) as avg_sleep_score,
        AVG(deep_sleep_mins) as avg_deep_sleep,
        AVG(rem_sleep_mins) as avg_rem_sleep,
        COUNT(CASE WHEN sleep_hours >= 7.5 THEN 1 END) as good_sleep_days,

        -- Heart Rate & HRV
        AVG(resting_hr) as avg_rhr,
        MIN(resting_hr) as min_rhr,
        MAX(resting_hr) as max_rhr,
        AVG(hrv_last_night) as avg_hrv,
        AVG(hrv_weekly_avg) as avg_hrv_weekly,

        -- Recovery
        AVG(body_battery_charged) as avg_bb_charged,
        AVG(body_battery_drained) as avg_bb_drained,
        AVG(readiness_recovery_mins) as avg_recovery_mins,
        AVG(avg_stress) as avg_stress,

        -- Training Intensity
        AVG(aerobic_low) as avg_low_aerobic,
        AVG(aerobic_high) as avg_high_aerobic,
        AVG(anaerobic) as avg_anaerobic,

        -- VO2 Max (most recent for the month)
        MAX(vo2_max) as latest_vo2_max,

        -- ACWR Risk Days
        COUNT(CASE WHEN acwr_ratio > 1.5 THEN 1 END) as high_risk_days,
        COUNT(CASE WHEN acwr_ratio BETWEEN 0.8 AND 1.3 THEN 1 END) as optimal_days

    FROM garmin_daily_metrics
    WHERE EXTRACT(YEAR FROM report_date) = %s
      AND EXTRACT(MONTH FROM report_date) = %s
    """

    cursor.execute(query, (year, month))
    result = cursor.fetchone()

    # Get weekly breakdown for the month
    weekly_query = """
    SELECT
        EXTRACT(WEEK FROM report_date) as week_num,
        AVG(acute_load) as avg_load,
        AVG(acwr_ratio) as avg_acwr,
        AVG(readiness_score) as avg_readiness,
        AVG(sleep_hours) as avg_sleep,
        AVG(resting_hr) as avg_rhr,
        AVG(hrv_last_night) as avg_hrv
    FROM garmin_daily_metrics
    WHERE EXTRACT(YEAR FROM report_date) = %s
      AND EXTRACT(MONTH FROM report_date) = %s
    GROUP BY EXTRACT(WEEK FROM report_date)
    ORDER BY week_num
    """

    cursor.execute(weekly_query, (year, month))
    weekly_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return result, weekly_data

def print_monthly_report(year, month):
    """Print comprehensive monthly workload report"""

    try:
        data, weekly_data = get_monthly_summary(year, month)

        if not data or data[0] == 0:
            print(f"\n❌ No data found for {month_name[month]} {year}")
            return

        # Unpack data and handle None values
        (days_tracked, avg_acute, avg_chronic, avg_acwr,
         avg_readiness, prime_days, moderate_days, low_days,
         avg_sleep, avg_sleep_score, avg_deep, avg_rem, good_sleep_days,
         avg_rhr, min_rhr, max_rhr, avg_hrv, avg_hrv_weekly,
         avg_bb_charged, avg_bb_drained, avg_recovery_mins, avg_stress,
         avg_low_aerobic, avg_high_aerobic, avg_anaerobic,
         latest_vo2_max, high_risk_days, optimal_days) = data

        # Convert None to 0 for numeric fields where needed
        avg_readiness = avg_readiness or 0
        avg_sleep = avg_sleep or 0
        avg_sleep_score = avg_sleep_score or 0
        avg_deep = avg_deep or 0
        avg_rem = avg_rem or 0
        avg_rhr = avg_rhr or 0
        min_rhr = min_rhr or 0
        max_rhr = max_rhr or 0
        avg_hrv = avg_hrv or 0
        avg_hrv_weekly = avg_hrv_weekly or 0
        avg_bb_charged = avg_bb_charged or 0
        avg_bb_drained = avg_bb_drained or 0
        avg_recovery_mins = avg_recovery_mins or 0
        avg_stress = avg_stress or 0
        avg_acute = avg_acute or 0
        avg_chronic = avg_chronic or 0
        avg_acwr = avg_acwr or 0
        good_sleep_days = good_sleep_days or 0
        prime_days = prime_days or 0
        moderate_days = moderate_days or 0
        low_days = low_days or 0
        high_risk_days = high_risk_days or 0
        optimal_days = optimal_days or 0

        # Print header
        print("\n" + "=" * 100)
        print(f"📊 MONTHLY WORKLOAD REPORT — {month_name[month].upper()} {year}")
        print(f"   Yehwan's Training Analysis ({days_tracked} days tracked)")
        print("=" * 100)

        # === TRAINING LOAD ===
        print("\n🏋️ TRAINING LOAD OVERVIEW")
        print("─" * 100)

        acwr_status = "✅ OPTIMAL" if 0.8 <= avg_acwr <= 1.3 else "⚠️ HIGH RISK" if avg_acwr > 1.5 else "🔵 LOW"
        load_trend = "BUILDING" if avg_acute > avg_chronic else "MAINTAINING" if avg_acute >= avg_chronic * 0.9 else "RECOVERING"

        print(f"""
   Acute Load (7-day avg):     {avg_acute:.1f}
   Chronic Load (28-day avg):  {avg_chronic:.1f}
   ACWR Ratio:                 {avg_acwr:.2f} {acwr_status}
   Load Trend:                 {load_trend}

   Optimal Training Days:      {optimal_days}/{days_tracked} ({optimal_days/days_tracked*100:.0f}%)
   High Risk Days (ACWR >1.5): {high_risk_days}/{days_tracked} ({high_risk_days/days_tracked*100:.0f}%)
""")

        # === READINESS & RECOVERY ===
        print("─" * 100)
        print("💪 READINESS & RECOVERY")
        print("─" * 100)

        readiness_level = "PRIME" if avg_readiness >= 80 else "MODERATE" if avg_readiness >= 60 else "LOW"

        print(f"""
   Average Readiness Score:    {avg_readiness:.0f} ({readiness_level})

   Daily Breakdown:
   ├─ PRIME days (80+):        {prime_days} days ({prime_days/days_tracked*100:.0f}%)
   ├─ MODERATE days (60-79):   {moderate_days} days ({moderate_days/days_tracked*100:.0f}%)
   └─ LOW days (<60):          {low_days} days ({low_days/days_tracked*100:.0f}%)

   Recovery Metrics:
   ├─ Avg Recovery Time:       {avg_recovery_mins:.0f} mins
   ├─ Body Battery Charged:    {avg_bb_charged:.0f}
   ├─ Body Battery Drained:    {avg_bb_drained:.0f}
   └─ Average Stress:          {avg_stress:.0f}
""")

        # === SLEEP ANALYSIS ===
        print("─" * 100)
        print("😴 SLEEP ANALYSIS")
        print("─" * 100)

        sleep_quality = "EXCELLENT" if avg_sleep >= 8 else "GOOD" if avg_sleep >= 7 else "NEEDS IMPROVEMENT"

        print(f"""
   Average Sleep:              {avg_sleep:.1f}h/night ({sleep_quality})
   Sleep Score:                {avg_sleep_score:.0f}/100
   Good Sleep Days (7.5h+):    {good_sleep_days}/{days_tracked} ({good_sleep_days/days_tracked*100:.0f}%)

   Sleep Composition:
   ├─ Deep Sleep:              {avg_deep:.0f} mins
   ├─ REM Sleep:               {avg_rem:.0f} mins
   └─ Light + Awake:           {(avg_sleep*60 - avg_deep - avg_rem):.0f} mins
""")

        # === HEART RATE & HRV ===
        print("─" * 100)
        print("❤️ HEART RATE & HRV")
        print("─" * 100)

        rhr_status = "EXCELLENT" if avg_rhr <= 45 else "GOOD" if avg_rhr <= 50 else "ELEVATED"
        hrv_status = "EXCELLENT" if avg_hrv >= 65 else "GOOD" if avg_hrv >= 55 else "LOW"

        print(f"""
   Resting Heart Rate:
   ├─ Average:                 {avg_rhr:.0f} bpm ({rhr_status})
   ├─ Minimum:                 {min_rhr} bpm
   └─ Maximum:                 {max_rhr} bpm

   Heart Rate Variability:
   ├─ Average (nightly):       {avg_hrv:.1f} ms ({hrv_status})
   └─ 7-day rolling avg:       {avg_hrv_weekly:.1f} ms
""")

        # === TRAINING INTENSITY ===
        print("─" * 100)
        print("🔥 TRAINING INTENSITY DISTRIBUTION")
        print("─" * 100)

        total_training = (avg_low_aerobic or 0) + (avg_high_aerobic or 0) + (avg_anaerobic or 0)

        if total_training > 0:
            low_pct = (avg_low_aerobic / total_training * 100) if avg_low_aerobic else 0
            high_pct = (avg_high_aerobic / total_training * 100) if avg_high_aerobic else 0
            anaerobic_pct = (avg_anaerobic / total_training * 100) if avg_anaerobic else 0

            print(f"""
   Low Aerobic (Zone 2):       {avg_low_aerobic:.0f} mins/week ({low_pct:.0f}%)
   High Aerobic (Zone 3-4):    {avg_high_aerobic:.0f} mins/week ({high_pct:.0f}%)
   Anaerobic (Zone 5):         {avg_anaerobic:.0f} mins/week ({anaerobic_pct:.0f}%)

   Total Training:             {total_training:.0f} mins/week ({total_training/60:.1f} hours)
""")
        else:
            print("\n   No training intensity data available for this month")

        # === PERFORMANCE METRICS ===
        print("─" * 100)
        print("📈 PERFORMANCE METRICS")
        print("─" * 100)

        if latest_vo2_max:
            vo2_level = "EXCELLENT" if latest_vo2_max >= 55 else "GOOD" if latest_vo2_max >= 50 else "AVERAGE"
            print(f"\n   VO2 Max:                    {latest_vo2_max:.1f} ml/kg/min ({vo2_level})")
        else:
            print("\n   VO2 Max:                    No data")

        # === WEEKLY BREAKDOWN ===
        if weekly_data:
            print("\n" + "─" * 100)
            print("📅 WEEKLY BREAKDOWN")
            print("─" * 100)
            print(f"{'Week':<6} │ {'Load':<8} │ {'ACWR':<8} │ {'Readiness':<10} │ {'Sleep':<8} │ {'RHR':<6} │ {'HRV':<6}")
            print("─" * 100)

            for week_num, load, acwr, readiness, sleep, rhr, hrv in weekly_data:
                load_str = f"{load:.1f}" if load else "-"
                acwr_str = f"{acwr:.2f}" if acwr else "-"
                ready_str = f"{readiness:.0f}" if readiness else "-"
                sleep_str = f"{sleep:.1f}h" if sleep else "-"
                rhr_str = f"{rhr:.0f}" if rhr else "-"
                hrv_str = f"{hrv:.1f}" if hrv else "-"

                print(f"Wk {int(week_num):<3} │ {load_str:<8} │ {acwr_str:<8} │ {ready_str:<10} │ {sleep_str:<8} │ {rhr_str:<6} │ {hrv_str:<6}")

        # === RECOMMENDATIONS ===
        print("\n" + "=" * 100)
        print("💡 COACHING INSIGHTS & RECOMMENDATIONS")
        print("=" * 100)

        insights = []

        # ACWR insights
        if avg_acwr > 1.5:
            insights.append("⚠️ HIGH INJURY RISK: ACWR above 1.5. Reduce training volume by 10-20% this week.")
        elif avg_acwr < 0.8:
            insights.append("🔵 UNDERTRAINING: ACWR below 0.8. Consider gradually increasing volume if recovered.")
        else:
            insights.append("✅ OPTIMAL LOAD: ACWR in sweet spot (0.8-1.3). Maintain current training approach.")

        # Readiness insights
        if avg_readiness < 60:
            insights.append("😰 LOW READINESS: Average below 60. Prioritize sleep, reduce intensity, focus on recovery.")
        elif avg_readiness >= 80:
            insights.append("💪 PRIME CONDITION: High readiness supports intense training blocks and competition.")

        # Sleep insights
        if avg_sleep < 7:
            insights.append(f"😴 SLEEP DEFICIT: Only {avg_sleep:.1f}h/night. Target 8+ hours for optimal tennis performance.")
        elif good_sleep_days < days_tracked * 0.5:
            insights.append(f"😴 INCONSISTENT SLEEP: Only {good_sleep_days} days with 7.5h+. Build consistent sleep routine.")
        else:
            insights.append(f"😴 EXCELLENT SLEEP: {avg_sleep:.1f}h average supports recovery and performance.")

        # HRV insights
        if avg_hrv < 55:
            insights.append("📉 LOW HRV: Consider reducing training stress or addressing non-training stressors.")
        elif avg_hrv >= 65:
            insights.append("📈 STRONG HRV: Parasympathetic nervous system well-balanced. Good recovery capacity.")

        # RHR insights
        if avg_rhr > 50:
            insights.append(f"❤️ ELEVATED RHR: {avg_rhr:.0f} bpm higher than baseline (44). Check for overtraining or illness.")
        elif avg_rhr <= 45:
            insights.append(f"❤️ EXCELLENT RHR: {avg_rhr:.0f} bpm shows strong cardiovascular fitness.")

        # Training intensity insights
        if total_training > 0:
            if anaerobic_pct < 20:
                insights.append(f"🎾 LOW ANAEROBIC WORK: Only {anaerobic_pct:.0f}% high intensity. Tennis needs more explosive training.")
            if low_pct > 60:
                insights.append(f"🔄 TOO MUCH ZONE 2: {low_pct:.0f}% low aerobic. Add more tennis-specific intensity.")

        for i, insight in enumerate(insights, 1):
            print(f"\n{i}. {insight}")

        print("\n" + "=" * 100)
        print(f"✅ Monthly workload report complete for {month_name[month]} {year}")
        print("=" * 100)

    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function - allows running for specific month or all available months"""

    if len(sys.argv) == 3:
        # Specific month: python monthly_workload_report.py 2026 2
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        print_monthly_report(year, month)

    elif len(sys.argv) == 2 and sys.argv[1] == 'all':
        # All months with data
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT
                EXTRACT(YEAR FROM report_date) as year,
                EXTRACT(MONTH FROM report_date) as month
            FROM garmin_daily_metrics
            ORDER BY year, month
        """)

        months = cursor.fetchall()
        cursor.close()
        conn.close()

        for year, month in months:
            print_monthly_report(int(year), int(month))
            print("\n" * 2)

    else:
        # Default: current month
        today = date.today()
        print_monthly_report(today.year, today.month)

        print("\n" + "─" * 100)
        print("📋 USAGE")
        print("─" * 100)
        print(f"""
   Current month:       python monthly_workload_report.py
   Specific month:      python monthly_workload_report.py 2026 1
   All months:          python monthly_workload_report.py all
""")

if __name__ == "__main__":
    main()
