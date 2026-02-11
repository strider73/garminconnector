from garminconnect import Garmin
import garth
import os
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
    print(f"❤️  HEART RATE ANALYSIS - {today}")
    print(f"{'=' * 80}\n")

    # Heart rate thresholds
    LOW_THRESHOLD = 70  # Below this is considered low
    RESTING_NORMAL = 60
    RESTING_HIGH = 80
    ELEVATED = 100
    HIGH = 120
    VERY_HIGH = 140  # Vigorous exercise zone starts here

    try:
        heart_rate = garmin.get_heart_rates(today)

        if heart_rate:
            # Summary stats
            resting_hr = heart_rate.get('restingHeartRate', 'N/A')
            max_hr = heart_rate.get('maxHeartRate', 'N/A')
            min_hr = heart_rate.get('minHeartRate', 'N/A')

            print("📊 SUMMARY")
            print("-" * 80)
            print(f"Resting HR:         {resting_hr} bpm")
            print(f"Maximum HR:         {max_hr} bpm")
            print(f"Minimum HR:         {min_hr} bpm")

            # Get all heart rate values (timestamps and values)
            hr_values = heart_rate.get('heartRateValues', [])

            if hr_values:
                print(f"\nTotal Readings:     {len(hr_values)}")

                # Analyze heart rate zones
                below_70 = 0  # < 70 (LOW)
                very_low = 0  # < 60
                normal = 0  # 60-80
                elevated = 0  # 80-100
                high = 0  # 100-120
                very_high = 0  # 120-140 (Vigorous zone)
                extreme = 0  # > 140 (High vigorous)

                below_70_times = []
                elevated_times = []
                high_times = []
                very_high_times = []  # Vigorous exercise
                extreme_times = []  # High vigorous exercise

                for timestamp, hr_value in hr_values:
                    if hr_value is None:
                        continue

                    # Convert timestamp to readable time
                    time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S')

                    # Track low heart rate (< 70)
                    if hr_value < LOW_THRESHOLD:
                        below_70 += 1
                        below_70_times.append((time_str, hr_value))

                    # Categorize into zones
                    if hr_value < RESTING_NORMAL:
                        very_low += 1
                    elif hr_value < RESTING_HIGH:
                        normal += 1
                    elif hr_value < ELEVATED:
                        elevated += 1
                        elevated_times.append((time_str, hr_value))
                    elif hr_value < HIGH:
                        high += 1
                        high_times.append((time_str, hr_value))
                    elif hr_value < VERY_HIGH:
                        very_high += 1
                        very_high_times.append((time_str, hr_value))
                    else:
                        extreme += 1
                        extreme_times.append((time_str, hr_value))

                total_readings = len(hr_values)

                print("\n🎯 HEART RATE ZONES")
                print("-" * 80)
                print(f"Below 70 (LOW):     {below_70:4} readings ({below_70/total_readings*100:5.1f}%) 🔵")
                print(f"Very Low (< 60):    {very_low:4} readings ({very_low/total_readings*100:5.1f}%)")
                print(f"Normal (60-80):     {normal:4} readings ({normal/total_readings*100:5.1f}%)")
                print(f"Elevated (80-100):  {elevated:4} readings ({elevated/total_readings*100:5.1f}%)")
                print(f"High (100-120):     {high:4} readings ({high/total_readings*100:5.1f}%) ⚠️")
                print(f"Vigorous (120-140): {very_high:4} readings ({very_high/total_readings*100:5.1f}%) 💪")
                print(f"High Vigorous (>140):{extreme:4} readings ({extreme/total_readings*100:5.1f}%) 🔥")

                # Show times when HR was BELOW 70 (LOW)
                if below_70_times:
                    print("\n🔵 LOW HEART RATE PERIODS (< 70 BPM)")
                    print("-" * 80)
                    print(f"Total occurrences: {len(below_70_times)}\n")

                    for i, (time_str, hr) in enumerate(below_70_times[:20], 1):  # Show first 20
                        print(f"  {i}. {time_str} - {hr} bpm")
                    if len(below_70_times) > 20:
                        print(f"  ... and {len(below_70_times) - 20} more")

                # Show times when HR was VIGOROUS (> 120 BPM for exercise)
                if very_high_times or extreme_times:
                    print("\n💪 VIGOROUS EXERCISE HEART RATE (> 120 BPM)")
                    print("-" * 80)

                    if very_high_times:
                        print(f"\n💪 Vigorous Zone (120-140 BPM) - {len(very_high_times)} occurrences:")
                        for i, (time_str, hr) in enumerate(very_high_times, 1):
                            print(f"  {i}. {time_str} - {hr} bpm")

                    if extreme_times:
                        print(f"\n🔥 High Vigorous Zone (> 140 BPM) - {len(extreme_times)} occurrences:")
                        for i, (time_str, hr) in enumerate(extreme_times, 1):
                            print(f"  {i}. {time_str} - {hr} bpm")

                # Show other elevated heart rates
                if elevated_times or high_times:
                    print("\n⚠️  ELEVATED HEART RATE PERIODS (80-120 BPM)")
                    print("-" * 80)

                    if elevated_times:
                        print(f"\n80-100 BPM ({len(elevated_times)} occurrences):")
                        for i, (time_str, hr) in enumerate(elevated_times[:10], 1):  # Show first 10
                            print(f"  {i}. {time_str} - {hr} bpm")
                        if len(elevated_times) > 10:
                            print(f"  ... and {len(elevated_times) - 10} more")

                    if high_times:
                        print(f"\n🔴 100-120 BPM ({len(high_times)} occurrences):")
                        for i, (time_str, hr) in enumerate(high_times, 1):
                            print(f"  {i}. {time_str} - {hr} bpm")

                # Health recommendations
                print("\n💡 RECOMMENDATIONS")
                print("-" * 80)

                abnormal_count = high + very_high + extreme
                if extreme > 0:
                    print("🚨 ALERT: Extreme heart rate detected (> 140 bpm)")
                    print("   Consider consulting a healthcare professional if not during exercise.")
                elif very_high > 10:
                    print("⚠️  WARNING: Multiple very high heart rate readings (> 120 bpm)")
                    print("   Monitor your activity and stress levels.")
                elif high > 20:
                    print("⚠️  NOTICE: Elevated heart rate detected frequently (> 100 bpm)")
                    print("   This is normal during exercise, but monitor if at rest.")
                else:
                    print("✅ Heart rate appears normal throughout the day.")

                if resting_hr != 'N/A':
                    if resting_hr > 100:
                        print(f"🚨 Resting HR is elevated ({resting_hr} bpm). Normal is 60-100 bpm.")
                    elif resting_hr > 80:
                        print(f"⚠️  Resting HR is slightly elevated ({resting_hr} bpm).")
                    elif resting_hr < 60:
                        print(f"💪 Excellent resting HR ({resting_hr} bpm) - indicates good fitness!")
                    else:
                        print(f"✅ Resting HR is normal ({resting_hr} bpm).")

            else:
                print("No detailed heart rate readings available")

        else:
            print("No heart rate data available for today")

    except Exception as e:
        print(f"Could not fetch heart rate data: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Heart rate analysis complete!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
