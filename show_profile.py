#!/usr/bin/env python3
"""Show currently logged in Garmin account"""

from garminconnect import Garmin
import garth
import os

try:
    # Set up garth home directory
    garth_home = os.path.expanduser("~/.garth")

    # Resume session
    garth.resume(garth_home)

    # Connect with garminconnect
    garmin = Garmin()
    garmin.login(tokenstore=garth_home)

    # Get user info
    full_name = garmin.get_full_name()
    device_info = garmin.get_device_last_used()
    profile_number = device_info.get("userProfileNumber", "N/A") if device_info else "N/A"

    print("\n" + "=" * 50)
    print("👤 Currently Logged In")
    print("=" * 50)
    print(f"📝 Name: {full_name}")
    print(f"🆔 Profile: {profile_number}")
    print("=" * 50 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 You may need to login first")
