import streamlit as st
from streamlit_extras.card_selector import card_selector

st.set_page_config(page_title="Symptoms Tracker App", layout="wide")

def home():
    st.title("Symptoms Tracker App")
    st.caption("A patient health log for daily pain, activity, and symptom tracking.")

    st.session_state.setdefault("patient_id", "")
    st.session_state.setdefault("care_team_label", "")

    with st.container():
        st.subheader("Patient profile")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Patient ID / profile ID",
                key="patient_id",
                help="This ID links all of this patient's submitted logs in the database.",
                placeholder="Example: patient_001",
            )
        with col2:
            st.text_input(
                "Care team / notes label",
                key="care_team_label",
                help="Optional label saved with the patient record when a log is submitted.",
                placeholder="Example: clinic_1 or family_member_2",
            )

    st.markdown("---")
    st.subheader("How to use this app")
    st.markdown(
        """
        1. Start by entering a patient ID above so each log can be traced to the correct person.
        2. Use the page cards below to record one of three categories: Daily Summary, Activities, or Pain Characteristics.
        3. Select the date for the entry. You may use today's date or a custom date from the calendar.
        4. Complete all relevant questions as honestly and specifically as possible.
        5. Submit the form on each page when you are done.
        6. Return to the Home page anytime to switch between log types.
        """
    )

    st.subheader("What each page tracks")
    pages = [
        {
            "icon": "📅",
            "title": "Daily Summary",
            "description": "Sleep, stiffness, walking, fatigue, hydration, and daily symptoms.",
            "path": "pages/daily_summary.py",
            "key": "daily_summary_home_card",
        },
        {
            "icon": "🏃‍♂️",
            "title": "Activities",
            "description": "Movement, repetitions, duration, and pain before/during/after activity.",
            "path": "pages/activities_log.py",
            "key": "activity_home_card",
        },
        {
            "icon": "📏",
            "title": "Pain",
            "description": "Primary and secondary pain regions, intensity, and pain quality.",
            "path": "pages/pain_intensity.py",
            "key": "pain_home_card",
        },
    ]

    selected_page = card_selector(
        [
            {key: value for key, value in page.items() if key not in {"path", "key"}}
            for page in pages
        ],
        key="page_selector",
    )

    if selected_page is not None:
        st.switch_page(pages[selected_page]["path"])

    with st.expander("How your logs are stored", expanded=False):
        st.markdown(
            """
            When you submit a Daily Summary, Activities, or Pain Characteristics log, the app saves it to the PostgreSQL `symptoms_tracker_db` database. Each log is associated with:

            - patient_id
            - entry_date

            Enter the same patient ID on the Home page for each log you want associated with the same patient. Daily summaries and pain logs are updated if submitted again for the same patient and date.
            """
        )

    with st.expander("Patient tips for better tracking", expanded=False):
        st.markdown(
            """
            - Log entries at the same time each day when possible.
            - Keep pain descriptions specific: location, timing, quality, and intensity.
            - Note activity details like duration, rest periods, and any pain changes after 30 minutes or 2 hours.
            - Use the same patient ID every time for consistent records.
            - If your symptoms change suddenly, add description notes in the free-text section.
            """
        )


def main():
    home_page = st.Page(home, title="Home", default=True)
    st.session_state["home_page"] = home_page

    daily_summary = st.Page("pages/daily_summary.py", title="Daily Summary")
    activities = st.Page("pages/activities_log.py", title="Activities")
    pain = st.Page("pages/pain_intensity.py", title="Pain")

    pg = st.navigation([home_page, daily_summary, activities, pain], position="hidden")
    pg.run()


if __name__ == "__main__":
    main()
