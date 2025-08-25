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

# Call this function at the top of every page
hide_sidebar_completely()

st.title("Pre-Quiz: Decision Trees")

# ===== Initialize session state =====
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "question_times" not in st.session_state:
    st.session_state.question_times = {}
if "q_start_time" not in st.session_state:
    st.session_state.q_start_time = None
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None

# ===== Questions =====
questions = [
    {
        "question": "What does the training algorithm use when no features are left?",
        "options": ["Predicts randomly", "Guesses the most frequent label", "Uses previous feature again", "Discards the data point"],
        "answer": "B"
    },
    {
        "question": "What is found at the leaf nodes of a decision tree?",
        "options": ["Questions", "Features", "Final predicted labels", "Loss values"],
        "answer": "C"
    },
    {
        "question": "What happens if the training data is unambiguous?",
        "options": ["Keep splitting", "Return a leaf node with majority label", "Discard the data", "Repeat the training"],
        "answer": "B"
    },
    {
        "question": "What is apple?",
        "options": ["Fruit", "sports", "vegetable", "dry-fruit"],
        "answer": "A"
    },
    {
        "question": "Which of the following is not a part of the decision tree structure?",
        "options": ["Root", "Loop", "Node", "Leaf"],
        "answer": "B"
    },
    {
        "question": "What is the base case for DecisionTreeTrain?",
        "options": ["Maximum depth reached", "All labels are the same or no features left", "Only two classes", "Test data is provided"],
        "answer": "B"
    },
    {
        "question": "Select the option with value 427",
        "options": ["424", "424", "123", "427"],
        "answer": "D"
    },
    {
        "question": "Tree pruning is typically used to:",
        "options": ["Increase test loss", "Remove overfitted branches", "Train deeper trees", "Avoid splits"],
        "answer": "B"
    },
    {
        "question": "What does it mean to 'overfit' a decision tree?",
        "options": ["Not learning the training data", "Using too few features", "Memorizing training data without generalizing", "Ignoring test data"],
        "answer": "C"
    },
    {
        "question": "What are feature values?",
        "options": ["Labels", "Responses to questions (like yes/no)", "Tree heights", "Prediction probabilities"],
        "answer": "B"
    },
    {
        "question": "What is 5 + 7?",
        "options": ["13", "11", "12", "16"],
        "answer": "C"
    },
    {
        "question": "Which of the following is an example of binary classification?",
        "options": ["Predicting temperature", "Predicting whether a user likes a course or not", "Ranking webpages", "Recommending top 10 movies"],
        "answer": "B"
    },
    {
        "question": "What type of machine learning problem involves predicting a real number?",
        "options": ["Regression", "Classification", "Clustering", "Ranking"],
        "answer": "A"
    },
    {
        "question": "What is 100 - 99?",
        "options": ["0", "1", "2", "3"],
        "answer": "B"
    },
    {
        "question": "What does the function DecisionTreeTest do?",
        "options": ["Traverses the tree using test example's features to make a prediction", "Calculates training loss", "Repeats the training", "Sorts data by labels"],
        "answer": "A"
    }
]

# ===== Student Info (before quiz) =====
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if st.session_state.student_name == "" or st.session_state.student_id == "":
    st.session_state.student_name = st.text_input("Enter your name:")
    st.session_state.student_id = st.text_input("Enter your prolific ID:")

if not st.session_state.quiz_started:
    st.write("Click here to start quiz")
    if st.button("Start Quiz"):
        if st.session_state.student_name and st.session_state.student_id:
            st.session_state.quiz_start_time = datetime.now()
            st.session_state.q_start_time = datetime.now()
            st.session_state.current_q = 0  # Start from first question
            st.session_state.quiz_started = True
            st.rerun()
        else:
            st.warning("Please enter both name and ID before starting.")
else:
    # ===== Show Current Question =====
    q_index = st.session_state.current_q
    q = questions[q_index]

    st.header(f"Question {q_index + 1} of {len(questions)}")
    st.markdown(f"**{q['question']}**")

    selected = st.radio(
        "Select an answer:",
        options=q["options"],
        index=None,
        key=f"q_{q_index}"
    )

    # ===== Navigation Buttons =====
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous") and q_index > 0:
            time_spent = (datetime.now() - st.session_state.q_start_time).total_seconds()
            st.session_state.question_times[f"Q{q_index+1}"] = time_spent
            st.session_state.q_start_time = datetime.now()
            st.session_state.current_q -= 1
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
                    st.session_state.current_q += 1
                    st.session_state.q_start_time = datetime.now()
                    st.rerun()
                else:
                    score = sum(1 for r in st.session_state.responses.values() if r["is_correct"])
                    total_time = (datetime.now() - st.session_state.quiz_start_time).total_seconds()

                    result_data = {
                        "name": st.session_state.student_name,
                        "student_id": st.session_state.student_id,
                        "timestamp": str(datetime.now()),
                        "score": score,
                        "total": len(questions),
                        "total_time_seconds": total_time,
                        "time_per_question": st.session_state.question_times,
                        "responses": st.session_state.responses
                    }

                    filename = "student_pre.json"

                    data = read_json_from_s3(filename)
                    if not isinstance(data, dict):
                        data = {}

                    data[st.session_state.student_id] = result_data

                    write_json_to_s3(filename, data)

                    st.success(f"Quiz submitted! You scored {score}/{len(questions)}.")
                    st.switch_page("pages/2_Read_PDF.py")
