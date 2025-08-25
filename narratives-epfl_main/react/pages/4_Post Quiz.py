import streamlit as st
import json
import os
from datetime import datetime
from s3 import read_json_from_s3, write_json_to_s3, append_to_json_in_s3

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

st.title("Post-Quiz: Decision Trees")

# ===== Initialize session state =====
if 'current_pq' not in st.session_state:
    st.session_state.current_pq = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "question_times" not in st.session_state:
    st.session_state.question_times = {}
if "q_start_time" not in st.session_state:
    st.session_state.q_start_time = None
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# Name & ID come from previous page
name = st.session_state.get("student_name", "")
student_id = st.session_state.get("student_id", "")

# ===== Questions =====
questions = [
    {"question": "In the context of decision trees, \"features\" are:",
     "options": ["Labels to be predicted", "Binary questions about input data", "Model weights", "Tree branches"], "answer": "B"},

    {"question": "Which feature is selected at each split?",
     "options": ["The one that results in the highest classification accuracy", "The one used first in data", "The one with the most yes/no answers", "Random feature"], "answer": "A"},

    {"question": "Which year is this?",
     "options": ["2024", "2023", "2025", "2089"], "answer": "C"},

    {"question": "Why might branches have different depths in pruned trees?",
     "options": ["Uniform data", "Different amounts of data in each branch", "Poor feature selection", "Constant loss values"], "answer": "B"},

    {"question": "What is the job of a loss function?",
     "options": ["Count number of predictions", "Track memory usage", "Quantify the error between prediction and true label", "Store training data"], "answer": "C"},

    {"question": "What does a \"loss function\" represent in supervised learning?",
     "options": ["Number of examples", "Error between true and predicted labels", "Model complexity", "Training time"], "answer": "B"},

    {"question": "What is the primary goal of a machine learning model?",
     "options": ["Memorizing training data", "Minimizing code length", "Generalizing from training data to unseen data", "Maximizing training loss"], "answer": "C"},

    {"question": "Sun rises from?",
     "options": ["North", "South", "East", "West"], "answer": "C"},

    {"question": "What does \"divide and conquer\" mean in decision trees?",
     "options": ["Assigning weights to examples", "Splitting data recursively based on features", "Using deep neural nets", "Labeling training examples"], "answer": "B"},

    {"question": "What is the structure of a decision tree classifier?",
     "options": ["Directed graph", "Hierarchical binary tree of feature-based splits", "Sorted array", "Unordered list"], "answer": "B"},

    {"question": "Why can't we just memorize the training data?",
     "options": ["It may not generalize to new data", "It's faster to generalize", "Memory is limited", "Labels are hidden"], "answer": "A"},

    {"question": "What is 200/10?",
     "options": ["20", "2", "200", "10"], "answer": "A"},

    {"question": "Which of the following is a way to control overfitting in decision trees?",
     "options": ["Limiting the depth of the tree", "Using larger datasets", "Repeating examples", "Ignoring pruning"], "answer": "A"},

    {"question": "Why might zero-one loss be inappropriate for regression tasks?",
     "options": ["It's too simple", "It doesn't capture magnitude of error", "It requires more computation", "It needs labels in percent"], "answer": "B"}
]


# ===== Start screen =====
if not st.session_state.quiz_started:
    if name and student_id:
        st.write(f"Welcome, {name} ({student_id})")
        st.write("Click the button below to start the quiz.")
        if st.button("Start Quiz"):
            st.session_state.quiz_start_time = datetime.now()
            st.session_state.q_start_time = datetime.now()
            st.session_state.current_pq = 0
            st.session_state.quiz_started = True
            st.rerun()
    else:
        st.warning("Please enter your name and student ID on the pre-quiz page before starting.")
else:
    # ===== Show Current Question =====
    q_index = st.session_state.current_pq
    q = questions[q_index]

    st.header(f"Question {q_index + 1} of {len(questions)}")
    st.markdown(f"**{q['question']}**")

    selected = st.radio(
        "Select an answer:",
        options=q["options"],
        index=None,
        key=f"post_q_{q_index}"
    )

    # ===== Navigation Buttons =====
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous") and q_index > 0:
            time_spent = (datetime.now() - st.session_state.q_start_time).total_seconds()
            st.session_state.question_times[f"Q{q_index+1}"] = time_spent
            st.session_state.q_start_time = datetime.now()
            st.session_state.current_pq -= 1
            st.rerun()

    with col2:
        if st.button("Next"):
            if selected is None:
                st.warning("Please select an answer before proceeding.")
            else:
                st.session_state.responses[f"Q{q_index+1}"] = {
                    "question": q["question"],
                    "selected": selected,
                    "correct": q["options"][ord(q["answer"]) - 65],
                    "is_correct": selected == q["options"][ord(q["answer"]) - 65]
                }
                time_spent = (datetime.now() - st.session_state.q_start_time).total_seconds()
                st.session_state.question_times[f"Q{q_index+1}"] = time_spent

                if q_index + 1 < len(questions):
                    st.session_state.current_pq += 1
                    st.session_state.q_start_time = datetime.now()
                    st.rerun()
                else:
                    score = sum(1 for r in st.session_state.responses.values() if r["is_correct"])
                    total_time = (datetime.now() - st.session_state.quiz_start_time).total_seconds()

                    result_data = {
                        "name": name,
                        "student_id": student_id,
                        "timestamp": str(datetime.now()),
                        "score": score,
                        "total": len(questions),
                        "total_time_seconds": total_time,
                        "time_per_question": st.session_state.question_times,
                        "responses": st.session_state.responses
                    }

                    data = read_json_from_s3("student_post.json")
                    if not isinstance(data, dict):
                        data = {}

                    data[student_id] = result_data
                    
                    write_json_to_s3("student_post.json", data)
                    st.success(f"Quiz submitted! You scored {score}/{len(questions)}.")
