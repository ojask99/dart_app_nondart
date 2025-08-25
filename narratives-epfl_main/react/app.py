import streamlit as st

st.set_page_config(
    page_title="DART",
    page_icon="👋",
    initial_sidebar_state="collapsed"
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
st.title("DART:By Schole")

st.header("Student Information")


# Initialize session state if not already set
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""

# Input fields
name = st.text_input("Enter your full name:")
student_id = st.text_input("Enter your prolific ID:")

# Submit button
if st.button("Submit"):
    if name.strip() and student_id.strip():
        # Save in session state
        st.session_state.student_name = name.strip()
        st.session_state.student_id = student_id.strip()
        
        # Redirect to the pre-quiz page
        st.switch_page("pages/1_Pre Quiz.py")
    else:
        st.warning("Please enter both name and student ID.")
