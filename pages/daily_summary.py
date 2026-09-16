from datetime import date
import streamlit as st


def main():
    # button to return to homepage
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write("This tracker is to enable the patient to log their daily summary.")
    st.subheader("Daily Summary page")

    with st.container():
        st.write("### Choose date")
        col1, col2 = st.columns(2)
        with col1:
            day = st.radio(
                "Entry for today, or a custom date?",
                ["Today", "Custom Date"],
                horizontal=True,
                captions=[
                    "Choose Today to enter the info for the current day",
                    "Choose Custom Date to enter the info for another date",
                ],
            )

        with col2:
            if day == "Today":
                selected_date = date.today()
                st.write(f"Entry date: {selected_date}")
            else:
                selected_date = st.date_input(
                    "Choose date", value="today", max_value="today"
                )
                st.write(f"Selected date: {selected_date}")

    with st.container():
        st.write("### Sleep")
        col1, col2, col3 = st.columns(3)
        with col1:
            sleep_hours = st.slider(
                "How many hours did you sleep for?",
                min_value=0,
                max_value=18,
                value=8,
            )

        with col2:
            sleep_quality = st.slider(
                "How was the quality of your sleep?",
                min_value=0,
                max_value=10,
                value=6,
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
                )
                mor_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Morning?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                )

        elif stiff_time == "Evening":
            with col1:
                eve_stiff_degree = st.slider(
                    "How much stiffness did you feel this Evening?",
                    min_value=0,
                    max_value=10,
                    value=0,
                )
                eve_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Evening?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                )
        elif stiff_time == "Both Morning and Evening":
            with col1:
                mor_stiff_degree = st.slider(
                    "How much stiffness did you feel this morning?",
                    min_value=0,
                    max_value=10,
                    value=0,
                )
                mor_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Morning?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                )
            with col2:
                eve_stiff_degree = st.slider(
                    "How much stiffness did you feel this Evening?",
                    min_value=0,
                    max_value=10,
                    value=0,
                )
                eve_stiff_duration = st.number_input(
                    "How many minutes did you feel stiffness during Evening?",
                    0,
                    300,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
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
            )
            eve_pain_degree = st.slider(
                "How much pain did you feel this Evening?",
                min_value=0,
                max_value=10,
                value=0,
            )

        with col2:
            noon_pain_degree = st.slider(
                "How much pain did you feel around Noon?",
                min_value=0,
                max_value=10,
                value=0,
            )
            night_pain_degree = st.slider(
                "How much pain did you feel at Night?",
                min_value=0,
                max_value=10,
                value=0,
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
            )
        with col2:
            lumbar_support_bool = st.radio(
                "Did your seat have a lumbar/back support for the majority of the time?",
                ["Yes", "No"],
                index=1,
                horizontal=True,
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
            )
            if exercise_bool == "Yes":
                workout_duration = st.number_input(
                    "How long did you Workout for?",
                    0,
                    240,
                    help="Enter Value in Minutes",
                    placeholder="45 Minutes",
                )

    with st.container():
        st.write("### Medications")

        medication_bool = st.radio(
            "Did you take any medications?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
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
                    )
                with col2:
                    medication_freq = st.number_input(
                        "How many times did you take the medication?",
                        1,
                        6,
                        help="Enter Value in Minutes",
                        placeholder="2",
                    )

    with st.container():
        st.write("### Abnormal Fatigue")
        abn_fatigue = st.radio(
            "Did you feel abnormally drained out (fatigue) throughout the day?",
            ["Yes", "No"],
            horizontal=True,
        )

    with st.container():
        st.write("### Adequate Hydration")
        adeq_hydration = st.radio(
            "Were you adequately hydrated throughout the day?",
            ["Yes", "No"],
            horizontal=True,
        )

    with st.container():
        st.write("### Exhausting Day")
        exhaust_day = st.radio(
            "Was your day too exhausting or tiring?",
            ["Yes", "No"],
            horizontal=True,
        )

    with st.container():
        st.write("### Overall Description")
        overall_descrip = st.text_area(
            "Any description that you want to mention?",
            max_chars=1000,
            placeholder="For example: After walking I felt relief in pain by approximately 20%, but bending forward made it worse for me.",
        )

    submitted = st.button("Submit", type="primary")


if __name__ == "__main__":
    main()
