from garminconnect import Garmin
import garth
import os
from datetime import date, timedelta
from config import email, password

try:
    print("Connecting to Garmin...")

    # Set up garth home directory
    garth_home = os.path.expanduser("~/.garth")
    os.makedirs(garth_home, exist_ok=True)

    # Resume session
    try:
        garth.resume(garth_home)
        print("Using saved session...")
    except:
        print("No saved session, logging in...")
        garth.login(email, password)
        garth.save(garth_home)
        print("Session saved!")

    # Connect with garminconnect
    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    print(f"\n✅ Connected as: {garmin.get_full_name()}")

    # Get activities from the last 7 days
    print("\n📊 Fetching your recent activities...")
    activities = garmin.get_activities(0, 10)  # Get last 10 activities

    if not activities:
        print("No activities found.")
    else:
        print(f"\nFound {len(activities)} recent activities:\n")

        for i, activity in enumerate(activities, 1):
            print(f"{i}. {activity['activityName']}")
            print(f"   Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}")
            print(f"   Date: {activity['startTimeLocal']}")
            print(f"   Duration: {activity.get('duration', 0) / 60:.1f} minutes")

            # Distance (if available)
            if activity.get('distance'):
                print(f"   Distance: {activity['distance'] / 1000:.2f} km")

            # Calories (if available)
            if activity.get('calories'):
                print(f"   Calories: {activity['calories']}")

            print()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
