import streamlit as st
import json
from datetime import datetime

st.title("Exam Revision Planning and Confidence Survey")

# ---------------- DEFAULT QUESTIONS ----------------
default_questions = [
    {"q": "How early do you start preparing for exams?",
     "opts": [("Very early",0),("Early",1),("A bit late",2),("Very late",3),("Last minute",4)]},

    {"q": "How organized is your revision schedule?",
     "opts": [("Extremely organized",0),("Organized",1),("Somewhat organized",2),("Poorly organized",3),("No schedule",4)]},

    {"q": "How consistently do you follow your revision plan or timetable?",
     "opts": [("Always follow it",0),("Often follow it",1),("Sometimes follow it",2),("Rarely follow it",3),("Never follow it",4)]},

    {"q": "How confident are you before exams?",
     "opts": [("Very confident",0),("Confident",1),("Neutral",2),("Slightly worried",3),("Very worried",4)]},

    {"q": "How often do you revise past exam papers?",
     "opts": [("Very frequently",0),("Frequently",1),("Sometimes",2),("Rarely",3),("Never",4)]},

    {"q": "How well do you understand the material while revising?",
     "opts": [("Fully understand all topics",0),("Mostly understand",1),("Partially understand",2),("Often struggle",3),("Do not understand",4)]},

    {"q": "How often do distractions affect your study sessions?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},

    {"q": "How do you feel after completing a revision session?",
     "opts": [("Very satisfied and confident",0),("Satisfied",1),("Neutral",2),("Unsure",3),("Very stressed",4)]},

    {"q": "How consistent is your study routine?",
     "opts": [("Very consistent",0),("Consistent",1),("Sometimes consistent",2),("Inconsistent",3),("No routine at all",4)]},

    {"q": "How often do you revise difficult topics?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},

    {"q": "How confident are you solving exam-style questions?",
     "opts": [("Very confident",0),("Confident",1),("Neutral",2),("Not confident",3),("Very unconfident",4)]},

    {"q": "How effectively do you manage your study time?",
     "opts": [("Extremely effectively",0),("Effectively",1),("Moderately",2),("Poorly",3),("Very poorly",4)]},

    {"q": "How often do you feel stressed before exams?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},

    {"q": "How motivated are you to study?",
     "opts": [("Highly motivated",0),("Motivated",1),("Slightly motivated",2),("Low motivation",3),("No motivation",4)]},

    {"q": "Overall, how prepared do you feel for exams?",
     "opts": [("Fully prepared",0),("Mostly prepared",1),("Somewhat prepared",2),("Slightly prepared",3),("Not prepared at all",4)]}
]

# ---------------- SESSION STATE ----------------
if "default_questions" not in st.session_state:
    st.session_state.custom_questions = None

if "start" not in st.session_state:
    st.session_state.start = False

if "participant" not in st.session_state:
    st.session_state.participant = {}

# ---------------- HELPERS ----------------
def normalize_questionnaire(raw_data):
    """
    Accepts:
    1) a list of questions
    2) a dict with key 'questions'
    
    Question format:
    {
        "q": "Question text",
        "opts": [("Option 1", 0), ("Option 2", 1)]
    }

    Also supports:
    {
        "question": "Question text",
        "options": ["A", "B", "C"]
    }
    or:
    {
        "question": "Question text",
        "options": [{"label": "A", "score": 0}, {"label": "B", "score": 1}]
    }
    """
    if isinstance(raw_data, dict) and "questions" in raw_data:
        raw_data = raw_data["questions"]

    if not isinstance(raw_data, list):
        raise ValueError("Questionnaire JSON must be a list of questions or an object with a 'questions' key.")

    normalized = []

    for i, item in enumerate(raw_data):
        if not isinstance(item, dict):
            raise ValueError(f"Question {i+1} is not an object.")

        q_text = item.get("q") or item.get("question") or item.get("text")
        opts = item.get("opts") or item.get("options")

        if not q_text:
            raise ValueError(f"Question {i+1} is missing question text.")

        if not opts or not isinstance(opts, list):
            raise ValueError(f"Question '{q_text}' is missing valid options.")

        norm_opts = []

        for j, opt in enumerate(opts):
            if isinstance(opt, (list, tuple)) and len(opt) == 2:
                label, score = opt[0], opt[1]
            elif isinstance(opt, str):
                label, score = opt, j
            elif isinstance(opt, dict):
                label = opt.get("label") or opt.get("text") or opt.get("option")
                score = opt.get("score", j)
            else:
                raise ValueError(f"Invalid option format in question '{q_text}'.")

            if label is None:
                raise ValueError(f"An option in question '{q_text}' is missing a label.")

            try:
                score = int(score)
            except:
                raise ValueError(f"Score for option '{label}' in question '{q_text}' must be a number.")

            norm_opts.append((str(label), score))

        normalized.append({"q": str(q_text), "opts": norm_opts})

    return normalized


def evaluate_result(total):

    if total <= 15:
        return "Excellent Preparation", "Strong revision planning, high confidence, and low exam stress. Students show clear understanding and consistent study habits."

    elif total <= 30:
        return "Good Preparation", "Good study habits with generally high confidence. Some minor stress or inconsistency may still be present."

    elif total <= 45:
        return "Moderate Preparation", "Some gaps in planning and unstable confidence. Students may experience moderate stress and inconsistent revision."

    else:
        return "Low Preparation", "Poor planning, low confidence, and high exam stress. Students are likely to feel unprepared and overwhelmed."


def render_participant_form():
    name = st.text_input("Given Name")
    surname = st.text_input("Surname")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    sid = st.text_input("Student ID")

    if st.button("Start Survey"):
        errors = []

        if name == "" or any(c.isdigit() for c in name):
            errors.append("Invalid given name")

        if surname == "" or any(c.isdigit() for c in surname):
            errors.append("Invalid surname")

        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except:
            errors.append("Invalid DOB format")

        if not sid.isdigit():
            errors.append("Student ID must be digits")

        if errors:
            for e in errors:
                st.error(e)
            st.session_state.start = False
        else:
            st.session_state.start = True
            st.session_state.participant = {
                "name": name,
                "surname": surname,
                "dob": dob,
                "student_id": sid
            }


def render_questionnaire(questions):
    if not questions:
        st.error("No questions available.")
        return

    total = 0
    answers = []

    for i in range(len(questions)):
        question = questions[i]
        opts = [opt[0] for opt in question["opts"]]

        choice = st.radio(
            f"Q{i+1}: {question['q']}",
            opts,
            key=f"q_{i}"
        )

        for opt in question["opts"]:
            if opt[0] == choice:
                total += opt[1]
                answers.append({
                    "question": question["q"],
                    "answer": choice,
                    "score": opt[1]
                })
                break

    if st.button("Submit"):
        state, msg = evaluate_result(total)

        st.success("Result: " + state)
        st.write("Score:", total)
        st.info(msg)

        participant = st.session_state.participant

        data = {
            "name": participant.get("name", ""),
            "surname": participant.get("surname", ""),
            "dob": participant.get("dob", ""),
            "student_id": participant.get("student_id", ""),
            "score": total,
            "result": state,
            "answers": answers
        }

        st.download_button(
            "Download JSON",
            json.dumps(data, indent=2),
            file_name=participant.get("student_id", "result") + "_result.json"
        )

        txt = "Exam Revision Survey Result\n\n"
        txt += "Name: " + participant.get("name", "") + "\n"
        txt += "Surname: " + participant.get("surname", "") + "\n"
        txt += "DOB: " + participant.get("dob", "") + "\n"
        txt += "Student ID: " + participant.get("student_id", "") + "\n"
        txt += "Score: " + str(total) + "\n"
        txt += "Result: " + state + "\n\n"

        txt += "Answers:\n"
        for a in answers:
            txt += a["question"] + "\n"
            txt += "Answer: " + a["answer"] + "\n\n"

        st.download_button(
            "Download TXT",
            txt,
            file_name=participant.get("student_id", "result") + "_result.txt"
        )

# ---------------- MENU ----------------
option = st.selectbox(
    "Choose option",
    [
        "Start new questionnaire",
        "Load existing result",
        "Load questionnaire from JSON"
    ]
)

# ---------------- LOAD EXISTING RESULT ----------------
if option == "Load existing result":
    file = st.file_uploader("Upload JSON or TXT file", type=["json", "txt"])

    if file is not None:
        data = None

        if file.name.endswith(".json"):
            try:
                data = json.load(file)
            except:
                st.error("Invalid JSON file.")
                data = None

        elif file.name.endswith(".txt"):
            content = file.read().decode("utf-8")
            st.write("TXT File Content:")
            st.text(content)

        else:
            st.error("Unsupported file format")

        if data:
            st.success("Loaded successfully")

            st.write("Name:", data.get("name", ""))
            st.write("Surname:", data.get("surname", ""))
            st.write("DOB:", data.get("dob", ""))
            st.write("Student ID:", data.get("student_id", ""))
            st.write("Score:", data.get("score", ""))
            st.write("Result:", data.get("result", ""))

            st.write("Answers:")
            for item in data.get("answers", []):
                st.write("-", item.get("question", ""))
                st.write("Answer:", item.get("answer", ""))

# ---------------- LOAD QUESTIONNAIRE FROM JSON ----------------
if option == "Load questionnaire from JSON":
    q_file = st.file_uploader("Upload questionnaire JSON", type=["json"])

    if q_file is not None:
        try:
            raw = json.load(q_file)
            loaded_questions = normalize_questionnaire(raw)

            st.session_state.custom_questions = loaded_questions

            st.success("Questionnaire loaded successfully!")

            st.write("Preview:")
            for q in loaded_questions:
                st.write("Q:", q["q"])
                for opt in q["opts"]:
                    st.write("-", opt[0])

            if st.button("Start this questionnaire"):
                st.session_state.start = True
                st.session_state.participant = {}

        except Exception as e:
            st.error(f"Invalid questionnaire file: {e}")

    if st.session_state.custom_questions and st.session_state.start:
        render_participant_form()
        if st.session_state.start and st.session_state.participant:
            render_questionnaire(st.session_state.custom_questions)

# ---------------- START NEW QUESTIONNAIRE ----------------
if option == "Start new questionnaire":
    render_participant_form()

    if st.session_state.start and st.session_state.participant:
        render_questionnaire(default_questions)