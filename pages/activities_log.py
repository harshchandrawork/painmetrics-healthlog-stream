from datetime import date
import streamlit as st

st.session_state.setdefault("activity_count", 1)


def add_activity():
    st.session_state.activity_count += 1


def submit_activities(selected_date=None):
    activity_rows = []
    for index in range(st.session_state.activity_count):
        activity_rows.append(
            {
                "patient_id": st.session_state.get("patient_id", ""),
                "entry_date": selected_date.isoformat() if selected_date else st.session_state.get("activity_selected_date"),
                "source_page": "activities",
                "record_id": f"{st.session_state.get('patient_id','patient')}_{selected_date.isoformat() if selected_date else st.session_state.get('activity_selected_date', date.today().isoformat())}_activities_{index}",
                "time_of_day": st.session_state.get(f"time_of_day_{index}", ""),
                "activity_type": st.session_state.get(f"activity_type_{index}", ""),
                "duration_mins": st.session_state.get(f"duration_mins_{index}", 0),
                "repititions": st.session_state.get(f"repititions_{index}", 0),
                "pain_before": st.session_state.get(f"pain_before_{index}", 0),
                "pain_during": st.session_state.get(f"pain_during_{index}", 0),
                "pain_after_30mins": st.session_state.get(f"pain_after_30mins_{index}", 0),
                "pain_after_2hrs": st.session_state.get(f"pain_after_2hrs_{index}", 0),
            }
        )
    st.session_state.submitted_activities = activity_rows


def main():
    if st.button("Return Home", icon=":material/home:", type="tertiary"):
        st.switch_page(st.session_state["home_page"])

    st.title("Symptoms Tracker App")
    st.write("This tracker is to enable the patient to log daily activities.")
    st.subheader("Activities page")

    st.session_state.setdefault("patient_id", "")
    st.caption(
        "Database mapping: patient_id, entry_date, source_page, and record_id are attached to every row for local database linking."
    )

    with st.container():
        st.write("### Choose date")
        col1, col2 = st.columns(2)
        with col1:
            day = st.radio(
                "Entry for today, or a custom date?",
                ["Today", "Custom Date"],
                horizontal=True,
                key="activity_date_option",
                captions=[
                    "Choose Today to enter the info for the current day",
                    "Choose Custom Date to enter the info for another date",
                ],
            )

        with col2:
            if day == "Today":
                selected_date = date.today()
                st.session_state["activity_selected_date"] = selected_date.isoformat()
                st.write(f"Entry date: {selected_date}")
            else:
                selected_date = st.date_input(
                    "Choose date",
                    value=date.today(),
                    max_value=date.today(),
                    key="activity_date_input",
                )
                st.session_state["activity_selected_date"] = selected_date.isoformat()
                st.write(f"Selected date: {selected_date}")

    with st.container():
        st.write("### Log activities")
        st.caption(
            "- Click **`Add Activity`** button to add multiple activities. When all activities entered, press **`Submit activities`** button to submit all activities.\n"
            "- Leave **`Repetitions`** empty if the intensity of the activity is primarily defined by the **`Duration`** and vice versa."
        )
        with st.form("activities_form"):
            for index in range(st.session_state.activity_count):
                st.write(f"#### Activity {index + 1}")

                st.time_input(
                    "Time of day",
                    key=f"time_of_day_{index}",
                )

                st.text_input(
                    "Activity type",
                    key=f"activity_type_{index}",
                    placeholder="For example, walking",
                )

                st.number_input(
                    "Duration in minutes",
                    min_value=0,
                    step=1,
                    key=f"duration_mins_{index}",
                )

                st.number_input(
                    "Repetitions",
                    min_value=0,
                    step=1,
                    key=f"repititions_{index}",
                )

                with st.container():
                    col1, col2 = st.columns(2)

                    with col1:
                        st.slider(
                            "Pain before activity",
                            min_value=0,
                            max_value=10,
                            value=0,
                            key=f"pain_before_{index}",
                        )

                        st.slider(
                            "Pain after 30 minutes",
                            min_value=0,
                            max_value=10,
                            value=0,
                            key=f"pain_after_30mins_{index}",
                        )

                    with col2:
                        st.slider(
                            "Pain during activity",
                            min_value=0,
                            max_value=10,
                            value=0,
                            key=f"pain_during_{index}",
                        )

                        st.slider(
                            "Pain after 2 hours",
                            min_value=0,
                            max_value=10,
                            value=0,
                            key=f"pain_after_2hrs_{index}",
                        )

                st.divider()

            submitted = st.form_submit_button(
                "Submit activities",
                icon=":material/check:",
                type="primary",
            )

        st.button(
            "Add activity",
            icon=":material/add:",
            on_click=add_activity,
        )

        if submitted:
            submit_activities(date.fromisoformat(st.session_state["activity_selected_date"]))

        if "submitted_activities" in st.session_state:
            st.success("Activities submitted.")
            st.json(st.session_state.submitted_activities)


if __name__ == "__main__":
    main()
