from datetime import date
import streamlit as st


def main():
    # button to return to homepage
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write(
        "This tracker is to enable the patient to log their daily pain characteristics."
    )
    st.subheader("Pain characteristics page")

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
        st.write("### Pain location & Intensity")
        col1, col2 = st.columns(2)
        with col1:
            primary_pain = st.text_input(
                "What is the primary region of your pain?",
                max_chars=40,
                placeholder="For example: Right SI Joint",
            )
            primary_pain_intensity = st.slider(
                "What was the intensity of pain at the primary region of pain?",
                min_value=0,
                max_value=10,
                value=0,
            )
        with col2:
            secondary_pain = st.text_input(
                "What is the secondary region of your pain?",
                max_chars=40,
                placeholder="For example: Lower back",
            )
            secondary_pain_intensity = st.slider(
                "What was the intensity of pain at the secondary region of pain?",
                min_value=0,
                max_value=10,
                value=0,
            )

    with st.container():
        st.write("### Pain type")
        stiff_time = st.segmented_control(
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
        )
    with st.container():
        st.write("### Pain Radiation")
        radiate_bool = st.radio(
            "Did the pain radiate downwards?", ["Yes", "No"], index=1, horizontal=True
        )

    with st.container():
        st.write("### Pinpoint of Diffuse pain")
        pin_diff_bool = st.radio(
            "Was the pain at a pinpoint location, or was it diffuse?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
        )

    with st.container():
        st.write("### Deep of Surface pain")
        radiate_bool = st.radio(
            "Was the pain at the surface of the skin, or deep under the skin?",
            ["Yes", "No"],
            index=1,
            horizontal=True,
        )


if __name__ == "__main__":
    main()
