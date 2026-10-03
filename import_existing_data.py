import csv
import os
from datetime import date, time
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from db_init import (
    DATABASE_NAME,
    connection_parameters,
    create_tables_and_reference_data,
)

DATA_DIRECTORY = Path(__file__).resolve().parent / "sample_data" / "data"
CSV_FILES = {
    "activities": DATA_DIRECTORY / "activities_log.csv",
    "daily_summary": DATA_DIRECTORY / "daily_summary.csv",
    "pain_characteristics": DATA_DIRECTORY / "pain_characteristics.csv",
}


def read_csv(path: Path, required_columns: set[str]):
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} is empty or has no header.")

        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        missing_columns = required_columns.difference(reader.fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{path} is missing required columns: {missing}")

        for line_number, source_row in enumerate(reader, start=2):
            if None in source_row:
                raise ValueError(f"{path}:{line_number} has more values than headers.")

            row = {
                key.strip(): value.strip() if value is not None else ""
                for key, value in source_row.items()
            }
            if not any(row.values()):
                continue
            yield line_number, row


def optional_text(value: str | None) -> str | None:
    if value is None or value.strip().casefold() in {"", "none", "null"}:
        return None
    return value.strip()


def required_text(row: dict[str, str], column: str, path: Path, line: int) -> str:
    value = optional_text(row.get(column))
    if value is None:
        raise ValueError(f"{path}:{line} requires a value for {column!r}.")
    return value


def integer_value(
    row: dict[str, str], column: str, path: Path, line: int, *, nullable: bool = False
) -> int | None:
    value = optional_text(row.get(column))
    if value is None and nullable:
        return None
    if value is None:
        raise ValueError(f"{path}:{line} requires a value for {column!r}.")
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"{path}:{line} has an invalid integer in {column!r}."
        ) from error


def decimal_value(
    row: dict[str, str], column: str, path: Path, line: int
) -> Decimal | None:
    value = optional_text(row.get(column))
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise ValueError(
            f"{path}:{line} has an invalid number in {column!r}."
        ) from error


def boolean_value(
    row: dict[str, str], column: str, path: Path, line: int
) -> bool | None:
    value = optional_text(row.get(column))
    if value is None:
        return None
    normalized = value.casefold()
    if normalized in {"true", "t", "yes", "y", "1"}:
        return True
    if normalized in {"false", "f", "no", "n", "0"}:
        return False
    raise ValueError(f"{path}:{line} has an invalid boolean in {column!r}.")


def date_value(row: dict[str, str], path: Path, line: int) -> date:
    value = required_text(row, "date", path, line)
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{path}:{line} has an invalid date: {value!r}.") from error


def list_value(value: str | None) -> list[str]:
    text = optional_text(value)
    if text is None:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def import_daily_summaries(cursor: psycopg.Cursor, patient_id: str) -> None:
    path = CSV_FILES["daily_summary"]
    required = {
        "date",
        "sleep_hours",
        "sleep_quality_1-10",
        "morning_pain_0-10",
        "afternoon_pain_0-10",
        "evening_pain_0-10",
        "night_pain_0-10",
        "pain_region",
        "morning_stiffness_mins",
        "total_walking_mins",
        "sitting_hours",
        "lumbar_support_type_seat_bool",
        "standing_mins",
        "exercise_minutes",
        "exercise_types",
        "medication_name",
        "abnormal_fatigue_bool",
        "adequate_hydration_bool",
        "exhausting_day_bool",
        "overall_description",
    }
    for line, row in read_csv(path, required):
        cursor.execute(
            """
            INSERT INTO daily_summary_logs (
                patient_id, entry_date, sleep_hours, sleep_quality, morning_pain,
                afternoon_pain, evening_pain, night_pain, morning_stiffness_mins,
                total_walking_mins, sitting_hours,
                lumbar_support_type_seat_bool, standing_mins, exercise_minutes,
                medication_name, abnormal_fatigue_bool, adequate_hydration_bool,
                exhausting_day_bool, overall_description
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (patient_id, entry_date) DO UPDATE SET
                sleep_hours = EXCLUDED.sleep_hours,
                sleep_quality = EXCLUDED.sleep_quality,
                morning_pain = EXCLUDED.morning_pain,
                afternoon_pain = EXCLUDED.afternoon_pain,
                evening_pain = EXCLUDED.evening_pain,
                night_pain = EXCLUDED.night_pain,
                morning_stiffness_mins = EXCLUDED.morning_stiffness_mins,
                total_walking_mins = EXCLUDED.total_walking_mins,
                sitting_hours = EXCLUDED.sitting_hours,
                lumbar_support_type_seat_bool = EXCLUDED.lumbar_support_type_seat_bool,
                standing_mins = EXCLUDED.standing_mins,
                exercise_minutes = EXCLUDED.exercise_minutes,
                medication_name = EXCLUDED.medication_name,
                abnormal_fatigue_bool = EXCLUDED.abnormal_fatigue_bool,
                adequate_hydration_bool = EXCLUDED.adequate_hydration_bool,
                exhausting_day_bool = EXCLUDED.exhausting_day_bool,
                overall_description = EXCLUDED.overall_description
            RETURNING id
            """,
            (
                patient_id,
                date_value(row, path, line),
                decimal_value(row, "sleep_hours", path, line),
                integer_value(row, "sleep_quality_1-10", path, line, nullable=True),
                integer_value(row, "morning_pain_0-10", path, line, nullable=True),
                integer_value(row, "afternoon_pain_0-10", path, line, nullable=True),
                integer_value(row, "evening_pain_0-10", path, line, nullable=True),
                integer_value(row, "night_pain_0-10", path, line, nullable=True),
                integer_value(row, "morning_stiffness_mins", path, line, nullable=True),
                integer_value(row, "total_walking_mins", path, line, nullable=True),
                decimal_value(row, "sitting_hours", path, line),
                boolean_value(row, "lumbar_support_type_seat_bool", path, line),
                integer_value(row, "standing_mins", path, line, nullable=True),
                integer_value(row, "exercise_minutes", path, line, nullable=True),
                optional_text(row["medication_name"]),
                boolean_value(row, "abnormal_fatigue_bool", path, line),
                boolean_value(row, "adequate_hydration_bool", path, line),
                boolean_value(row, "exhausting_day_bool", path, line),
                optional_text(row["overall_description"]),
            ),
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
                for pain_region in list_value(row["pain_region"])
            ],
        )
        cursor.execute(
            "DELETE FROM daily_summary_exercises WHERE daily_summary_id = %s",
            (daily_summary_id,),
        )
        cursor.executemany(
            """
            INSERT INTO daily_summary_exercises (daily_summary_id, exercise_type)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            [
                (daily_summary_id, exercise_type)
                for exercise_type in list_value(row["exercise_types"])
            ],
        )


def import_activities(cursor: psycopg.Cursor, patient_id: str) -> None:
    path = CSV_FILES["activities"]
    required = {
        "date",
        "time_of_day",
        "activity_type",
        "duration_mins",
        "repetitions",
        "pain_before",
        "pain_during",
        "pain_after_30mins",
        "pain_after_2hrs",
    }
    for line, row in read_csv(path, required):
        time_text = required_text(row, "time_of_day", path, line)
        try:
            time_of_day = time.fromisoformat(time_text)
        except ValueError as error:
            raise ValueError(
                f"{path}:{line} has an invalid time: {time_text!r}."
            ) from error

        cursor.execute(
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
            (
                patient_id,
                date_value(row, path, line),
                time_of_day,
                required_text(row, "activity_type", path, line),
                integer_value(row, "duration_mins", path, line, nullable=True),
                integer_value(row, "repetitions", path, line, nullable=True),
                integer_value(row, "pain_before", path, line, nullable=True),
                integer_value(row, "pain_during", path, line, nullable=True),
                integer_value(row, "pain_after_30mins", path, line, nullable=True),
                integer_value(row, "pain_after_2hrs", path, line, nullable=True),
                f"activities_log.csv:{line}",
            ),
        )


def import_pain_characteristics(cursor: psycopg.Cursor, patient_id: str) -> None:
    path = CSV_FILES["pain_characteristics"]
    required = {
        "date",
        "primary_location",
        "secondary_location",
        "pain_intensity",
        "pain_intensity_2",
        "pain_type",
        "radiation",
        "pinpoint_or_diffuse",
        "deep_or_surface",
    }
    for line, row in read_csv(path, required):
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
                patient_id,
                date_value(row, path, line),
                optional_text(row["primary_location"]),
                optional_text(row["secondary_location"]),
                integer_value(row, "pain_intensity", path, line, nullable=True),
                integer_value(row, "pain_intensity_2", path, line, nullable=True),
                boolean_value(row, "radiation", path, line),
                optional_text(row["pinpoint_or_diffuse"]),
                optional_text(row["deep_or_surface"]),
            ),
        )
        pain_characteristic_id = cursor.fetchone()[0]
        cursor.execute(
            "DELETE FROM pain_characteristic_types WHERE pain_characteristic_id = %s",
            (pain_characteristic_id,),
        )
        cursor.executemany(
            """
            INSERT INTO pain_characteristic_types (
                pain_characteristic_id, pain_type_code
            )
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            [
                (pain_characteristic_id, pain_type.upper())
                for pain_type in list_value(row["pain_type"])
            ],
        )


def main() -> None:
    load_dotenv()
    patient_id = os.getenv("IMPORT_PATIENT_ID", "sample_patient").strip()
    if not patient_id:
        raise ValueError("IMPORT_PATIENT_ID cannot be empty.")

    with psycopg.connect(**connection_parameters(DATABASE_NAME)) as connection:
        with connection.cursor() as cursor:
            create_tables_and_reference_data(cursor)
            cursor.execute(
                "INSERT INTO patients (patient_id) VALUES (%s) ON CONFLICT DO NOTHING",
                (patient_id,),
            )
            import_daily_summaries(cursor, patient_id)
            import_activities(cursor, patient_id)
            import_pain_characteristics(cursor, patient_id)

    print(f"Database {DATABASE_NAME!r} is ready; CSV data imported for {patient_id!r}.")


if __name__ == "__main__":
    main()
