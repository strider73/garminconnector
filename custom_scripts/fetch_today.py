import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from datetime import date
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
    print(f"📅 Fetching data for: {today}\n")

    # ===== 1. SLEEP DATA =====
    print("😴 SLEEP DATA")
    print("-" * 50)
    try:
        sleep_data = garmin.get_sleep_data(today)

        if sleep_data:
            daily_sleep = sleep_data.get('dailySleepDTO', {})

            # Sleep duration (in seconds, convert to hours)
            sleep_seconds = daily_sleep.get('sleepTimeSeconds', 0)
            sleep_hours = sleep_seconds / 3600

            print(f"Sleep Duration: {sleep_hours:.2f} hours ({sleep_seconds / 60:.0f} minutes)")
            print(f"Deep Sleep: {daily_sleep.get('deepSleepSeconds', 0) / 60:.0f} minutes")
            print(f"Light Sleep: {daily_sleep.get('lightSleepSeconds', 0) / 60:.0f} minutes")
            print(f"REM Sleep: {daily_sleep.get('remSleepSeconds', 0) / 60:.0f} minutes")
            print(f"Awake: {daily_sleep.get('awakeSleepSeconds', 0) / 60:.0f} minutes")
        else:
            print("No sleep data available for today")
    except Exception as e:
        print(f"Could not fetch sleep data: {e}")

    print()

    # ===== 2. ACTIVITY DATA (STEPS, CALORIES, INTENSITY MINUTES) =====
    print("🏃 ACTIVITY DATA")
    print("-" * 50)
    try:
        stats = garmin.get_stats(today)

        if stats:
            print(f"Steps: {stats.get('totalSteps', 0):,}")
            print(f"Distance: {stats.get('totalDistanceMeters', 0) / 1000:.2f} km")
            print(f"Calories: {stats.get('totalKilocalories', 0):,} kcal (Total)")
            print(f"Active Calories: {stats.get('activeKilocalories', 0):,} kcal")
            print(f"Intensity Minutes: {stats.get('intensityMinutesGoal', 0)} (Goal: {stats.get('weeklyIntensityMinutesGoal', 150)})")
            print(f"Moderate Intensity: {stats.get('moderateIntensityMinutes', 0)} minutes")
            print(f"Vigorous Intensity: {stats.get('vigorousIntensityMinutes', 0)} minutes")
            print(f"Floors Climbed: {stats.get('floorsClimbed', 0)}")
        else:
            print("No activity data available for today")
    except Exception as e:
        print(f"Could not fetch activity data: {e}")

    print()

    # ===== 3. TODAY'S ACTIVITIES (WORKOUTS) =====
    print("🎯 TODAY'S ACTIVITIES")
    print("-" * 50)
    try:
        activities = garmin.get_activities_by_date(today, today)

        if activities:
            print(f"Found {len(activities)} activity/activities today:\n")

            for i, activity in enumerate(activities, 1):
                print(f"{i}. {activity.get('activityName', 'Unnamed Activity')}")
                print(f"   Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}")
                print(f"   Start: {activity.get('startTimeLocal', 'N/A')}")
                print(f"   Duration: {activity.get('duration', 0) / 60:.1f} minutes")

                if activity.get('distance'):
                    print(f"   Distance: {activity['distance'] / 1000:.2f} km")

                if activity.get('calories'):
                    print(f"   Calories: {activity['calories']}")

                if activity.get('averageHR'):
                    print(f"   Avg Heart Rate: {activity['averageHR']} bpm")

                print()
        else:
            print("No activities recorded for today")
    except Exception as e:
        print(f"Could not fetch today's activities: {e}")

    print("\n✅ Data fetch complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
