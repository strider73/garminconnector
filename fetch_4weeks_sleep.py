from garminconnect import Garmin
import garth
import os
from datetime import date, timedelta, datetime
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

    # Get date range for last 4 weeks (28 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=28)

    print(f"📅 Fetching sleep data from {start_date} to {end_date}")
    print(f"   (Last 4 weeks / 28 days)\n")
    print("=" * 80)

    # Fetch sleep data for each day
    total_days = 0
    total_sleep_hours = 0
    total_deep_sleep = 0
    total_light_sleep = 0
    total_rem_sleep = 0
    total_awake = 0

    sleep_records = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()

        try:
            sleep_data = garmin.get_sleep_data(date_str)

            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})

                # Get sleep metrics (in seconds)
                sleep_seconds = daily_sleep.get('sleepTimeSeconds', 0)
                deep_sleep_seconds = daily_sleep.get('deepSleepSeconds', 0)
                light_sleep_seconds = daily_sleep.get('lightSleepSeconds', 0)
                rem_sleep_seconds = daily_sleep.get('remSleepSeconds', 0)
                awake_seconds = daily_sleep.get('awakeSleepSeconds', 0)

                # Sleep score (if available)
                sleep_score = daily_sleep.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')

                # Sleep start and end times
                sleep_start_timestamp = daily_sleep.get('sleepStartTimestampGMT')
                sleep_end_timestamp = daily_sleep.get('sleepEndTimestampGMT')

                # Convert timestamps to readable format
                if sleep_start_timestamp:
                    sleep_start_time = datetime.fromtimestamp(sleep_start_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    sleep_start_time = 'N/A'

                if sleep_end_timestamp:
                    sleep_end_time = datetime.fromtimestamp(sleep_end_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    sleep_end_time = 'N/A'

                # Convert to hours and minutes
                sleep_hours = sleep_seconds / 3600
                deep_sleep_mins = deep_sleep_seconds / 60
                light_sleep_mins = light_sleep_seconds / 60
                rem_sleep_mins = rem_sleep_seconds / 60
                awake_mins = awake_seconds / 60

                # Store record
                sleep_records.append({
                    'date': date_str,
                    'sleep_start': sleep_start_time,
                    'sleep_end': sleep_end_time,
                    'sleep_hours': sleep_hours,
                    'deep_sleep': deep_sleep_mins,
                    'light_sleep': light_sleep_mins,
                    'rem_sleep': rem_sleep_mins,
                    'awake': awake_mins,
                    'sleep_score': sleep_score
                })

                # Add to totals
                total_days += 1
                total_sleep_hours += sleep_hours
                total_deep_sleep += deep_sleep_mins
                total_light_sleep += light_sleep_mins
                total_rem_sleep += rem_sleep_mins
                total_awake += awake_mins

                # Print daily data
                print(f"\n📅 {date_str} ({current_date.strftime('%A')})")
                print(f"   Sleep Start: {sleep_start_time}")
                print(f"   Sleep End:   {sleep_end_time}")
                print(f"   Sleep Score: {sleep_score}")
                print(f"   Total Sleep: {sleep_hours:.2f} hours ({sleep_seconds / 60:.0f} mins)")
                print(f"   Deep Sleep:  {deep_sleep_mins:.0f} mins")
                print(f"   Light Sleep: {light_sleep_mins:.0f} mins")
                print(f"   REM Sleep:   {rem_sleep_mins:.0f} mins")
                print(f"   Awake:       {awake_mins:.0f} mins")

            else:
                print(f"\n📅 {date_str} ({current_date.strftime('%A')})")
                print(f"   No sleep data available")

        except Exception as e:
            print(f"\n📅 {date_str} ({current_date.strftime('%A')})")
            print(f"   Error fetching data: {e}")

        # Move to next day
        current_date += timedelta(days=1)

    # Print summary statistics
    print("\n" + "=" * 80)
    print("\n📊 4-WEEK SUMMARY")
    print("-" * 80)

    if total_days > 0:
        avg_sleep = total_sleep_hours / total_days
        avg_deep = total_deep_sleep / total_days
        avg_light = total_light_sleep / total_days
        avg_rem = total_rem_sleep / total_days
        avg_awake = total_awake / total_days

        print(f"Days with data: {total_days} / 29 days")
        print(f"\nAverage Sleep Duration: {avg_sleep:.2f} hours ({avg_sleep * 60:.0f} mins)")
        print(f"Average Deep Sleep:     {avg_deep:.0f} mins")
        print(f"Average Light Sleep:    {avg_light:.0f} mins")
        print(f"Average REM Sleep:      {avg_rem:.0f} mins")
        print(f"Average Awake Time:     {avg_awake:.0f} mins")

        print(f"\nTotal Sleep (4 weeks):  {total_sleep_hours:.1f} hours")

        # Find best and worst sleep days
        if sleep_records:
            best_sleep = max(sleep_records, key=lambda x: x['sleep_hours'])
            worst_sleep = min(sleep_records, key=lambda x: x['sleep_hours'])

            print(f"\n🏆 Best Sleep: {best_sleep['date']} - {best_sleep['sleep_hours']:.2f} hours")
            print(f"😴 Worst Sleep: {worst_sleep['date']} - {worst_sleep['sleep_hours']:.2f} hours")
    else:
        print("No sleep data available for the selected period")

    print("\n✅ 4-week sleep data fetch complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
