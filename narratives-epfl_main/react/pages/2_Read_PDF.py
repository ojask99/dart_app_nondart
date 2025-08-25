import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer
from s3 import read_json_from_s3, write_json_to_s3

st.set_page_config(
    page_title="DART",
    page_icon="👋",
    initial_sidebar_state="collapsed",
)

# More importantly, add this CSS to EVERY page file
def hide_sidebar_completely():
    st.markdown("""
    <style>
        /* Hide the entire sidebar */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Hide the sidebar toggle button */
        button[data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Hide any remaining sidebar elements */
        .css-1d391kg, .css-1rs6os, .css-17eq0hr {
            display: none !important;
        }
        
        /* Expand main content to full width */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
        }
        
        /* Remove left margin */
        .main {
            margin-left: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Call this function at the top of every page
hide_sidebar_completely()

# env dir
parent_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=parent_dir / '.env')

# Initialize session state variables
if "student_id" not in st.session_state:
    st.session_state.student_id = ""   # Prolific ID
if "student_name" not in st.session_state:
    st.session_state.student_name = ""  # Name
if "started" not in st.session_state:
    st.session_state.started = False
if "finished" not in st.session_state:
    st.session_state.finished = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None  
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None

st.title('DART: by Schole')
st.subheader('Read the following PDF')
import streamlit as st

student_json_path = "student_detail.json"

try:
    # Load existing student data
    student_data = read_json_from_s3(student_json_path)
    if not isinstance(student_data, dict):
        student_data = {}

    # Ask Prolific ID and Name only if not asked earlier
    if "student_id" not in st.session_state or not st.session_state.student_id.strip():
        st.session_state.student_id = st.text_input("Enter your Prolific ID:")

    if "student_name" not in st.session_state or not st.session_state.student_name.strip():
        st.session_state.student_name = st.text_input("Enter your Name:")

    # Show form only if ID and name are provided
    if st.session_state.get("student_id") and st.session_state.get("student_name"):
        with st.form("student_details_form"):
            st.subheader("Enter Your Details")

            # Age
            age = st.number_input("Age", min_value=10, max_value=100, step=1)

            # Education Level
            education_level = st.text_input(
                "Education Level (e.g., Doctorate, Masters, Undergraduate, High School, Uneducated)"
            )

            # Education Subject
            education_subject = st.text_input(
                "Education Subject (e.g., Engineering, Medical, Finance, JD, Arts)"
            )

            # Occupation
            occupation = st.text_input(
                "Occupation (e.g., Doctor, Software Engineer, Homemaker, Banker, Architect, Lawyer)"
            )

            submitted = st.form_submit_button("Save Details")

        if submitted:
            student_id = st.session_state.student_id.strip()
            student_name = st.session_state.student_name.strip()

            new_details = {
                "student_name": student_name,
                "age": age,
                "education_level": education_level,
                "education_subject": education_subject,
                "occupation": occupation
            }

            # Update if ID exists, else add new
            student_data[student_id] = new_details

            # Save updated data back
            write_json_to_s3(student_json_path, student_data)

            st.success("Details updated successfully!")

except Exception as e:
    st.error(f"Error while updating student details: {e}")


# Step 1: Start button
if not st.session_state.started and st.session_state.student_id and st.session_state.student_name:
    if st.button("Start Reading"):
        st.session_state.start_time = time.time()
        st.session_state.started = True
        st.session_state.finished = False

# Step 2: Show PDF only after start
if st.session_state.started and not st.session_state.finished:
    st.write("Scroll through the PDF below 👇")
    pdf_viewer("C:/Python/narratives-epfl nondart/narratives-epfl_main/dart_exp2.pdf")

    if st.button("Finish Reading"):
        st.session_state.end_time = time.time()
        reading_time = st.session_state.end_time - st.session_state.start_time
        st.session_state.finished = True

        # Prepare summary container for next page
        st.session_state.summary_data = {
            "student_id": st.session_state.student_id,
            "student_name": st.session_state.student_name,
            "reading_time_sec": round(reading_time, 2),
            "written_summary": ""
        }
        st.success(f"Finished reading! ⏱ {round(reading_time,2)} seconds")

# Step 3: After finishing → Next button
if st.session_state.finished:
    if st.button("Go to Summary ➡️"):
        st.switch_page("pages/3_Summary.py")
