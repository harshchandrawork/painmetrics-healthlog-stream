from datetime import date
import streamlit as st


def apply_database_meta(page_name: str):
    st.session_state.setdefault("patient_id", "")
    st.session_state.setdefault("database_record_meta", {})

    selected_date = st.session_state.get(f"{page_name}_selected_date")
    if selected_date is None:
        selected_date = date.today()

    st.session_state["database_record_meta"] = {
        "patient_id": st.session_state.get("patient_id", ""),
        "entry_date": selected_date.isoformat() if hasattr(selected_date, "isoformat") else str(selected_date),
        "source_page": page_name,
        "record_id": f"{st.session_state.get('patient_id', 'patient')}_{selected_date.isoformat() if hasattr(selected_date, 'isoformat') else str(selected_date)}_{page_name}",
    }

    return st.session_state["database_record_meta"]


def main():
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write("This tracker is to enable the patient to log their daily summary.")
    st.subheader("Daily Summary page")

    meta = apply_database_meta("daily_summary")
    st.caption(
        "Database-ready record: "
        f"patient_id={meta['patient_id']} | entry_date={meta['entry_date']} | source_page={meta['source_page']}"
    )

    with st.container():
        st.write("### Choose date")
        col1, col2 = st.columns(2)
        with col1:
            day = st.radio(
                "Entry for today, or a custom date?",
                ["Today", "Custom Date"],
                horizontal=True,
                key="daily_summary_date_option",
                captions=[
                    "Choose Today to enter the info for the current day",
                    "Choose Custom Date to enter the info for another date",
                ],
            )

        with col2:
            if day == "Today":
                selected_date = date.today()
                st.session_state["daily_summary_selected_date"] = selected_date
                st.write(f"Entry date: {selected_date}")
            else:
                selected_date = st.date_input(
                    "Choose date",
                    value=date.today(),
                    max_value=date.today(),
                    key="daily_summary_date_input",
                )
                st.session_state["daily_summary_selected_date"] = selected_date
                st.write(f"Selected date: {selected_date}")

    meta = apply_database_meta("daily_summary")

    with st.container():
        st.write("### Sleep")
        col1, col2 = st.columns(2)
        with col1:
            sleep_hours = st.slider(
                "How many hours did you sleep for?",
                min_value=0,
                max_value=18,
                value=8,
                key="daily_summary_sleep_hours",
            )

        with col2:
            sleep_quality = st.slider(
                "How was the quality of your sleep?",
                min_value=0,
                max_value=10,
                value=6,
                key="daily_summary_sleep_quality",
            )

    with st.container():
        st.write("### Time of Day for Stiffness")

        stiff_time = st.segmented_control(
            "When did you feel stiff?",
            [
                "Morning",
                "Evening",
                "Both Morning and Evening",
                "Didn't feel Stiffness",
            ],
            default="Didn't feel Stiffness",
            key="daily_summary_stiff_time",
        )

        col1, col2 = st.columns(2)

        if stiff_time == "Morning":
            with col1:
                mor_stiff_degree = st.slider(
                    "How much stiffness did you feel this Morning?",
                    min_value=0,
                    max_value=10,
                    value=0,
                    help="Rate on a value of 1-10 as per the Degree of your Stiffness.",
                    key="daily_summary_morning_stiff_degree",
                )
                mor_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Morning?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                    key="daily_summary_morning_stiff_duration",
                )

        elif stiff_time == "Evening":
            with col1:
                eve_stiff_degree = st.slider(
                    "How much stiffness did you feel this Evening?",
                    min_value=0,
                    max_value=10,
                    value=0,
                    key="daily_summary_evening_stiff_degree",
                )
                eve_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Evening?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                    key="daily_summary_evening_stiff_duration",
                )
        elif stiff_time == "Both Morning and Evening":
            with col1:
                mor_stiff_degree = st.slider(
                    "How much stiffness did you feel this morning?",
                    min_value=0,
                    max_value=10,
                    value=0,
                    key="daily_summary_both_morning_stiff_degree",
                )
                mor_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Morning?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                    key="daily_summary_both_morning_stiff_duration",
                )
            with col2:
                eve_stiff_degree = st.slider(
                    "How much stiffness did you feel this Evening?",
                    min_value=0,
                    max_value=10,
                    value=0,
                    key="daily_summary_both_evening_stiff_degree",
                )
                eve_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Evening?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                    key="daily_summary_both_evening_stiff_duration",
                )

    with st.container():
        st.write("### Degree of Pain Throughout the Day")

        col1, col2 = st.columns(2)
        with col1:
            mor_pain_degree = st.slider(
                "How much pain did you feel this Morning?",
                min_value=0,
                max_value=10,
                value=0,
                key="daily_summary_morning_pain_degree",
            )
            eve_pain_degree = st.slider(
                "How much pain did you feel this Evening?",
                min_value=0,
                max_value=10,
                value=0,
                key="daily_summary_evening_pain_degree",
            )

        with col2:
            noon_pain_degree = st.slider(
                "How much pain did you feel around Noon?",
                min_value=0,
                max_value=10,
                value=0,
                key="daily_summary_noon_pain_degree",
            )
            night_pain_degree = st.slider(
                "How much pain did you feel at Night?",
                min_value=0,
                max_value=10,
                value=0,
                key="daily_summary_night_pain_degree",
            )

    with st.container():
        st.write("### Pain Region")
        col1, col2 = st.columns(2)
        with col1:
            pain_region = st.text_input(
                "Where did you feel the pain throughout the day?",
                max_chars=200,
                help="Seperate distinct regions with commas",
                placeholder="Right SI Joint, Lower Back, Knees, etc.",
                key="daily_summary_pain_region",
            )

    with st.container():
        st.write("### Walking Duration")
        col1, col2 = st.columns(2)
        with col1:
            walk_duration = st.number_input(
                "How long did you Walk for?",
                0,
                600,
                help="Enter Value in Minutes",
                placeholder="45 Minutes",
                key="daily_summary_walk_duration",
            )

    with st.container():
        st.write("### Sitting Duration")
        col1, col2 = st.columns(2)
        with col1:
            sitting_duration = st.number_input(
                "How long did you Sit for?",
                0,
                600,
                help="Enter Value in Minutes",
                placeholder="45 Minutes",
                key="daily_summary_sitting_duration",
            )
        with col2:
            lumbar_support_bool = st.radio(
                "Did your seat have a lumbar/back support for the majority of the time?",
                ["Yes", "No"],
                index=1,
                horizontal=True,
                key="daily_summary_lumbar_support",
            )

    with st.container():
        st.write("### Standing Duration")
        col1, col2 = st.columns(2)
        with col1:
            standing_duration = st.number_input(
                "How long did you Stand for?",
                0,
                600,
                help="Enter Value in Minutes",
                placeholder="45 Minutes",
                key="daily_summary_standing_duration",
            )
    with st.container():
        st.write("### Exercise/Workout")
        col1, col2 = st.columns(2)
        with col1:
            exercise_bool = st.radio(
                "Did you do exercise/workout or not?",
                ["Yes", "No"],
                index=1,
                horizontal=True,
                key="daily_summary_exercise_bool",
            )
            if exercise_bool == "Yes":
                workout_duration = st.number_input(
                    "How long did you Workout for?",
                    0,
                    240,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                    key="daily_summary_workout_duration",
                )

    with st.container():
        st.write("### Medications")

        medication_bool = st.radio(
            "Did you take any medications?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
            key="daily_summary_medication_bool",
        )
        col1, col2 = st.columns(2)

        if medication_bool == "Yes":
            with st.container(horizontal=True):
                with col1:
                    medications = st.text_input(
                        "Which medications did you take?",
                        max_chars=200,
                        help="Seperate distinct medicines with commas",
                        placeholder="Etoricoxib 90 mg, Tofacitinib 5 mg, Acecoflenac 300 mg etc.",
                        key="daily_summary_medications",
                    )
                with col2:
                    medication_freq = st.number_input(
                        "How many times did you take the medication?",
                        1,
                        6,
                        help="Enter Value in Minutes",
                        placeholder="2",
                        key="daily_summary_medication_freq",
                    )

    with st.container():
        st.write("### Abnormal Fatigue")
        abn_fatigue = st.radio(
            "Did you feel abnormally drained out (fatigue) throughout the day?",
            ["Yes", "No"],
            horizontal=True,
            key="daily_summary_abnormal_fatigue",
        )

    with st.container():
        st.write("### Adequate Hydration")
        adeq_hydration = st.radio(
            "Were you adequately hydrated throughout the day?",
            ["Yes", "No"],
            horizontal=True,
            key="daily_summary_hydration",
        )

    with st.container():
        st.write("### Exhausting Day")
        exhaust_day = st.radio(
            "Was your day too exhausting or tiring?",
            ["Yes", "No"],
            horizontal=True,
            key="daily_summary_exhausting_day",
        )

    with st.container():
        st.write("### Overall Description")
        overall_descrip = st.text_area(
            "Any description that you want to mention?",
            max_chars=1000,
            placeholder="For example: After walking I felt relief in pain by approximately 20%, but bending forward made it worse for me.",
            key="daily_summary_overall_description",
        )

    submitted = st.button("Submit", type="primary", key="daily_summary_submit")


if __name__ == "__main__":
    main()
