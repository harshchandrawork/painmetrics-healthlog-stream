from datetime import date
import streamlit as st

st.session_state.setdefault("activity_count", 1)


def add_activity():
    st.session_state.activity_count += 1


def submit_activities():
    activities = []

    for index in range(st.session_state.activity_count):
        activity = st.session_state.get(f"activity_{index}", "").strip()

        if activity:
            activities.append(activity)

    st.session_state.submitted_activities = activities


st.subheader("This is Activities page")


# trigger = st.button("Add Activity")
# if trigger:
#     text = st.text_input("Enter text")
#     enter = st.button("Enter")
#     if enter:
#         activities["act_count"].append(act_count)
#         activities["activity"].append(text)
#         act_count += 1
#         add_act(act_count, activities)
# return activities


st.subheader("This is the Activities page")


def main():
    # button to return to homepage
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write("This tracker is to enable the patient to log daily activities.")
    st.subheader("Activities page")

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

    with st.container():
        st.write("### Log Activities")
        st.caption(
            "Click **`Add Activity`** button to add multiple activities. When all activities entered, press **`Submit activities`** button to submit all activities"
        )
        # Render all currently requested activity fields
        with st.form("Activities Form"):
            for index in range(st.session_state.activity_count):
                st.text_input(
                    f"Activity {index + 1}",
                    key=f"activity_{index}",
                    placeholder="Enter an activity",
                )
            submitted = st.form_submit_button(
                "Submit activities", icon=":material/check:", type="primary"
            )

        st.button(
            "Add activity",
            icon=":material/add:",
            on_click=add_activity,
        )

        if submitted:
            submit_activities()

        if "submitted_activities" in st.session_state:
            st.success("Activities submitted.")
            st.write(st.session_state.submitted_activities)


if __name__ == "__main__":
    main()
