import streamlit as st
from streamlit_extras.card_selector import card_selector

st.set_page_config(page_title="Symptoms Tracker App")  # optional: set layout="wide"


def home():
    st.title("Symptoms Tracker App")
    st.write("This tracker is to enable the patient to log their daily pain logs.")

    st.subheader("Choose a page to go to")
    pages = [
        {
            "icon": "📅",
            "title": "Daily Summary",
            "description": "Input Daily Summary",
            "path": "pages/daily_summary.py",
        },
        {
            "icon": "🏃‍♂️",
            "title": "Activities",
            "description": "Input Daily Activities",
            "path": "pages/activities_log.py",
        },
        {
            "icon": "📏",
            "title": "Pain",
            "description": "Input Pain Characteristics",
            "path": "pages/pain_intensity.py",
        },
    ]

    selected_page = card_selector(
        [
            {key: value for key, value in page.items() if key != "path"}
            for page in pages
        ],
        key="page_selector",
    )

    if selected_page is not None:
        st.switch_page(pages[selected_page]["path"])


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
