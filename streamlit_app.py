import psycopg
import streamlit as st
from streamlit_extras.card_selector import card_selector

from database import get_latest_log_dates
from user_identity import authenticated_user_id

st.set_page_config(page_title="Symptoms Tracker App", layout="wide")


def sign_in():
    st.title("PainMetrics")
    st.caption(
        "A structured health journal for noticing patterns in pain, symptoms, "
        "daily routines, and activities."
    )
    st.button("Sign in", on_click=st.login, type="primary")

    st.subheader("How to use PainMetrics")
    st.markdown("""
        1. Sign in to create private records for your own account.
        2. Add a daily summary with sleep, stiffness, pain at different times of day,
           movement, and other context.
        3. Record activities with pain ratings before, during, and after each activity.
        4. Add pain locations, intensity, and characteristics.
        5. Return to your personal Analysis page to explore descriptive patterns in
           your saved history.
        """)
    st.info(
        "You can explore a general analysis of a synthetic mock patient in the "
        "Sample analysis section without signing in. Sign-in is for real users who "
        "want to track their own data over time for future reference, consultation, "
        "or sharing their history with a doctor."
    )

    with st.container(border=True):
        st.subheader("Your information stays account-scoped")
        st.markdown(
            "Signed-in patients see analysis based only on their own records. "
            "The public sample analysis uses synthetic data for `sample_patient`; "
            "it does not expose any real patient's records."
        )


def project_overview():
    st.title("About the project", icon=":material/info:")
    st.caption(
        "A portfolio overview of PainMetrics for recruiters, collaborators, "
        "employers, and anyone exploring the project."
    )
    st.markdown("""
        ## The problem and approach

        Pain and symptom experiences are hard to summarize from memory. PainMetrics
        provides a repeatable way to record dated observations about pain, sleep,
        stiffness, activities, and daily routines, then review those observations
        as descriptive trends.

        ## What the app can do

        - **Daily summaries:** log sleep duration and quality, pain throughout the
          day, stiffness, movement, exercise, medication context, fatigue,
          hydration, and notes.
        - **Activity tracking:** record activity type, time, duration or repetitions,
          and pain before, during, 30 minutes after, and two hours after.
        - **Pain characteristics:** record primary and secondary locations and
          intensity, pain type, radiation, and other descriptors.
        - **Personal analysis:** explore saved-log coverage, pain and sleep trends,
          routine context, activity-related ratings, and recorded characteristics.
        - **Public demonstration:** browse a fully synthetic sample analysis without
          creating an account.

        ## Engineering overview

        The interface is built with Streamlit and Python. Psycopg connects the
        persistence layer to PostgreSQL (including Supabase-hosted PostgreSQL).
        The relational schema separates daily summaries, activities, pain
        characteristics, and their lookup/link tables. Constraints and foreign
        keys protect basic data integrity; parameterized SQL handles database
        operations.

        Account keys are derived server-side from the OpenID Connect issuer and
        subject. Row-level security policies scope application access to the
        active identity. The public sample analysis explicitly selects only the
        reserved `sample_patient` synthetic account; it does not provide a
        cross-patient browser.

        ## Interpreting the analysis

        Charts and summaries are descriptive views of self-reported observations.
        They are not diagnoses, predictions, treatment recommendations, or proof
        that one factor caused another. This educational portfolio project is not
        a medical device or a production clinical records service.

        ## Repository and contribution

        The repository separates the Streamlit entry point, page scripts,
        persistence functions, database initialization, and optional CSV
        importer. Contributions and feedback are welcome; use synthetic data in
        examples and reports, and never publish credentials or real patient data.
        """)


def home():
    account_data_key = authenticated_user_id()
    st.title("Symptoms Tracker App")
    st.caption("A patient health log for daily pain, activity, and symptom tracking.")
    st.subheader("How to use this app")
    st.markdown("""
        1. Choose a page card below to record a daily summary, activities, or pain characteristics, or to explore your personal analysis.
        2. Select the date for the entry. You may use today's date or a custom date from the calendar.
        3. Complete all relevant questions as honestly and specifically as possible.
        4. Submit the form on each page when you are done.
        5. Open Analysis to review descriptive patterns in your saved logs.
        """)

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
        {
            "icon": "📈",
            "title": "Analysis",
            "description": "Review personal trends across pain, sleep, stiffness, activities, and daily routines.",
            "path": "pages/analysis.py",
            "key": "analysis_home_card",
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
        st.markdown("""
            When you submit a log, the app saves it to the configured PostgreSQL database and associates it with your signed-in account and entry date. Your account identity is not entered into a form.

            Daily summaries and pain logs are updated if submitted again for the same account and date.
            """)

    with st.expander("Patient tips for better tracking", expanded=False):
        st.markdown("""
            - Log entries at the same time each day when possible.
            - Keep pain descriptions specific: location, timing, quality, and intensity.
            - Note activity details like duration, rest periods, and any pain changes after 30 minutes or 2 hours.
            - Use the same patient ID every time for consistent records.
            - If your symptoms change suddenly, add description notes in the free-text section.
            """)

    st.markdown("---")
    st.subheader("Your profile")
    st.caption("Your logs are associated with your signed-in account.")
    with st.expander("Account data key for a one-time import", expanded=False):
        st.code(account_data_key, language=None)
        st.caption(
            "Set this value as IMPORT_PATIENT_ID when importing this account's CSV history."
        )


def main():
    home_page = st.Page(home, title="Home", default=True)
    is_logged_in = st.user.is_logged_in
    if is_logged_in:
        st.session_state["home_page"] = home_page
        pages = [
            home_page,
            st.Page("pages/daily_summary.py", title="Daily Summary"),
            st.Page("pages/activities_log.py", title="Activities"),
            st.Page("pages/pain_intensity.py", title="Pain"),
            st.Page("pages/analysis.py", title="Analysis"),
        ]
        navigation_position = "hidden"
    else:
        pages = [
            st.Page(
                sign_in,
                title="Getting started",
                icon=":material/home:",
                default=True,
            ),
            st.Page(
                project_overview,
                title="Project",
                icon=":material/info:",
            ),
            st.Page(
                "pages/analysis.py",
                title="Sample analysis",
                icon=":material/analytics:",
            ),
        ]
        navigation_position = "top"

    pg = st.navigation(pages, position=navigation_position)
    if not is_logged_in:
        pg.run()
        return

    account_data_key = authenticated_user_id()
    with st.sidebar:
        st.write("Signed in as")
        st.caption(f"{st.user.get('email', 'your account')}")
        st.button("Sign out", on_click=st.logout, icon=":material/logout:")
        st.divider()
        st.markdown("**Most recent entries**")
        try:
            latest_log_dates = get_latest_log_dates(account_data_key)
        except (psycopg.Error, ValueError) as error:
            st.error(f"Could not load recent log dates: {error}")
        else:
            for log_type, entry_date in latest_log_dates.items():
                date_label = (
                    entry_date.strftime("%b %d, %Y")
                    if entry_date is not None
                    else "No entries yet"
                )
                st.caption(f"{log_type}: {date_label}")

    pg.run()


if __name__ == "__main__":
    main()
