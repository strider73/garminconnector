import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date, datetime
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

    # Get today's date
    today = date.today().isoformat()
    print(f"{'=' * 80}")
    print(f"💪 INTENSITY MINUTES ANALYSIS - {today}")
    print(f"{'=' * 80}\n")

    # Get daily stats for intensity minutes summary
    print("📊 DAILY INTENSITY SUMMARY")
    print("-" * 80)
    try:
        stats = garmin.get_stats(today)

        if stats:
            moderate_mins = stats.get('moderateIntensityMinutes', 0)
            vigorous_mins = stats.get('vigorousIntensityMinutes', 0)
            total_intensity = moderate_mins + (vigorous_mins * 2)
            intensity_goal = stats.get('weeklyIntensityMinutesGoal', 150)

            print(f"Moderate Intensity:  {moderate_mins} minutes")
            print(f"Vigorous Intensity:  {vigorous_mins} minutes")
            print(f"Total (Weekly):      {total_intensity} / {intensity_goal} minutes")
            print(f"Progress:            {total_intensity/intensity_goal*100:.1f}%")
    except Exception as e:
        print(f"Could not fetch intensity summary: {e}")

    print()

    # Get activities to see WHEN vigorous activity happened
    print("🔥 VIGOROUS INTENSITY PERIODS (from activities)")
    print("-" * 80)
    try:
        activities = garmin.get_activities_by_date(today, today)

        if activities:
            print(f"Total Activities: {len(activities)}\n")

            vigorous_found = False

            for i, activity in enumerate(activities, 1):
                activity_name = activity.get('activityName', 'Unnamed')
                activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
                start_time = activity.get('startTimeLocal', 'N/A')
                duration_mins = activity.get('duration', 0) / 60

                # Get heart rate zones to determine intensity
                avg_hr = activity.get('averageHR')
                max_hr = activity.get('maxHR')

                # Check if this was vigorous intensity
                # Vigorous = typically HR > 140 or running/cycling at high pace
                is_vigorous = False
                vigorous_reason = []

                if avg_hr and avg_hr >= 120:
                    is_vigorous = True
                    vigorous_reason.append(f"Avg HR: {avg_hr} bpm")

                if max_hr and max_hr >= 140:
                    is_vigorous = True
                    vigorous_reason.append(f"Max HR: {max_hr} bpm")

                # High intensity activity types
                high_intensity_types = ['running', 'cycling', 'hiit', 'cardio', 'swimming']
                if any(activity_type.lower() in activity_type.lower() for activity_type in high_intensity_types):
                    is_vigorous = True

                if is_vigorous:
                    vigorous_found = True
                    print(f"{'🔥' if avg_hr and avg_hr >= 140 else '💪'} VIGOROUS ACTIVITY #{i}")
                    print(f"   Name:            {activity_name}")
                    print(f"   Type:            {activity_type}")
                    print(f"   Start Time:      {start_time}")
                    print(f"   Duration:        {duration_mins:.1f} minutes")

                    if avg_hr:
                        print(f"   Avg Heart Rate:  {avg_hr} bpm")
                    if max_hr:
                        print(f"   Max Heart Rate:  {max_hr} bpm")

                    if activity.get('distance'):
                        distance = activity['distance'] / 1000
                        print(f"   Distance:        {distance:.2f} km")

                        if duration_mins > 0:
                            pace = duration_mins / distance
                            print(f"   Avg Pace:        {pace:.2f} min/km")

                    if activity.get('calories'):
                        print(f"   Calories:        {activity['calories']} kcal")

                    if vigorous_reason:
                        print(f"   Vigorous due to: {', '.join(vigorous_reason)}")

                    print()

            if not vigorous_found:
                print("No vigorous intensity activities detected today.")
                print("(Vigorous intensity typically means HR > 120 bpm or high-intensity exercise)")

        else:
            print("No activities recorded for today.")
            print("\nNote: Intensity minutes can also accumulate from:")
            print("  - Walking at brisk pace")
            print("  - Climbing stairs")
            print("  - Daily movement with elevated heart rate")

    except Exception as e:
        print(f"Could not fetch activities: {e}")

    # Get heart rate data to show vigorous periods
    print("\n💓 HEART RATE BASED VIGOROUS PERIODS")
    print("-" * 80)
    try:
        heart_rate = garmin.get_heart_rates(today)

        if heart_rate:
            hr_values = heart_rate.get('heartRateValues', [])

            if hr_values:
                # Find periods where HR was in vigorous zone (> 120)
                vigorous_periods = []
                current_period_start = None
                current_period_hr = []

                for timestamp, hr_value in hr_values:
                    if hr_value is None:
                        continue

                    time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S')

                    if hr_value >= 120:  # Vigorous zone
                        if current_period_start is None:
                            current_period_start = time_str
                        current_period_hr.append(hr_value)
                    else:
                        if current_period_start is not None:
                            # End of vigorous period
                            period_end = datetime.fromtimestamp((timestamp - 1000) / 1000).strftime('%H:%M:%S')
                            avg_hr = sum(current_period_hr) / len(current_period_hr)
                            max_hr = max(current_period_hr)
                            duration = len(current_period_hr)  # Approximate minutes

                            vigorous_periods.append({
                                'start': current_period_start,
                                'end': period_end,
                                'avg_hr': avg_hr,
                                'max_hr': max_hr,
                                'duration': duration
                            })

                            current_period_start = None
                            current_period_hr = []

                if vigorous_periods:
                    print(f"Found {len(vigorous_periods)} vigorous periods (HR > 120 bpm):\n")

                    for i, period in enumerate(vigorous_periods, 1):
                        print(f"{i}. {period['start']} → {period['end']}")
                        print(f"   Avg HR: {period['avg_hr']:.0f} bpm")
                        print(f"   Max HR: {period['max_hr']:.0f} bpm")
                        print(f"   Est. Duration: ~{period['duration']} readings")
                        print()
                else:
                    print("No vigorous heart rate periods detected (HR > 120 bpm)")

    except Exception as e:
        print(f"Could not analyze heart rate for vigorous periods: {e}")

    print("=" * 80)
    print("✅ Intensity analysis complete!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
