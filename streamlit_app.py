import streamlit as st
from streamlit_extras.card_selector import card_selector

st.set_page_config(page_title="Symptoms Tracker App", layout="wide")

APP_CONFIG = {
    "database": {
        "status": "not_connected",
        "local_path": "local_database.db",
        "tables": {
            "daily_summary": "daily_summary_logs",
            "activities": "activity_logs",
            "pain": "pain_characteristics",
        },
    },
    "record_keys": {
        "patient_id": "patient_id",
        "entry_date": "entry_date",
        "source_page": "source_page",
        "record_id": "record_id",
    },
}


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
                help="Use this value to map entries to a local database or clinic record later.",
                placeholder="Example: patient_001",
            )
        with col2:
            st.text_input(
                "Care team / notes label",
                key="care_team_label",
                help="Optional label for internal tracking or future database linking.",
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

    with st.expander("Database-ready structure and record keys", expanded=False):
        st.markdown(
            """
            This app is designed so it can be connected to a local database later. The current structure uses a consistent record pattern based on:

            - patient_id
            - entry_date
            - source_page
            - record_id

            Example record ID pattern:
            `patient_001_2026-09-27_daily_summary`

            These values are ready for mapping to SQLite, PostgreSQL, or a local file-based database once connected.
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
