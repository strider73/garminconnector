# Garmin Connect API Functions Reference

All available API calls from `demo.py` organized by category.

## 1. User & Profile

| Key | Function | Description |
|-----|----------|-------------|
| `get_full_name` | `api.get_full_name()` | Get full name |
| `get_unit_system` | `api.get_unit_system()` | Get unit system |
| `get_user_profile` | `api.get_user_profile()` | Get user profile |
| `get_userprofile_settings` | `api.get_userprofile_settings()` | Get userprofile settings |

## 2. Daily Health & Activity

| Key | Function | Description |
|-----|----------|-------------|
| `get_stats` | `api.get_stats(date)` | Get activity data for a date |
| `get_user_summary` | `api.get_user_summary(date)` | Get user summary for a date |
| `get_stats_and_body` | `api.get_stats_and_body(date)` | Get stats and body composition |
| `get_steps_data` | `api.get_steps_data(date)` | Get steps data |
| `get_heart_rates` | `api.get_heart_rates(date)` | Get heart rate data |
| `get_resting_heart_rate` | `api.get_resting_heart_rate(date)` | Get resting heart rate |
| `get_sleep_data` | `api.get_sleep_data(date)` | Get sleep data |
| `get_all_day_stress` | `api.get_all_day_stress(date)` | Get stress data (all day) |
| `get_lifestyle_logging_data` | `api.get_lifestyle_logging_data(date)` | Get lifestyle logging data |

## 3. Advanced Health Metrics

| Key | Function | Description |
|-----|----------|-------------|
| `get_training_readiness` | `api.get_training_readiness(date)` | Get training readiness |
| `get_training_status` | `api.get_training_status(date)` | Get training status |
| `get_respiration_data` | `api.get_respiration_data(date)` | Get respiration data |
| `get_spo2_data` | `api.get_spo2_data(date)` | Get SpO2 data |
| `get_max_metrics` | `api.get_max_metrics(date)` | Get max metrics (VO2, fitness age) |
| `get_hrv_data` | `api.get_hrv_data(date)` | Get Heart Rate Variability (HRV) |
| `get_fitnessage_data` | `api.get_fitnessage_data(date)` | Get Fitness Age data |
| `get_stress_data` | `api.get_stress_data(date)` | Get stress data |
| `get_lactate_threshold` | `api.get_lactate_threshold()` | Get lactate threshold data |
| `get_intensity_minutes_data` | `api.get_intensity_minutes_data(date)` | Get intensity minutes |

## 4. Historical Data & Trends

| Key | Function | Description |
|-----|----------|-------------|
| `get_daily_steps` | `api.get_daily_steps(start, end)` | Get daily steps over date range |
| `get_body_battery` | `api.get_body_battery(start, end)` | Get body battery over date range |
| `get_floors` | `api.get_floors(date)` | Get floors data |
| `get_blood_pressure` | `api.get_blood_pressure(start, end)` | Get blood pressure over date range |
| `get_progress_summary_between_dates` | `api.get_progress_summary_between_dates(start, end)` | Get progress summary |
| `get_body_battery_events` | `api.get_body_battery_events(date)` | Get body battery events |

## 5. Activities & Workouts

| Key | Function | Description |
|-----|----------|-------------|
| `get_activities` | `api.get_activities(start, limit)` | Get recent activities |
| `get_last_activity` | `api.get_last_activity()` | Get last activity |
| `get_activities_fordate` | `api.get_activities_fordate(date)` | Get activities for a date |
| `get_activities_by_date` | `api.get_activities_by_date(start, end, type)` | Get activities by date range |
| `count_activities` | `api.count_activities()` | Count activities for current user |
| `download_activities` | `api.download_activities_by_date(...)` | Download activities by date range |
| `upload_activity` | `api.upload_activity(path)` | Upload activity data from file |
| `get_workouts` | `api.get_workouts(start, limit)` | Get workouts |
| `get_activity_splits` | `api.get_activity_splits(id)` | Get activity splits (laps) |
| `get_activity_typed_splits` | `api.get_activity_typed_splits(id)` | Get activity typed splits |
| `get_activity_split_summaries` | `api.get_activity_split_summaries(id)` | Get activity split summaries |
| `get_activity_weather` | `api.get_activity_weather(id)` | Get activity weather data |
| `get_activity_hr_in_timezones` | `api.get_activity_hr_in_timezones(id)` | Get activity heart rate zones |
| `get_activity_details` | `api.get_activity_details(id)` | Get detailed activity information |
| `get_activity_gear` | `api.get_activity_gear(id)` | Get activity gear information |
| `get_activity` | `api.get_activity(id)` | Get single activity data |
| `get_activity_exercise_sets` | `api.get_activity_exercise_sets(id)` | Get strength training exercise sets |
| `get_workout_by_id` | `api.get_workout_by_id(id)` | Get workout by ID |
| `download_workout` | `api.download_workout(id)` | Download workout to .FIT file |
| `upload_workout` | `api.upload_workout(data)` | Upload workout from JSON file |
| `upload_running_workout` | via `RunningWorkout` | Upload typed running workout |
| `upload_cycling_workout` | via `CyclingWorkout` | Upload typed cycling workout |
| `upload_swimming_workout` | via `SwimmingWorkout` | Upload typed swimming workout |
| `upload_walking_workout` | via `WalkingWorkout` | Upload typed walking workout |
| `upload_hiking_workout` | via `HikingWorkout` | Upload typed hiking workout |
| `get_scheduled_workout_by_id` | `api.get_scheduled_workout_by_id(id)` | Get scheduled workout by ID |
| `set_activity_name` | `api.set_activity_name(id, name)` | Set activity name |
| `set_activity_type` | `api.set_activity_type(id, type)` | Set activity type |
| `create_manual_activity` | `api.create_manual_activity(...)` | Create manual activity |
| `delete_activity` | `api.delete_activity(id)` | Delete activity |

## 6. Body Composition & Weight

| Key | Function | Description |
|-----|----------|-------------|
| `get_body_composition` | `api.get_body_composition(date)` | Get body composition |
| `get_weigh_ins` | `api.get_weigh_ins(start, end)` | Get weigh-ins over date range |
| `get_daily_weigh_ins` | `api.get_daily_weigh_ins(date)` | Get daily weigh-ins |
| `add_weigh_in` | `api.add_weigh_in(...)` | Add a weigh-in (interactive) |
| `set_body_composition` | `api.set_body_composition(...)` | Set body composition data |
| `add_body_composition` | `api.add_body_composition(...)` | Add body composition data |
| `delete_weigh_ins` | `api.delete_weigh_ins(date)` | Delete all weigh-ins for a date |
| `delete_weigh_in` | `api.delete_weigh_in(...)` | Delete a specific weigh-in |

## 7. Goals & Achievements

| Key | Function | Description |
|-----|----------|-------------|
| `get_personal_records` | `api.get_personal_records()` | Get personal records |
| `get_earned_badges` | `api.get_earned_badges()` | Get earned badges |
| `get_adhoc_challenges` | `api.get_adhoc_challenges(start, limit)` | Get adhoc challenges |
| `get_available_badge_challenges` | `api.get_available_badge_challenges(start, limit)` | Get available badge challenges |
| `get_active_goals` | `api.get_active_goals()` | Get active goals |
| `get_future_goals` | `api.get_future_goals()` | Get future goals |
| `get_past_goals` | `api.get_past_goals()` | Get past goals |
| `get_badge_challenges` | `api.get_badge_challenges(start, limit)` | Get badge challenges |
| `get_non_completed_badge_challenges` | `api.get_non_completed_badge_challenges(start, limit)` | Get non-completed badge challenges |
| `get_inprogress_virtual_challenges` | `api.get_inprogress_virtual_challenges(start, limit)` | Get virtual challenges in progress |
| `get_race_predictions` | `api.get_race_predictions()` | Get race predictions |
| `get_hill_score` | `api.get_hill_score(start, end)` | Get hill score |
| `get_endurance_score` | `api.get_endurance_score(start, end)` | Get endurance score |
| `get_available_badges` | `api.get_available_badges()` | Get available badges |
| `get_in_progress_badges` | `api.get_in_progress_badges()` | Get badges in progress |

## 8. Device & Technical

| Key | Function | Description |
|-----|----------|-------------|
| `get_devices` | `api.get_devices()` | Get all device information |
| `get_device_alarms` | `api.get_device_alarms()` | Get device alarms |
| `get_solar_data` | (custom function) | Get solar data from your devices |
| `request_reload` | `api.request_reload(date)` | Request data reload (epoch) |
| `get_device_settings` | `api.get_device_settings(id)` | Get device settings |
| `get_device_last_used` | `api.get_device_last_used()` | Get device last used |
| `get_primary_training_device` | `api.get_primary_training_device()` | Get primary training device |

## 9. Gear & Equipment

| Key | Function | Description |
|-----|----------|-------------|
| `get_gear` | `api.get_gear(uuid)` | Get user gear list |
| `get_gear_defaults` | `api.get_gear_defaults(uuid)` | Get gear defaults |
| `get_gear_stats` | `api.get_gear_stats(uuid)` | Get gear statistics |
| `get_gear_activities` | `api.get_gear_activities(uuid, start, limit)` | Get gear activities |
| `set_gear_default` | `api.set_gear_default(uuid, type, default)` | Set gear default |
| `track_gear_usage` | (custom function) | Track gear usage (total time used) |
| `add_and_remove_gear_to_activity` | `api.add_gear_to_activity(...)` / `api.remove_gear_from_activity(...)` | Add/remove gear to activity |

## 10. Hydration & Wellness

| Key | Function | Description |
|-----|----------|-------------|
| `get_hydration_data` | `api.get_hydration_data(date)` | Get hydration data |
| `add_hydration_data` | `api.add_hydration_data(value, date)` | Add hydration data |
| `set_blood_pressure` | `api.set_blood_pressure(...)` | Set blood pressure and pulse |
| `delete_blood_pressure` | `api.delete_blood_pressure(...)` | Delete blood pressure entry |
| `get_pregnancy_summary` | `api.get_pregnancy_summary()` | Get pregnancy summary data |
| `get_all_day_events` | `api.get_all_day_events(date)` | Get all day events |
| `get_body_battery_events` | `api.get_body_battery_events(date)` | Get body battery events |
| `get_menstrual_data_for_date` | `api.get_menstrual_data_for_date(date)` | Get menstrual data |
| `get_menstrual_calendar_data` | `api.get_menstrual_calendar_data(start, end)` | Get menstrual calendar |

## 11. Training Plans

| Key | Function | Description |
|-----|----------|-------------|
| `get_training_plans` | `api.get_training_plans()` | Get training plans |
| `get_training_plan_by_id` | `api.get_training_plan_by_id(id)` | Get training plan by ID |

## 12. System & Export

| Key | Function | Description |
|-----|----------|-------------|
| `create_health_report` | (custom function) | Create sample health report |
| `remove_tokens` | (custom function) | Remove stored login tokens (logout) |
| `disconnect` | `api.logout()` | Disconnect from Garmin Connect |
| `query_garmin_graphql` | `api.garmin_graphql(query)` | Execute GraphQL query |
