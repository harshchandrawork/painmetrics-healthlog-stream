from datetime import date

import psycopg
import streamlit as st

from database import save_pain_characteristics


def main():
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write(
        "This tracker is to enable the patient to log their daily pain characteristics."
    )
    st.subheader("Pain characteristics page")

    st.session_state.setdefault("patient_id", "")
    st.caption("Submitting this form saves the pain log with your patient ID and selected date.")

    with st.container():
        st.write("### Choose date")
        col1, col2 = st.columns(2)
        with col1:
            day = st.radio(
                "Entry for today, or a custom date?",
                ["Today", "Custom Date"],
                horizontal=True,
                key="pain_date_option",
                captions=[
                    "Choose Today to enter the info for the current day",
                    "Choose Custom Date to enter the info for another date",
                ],
            )

        with col2:
            if day == "Today":
                selected_date = date.today()
                st.session_state["pain_selected_date"] = selected_date.isoformat()
                st.write(f"Entry date: {selected_date}")
            else:
                selected_date = st.date_input(
                    "Choose date",
                    value=date.today(),
                    max_value=date.today(),
                    key="pain_date_input",
                )
                st.session_state["pain_selected_date"] = selected_date.isoformat()
                st.write(f"Selected date: {selected_date}")

    with st.container():
        st.write("### Pain location & Intensity")
        col1, col2 = st.columns(2)
        with col1:
            primary_pain = st.text_input(
                "What is the primary region of your pain?",
                max_chars=40,
                placeholder="For example: Right SI Joint",
                key="pain_primary_region",
            )
            primary_pain_intensity = st.slider(
                "What was the intensity of pain at the primary region of pain?",
                min_value=0,
                max_value=10,
                value=0,
                key="pain_primary_intensity",
            )
        with col2:
            secondary_pain = st.text_input(
                "What is the secondary region of your pain?",
                max_chars=40,
                placeholder="For example: Lower back",
                key="pain_secondary_region",
            )
            secondary_pain_intensity = st.slider(
                "What was the intensity of pain at the secondary region of pain?",
                min_value=0,
                max_value=10,
                value=0,
                key="pain_secondary_intensity",
            )

    with st.container():
        st.write("### Pain type")
        pain_type = st.segmented_control(
            "What type of pain did you feel?",
            [
                "Dull ache",
                "Sharp pain",
                "Muscle fatigue",
                "Stiffness",
                "Burning",
                "Throbbing",
                "Muscle spasm",
                "Pulling sensation",
                "Pressure sensation",
            ],
            key="pain_type",
        )
    with st.container():
        st.write("### Pain Radiation")
        radiate_bool = st.radio(
            "Did the pain radiate downwards?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
            key="pain_radiate_bool",
        )

    with st.container():
        st.write("### Pinpoint of Diffuse pain")
        pinpoint_or_diffuse = st.radio(
            "Was the pain at a pinpoint location or diffuse?",
            ["Pinpoint", "Diffuse"],
            index=1,
            horizontal=True,
            key="pain_diffuse_type",
        )

    with st.container():
        st.write("### Deep of Surface pain")
        deep_or_surface = st.radio(
            "Was the pain deep under the skin or at the surface?",
            ["Deep", "Surface"],
            index=0,
            horizontal=True,
            key="pain_depth_type",
        )

    submitted = st.button("Save pain log", type="primary", key="pain_submit_button")
    if submitted:
        patient_id = st.session_state.get("patient_id", "").strip()
        try:
            save_pain_characteristics(
                patient_id,
                date.fromisoformat(st.session_state["pain_selected_date"]),
                {
                    "primary_location": st.session_state["pain_primary_region"],
                    "secondary_location": st.session_state["pain_secondary_region"],
                    "primary_intensity": st.session_state["pain_primary_intensity"],
                    "secondary_intensity": st.session_state["pain_secondary_intensity"],
                    "pain_type": st.session_state.get("pain_type"),
                    "radiation": st.session_state["pain_radiate_bool"],
                    "pinpoint_or_diffuse": pinpoint_or_diffuse,
                    "deep_or_surface": deep_or_surface,
                },
                care_team_label=st.session_state.get("care_team_label", ""),
            )
            st.success("Pain log saved to the database.")
        except (psycopg.Error, ValueError) as error:
            st.error(f"Could not save the pain log: {error}")


if __name__ == "__main__":
    main()
