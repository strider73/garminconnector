import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
from config import email, password

try:
    print("Connecting to Garmin...")

    # Set up garth home directory
    garth_home = os.path.expanduser("~/.garth")
    os.makedirs(garth_home, exist_ok=True)

    # Try to resume session, or login fresh
    try:
        garth.resume(garth_home)
        print("Using saved session...")
    except:
        print("No saved session, logging in...")
        garth.login(email, password)
        garth.save(garth_home)
        print("Session saved!")

    # Now use garminconnect with the authenticated garth session
    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    # Get and display user info
    print(f"\n✅ Successfully connected to Garmin!")
    print(f"Display Name: {garmin.display_name}")
    print(f"Full Name: {garmin.get_full_name()}")

    # Get today's date for stats
    from datetime import date
    today = date.today().isoformat()
    user_summary = garmin.get_user_summary(today)
    print(f"User ID: {user_summary.get('userId', 'N/A')}")
    print("\n🎉 Connection successful! You can now fetch Garmin data.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
