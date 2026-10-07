import math
from datetime import date, time
from decimal import Decimal

from database import _connect, _set_rls_identity

SAMPLE_PATIENT_ID = "sample_patient"
START_DATE = date(2026, 6, 29)
RECORD_COUNT = 100


def _daily_summary(offset: int) -> tuple:
    entry_date = date.fromordinal(START_DATE.toordinal() + offset)
    baseline_pain = max(
        2,
        min(
            9,
            round(6.2 - offset * 0.025 + 0.65 * math.sin(offset * 2 * math.pi / 23)),
        ),
    )
    sleep_hours = Decimal(
        f"{6.0 + offset * 0.015 + 0.4 * math.sin(offset * 2 * math.pi / 19):.2f}"
    )
    sleep_quality = max(
        1,
        min(
            10,
            round(5.0 + offset * 0.025 + 0.8 * math.sin(offset * 2 * math.pi / 17)),
        ),
    )
    exercise_done = offset % 4 != 0
    medication_taken = offset % 5 == 0
    return (
        SAMPLE_PATIENT_ID,
        entry_date,
        sleep_hours,
        sleep_quality,
        "Both Morning and Evening",
        max(1, baseline_pain - 1),
        max(5, 48 - offset // 2 + offset % 7),
        max(1, baseline_pain - 2),
        max(3, 31 - offset // 3 + offset % 5),
        min(10, baseline_pain + 1),
        baseline_pain,
        max(0, baseline_pain - 1),
        baseline_pain,
        20 + offset // 2 + (offset % 7) * 3,
        Decimal(f"{max(2.0, 8.5 - offset * 0.008):.2f}"),
        offset % 3 == 0,
        35 + offset % 6 * 5,
        exercise_done,
        20 + offset % 5 * 5 if exercise_done else None,
        medication_taken,
        "Mock medication A" if medication_taken else None,
        1 + offset % 3 if medication_taken else None,
        offset % 6 in {1, 2},
        offset % 8 != 0,
        offset % 9 == 0,
        "Synthetic demonstration entry; not a real patient's health record.",
    )


def _activity(offset: int, daily_pain: int) -> tuple:
    entry_date = date.fromordinal(START_DATE.toordinal() + offset)
    activity_types = (
        "Walking",
        "Gentle stretching",
        "Household tasks",
        "Desk work",
    )
    activity_type = activity_types[offset % len(activity_types)]
    pain_before = min(10, daily_pain + (1 if activity_type == "Household tasks" else 0))
    pain_during = min(10, pain_before + (1 if offset % 5 == 0 else 0))
    pain_after_30mins = max(0, pain_during - (1 if offset % 4 != 0 else 0))
    pain_after_2hrs = max(0, pain_before - (1 if offset % 3 != 0 else 0))
    return (
        SAMPLE_PATIENT_ID,
        entry_date,
        time(8 + offset % 10, (offset * 7) % 60),
        activity_type,
        15 + offset % 6 * 5,
        None,
        pain_before,
        pain_during,
        pain_after_30mins,
        pain_after_2hrs,
        f"synthetic:sample_patient:{entry_date.isoformat()}:0",
    )


def _pain_characteristics(offset: int, daily_pain: int) -> tuple:
    entry_date = date.fromordinal(START_DATE.toordinal() + offset)
    secondary_locations = ("Left hip", "Right hip", "Upper back", "None")
    return (
        SAMPLE_PATIENT_ID,
        entry_date,
        "Lower back",
        secondary_locations[offset % len(secondary_locations)],
        daily_pain,
        max(0, daily_pain - 2),
        offset % 6 == 0,
        "Diffuse" if offset % 3 else "Pinpoint",
        "Deep" if offset % 2 else "Surface",
    )


def _insert_daily_summary(cursor, values: tuple) -> tuple[int, bool]:
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
            abnormal_fatigue_bool, adequate_hydration_bool, exhausting_day_bool,
            overall_description
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (patient_id, entry_date) DO NOTHING
        RETURNING id
        """,
        values,
    )
    inserted = cursor.fetchone()
    if inserted is not None:
        return inserted[0], True

    cursor.execute(
        """
        SELECT id, sleep_hours, sleep_quality, stiffness_time,
               morning_stiffness_degree, morning_stiffness_mins,
               evening_stiffness_degree, evening_stiffness_mins,
               morning_pain, afternoon_pain, evening_pain, night_pain,
               total_walking_mins, sitting_hours, lumbar_support_type_seat_bool,
               standing_mins, exercise_done_bool, exercise_minutes,
               medication_taken_bool, medication_name, medication_frequency,
               abnormal_fatigue_bool, adequate_hydration_bool, exhausting_day_bool,
               overall_description
        FROM daily_summary_logs
        WHERE patient_id = %s AND entry_date = %s
        """,
        values[:2],
    )
    existing = cursor.fetchone()
    if existing is None or tuple(existing[1:]) != values[2:]:
        raise ValueError(
            f"Existing sample_patient daily summary for {values[1]} differs "
            "from the synthetic seed; no existing data was overwritten."
        )
    return existing[0], False


def _insert_pain_characteristics(cursor, values: tuple) -> tuple[int, bool]:
    cursor.execute(
        """
        INSERT INTO pain_characteristics (
            patient_id, entry_date, primary_location, secondary_location,
            pain_intensity, pain_intensity_2, radiation, pinpoint_or_diffuse,
            deep_or_surface
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (patient_id, entry_date) DO NOTHING
        RETURNING id
        """,
        values,
    )
    inserted = cursor.fetchone()
    if inserted is not None:
        return inserted[0], True

    cursor.execute(
        """
        SELECT id, primary_location, secondary_location, pain_intensity,
               pain_intensity_2, radiation, pinpoint_or_diffuse, deep_or_surface
        FROM pain_characteristics
        WHERE patient_id = %s AND entry_date = %s
        """,
        values[:2],
    )
    existing = cursor.fetchone()
    if existing is None or tuple(existing[1:]) != values[2:]:
        raise ValueError(
            f"Existing sample_patient pain record for {values[1]} differs "
            "from the synthetic seed; no existing data was overwritten."
        )
    return existing[0], False


def _insert_activity(cursor, values: tuple) -> bool:
    cursor.execute(
        """
        INSERT INTO activity_logs (
            patient_id, entry_date, time_of_day, activity_type, duration_mins,
            repetitions, pain_before, pain_during, pain_after_30mins,
            pain_after_2hrs, source_record_key
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (patient_id, source_record_key) DO NOTHING
        RETURNING id
        """,
        values,
    )
    if cursor.fetchone() is not None:
        return True

    cursor.execute(
        """
        SELECT entry_date, time_of_day, activity_type, duration_mins,
               repetitions, pain_before, pain_during, pain_after_30mins,
               pain_after_2hrs, source_record_key
        FROM activity_logs
        WHERE patient_id = %s AND source_record_key = %s
        """,
        (values[0], values[-1]),
    )
    existing = cursor.fetchone()
    if existing is None or tuple(existing) != values[1:]:
        raise ValueError(
            f"Existing sample_patient activity {values[-1]} differs from the "
            "synthetic seed; no existing data was overwritten."
        )
    return False


def seed_sample_data() -> dict[str, int]:
    inserted_counts = {"daily summaries": 0, "activities": 0, "pain records": 0}
    with _connect() as connection:
        with connection.cursor() as cursor:
            _set_rls_identity(cursor, SAMPLE_PATIENT_ID)
            cursor.execute(
                """
                INSERT INTO patients (patient_id, care_team_label)
                VALUES (%s, %s)
                ON CONFLICT (patient_id) DO NOTHING
                """,
                (SAMPLE_PATIENT_ID, "Synthetic demonstration patient"),
            )

            for offset in range(RECORD_COUNT):
                daily_values = _daily_summary(offset)
                baseline_pain = daily_values[10]
                daily_id, was_inserted = _insert_daily_summary(cursor, daily_values)
                inserted_counts["daily summaries"] += int(was_inserted)

                cursor.execute(
                    """
                    INSERT INTO daily_summary_pain_regions (daily_summary_id, pain_region)
                    VALUES (%s, %s), (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (daily_id, "Lower back", daily_id, "Hip"),
                )
                if daily_values[17]:
                    cursor.execute(
                        """
                        INSERT INTO daily_summary_exercises (
                            daily_summary_id, exercise_type
                        )
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (daily_id, "Gentle mobility"),
                    )

                pain_values = _pain_characteristics(offset, baseline_pain)
                pain_id, was_inserted = _insert_pain_characteristics(
                    cursor, pain_values
                )
                inserted_counts["pain records"] += int(was_inserted)
                pain_types = ["DULL", "STIFF"]
                if offset % 4 == 0:
                    pain_types.append("SHARP")
                if offset % 7 == 0:
                    pain_types.append("THROB")
                cursor.executemany(
                    """
                    INSERT INTO pain_characteristic_types (
                        pain_characteristic_id, pain_type_code
                    )
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    [(pain_id, pain_type) for pain_type in pain_types],
                )

                activity_values = _activity(offset, baseline_pain)
                inserted_counts["activities"] += int(
                    _insert_activity(cursor, activity_values)
                )

    return inserted_counts


def main() -> None:
    inserted_counts = seed_sample_data()
    inserted_total = sum(inserted_counts.values())
    print(
        f"Seeded {inserted_total} core synthetic records for "
        f"{SAMPLE_PATIENT_ID!r}: "
        + ", ".join(f"{count} {label}" for label, count in inserted_counts.items())
        + ". Existing rows were preserved."
    )


if __name__ == "__main__":
    main()
