import streamlit as st
from streamlit_extras.card_selector import card_selector

from user_identity import authenticated_user_id

st.set_page_config(page_title="Symptoms Tracker App", layout="wide")

if not st.user.is_logged_in:
    st.title("PainMetrics")
    st.caption("A private account is required to save symptom and activity logs.")
    st.button("Sign in", on_click=st.login, type="primary")
    st.stop()

account_data_key = authenticated_user_id()

with st.sidebar:
    st.caption(f"Signed in as {st.user.get('email', 'your account')}")
    st.button("Sign out", on_click=st.logout, icon=":material/logout:")


def home():
    st.title("Symptoms Tracker App")
    st.caption("A patient health log for daily pain, activity, and symptom tracking.")

    st.subheader("Your profile")
    st.caption("Your logs are associated with your signed-in account.")
    with st.expander("Account data key for a one-time import", expanded=False):
        st.code(account_data_key, language=None)
        st.caption(
            "Set this value as IMPORT_PATIENT_ID when importing this account's CSV history."
        )

    st.markdown("---")
    st.subheader("How to use this app")
    st.markdown("""
        1. Use the page cards below to record one of three categories: Daily Summary, Activities, or Pain Characteristics.
            2. Select the date for the entry. You may use today's date or a custom date from the calendar.
            3. Complete all relevant questions as honestly and specifically as possible.
            4. Submit the form on each page when you are done.
            5. Return to the Home page anytime to switch between log types.
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
