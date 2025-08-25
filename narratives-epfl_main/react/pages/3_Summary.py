import streamlit as st
from s3 import read_json_from_s3, write_json_to_s3
import time

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

hide_sidebar_completely()

SUMMARY_FILE = "reading_summary.json"

if 'summary_start_time' not in st.session_state:
    st.session_state.summary_start_time = None

if 'summary_end_time' not in st.session_state:
    st.session_state.summary_end_time = None

if 'summary_written' not in st.session_state:
    st.session_state.summary_written = False

def update_reading_summary(summary, filename=SUMMARY_FILE):
    """Read from S3, update student entry or append new, then write back."""
    try:
        data = read_json_from_s3(filename)
        if not isinstance(data, list):
            data = []
    except Exception:
        data = []  # file not found or empty → start fresh

    # Check if student already exists
    updated = False
    for entry in data:
        if (entry["student_id"] == summary["student_id"] and 
            entry["student_name"] == summary["student_name"]):
            entry["reading_time_sec"] = summary["reading_time_sec"]
            entry["written_summary"] = summary.get("written_summary", "")
            updated = True
            break

    if not updated:
        data.append(summary)

    # Write back to S3
    write_json_to_s3(filename, data)

# Main UI
st.title("✍️ Write Your Summary")

# Ensure student has finished reading
if "summary_data" not in st.session_state or not st.session_state.finished:
    st.error("⚠️ You must finish reading first!")
    st.stop()

# Input summary
if st.button('Write passage summary'):
    st.session_state.start_summary_time = time.time()
    st.session_state.summary_data["written_summary"] = st.text_area(
        "Please write a short summary of what you read:",
        value=st.session_state.summary_data.get("written_summary", ""),
        height=200
    )
    st.session_state.summary_written = True

# Save summary
if st.session_state.summary_written and not st.session_state.get("summary_saved", False):
    if st.button("Submit Summary"):
        st.session_state.end_summary_time = time.time()
        st.session_state.summary_data['summary_writing_time'] = st.session_state.end_summary_time - st.session_state.start_summary_time
        update_reading_summary(st.session_state.summary_data)
        st.session_state.summary_saved = True
        st.success("Reading summary saved")

# Next step
if st.session_state.get("summary_saved", False):
    if st.button("Next"):
        st.switch_page("pages/4_Post Quiz.py")
