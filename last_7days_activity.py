from garminconnect import Garmin
import garth
import os
from datetime import date, timedelta, datetime
from config import email, password, MODERATE_MIN, MODERATE_MAX, VIGOROUS_MIN

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

    # Get date range for last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=6)  # 6 days ago + today = 7 days

    print(f"{'=' * 50}")
    print(f"🏃 LAST 7 DAYS RUNNING SUMMARY")
    print(f"   {start_date} to {end_date}")
    print(f"{'=' * 50}\n")

    # Track totals
    total_steps = 0
    total_distance = 0
    total_calories = 0
    total_sleep = 0
    total_activities = 0
    days_with_data = 0

    # Loop through each day
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        day_name = current_date.strftime('%A')

        print(f"\n{'─' * 50}")
        print(f"📅 {date_str} ({day_name})")
        print(f"{'─' * 50}")

        # Get daily stats
        try:
            stats = garmin.get_stats(date_str)

            if stats:
                days_with_data += 1

                steps = stats.get('totalSteps', 0)
                distance_km = stats.get('totalDistanceMeters', 0) / 1000
                calories = stats.get('totalKilocalories', 0)
                floors = stats.get('floorsClimbed', 0)

                total_steps += steps
                total_distance += distance_km
                total_calories += calories

                # Get heart rate data for the day
                avg_hr_moderate = None
                avg_hr_vigorous = None
                moderate_mins = 0
                vigorous_mins = 0
                max_hr = None
                max_hr_time = None
                moderate_periods = []
                vigorous_periods = []

                try:
                    heart_rate = garmin.get_heart_rates(date_str)
                    if heart_rate:
                        max_hr = heart_rate.get('maxHeartRate')
                        hr_values = heart_rate.get('heartRateValues', [])

                        if hr_values:
                            # First, collect vigorous data and track vigorous hours
                            vigorous_hrs = []
                            vigorous_timestamps = set()
                            for timestamp, hr in hr_values:
                                if hr and hr >= VIGOROUS_MIN:
                                    vigorous_hrs.append(hr)
                                    vigorous_timestamps.add(timestamp)

                            # Then collect moderate data ONLY from non-vigorous timestamps
                            moderate_hrs = []
                            for timestamp, hr in hr_values:
                                if hr and MODERATE_MIN <= hr < MODERATE_MAX and timestamp not in vigorous_timestamps:
                                    moderate_hrs.append(hr)

                            if moderate_hrs:
                                avg_hr_moderate = sum(moderate_hrs) / len(moderate_hrs)
                                moderate_mins = len(moderate_hrs)  # Each reading ≈ 1 minute
                            if vigorous_hrs:
                                avg_hr_vigorous = sum(vigorous_hrs) / len(vigorous_hrs)
                                vigorous_mins = len(vigorous_hrs)  # Each reading ≈ 1 minute

                            # Find when max HR occurred
                            if max_hr:
                                for timestamp, hr in hr_values:
                                    if hr == max_hr:
                                        max_hr_time = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M')
                                        break

                            # Find time periods - vigorous takes priority over moderate
                            current_vigorous_start = None
                            vigorous_hours = set()  # Track which hours had vigorous activity

                            # First pass: collect vigorous periods
                            for i, (timestamp, hr) in enumerate(hr_values):
                                if hr is None:
                                    continue

                                time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M')

                                # Track vigorous periods
                                if hr >= VIGOROUS_MIN:
                                    if current_vigorous_start is None:
                                        current_vigorous_start = time_str
                                    # Track the hour for this vigorous activity
                                    hour = int(time_str.split(':')[0])
                                    vigorous_hours.add(hour)
                                else:
                                    if current_vigorous_start is not None:
                                        vigorous_periods.append((current_vigorous_start, time_str))
                                        current_vigorous_start = None

                            # Close any open vigorous period
                            if current_vigorous_start:
                                vigorous_periods.append((current_vigorous_start, time_str))

                            # Second pass: collect moderate periods ONLY if not in vigorous hours
                            current_moderate_start = None
                            for i, (timestamp, hr) in enumerate(hr_values):
                                if hr is None:
                                    continue

                                time_str = datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M')
                                hour = int(time_str.split(':')[0])

                                # Only track moderate if this hour didn't have vigorous activity
                                if MODERATE_MIN <= hr < MODERATE_MAX and hour not in vigorous_hours:
                                    if current_moderate_start is None:
                                        current_moderate_start = time_str
                                else:
                                    if current_moderate_start is not None:
                                        moderate_periods.append((current_moderate_start, time_str))
                                        current_moderate_start = None

                            # Close any open moderate period
                            if current_moderate_start:
                                moderate_periods.append((current_moderate_start, time_str))

                except:
                    pass

                print(f"\n📈 Daily Stats:")
                print(f"   Steps:              {steps:,}")
                print(f"   Distance:           {distance_km:.2f} km")
                print(f"   Calories:           {calories:,} kcal")

                # Print intensity with time periods (merged by hour)
                intensity_parts = []

                # Only show moderate if there are actual moderate periods
                if moderate_mins > 0 and moderate_periods:
                    moderate_text = f"{moderate_mins} moderate"
                    if avg_hr_moderate:
                        moderate_text += f" (avg {avg_hr_moderate:.0f} bpm)"
                    # Extract hours and merge
                    hours = set()
                    for start, end in moderate_periods:
                        start_hour = int(start.split(':')[0])
                        end_hour = int(end.split(':')[0])
                        for h in range(start_hour, end_hour + 1):
                            hours.add(h)
                    if hours:
                        hour_ranges = sorted(hours)
                        # Group consecutive hours
                        ranges = []
                        start_range = hour_ranges[0]
                        end_range = hour_ranges[0]
                        for h in hour_ranges[1:]:
                            if h == end_range + 1:
                                end_range = h
                            else:
                                ranges.append(f"{start_range:02d}:00-{end_range+1:02d}:00")
                                start_range = h
                                end_range = h
                        ranges.append(f"{start_range:02d}:00-{end_range+1:02d}:00")
                        moderate_text += f" @ {', '.join(ranges)}"
                    intensity_parts.append(moderate_text)

                # Always show vigorous if present
                if vigorous_mins > 0:
                    vigorous_text = f"{vigorous_mins} vigorous"
                    if avg_hr_vigorous:
                        vigorous_text += f" (avg {avg_hr_vigorous:.0f} bpm)"
                    if vigorous_periods:
                        # Extract hours and merge
                        hours = set()
                        for start, end in vigorous_periods:
                            start_hour = int(start.split(':')[0])
                            end_hour = int(end.split(':')[0])
                            for h in range(start_hour, end_hour + 1):
                                hours.add(h)
                        if hours:
                            hour_ranges = sorted(hours)
                            # Group consecutive hours
                            ranges = []
                            start_range = hour_ranges[0]
                            end_range = hour_ranges[0]
                            for h in hour_ranges[1:]:
                                if h == end_range + 1:
                                    end_range = h
                                else:
                                    ranges.append(f"{start_range:02d}:00-{end_range+1:02d}:00")
                                    start_range = h
                                    end_range = h
                            ranges.append(f"{start_range:02d}:00-{end_range+1:02d}:00")
                            vigorous_text += f" @ {', '.join(ranges)}"
                    intensity_parts.append(vigorous_text)

                # Print intensity line
                if intensity_parts:
                    print(f"   Intensity Minutes:  {', '.join(intensity_parts)}")
                else:
                    print(f"   Intensity Minutes:  No intense activity")

                print(f"   Floors Climbed:     {floors}")

                if max_hr:
                    hr_text = f"   Max Heart Rate:     {max_hr} bpm"
                    if max_hr_time:
                        hr_text += f" @ {max_hr_time}"
                    print(hr_text)

        except Exception as e:
            print(f"   Could not fetch stats: {e}")

        # Get sleep data
        try:
            sleep_data = garmin.get_sleep_data(date_str)

            if sleep_data:
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                sleep_seconds = daily_sleep.get('sleepTimeSeconds', 0)
                sleep_hours = sleep_seconds / 3600

                if sleep_hours > 0:
                    total_sleep += sleep_hours

                    sleep_score = daily_sleep.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')

                    # Get sleep start and end times
                    sleep_start_timestamp = daily_sleep.get('sleepStartTimestampGMT')
                    sleep_end_timestamp = daily_sleep.get('sleepEndTimestampGMT')

                    sleep_period = ""
                    if sleep_start_timestamp and sleep_end_timestamp:
                        sleep_start = datetime.fromtimestamp(sleep_start_timestamp / 1000).strftime('%H:%M')
                        sleep_end = datetime.fromtimestamp(sleep_end_timestamp / 1000).strftime('%H:%M')
                        sleep_period = f" ({sleep_start} → {sleep_end})"

                    print(f"\n😴 Sleep:")
                    print(f"   Duration:           {sleep_hours:.2f} hours{sleep_period}")
                    print(f"   Sleep Score:        {sleep_score}")

        except Exception as e:
            print(f"   Could not fetch sleep: {e}")

        # Get activities/workouts for the day - RUNNING ONLY
        try:
            activities = garmin.get_activities_by_date(date_str, date_str)

            if activities:
                # Filter for running activities only
                running_activities = [a for a in activities if 'running' in a.get('activityType', {}).get('typeKey', '').lower()]

                if running_activities:
                    total_activities += len(running_activities)
                    print(f"\n🏃 Running Activities ({len(running_activities)}):")

                    for i, activity in enumerate(running_activities, 1):
                        activity_name = activity.get('activityName', 'Unnamed')
                        start_time = activity.get('startTimeLocal', 'N/A')
                        duration_mins = activity.get('duration', 0) / 60

                        # Extract just the time from start_time (format: 2025-11-15 07:30:00)
                        if start_time != 'N/A' and len(start_time) > 10:
                            time_only = start_time[11:16]  # Get HH:MM
                        else:
                            time_only = 'N/A'

                        print(f"   {i}. {activity_name} @ {time_only}")
                        print(f"      Duration: {duration_mins:.1f} mins", end="")

                        if activity.get('distance'):
                            distance = activity['distance'] / 1000
                            print(f", Distance: {distance:.2f} km", end="")

                            # Calculate pace
                            if duration_mins > 0:
                                pace = duration_mins / distance
                                print(f", Pace: {pace:.2f} min/km", end="")

                        if activity.get('calories'):
                            print(f", Calories: {activity['calories']} kcal", end="")

                        if activity.get('averageHR'):
                            print(f", Avg HR: {activity['averageHR']} bpm", end="")

                        if activity.get('maxHR'):
                            print(f", Max HR: {activity['maxHR']} bpm", end="")

                        print()  # New line

        except Exception as e:
            print(f"   Could not fetch activities: {e}")

        # Move to next day
        current_date += timedelta(days=1)

    # Print 7-day summary
    print(f"\n{'=' * 50}")
    print(f"📊 7-DAY SUMMARY")
    print(f"{'=' * 50}")

    if days_with_data > 0:
        avg_steps = total_steps / days_with_data
        avg_distance = total_distance / days_with_data
        avg_calories = total_calories / days_with_data
        avg_sleep = total_sleep / days_with_data if total_sleep > 0 else 0

        print(f"\nDays with data:      {days_with_data} / 7")
        print(f"\nTotals:")
        print(f"   Total Steps:         {total_steps:,}")
        print(f"   Total Distance:      {total_distance:.2f} km")
        print(f"   Total Calories:      {total_calories:,} kcal")
        print(f"   Total Running Runs:  {total_activities}")
        print(f"   Total Sleep:         {total_sleep:.1f} hours")

        print(f"\nDaily Averages:")
        print(f"   Avg Steps:           {avg_steps:,.0f}")
        print(f"   Avg Distance:        {avg_distance:.2f} km")
        print(f"   Avg Calories:        {avg_calories:,.0f} kcal")
        print(f"   Avg Sleep:           {avg_sleep:.2f} hours")

    else:
        print("No data available for the last 7 days")

    # ===== STAMINA IMPROVEMENT GOALS =====
    if days_with_data > 0:
        print(f"\n{'=' * 50}")
        print("🎯 NEXT DAY STAMINA GOALS (For Tennis)")
        print(f"{'=' * 50}")

        # Calculate weekly vigorous intensity (from summary section)
        total_vigorous_mins = 0
        total_moderate_mins = 0

        # We need to recalculate from daily data with proper exclusion
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            try:
                heart_rate = garmin.get_heart_rates(date_str)
                if heart_rate:
                    hr_values = heart_rate.get('heartRateValues', [])
                    if hr_values:
                        # First collect vigorous and track timestamps
                        vigorous_timestamps = set()
                        for timestamp, hr in hr_values:
                            if hr and hr >= VIGOROUS_MIN:
                                vigorous_timestamps.add(timestamp)
                                total_vigorous_mins += 1

                        # Then collect moderate ONLY from non-vigorous timestamps
                        for timestamp, hr in hr_values:
                            if hr and MODERATE_MIN <= hr < MODERATE_MAX and timestamp not in vigorous_timestamps:
                                total_moderate_mins += 1
            except:
                pass
            current_date += timedelta(days=1)

        # WHO recommendation: 150 mins moderate OR 75 mins vigorous per week
        # For tennis stamina: vigorous intensity is key
        weekly_vigorous_target = 75  # WHO minimum for vigorous
        weekly_moderate_target = 150  # WHO minimum for moderate

        # Calculate daily targets (spread over 5 training days)
        daily_vigorous_target = 15  # 75 / 5 = 15 mins per training day
        daily_moderate_target = 30  # 150 / 5 = 30 mins per training day

        # Current weekly averages
        avg_vigorous = total_vigorous_mins / 7
        avg_moderate = total_moderate_mins / 7

        # Improvement targets (increase by 10% per week, safe progression)
        improvement_rate = 0.10
        next_vigorous_target = int(avg_vigorous * (1 + improvement_rate))
        next_moderate_target = int(avg_moderate * (1 + improvement_rate))

        # IMPORTANT: Never set targets BELOW current performance
        # If already exceeding base targets, continue progressive overload
        if avg_vigorous >= daily_vigorous_target:
            # Already meeting or exceeding base target
            # Keep progressive increase (10% weekly)
            next_vigorous_target = max(next_vigorous_target, int(avg_vigorous * (1 + improvement_rate)))
        else:
            # Below base target, work towards it
            next_vigorous_target = min(next_vigorous_target, daily_vigorous_target)

        if avg_moderate >= daily_moderate_target:
            next_moderate_target = max(next_moderate_target, int(avg_moderate * (1 + improvement_rate)))
        else:
            next_moderate_target = min(next_moderate_target, daily_moderate_target)

        print(f"\n📊 Current Week Performance:")
        print(f"   Avg Vigorous/day:   {avg_vigorous:.0f} mins")
        print(f"   Avg Moderate/day:   {avg_moderate:.0f} mins")
        print(f"   Total Vigorous:     {total_vigorous_mins} mins")
        print(f"   Total Moderate:     {total_moderate_mins} mins")

        print(f"\n🎯 Tomorrow's Training Goals:")
        vigorous_change = next_vigorous_target - avg_vigorous
        moderate_change = next_moderate_target - avg_moderate

        vigorous_symbol = "↑" if vigorous_change > 0 else "→" if vigorous_change == 0 else "↓"
        moderate_symbol = "↑" if moderate_change > 0 else "→" if moderate_change == 0 else "↓"

        print(f"   Vigorous Target:    {next_vigorous_target} mins ({vigorous_symbol}{abs(vigorous_change):.0f} mins)")
        print(f"   Moderate Target:    {next_moderate_target} mins ({moderate_symbol}{abs(moderate_change):.0f} mins)")

        print(f"\n💡 Why These Goals?")
        print(f"   • Tennis requires HIGH INTENSITY bursts")
        print(f"   • Vigorous training (HR {VIGOROUS_MIN}+ bpm) builds:")
        print(f"     - Explosive power for serves & volleys")
        print(f"     - Quick recovery between points")
        print(f"     - Sustained energy in long matches")
        print(f"   • 10% weekly increase = safe progression")
        print(f"   • Prevents overtraining & injury")

        print(f"\n🏃 Training Recommendations:")

        # Check performance level
        vigorous_percentage = (total_vigorous_mins / weekly_vigorous_target) * 100
        moderate_percentage = (total_moderate_mins / weekly_moderate_target) * 100

        if vigorous_percentage >= 200:
            # EXCEPTIONAL: 2x or more above target
            print(f"   🔥 EXCEPTIONAL! {vigorous_percentage:.0f}% of weekly target!")
            print(f"   → You're at ELITE tennis conditioning level")
            print(f"   → Focus on maintaining this intensity")
            print(f"   → Work on technique and match strategy")
            print(f"   → Ensure adequate recovery between sessions")
        elif vigorous_percentage >= 150:
            # EXCELLENT: 1.5x or more above target
            print(f"   💪 EXCELLENT! {vigorous_percentage:.0f}% of weekly target!")
            print(f"   → You're exceeding competitive tennis standards")
            print(f"   → Maintain current level or slight increase")
            print(f"   → Add variety: sprints, plyometrics, agility")
        elif vigorous_percentage >= 100:
            # GOOD: Meeting target
            print(f"   ✅ GOOD! Meeting vigorous intensity target!")
            print(f"   → {vigorous_percentage:.0f}% of weekly target achieved")
            print(f"   → Continue progressive increase (10%/week)")
            print(f"   → Add variety to prevent plateau")
        else:
            # BELOW TARGET
            vigorous_needed = weekly_vigorous_target - total_vigorous_mins
            print(f"   ⚠️  {vigorous_percentage:.0f}% of target - need {vigorous_needed} more mins")
            print(f"   → Focus on high-intensity intervals")
            print(f"   → Sprint drills, agility ladder, burpees")

        # Training plan based on current level
        if avg_vigorous >= daily_vigorous_target * 2:
            print(f"\n   🏆 Elite Training Protocol:")
            print(f"   → Maintain {next_vigorous_target}+ mins vigorous/day")
            print(f"   → Focus on QUALITY over quantity")
            print(f"   → Match simulation & tactical drills")
            print(f"   → Ensure 1-2 rest days per week")
        elif avg_vigorous >= daily_vigorous_target:
            print(f"\n   💪 Advanced Training:")
            print(f"   → Target {next_vigorous_target} mins vigorous tomorrow")
            print(f"   → Mix sprints, agility, and tennis drills")
            print(f"   → Progressive overload: +10% weekly")
            print(f"   → Monitor recovery and sleep")
        else:
            print(f"\n   📈 Stamina Building Plan:")
            print(f"   1. Warm-up: 5-10 mins moderate (jogging)")
            print(f"   2. High-intensity: {next_vigorous_target} mins")
            print(f"      - 30 sec sprint + 30 sec rest (repeat)")
            print(f"      - OR tennis rally drills at match pace")
            print(f"   3. Cool-down: 5 mins light activity")

    print(f"\n{'=' * 50}")
    print("✅ 7-day activity report complete!")
    print(f"{'=' * 50}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
