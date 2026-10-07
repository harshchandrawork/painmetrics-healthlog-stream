from datetime import date

import pandas as pd
import psycopg
import streamlit as st

from database import get_analysis_data
from user_identity import authenticated_user_id

DAILY_COLUMNS = [
    "entry_date",
    "sleep_hours",
    "sleep_quality",
    "stiffness_time",
    "morning_stiffness_degree",
    "morning_stiffness_mins",
    "evening_stiffness_degree",
    "evening_stiffness_mins",
    "morning_pain",
    "afternoon_pain",
    "evening_pain",
    "night_pain",
    "total_walking_mins",
    "sitting_hours",
    "lumbar_support_type_seat_bool",
    "standing_mins",
    "exercise_done_bool",
    "exercise_minutes",
    "medication_taken_bool",
    "medication_frequency",
    "medication_name",
    "abnormal_fatigue_bool",
    "adequate_hydration_bool",
    "exhausting_day_bool",
    "pain_regions",
    "exercise_types",
]
ACTIVITY_COLUMNS = [
    "entry_date",
    "time_of_day",
    "activity_type",
    "duration_mins",
    "repetitions",
    "pain_before",
    "pain_during",
    "pain_after_30mins",
    "pain_after_2hrs",
]
PAIN_COLUMNS = [
    "entry_date",
    "primary_location",
    "secondary_location",
    "pain_intensity",
    "pain_intensity_2",
    "radiation",
    "pinpoint_or_diffuse",
    "deep_or_surface",
    "pain_types",
]
DAILY_PAIN_COLUMNS = [
    "morning_pain",
    "afternoon_pain",
    "evening_pain",
    "night_pain",
]
ACTIVITY_PAIN_COLUMNS = [
    "pain_before",
    "pain_during",
    "pain_after_30mins",
    "pain_after_2hrs",
]


def _in_date_range(frame: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    entry_dates = pd.to_datetime(frame["entry_date"])
    return frame.loc[
        entry_dates.dt.date.between(start, end)
    ].copy()


def _mean_daily_pain(daily: pd.DataFrame) -> pd.Series:
    return daily[DAILY_PAIN_COLUMNS].mean(axis=1)


def _day_period(hour: int | float) -> str | None:
    if pd.isna(hour):
        return None
    if hour < 6 or hour >= 21:
        return "Night"
    if hour < 12:
        return "Morning"
    if hour < 17:
        return "Afternoon"
    return "Evening"


def _average_label(values: pd.Series, suffix: str) -> str:
    average = values.mean()
    return f"{average:.1f} {suffix}" if pd.notna(average) else "—"


def _show_tracking_coverage(
    daily: pd.DataFrame, activities: pd.DataFrame, pain: pd.DataFrame
) -> None:
    st.subheader("Tracking coverage")
    coverage = pd.DataFrame(
        [
            {
                "Log type": "Daily summary",
                "Records": len(daily),
                "Dates represented": daily["entry_date"].nunique(),
            },
            {
                "Log type": "Activities",
                "Records": len(activities),
                "Dates represented": activities["entry_date"].nunique(),
            },
            {
                "Log type": "Pain characteristics",
                "Records": len(pain),
                "Dates represented": pain["entry_date"].nunique(),
            },
        ]
    )
    st.dataframe(coverage, hide_index=True)

    if daily["entry_date"].nunique() > 1:
        logged_dates = pd.to_datetime(daily["entry_date"]).drop_duplicates().sort_values()
        unlogged_days = logged_dates.diff().dt.days.sub(1).dropna().clip(lower=0)
        gap_count = int(unlogged_days.gt(0).sum())
        longest_gap = int(unlogged_days.max())
        st.metric("Longest gap between daily summaries", f"{longest_gap} days")
        st.caption(
            f"{gap_count} interval(s) had unlogged calendar days between summaries. "
            "This describes saved records and does not imply a required logging schedule."
        )

    completeness_columns = {
        "Sleep hours": "sleep_hours",
        "Sleep quality": "sleep_quality",
        "Morning pain": "morning_pain",
        "Afternoon pain": "afternoon_pain",
        "Evening pain": "evening_pain",
        "Night pain": "night_pain",
        "Walking": "total_walking_mins",
        "Sitting": "sitting_hours",
        "Standing": "standing_mins",
    }
    if not daily.empty:
        completeness = (
            daily[list(completeness_columns.values())]
            .notna()
            .mean()
            .mul(100)
            .rename(index={value: key for key, value in completeness_columns.items()})
            .rename("Completed (%)")
            .sort_values()
        )
        st.markdown("**Daily-summary field completion**")
        st.bar_chart(completeness)
        st.caption(
            "Percentage of saved daily summaries with a value for each field. "
            "This does not score conditional or optional fields."
        )

    non_null_fields = {
        "Daily summary": (
            daily,
            {
                "Sleep hours": "sleep_hours",
                "Sleep quality": "sleep_quality",
                "Morning pain": "morning_pain",
                "Afternoon pain": "afternoon_pain",
                "Evening pain": "evening_pain",
                "Night pain": "night_pain",
                "Walking": "total_walking_mins",
                "Sitting": "sitting_hours",
                "Standing": "standing_mins",
            },
        ),
        "Activities": (
            activities,
            {
                "Activity type": "activity_type",
                "Duration": "duration_mins",
                "Repetitions": "repetitions",
                "Pain before": "pain_before",
                "Pain during": "pain_during",
                "Pain after 30 minutes": "pain_after_30mins",
                "Pain after 2 hours": "pain_after_2hrs",
            },
        ),
        "Pain characteristics": (
            pain,
            {
                "Primary location": "primary_location",
                "Secondary location": "secondary_location",
                "Primary intensity": "pain_intensity",
                "Secondary intensity": "pain_intensity_2",
                "Radiation": "radiation",
                "Pinpoint or diffuse": "pinpoint_or_diffuse",
                "Deep or surface": "deep_or_surface",
            },
        ),
    }
    availability_rows = []
    for log_type, (frame, fields) in non_null_fields.items():
        if frame.empty:
            continue
        for label, column in fields.items():
            availability_rows.append(
                {
                    "Log type": log_type,
                    "Field": label,
                    "Completed (%)": round(frame[column].notna().mean() * 100, 1),
                }
            )
    with st.expander("Field availability across all log types"):
        st.caption(
            "For activity logs, duration and repetitions can be alternatives; "
            "a missing value does not necessarily indicate an incomplete entry."
        )
        st.dataframe(pd.DataFrame(availability_rows), hide_index=True)


def _show_pain_trends(daily: pd.DataFrame, pain: pd.DataFrame) -> None:
    st.subheader("Pain over time")
    pain_trends = daily.set_index("entry_date")[DAILY_PAIN_COLUMNS].rename(
        columns={
            "morning_pain": "Morning",
            "afternoon_pain": "Afternoon",
            "evening_pain": "Evening",
            "night_pain": "Night",
        }
    )
    if not pain.empty:
        characteristic_pain = pain.set_index("entry_date")[
            ["pain_intensity", "pain_intensity_2"]
        ].rename(
            columns={
                "pain_intensity": "Primary pain",
                "pain_intensity_2": "Secondary pain",
            }
        )
        pain_trends = pain_trends.join(characteristic_pain, how="outer")

    if not pain_trends.dropna(how="all").empty:
        st.line_chart(pain_trends.sort_index())
        st.caption("Scores range from 0 to 10. Missing scores are not treated as zero.")
    else:
        st.info("There are no pain ratings in this date range.")


def _show_sleep_and_routine(daily: pd.DataFrame) -> None:
    st.subheader("Sleep and daily routine")
    if daily.empty:
        st.info("There are no daily summaries in this date range.")
        return

    with st.container(horizontal=True):
        st.metric("Average sleep", _average_label(daily["sleep_hours"], "hours"))
        st.metric(
            "Average sleep quality",
            _average_label(daily["sleep_quality"], "/ 10"),
        )
        st.metric(
            "Average daily pain",
            _average_label(_mean_daily_pain(daily), "/ 10"),
        )

    sleep_trends = daily.set_index("entry_date")[
        ["sleep_hours", "sleep_quality"]
    ].rename(
        columns={
            "sleep_hours": "Sleep (hours)",
            "sleep_quality": "Sleep quality",
        }
    )
    st.markdown("**Sleep over time**")
    st.line_chart(sleep_trends.sort_index())

    routine_trends = daily.set_index("entry_date")[
        [
            "total_walking_mins",
            "sitting_hours",
            "standing_mins",
            "exercise_minutes",
        ]
    ].rename(
        columns={
            "total_walking_mins": "Walking (minutes)",
            "sitting_hours": "Sitting (hours)",
            "standing_mins": "Standing (minutes)",
            "exercise_minutes": "Exercise (minutes)",
        }
    )
    st.markdown("**Movement and exercise duration**")
    st.line_chart(routine_trends.sort_index())

    medication_frequency = daily.set_index("entry_date")[
        ["medication_frequency"]
    ].rename(columns={"medication_frequency": "Medication frequency"})
    if medication_frequency["Medication frequency"].notna().any():
        st.markdown("**Medication frequency entered**")
        st.line_chart(medication_frequency.sort_index())

    sleep_pain = daily[["sleep_hours", "sleep_quality"]].copy()
    sleep_pain["Average same-day pain"] = _mean_daily_pain(daily)
    sleep_pain = sleep_pain.dropna(
        subset=["sleep_hours", "Average same-day pain"]
    )
    if not sleep_pain.empty:
        st.markdown("**Sleep and same-day pain**")
        st.scatter_chart(
            sleep_pain,
            x="sleep_hours",
            y="Average same-day pain",
            color="sleep_quality",
            x_label="Sleep (hours)",
            y_label="Average pain (0–10)",
        )
        st.caption(
            "Each point is one daily summary. This is a descriptive comparison, "
            "not evidence that sleep caused a pain change."
        )

    stiffness_severity = daily.set_index("entry_date")[
        ["morning_stiffness_degree", "evening_stiffness_degree"]
    ].rename(
        columns={
            "morning_stiffness_degree": "Morning severity",
            "evening_stiffness_degree": "Evening severity",
        }
    )
    if not stiffness_severity.dropna(how="all").empty:
        st.markdown("**Stiffness reported over time**")
        st.line_chart(stiffness_severity.sort_index())

    stiffness_duration = daily.set_index("entry_date")[
        ["morning_stiffness_mins", "evening_stiffness_mins"]
    ].rename(
        columns={
            "morning_stiffness_mins": "Morning duration (min)",
            "evening_stiffness_mins": "Evening duration (min)",
        }
    )
    if not stiffness_duration.dropna(how="all").empty:
        st.markdown("**Stiffness duration over time**")
        st.line_chart(stiffness_duration.sort_index())

    stiffness_time_counts = daily["stiffness_time"].dropna().value_counts()
    if not stiffness_time_counts.empty:
        st.markdown("**When stiffness was reported**")
        st.bar_chart(stiffness_time_counts)

    context_specs = {
        "Hydration": "adequate_hydration_bool",
        "Fatigue": "abnormal_fatigue_bool",
        "Exhausting day": "exhausting_day_bool",
        "Exercise": "exercise_done_bool",
        "Medication": "medication_taken_bool",
        "Lumbar support": "lumbar_support_type_seat_bool",
    }
    context_rows = []
    daily_with_pain = daily.copy()
    daily_with_pain["average_pain"] = _mean_daily_pain(daily)
    for label, column in context_specs.items():
        observed = daily_with_pain.dropna(subset=[column, "average_pain"])
        if observed.empty:
            continue
        observed = observed.copy()
        observed["Response"] = observed[column].map({True: "Yes", False: "No"})
        grouped = observed.groupby("Response")["average_pain"].agg(["mean", "count"])
        for response, values in grouped.iterrows():
            context_rows.append(
                {
                    "Context": f"{label}: {response}",
                    "Mean daily pain": values["mean"],
                    "Days": int(values["count"]),
                }
            )

    if context_rows:
        st.markdown("**Pain by reported daily context**")
        context = pd.DataFrame(context_rows)
        st.bar_chart(context, x="Context", y="Mean daily pain")
        st.dataframe(context, hide_index=True)
        st.caption(
            "Descriptive averages only. Categories may have few observations and "
            "do not account for other factors."
        )

    exercise_types = daily.explode("exercise_types")["exercise_types"].dropna()
    if not exercise_types.empty:
        st.markdown("**Exercise types recorded**")
        st.bar_chart(exercise_types.value_counts())

    medication_names = daily["medication_name"].dropna().str.split(r"[;,]")
    medication_counts = medication_names.explode().str.strip().value_counts()
    medication_counts = medication_counts[medication_counts.index != ""]
    if not medication_counts.empty:
        st.markdown("**Medication names recorded**")
        st.bar_chart(medication_counts)
        st.caption(
            "Names are shown as entered and may include spelling or formatting "
            "variations."
        )


def _show_activity_response(activities: pd.DataFrame) -> None:
    st.subheader("Activity-related pain")
    if activities.empty:
        st.info("There are no activity logs in this date range.")
        return

    activity_summary = activities[ACTIVITY_PAIN_COLUMNS].mean().rename(
        index={
            "pain_before": "Before",
            "pain_during": "During",
            "pain_after_30mins": "After 30 minutes",
            "pain_after_2hrs": "After 2 hours",
        }
    )
    if activity_summary.notna().any():
        st.bar_chart(activity_summary)
        st.caption(
            f"Mean pain ratings from {len(activities)} activity log(s). "
            "These are not controlled comparisons."
        )

    activities = activities.copy()
    activities["During vs before"] = (
        activities["pain_during"] - activities["pain_before"]
    )
    activities["30 minutes vs before"] = (
        activities["pain_after_30mins"] - activities["pain_before"]
    )
    activities["2 hours vs before"] = (
        activities["pain_after_2hrs"] - activities["pain_before"]
    )
    change_columns = [
        "During vs before",
        "30 minutes vs before",
        "2 hours vs before",
    ]
    changes = activities[change_columns].mean()
    if changes.notna().any():
        st.markdown("**Average change from pre-activity pain**")
        st.bar_chart(changes)
        st.caption(
            "Positive values mean a higher reported score than before the activity; "
            "negative values mean a lower score."
        )

    if "time_of_day" in activities:
        activity_hours = pd.to_datetime(
            activities["time_of_day"].astype(str),
            format="mixed",
            errors="coerce",
        ).dt.hour
        activities["Time of day"] = activity_hours.map(_day_period)
        by_time = activities.groupby("Time of day", observed=False)[
            ACTIVITY_PAIN_COLUMNS
        ].mean()
        if not by_time.dropna(how="all").empty:
            st.markdown("**Activity pain ratings by time of day**")
            st.line_chart(
                by_time.rename(
                    columns={
                        "pain_before": "Before",
                        "pain_during": "During",
                        "pain_after_30mins": "After 30 minutes",
                        "pain_after_2hrs": "After 2 hours",
                    }
                )
            )

    by_activity = (
        activities.groupby("activity_type", dropna=False)
        .agg(
            Activities=("activity_type", "size"),
            Mean_duration_minutes=("duration_mins", "mean"),
            Mean_repetitions=("repetitions", "mean"),
            Mean_pain_before=("pain_before", "mean"),
            Mean_pain_during=("pain_during", "mean"),
            Mean_pain_after_30_minutes=("pain_after_30mins", "mean"),
            Mean_pain_after_2_hours=("pain_after_2hrs", "mean"),
            Mean_change_after_2_hours=("2 hours vs before", "mean"),
        )
        .sort_values("Activities", ascending=False)
        .reset_index()
    )
    st.markdown("**Summary by activity type**")
    st.dataframe(by_activity, hide_index=True)


def _show_pain_characteristics(pain: pd.DataFrame, daily: pd.DataFrame) -> None:
    st.subheader("Pain characteristics")
    if pain.empty:
        st.info("There are no pain-characteristic logs in this date range.")
        return

    chart_columns = st.columns(2)
    with chart_columns[0]:
        pain_types = pain.explode("pain_types")
        pain_type_counts = pain_types["pain_types"].dropna().value_counts()
        if not pain_type_counts.empty:
            st.markdown("**Reported pain types**")
            st.bar_chart(pain_type_counts)
        else:
            st.caption("No pain types were selected in this date range.")

    with chart_columns[1]:
        region_counts = daily.explode("pain_regions")["pain_regions"].dropna()
        if not region_counts.empty:
            st.markdown("**Daily-summary pain regions**")
            st.bar_chart(region_counts.value_counts())
        else:
            st.caption("No daily-summary pain regions were entered.")

    primary_locations = pain[["primary_location", "pain_intensity"]].rename(
        columns={"primary_location": "Location", "pain_intensity": "Intensity"}
    )
    secondary_locations = pain[["secondary_location", "pain_intensity_2"]].rename(
        columns={"secondary_location": "Location", "pain_intensity_2": "Intensity"}
    )
    locations = pd.concat(
        [primary_locations, secondary_locations], ignore_index=True
    ).dropna(subset=["Location"])
    locations["Location"] = locations["Location"].astype(str).str.strip()
    locations = locations[locations["Location"] != ""]
    if not locations.empty:
        location_summary = (
            locations.groupby("Location")
            .agg(
                Logs=("Location", "size"),
                Mean_intensity=("Intensity", "mean"),
            )
            .sort_values("Logs", ascending=False)
            .reset_index()
        )
        st.markdown("**Pain locations and recorded intensity**")
        st.bar_chart(location_summary, x="Location", y="Logs")
        st.dataframe(location_summary, hide_index=True)

    categorical_columns = [
        "radiation",
        "pinpoint_or_diffuse",
        "deep_or_surface",
    ]
    category_rows = []
    for column in categorical_columns:
        for response, count in pain[column].value_counts(dropna=True).items():
            category_rows.append(
                {
                    "Characteristic": column.replace("_", " ").title(),
                    "Response": str(response),
                    "Logs": int(count),
                }
            )
    if category_rows:
        st.markdown("**Other reported characteristics**")
        st.dataframe(pd.DataFrame(category_rows), hide_index=True)


def _show_sample_insights(
    daily: pd.DataFrame, activities: pd.DataFrame, pain: pd.DataFrame
) -> None:
    st.subheader("Descriptive highlights from the mock patient")
    highlights = []

    daily_pain = _mean_daily_pain(daily).dropna()
    if not daily_pain.empty:
        highlights.append(
            f"Across {len(daily_pain)} daily summaries, mean recorded daily pain "
            f"was {daily_pain.mean():.1f}/10."
        )
        if len(daily_pain) >= 4:
            midpoint = len(daily_pain) // 2
            first_half_mean = daily_pain.iloc[:midpoint].mean()
            second_half_mean = daily_pain.iloc[midpoint:].mean()
            change = second_half_mean - first_half_mean
            if change < -0.25:
                direction = "lower"
            elif change > 0.25:
                direction = "higher"
            else:
                direction = "similar"
            highlights.append(
                f"Mean daily pain was {first_half_mean:.1f}/10 in the first half "
                f"of the selected period and {second_half_mean:.1f}/10 in the "
                f"second half ({direction} by {abs(change):.1f} points)."
            )

    if not daily.empty:
        daypart_means = daily[DAILY_PAIN_COLUMNS].mean().dropna()
        if not daypart_means.empty:
            peak_period = daypart_means.idxmax().replace("_pain", "")
            highlights.append(
                f"The highest average daily pain rating was reported in the "
                f"{peak_period} ({daypart_means.max():.1f}/10)."
            )

        sleep_pain = daily[["sleep_hours"]].copy()
        sleep_pain["daily_pain"] = _mean_daily_pain(daily)
        sleep_pain = sleep_pain.dropna()
        if len(sleep_pain) >= 6 and sleep_pain["sleep_hours"].nunique() > 1:
            median_sleep = sleep_pain["sleep_hours"].median()
            shorter_sleep = sleep_pain.loc[
                sleep_pain["sleep_hours"] < median_sleep, "daily_pain"
            ]
            longer_sleep = sleep_pain.loc[
                sleep_pain["sleep_hours"] >= median_sleep, "daily_pain"
            ]
            if len(shorter_sleep) >= 3 and len(longer_sleep) >= 3:
                highlights.append(
                    f"Mean daily pain was {shorter_sleep.mean():.1f}/10 on "
                    f"below-median sleep-duration days and "
                    f"{longer_sleep.mean():.1f}/10 on at-or-above-median days. "
                    "This is a descriptive grouping, not evidence of cause."
                )

    activity_ratings = activities[ACTIVITY_PAIN_COLUMNS].mean()
    available_activity_ratings = activity_ratings.dropna()
    if not available_activity_ratings.empty:
        rating_summary = ", ".join(
            f"{label} {value:.1f}/10"
            for label, value in available_activity_ratings.rename(
                {
                    "pain_before": "before",
                    "pain_during": "during",
                    "pain_after_30mins": "after 30 minutes",
                    "pain_after_2hrs": "after 2 hours",
                }
            ).items()
        )
        highlights.append(
            f"Average pain ratings across {len(activities)} activity logs were "
            f"{rating_summary}."
        )

    if not pain.empty:
        primary_locations = pain["primary_location"].dropna().astype(str).str.strip()
        primary_locations = primary_locations[primary_locations != ""]
        if not primary_locations.empty:
            location = primary_locations.value_counts().idxmax()
            count = int(primary_locations.value_counts().iloc[0])
            highlights.append(
                f"{location} was the most frequently recorded primary pain "
                f"location ({count} log(s))."
            )

    if highlights:
        st.markdown("\n".join(f"- {highlight}" for highlight in highlights))
    else:
        st.info(
            "There are not enough non-missing observations in this date range "
            "to produce descriptive highlights."
        )
    st.caption(
        "These findings describe only this synthetic example. They are not "
        "clinical conclusions, diagnoses, or evidence of causation."
    )


def main() -> None:
    is_logged_in = st.user.is_logged_in
    if is_logged_in:
        if st.button("Return Home", icon=":material/home:", type="tertiary"):
            st.switch_page(st.session_state["home_page"])
        patient_id = authenticated_user_id()
        st.title("Your analysis", icon=":material/analytics:")
        st.caption(
            "Explore patterns in your own logs. These summaries are descriptive "
            "and are not medical advice or a diagnosis."
        )
    else:
        patient_id = "sample_patient"
        st.title("Sample patient analysis", icon=":material/analytics:")
        st.info(
            "This public analysis uses only synthetic records created for the mock "
            "patient `sample_patient`. It does not show real patient data. Real "
            "patient records are available only after sign-in, and each signed-in "
            "patient can see analysis of only their own data—not another user's "
            "records."
        )

    try:
        data = get_analysis_data(patient_id)
    except (psycopg.Error, ValueError) as error:
        analysis_owner = "your" if is_logged_in else "the sample patient's"
        st.error(f"Could not load {analysis_owner} analysis data: {error}")
        return

    daily = pd.DataFrame(data["daily_summaries"], columns=DAILY_COLUMNS)
    activities = pd.DataFrame(data["activities"], columns=ACTIVITY_COLUMNS)
    pain = pd.DataFrame(data["pain_characteristics"], columns=PAIN_COLUMNS)
    for frame, columns in (
        (
            daily,
            [
                column
                for column in DAILY_COLUMNS
                if column
                not in {
                    "entry_date",
                    "stiffness_time",
                    "medication_name",
                    "pain_regions",
                    "exercise_types",
                }
            ],
        ),
        (
            activities,
            [
                column
                for column in ACTIVITY_COLUMNS
                if column not in {"entry_date", "time_of_day", "activity_type"}
            ],
        ),
        (
            pain,
            [
                column
                for column in PAIN_COLUMNS
                if column
                not in {
                    "entry_date",
                    "primary_location",
                    "secondary_location",
                    "radiation",
                    "pinpoint_or_diffuse",
                    "deep_or_surface",
                    "pain_types",
                }
            ],
        ),
    ):
        for column in columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    if daily.empty and activities.empty and pain.empty:
        if is_logged_in:
            st.info(
                "No saved logs yet. Add a daily summary, activity, or pain log to begin."
            )
        else:
            st.info(
                "The synthetic sample dataset has not been seeded in the configured "
                "database yet."
            )
        return

    all_entry_dates = pd.concat(
        [
            frame["entry_date"]
            for frame in (daily, activities, pain)
            if not frame.empty
        ],
        ignore_index=True,
    )
    first_date = pd.to_datetime(all_entry_dates).min().date()
    last_date = pd.to_datetime(all_entry_dates).max().date()
    date_range_key = (
        f"analysis_date_range_{patient_id}"
        if not is_logged_in
        else f"analysis_date_range_{authenticated_user_id()}"
    )
    selected_range = st.date_input(
        "Date range",
        value=(first_date, last_date),
        key=date_range_key,
    )
    if isinstance(selected_range, tuple):
        start_date, end_date = selected_range
    else:
        start_date = end_date = selected_range
    if start_date > end_date:
        st.warning("Choose a start date on or before the end date.")
        return

    daily = _in_date_range(daily, start_date, end_date)
    activities = _in_date_range(activities, start_date, end_date)
    pain = _in_date_range(pain, start_date, end_date)
    if daily.empty and activities.empty and pain.empty:
        st.info("No logs fall within the selected date range.")
        return

    with st.container(horizontal=True):
        st.metric("Daily summaries", len(daily), border=True)
        st.metric("Activity logs", len(activities), border=True)
        st.metric("Pain logs", len(pain), border=True)
        st.metric(
            "Days with a daily summary",
            daily["entry_date"].nunique() if not daily.empty else 0,
            border=True,
        )

    st.caption(
        f"Showing {start_date:%b %d, %Y} – {end_date:%b %d, %Y}. "
        "Counts describe saved records; they do not imply daily tracking is expected."
    )

    if not is_logged_in:
        _show_sample_insights(daily, activities, pain)

    _show_tracking_coverage(daily, activities, pain)
    _show_pain_trends(daily, pain)
    _show_sleep_and_routine(daily)
    _show_activity_response(activities)
    _show_pain_characteristics(pain, daily)


if __name__ == "__main__":
    main()
