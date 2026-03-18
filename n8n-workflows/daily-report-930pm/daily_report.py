import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from garminconnect import Garmin
import garth
from datetime import date, datetime, timedelta
from config import email, password

try:
    print("Connecting to Garmin...")

    # Set up garth home directory
    garth_home = os.path.expanduser("~/.garth")
    os.makedirs(garth_home, exist_ok=True)

    # Resume session
    try:
        garth.resume(garth_home)
    except:
        garth.login(email, password)
        garth.save(garth_home)

    # Connect with garminconnect
    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    print(f"✅ Connected as: {garmin.get_full_name()}\n")

    # Get target date (today or from argument)
    if len(sys.argv) > 1:
        target_date = date.fromisoformat(sys.argv[1])
    else:
        target_date = date.today()
    today = target_date.isoformat()

    print(f"{'=' * 80}")
    print(f"📊 DAILY HEALTH & ACTIVITY REPORT - {today}")
    print(f"{'=' * 80}\n")

    # ===== COLLECT 7-DAY DATA FOR COMPARISON =====
    print("📈 Analyzing last 7 days for comparison...\n")

    seven_day_max = {
        'steps': 0,
        'active_calories': 0,
        'sleep_hours': 0,
        'sleep_score': 0,
        'intensity_mins': 0,
        'max_hr': 0,
        'min_stress': float('inf')
    }

    # Fetch last 7 days data
    for i in range(1, 8):
        past_date = (target_date - timedelta(days=i)).isoformat()

        try:
            # Get activity stats
            stats = garmin.get_stats(past_date)
            if stats:
                steps = stats.get('totalSteps', 0) or 0
                active_cal = stats.get('activeKilocalories', 0) or 0

                seven_day_max['steps'] = max(seven_day_max['steps'], steps)
                seven_day_max['active_calories'] = max(seven_day_max['active_calories'], active_cal)

                moderate = stats.get('moderateIntensityMinutes', 0) or 0
                vigorous = stats.get('vigorousIntensityMinutes', 0) or 0
                seven_day_max['intensity_mins'] = max(seven_day_max['intensity_mins'], moderate + (vigorous * 2))

            # Get sleep data
            sleep_data = garmin.get_sleep_data(past_date)
            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                sleep_hours = (daily_sleep.get('sleepTimeSeconds') or 0) / 3600
                seven_day_max['sleep_hours'] = max(seven_day_max['sleep_hours'], sleep_hours)

                sleep_scores = daily_sleep.get('sleepScores', {})
                overall_score = sleep_scores.get('overall', {}).get('value', 0)
                if overall_score:
                    seven_day_max['sleep_score'] = max(seven_day_max['sleep_score'], overall_score)

            # Get heart rate
            hr_data = garmin.get_heart_rates(past_date)
            if hr_data:
                max_hr = hr_data.get('maxHeartRate', 0)
                if max_hr:
                    seven_day_max['max_hr'] = max(seven_day_max['max_hr'], max_hr)

            # Get stress data
            stress_data = garmin.get_stress_data(past_date)
            if stress_data:
                avg_stress = stress_data.get('avgStressLevel', None)
                if avg_stress and avg_stress < seven_day_max['min_stress']:
                    seven_day_max['min_stress'] = avg_stress

        except:
            continue

    # Reset min_stress if no data found
    if seven_day_max['min_stress'] == float('inf'):
        seven_day_max['min_stress'] = 0

    # ===== 1. WORKOUTS/ACTIVITIES (moved to top) =====
    print("🎯 WORKOUTS & ACTIVITIES")
    print("-" * 80)
    try:
        activities = garmin.get_activities_by_date(today, today)

        if activities:
            print(f"Total Activities: {len(activities)}\n")

            for i, activity in enumerate(activities, 1):
                activity_name = activity.get('activityName', 'Unnamed')
                activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
                start_time = activity.get('startTimeLocal', 'N/A')
                duration_mins = activity.get('duration', 0) / 60

                print(f"{i}. {activity_name}")
                print(f"   Type:            {activity_type}")
                print(f"   Start Time:      {start_time}")
                print(f"   Duration:        {duration_mins:.1f} minutes")

                if activity.get('calories'):
                    print(f"   Calories:        {activity['calories']} kcal")

                if activity.get('averageHR'):
                    print(f"   Avg Heart Rate:  {activity['averageHR']} bpm")

                if activity.get('maxHR'):
                    print(f"   Max Heart Rate:  {activity['maxHR']} bpm")

                print()
        else:
            print("No workouts recorded for today")
    except Exception as e:
        print(f"Could not fetch activities: {e}")

    print()

    # ===== 2. SLEEP DATA =====
    print("💤 SLEEP ANALYSIS")
    print("-" * 80)
    try:
        sleep_data = garmin.get_sleep_data(today)

        if sleep_data:
            daily_sleep = sleep_data.get('dailySleepDTO', {})

            # Sleep times
            sleep_start_timestamp = daily_sleep.get('sleepStartTimestampGMT')
            sleep_end_timestamp = daily_sleep.get('sleepEndTimestampGMT')

            if sleep_start_timestamp:
                sleep_start = datetime.fromtimestamp(sleep_start_timestamp / 1000).strftime('%H:%M')
            else:
                sleep_start = 'N/A'

            if sleep_end_timestamp:
                sleep_end = datetime.fromtimestamp(sleep_end_timestamp / 1000).strftime('%H:%M')
            else:
                sleep_end = 'N/A'

            # Sleep metrics
            sleep_seconds = daily_sleep.get('sleepTimeSeconds') or 0
            sleep_hours = sleep_seconds / 3600

            # Sleep score
            sleep_scores = daily_sleep.get('sleepScores', {})
            overall_score = sleep_scores.get('overall', {}).get('value', 'N/A')

            print(f"Sleep Period:       {sleep_start} → {sleep_end}")
            print(f"Total Duration:     {sleep_hours:.2f} hours ({sleep_seconds / 60:.0f} mins)")
            print(f"Sleep Score:        {overall_score}")

            # Comparison with best of last 7 days
            if seven_day_max['sleep_hours'] > 0 or seven_day_max['sleep_score'] > 0:
                print(f"\n🔄 Comparison to Best of Last 7 Days:")
                if seven_day_max['sleep_hours'] > 0:
                    diff_hours = sleep_hours - seven_day_max['sleep_hours']
                    diff_mins = diff_hours * 60
                    comparison = "=" if diff_hours == 0 else ("↗" if diff_hours > 0 else "↘")
                    print(f"  Duration:         {comparison} Best was {seven_day_max['sleep_hours']:.2f}h (today: {diff_mins:+.0f} mins)")
                if seven_day_max['sleep_score'] > 0 and overall_score != 'N/A':
                    diff_score = overall_score - seven_day_max['sleep_score']
                    comparison = "=" if diff_score == 0 else ("↗" if diff_score > 0 else "↘")
                    print(f"  Sleep Score:      {comparison} Best was {seven_day_max['sleep_score']} (today: {diff_score:+.0f})")
        else:
            print("No sleep data available for today")
    except Exception as e:
        print(f"Could not fetch sleep data: {e}")

    print()

    # ===== 3. ACTIVITY & FITNESS DATA =====
    print("🏃 ACTIVITY & FITNESS")
    print("-" * 80)
    try:
        stats = garmin.get_stats(today)

        if stats:
            steps = stats.get('totalSteps', 0) or 0
            step_goal = stats.get('dailyStepGoal', 10000) or 10000

            total_calories = stats.get('totalKilocalories', 0) or 0
            active_calories = stats.get('activeKilocalories', 0) or 0
            bmr_calories = stats.get('bmrKilocalories', 0) or 0

            moderate_mins = stats.get('moderateIntensityMinutes', 0) or 0
            vigorous_mins = stats.get('vigorousIntensityMinutes', 0) or 0
            total_intensity = moderate_mins + (vigorous_mins * 2)
            intensity_goal = stats.get('weeklyIntensityMinutesGoal', 150) or 150

            print(f"Steps:              {steps:,} / {step_goal:,} ({steps/step_goal*100:.1f}%)")
            print(f"\nCalories:")
            print(f"  Total Burned:     {total_calories:,} kcal")
            print(f"  Active:           {active_calories:,} kcal")
            print(f"  BMR (Resting):    {bmr_calories:,} kcal")
            print(f"\nIntensity Minutes:")
            print(f"  Moderate:         {moderate_mins} mins")
            print(f"  Vigorous:         {vigorous_mins} mins")
            print(f"  Total (Weekly):   {total_intensity} / {intensity_goal} mins")

            # Comparison with best of last 7 days
            if any([seven_day_max['steps'] > 0, seven_day_max['active_calories'] > 0, seven_day_max['intensity_mins'] > 0]):
                print(f"\n🔄 Comparison to Best of Last 7 Days:")
                if seven_day_max['steps'] > 0:
                    diff_steps = steps - seven_day_max['steps']
                    comparison = "=" if diff_steps == 0 else ("↗" if diff_steps > 0 else "↘")
                    pct = (steps / seven_day_max['steps'] * 100) if seven_day_max['steps'] > 0 else 0
                    print(f"  Steps:            {comparison} Best was {seven_day_max['steps']:,} (today: {pct:.1f}%, {diff_steps:+,})")
                if seven_day_max['active_calories'] > 0:
                    diff_cal = active_calories - seven_day_max['active_calories']
                    comparison = "=" if diff_cal == 0 else ("↗" if diff_cal > 0 else "↘")
                    pct = (active_calories / seven_day_max['active_calories'] * 100) if seven_day_max['active_calories'] > 0 else 0
                    print(f"  Active Calories:  {comparison} Best was {seven_day_max['active_calories']:,} kcal (today: {pct:.1f}%, {diff_cal:+,})")
                if seven_day_max['intensity_mins'] > 0:
                    diff_int = total_intensity - seven_day_max['intensity_mins']
                    comparison = "=" if diff_int == 0 else ("↗" if diff_int > 0 else "↘")
                    pct = (total_intensity / seven_day_max['intensity_mins'] * 100) if seven_day_max['intensity_mins'] > 0 else 0
                    print(f"  Intensity Mins:   {comparison} Best was {seven_day_max['intensity_mins']} mins (today: {pct:.1f}%, {diff_int:+.0f})")
        else:
            print("No activity data available for today")
    except Exception as e:
        print(f"Could not fetch activity data: {e}")

    print()

    # ===== 4. HEART RATE DATA =====
    print("❤️  HEART RATE")
    print("-" * 80)
    try:
        heart_rate = garmin.get_heart_rates(today)

        if heart_rate:
            resting_hr = heart_rate.get('restingHeartRate', 'N/A')
            max_hr = heart_rate.get('maxHeartRate', 'N/A')
            min_hr = heart_rate.get('minHeartRate', 'N/A')

            print(f"Resting HR:         {resting_hr} bpm")
            print(f"Max HR:             {max_hr} bpm")
            print(f"Min HR:             {min_hr} bpm")

            # Comparison with best of last 7 days
            if seven_day_max['max_hr'] > 0 and max_hr != 'N/A':
                print(f"\n🔄 Comparison to Best of Last 7 Days:")
                diff_hr = max_hr - seven_day_max['max_hr']
                comparison = "=" if diff_hr == 0 else ("↗" if diff_hr > 0 else "↘")
                print(f"  Max HR:           {comparison} Best was {seven_day_max['max_hr']} bpm (today: {diff_hr:+.0f})")
        else:
            print("No heart rate data available")
    except Exception as e:
        print(f"Could not fetch heart rate data: {e}")

    print()

    # ===== 5. STRESS & BODY BATTERY =====
    print("🧘 STRESS & RECOVERY")
    print("-" * 80)
    try:
        # Stress data
        stress_data = garmin.get_stress_data(today)
        if stress_data:
            avg_stress = stress_data.get('avgStressLevel', 'N/A')
            max_stress = stress_data.get('maxStressLevel', 'N/A')
            print(f"Average Stress:     {avg_stress}")
            print(f"Max Stress:         {max_stress}")

            # Comparison with best (lowest) stress of last 7 days
            if seven_day_max['min_stress'] > 0 and avg_stress != 'N/A':
                print(f"\n🔄 Comparison to Best of Last 7 Days:")
                diff_stress = avg_stress - seven_day_max['min_stress']
                comparison = "=" if diff_stress == 0 else ("↘" if diff_stress > 0 else "↗")  # Lower is better for stress
                print(f"  Avg Stress:       {comparison} Best was {seven_day_max['min_stress']} (today: {diff_stress:+.0f})")

        # Body Battery (if available)
        try:
            stats_body = garmin.get_stats_and_body(today)
            if stats_body:
                body_battery = stats_body.get('bodyBattery', {})
                if body_battery:
                    current_bb = body_battery.get('charged', 'N/A')
                    print(f"Body Battery:       {current_bb}")
        except:
            pass

    except Exception as e:
        print(f"Could not fetch stress/recovery data: {e}")

    print()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
