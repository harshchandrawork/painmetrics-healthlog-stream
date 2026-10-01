import os
import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

import psycopg
from dotenv import load_dotenv
from psycopg.conninfo import conninfo_to_dict


DATABASE_NAME = "symptoms_tracker_db"
PAIN_TYPE_CODES = {
    "Dull ache": "DULL",
    "Sharp pain": "SHARP",
    "Muscle fatigue": "FATIGUE",
    "Stiffness": "STIFF",
    "Burning": "BURN",
    "Throbbing": "THROB",
    "Muscle spasm": "SPASM",
    "Pulling sensation": "PULL",
    "Pressure sensation": "PRESS",
}

LIVE_SCHEMA_MIGRATIONS = (
    "ALTER TABLE patients ADD COLUMN IF NOT EXISTS care_team_label TEXT",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS stiffness_time TEXT",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS morning_stiffness_degree SMALLINT",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS evening_stiffness_degree SMALLINT",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS evening_stiffness_mins INTEGER",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS exercise_done_bool BOOLEAN",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS medication_taken_bool BOOLEAN",
    "ALTER TABLE daily_summary_logs ADD COLUMN IF NOT EXISTS medication_frequency SMALLINT",
)


def _connect() -> psycopg.Connection:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    connection_info = os.getenv("CONN_INFO")
    if not connection_info:
        raise ValueError(
            "Database connection is not configured. Set CONN_INFO in the project .env file."
        )

    connection_parameters = conninfo_to_dict(connection_info)
    connection_parameters["dbname"] = DATABASE_NAME
    return psycopg.connect(**connection_parameters)


def _ensure_live_schema(cursor: psycopg.Cursor) -> None:
    for statement in LIVE_SCHEMA_MIGRATIONS:
        cursor.execute(statement)


def _ensure_patient(
    cursor: psycopg.Cursor,
    patient_id: str,
    care_team_label: str,
) -> None:
    normalized_patient_id = patient_id.strip()
    if not normalized_patient_id:
        raise ValueError("Enter a patient ID on the Home page before saving a log.")
    cursor.execute(
        """
        INSERT INTO patients (patient_id, care_team_label)
        VALUES (%s, %s)
        ON CONFLICT (patient_id) DO UPDATE SET
            care_team_label = COALESCE(
                NULLIF(EXCLUDED.care_team_label, ''),
                patients.care_team_label
            )
        """,
        (normalized_patient_id, care_team_label.strip()),
    )


def _boolean_choice(value: str) -> bool:
    return value == "Yes"


def _pain_regions(value: str) -> list[str]:
    return [region.strip() for region in re.split(r"[;,]", value) if region.strip()]


def save_daily_summary(
    patient_id: str,
    entry_date: date,
    values: Mapping[str, Any],
    care_team_label: str = "",
) -> None:
    stiffness_time = values["stiffness_time"]
    if stiffness_time == "Morning":
        morning_degree = values.get("daily_summary_morning_stiff_degree")
        morning_minutes = values.get("daily_summary_morning_stiff_duration")
        evening_degree = None
        evening_minutes = None
    elif stiffness_time == "Evening":
        morning_degree = None
        morning_minutes = None
        evening_degree = values.get("daily_summary_evening_stiff_degree")
        evening_minutes = values.get("daily_summary_evening_stiff_duration")
    elif stiffness_time == "Both Morning and Evening":
        morning_degree = values.get("daily_summary_both_morning_stiff_degree")
        morning_minutes = values.get("daily_summary_both_morning_stiff_duration")
        evening_degree = values.get("daily_summary_both_evening_stiff_degree")
        evening_minutes = values.get("daily_summary_both_evening_stiff_duration")
    else:
        morning_degree = None
        morning_minutes = None
        evening_degree = None
        evening_minutes = None

    exercise_done = _boolean_choice(values["exercise_done"])
    medication_taken = _boolean_choice(values["medication_taken"])
    sitting_hours = Decimal(values["sitting_minutes"]) / Decimal(60)
    record = (
        patient_id.strip(),
        entry_date,
        values["sleep_hours"],
        values["sleep_quality"],
        stiffness_time,
        morning_degree,
        morning_minutes,
        evening_degree,
        evening_minutes,
        values["morning_pain"],
        values["afternoon_pain"],
        values["evening_pain"],
        values["night_pain"],
        values["walking_minutes"],
        sitting_hours,
        _boolean_choice(values["lumbar_support"]),
        values["standing_minutes"],
        exercise_done,
        values.get("workout_minutes") if exercise_done else None,
        medication_taken,
        values.get("medication_name") if medication_taken else None,
        values.get("medication_frequency") if medication_taken else None,
        _boolean_choice(values["abnormal_fatigue"]),
        _boolean_choice(values["adequate_hydration"]),
        _boolean_choice(values["exhausting_day"]),
        values["overall_description"].strip() or None,
    )

    with _connect() as connection:
        with connection.cursor() as cursor:
            _ensure_live_schema(cursor)
            _ensure_patient(cursor, patient_id, care_team_label)
            cursor.execute(
                """
                INSERT INTO daily_summary_logs (
                    patient_id, entry_date, sleep_hours, sleep_quality, stiffness_time,
                    morning_stiffness_degree, morning_stiffness_mins,
                    evening_stiffness_degree, evening_stiffness_mins,
                    morning_pain, afternoon_pain, evening_pain, night_pain,
                    total_walking_mins, sitting_hours, lumbar_support_type_seat_bool,
                    standing_mins, exercise_done_bool, exercise_minutes,
                    medication_taken_bool, medication_name, medication_frequency,
                    abnormal_fatigue_bool, adequate_hydration_bool,
                    exhausting_day_bool, overall_description
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (patient_id, entry_date) DO UPDATE SET
                    sleep_hours = EXCLUDED.sleep_hours,
                    sleep_quality = EXCLUDED.sleep_quality,
                    stiffness_time = EXCLUDED.stiffness_time,
                    morning_stiffness_degree = EXCLUDED.morning_stiffness_degree,
                    morning_stiffness_mins = EXCLUDED.morning_stiffness_mins,
                    evening_stiffness_degree = EXCLUDED.evening_stiffness_degree,
                    evening_stiffness_mins = EXCLUDED.evening_stiffness_mins,
                    morning_pain = EXCLUDED.morning_pain,
                    afternoon_pain = EXCLUDED.afternoon_pain,
                    evening_pain = EXCLUDED.evening_pain,
                    night_pain = EXCLUDED.night_pain,
                    total_walking_mins = EXCLUDED.total_walking_mins,
                    sitting_hours = EXCLUDED.sitting_hours,
                    lumbar_support_type_seat_bool = EXCLUDED.lumbar_support_type_seat_bool,
                    standing_mins = EXCLUDED.standing_mins,
                    exercise_done_bool = EXCLUDED.exercise_done_bool,
                    exercise_minutes = EXCLUDED.exercise_minutes,
                    medication_taken_bool = EXCLUDED.medication_taken_bool,
                    medication_name = EXCLUDED.medication_name,
                    medication_frequency = EXCLUDED.medication_frequency,
                    abnormal_fatigue_bool = EXCLUDED.abnormal_fatigue_bool,
                    adequate_hydration_bool = EXCLUDED.adequate_hydration_bool,
                    exhausting_day_bool = EXCLUDED.exhausting_day_bool,
                    overall_description = EXCLUDED.overall_description
                RETURNING id
                """,
                record,
            )
            daily_summary_id = cursor.fetchone()[0]
            cursor.execute(
                "DELETE FROM daily_summary_pain_regions WHERE daily_summary_id = %s",
                (daily_summary_id,),
            )
            cursor.executemany(
                """
                INSERT INTO daily_summary_pain_regions (daily_summary_id, pain_region)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                [
                    (daily_summary_id, pain_region)
                    for pain_region in _pain_regions(values["pain_region"])
                ],
            )


def save_activities(
    patient_id: str,
    entry_date: date,
    activities: list[Mapping[str, Any]],
    care_team_label: str = "",
) -> int:
    entries = []
    for index, activity in enumerate(activities):
        activity_type = str(activity["activity_type"]).strip()
        if not activity_type:
            continue

        duration = activity["duration_mins"] or None
        repetitions = activity["repetitions"] or None
        if duration is None and repetitions is None:
            raise ValueError(
                f"Enter a duration or repetition count for activity {index + 1}."
            )
        entries.append(
            (
                patient_id.strip(),
                entry_date,
                activity["time_of_day"],
                activity_type,
                duration,
                repetitions,
                activity["pain_before"],
                activity["pain_during"],
                activity["pain_after_30mins"],
                activity["pain_after_2hrs"],
                f"streamlit:{entry_date.isoformat()}:{index}",
            )
        )

    if not entries:
        raise ValueError("Enter at least one activity before submitting.")

    with _connect() as connection:
        with connection.cursor() as cursor:
            _ensure_live_schema(cursor)
            _ensure_patient(cursor, patient_id, care_team_label)
            cursor.execute(
                """
                DELETE FROM activity_logs
                WHERE patient_id = %s AND source_record_key LIKE %s
                """,
                (patient_id.strip(), f"streamlit:{entry_date.isoformat()}:%"),
            )
            cursor.executemany(
                """
                INSERT INTO activity_logs (
                    patient_id, entry_date, time_of_day, activity_type, duration_mins,
                    repetitions, pain_before, pain_during, pain_after_30mins,
                    pain_after_2hrs, source_record_key
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id, source_record_key) DO UPDATE SET
                    entry_date = EXCLUDED.entry_date,
                    time_of_day = EXCLUDED.time_of_day,
                    activity_type = EXCLUDED.activity_type,
                    duration_mins = EXCLUDED.duration_mins,
                    repetitions = EXCLUDED.repetitions,
                    pain_before = EXCLUDED.pain_before,
                    pain_during = EXCLUDED.pain_during,
                    pain_after_30mins = EXCLUDED.pain_after_30mins,
                    pain_after_2hrs = EXCLUDED.pain_after_2hrs
                """,
                entries,
            )
    return len(entries)


def save_pain_characteristics(
    patient_id: str,
    entry_date: date,
    values: Mapping[str, Any],
    care_team_label: str = "",
) -> None:
    selected_type = values.get("pain_type")
    pain_type_code = PAIN_TYPE_CODES.get(selected_type) if selected_type else None

    with _connect() as connection:
        with connection.cursor() as cursor:
            _ensure_live_schema(cursor)
            _ensure_patient(cursor, patient_id, care_team_label)
            cursor.execute(
                """
                INSERT INTO pain_characteristics (
                    patient_id, entry_date, primary_location, secondary_location,
                    pain_intensity, pain_intensity_2, radiation,
                    pinpoint_or_diffuse, deep_or_surface
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id, entry_date) DO UPDATE SET
                    primary_location = EXCLUDED.primary_location,
                    secondary_location = EXCLUDED.secondary_location,
                    pain_intensity = EXCLUDED.pain_intensity,
                    pain_intensity_2 = EXCLUDED.pain_intensity_2,
                    radiation = EXCLUDED.radiation,
                    pinpoint_or_diffuse = EXCLUDED.pinpoint_or_diffuse,
                    deep_or_surface = EXCLUDED.deep_or_surface
                RETURNING id
                """,
                (
                    patient_id.strip(),
                    entry_date,
                    values["primary_location"].strip() or None,
                    values["secondary_location"].strip() or None,
                    values["primary_intensity"],
                    values["secondary_intensity"],
                    _boolean_choice(values["radiation"]),
                    values["pinpoint_or_diffuse"],
                    values["deep_or_surface"],
                ),
            )
            pain_characteristic_id = cursor.fetchone()[0]
            cursor.execute(
                "DELETE FROM pain_characteristic_types WHERE pain_characteristic_id = %s",
                (pain_characteristic_id,),
            )
            if pain_type_code:
                cursor.execute(
                    """
                    INSERT INTO pain_characteristic_types (
                        pain_characteristic_id, pain_type_code
                    )
                    VALUES (%s, %s)
                    """,
                    (pain_characteristic_id, pain_type_code),
                )
