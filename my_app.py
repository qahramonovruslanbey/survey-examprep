import streamlit as st
import json
from datetime import datetime

st.title("Exam Revision Planning and Confidence Survey")

# ---------------- MENU ----------------
option = st.selectbox(
    "Choose option",
    ["Start new questionnaire", "Load existing result"]
)

# ---------------- QUESTIONS ----------------
questions = [
    {"q": "How early do you start preparing for exams?",
     "opts": [("Very early",0),("Early",1),("A bit late",2),("Very late",3),("Last minute",4)]},

    {"q": "How organized is your revision schedule?",
     "opts": [("Very organized",0),("Organized",1),("Average",2),("Poor",3),("No plan",4)]},

    {"q": "How often do you follow your revision plan?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},

    {"q": "How confident are you before exams?",
     "opts": [("Very confident",0),("Confident",1),("Neutral",2),("Worried",3),("Very worried",4)]},

    {"q": "How often do you revise past papers?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},

    {"q": "How well do you understand topics?",
     "opts": [("Very well",0),("Well",1),("Average",2),("Poor",3),("Very poor",4)]},

    {"q": "How often do you get distracted?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},

    {"q": "How do you feel after studying?",
     "opts": [("Satisfied",0),("Good",1),("Neutral",2),("Unsure",3),("Stressed",4)]},

    {"q": "How consistent is your study routine?",
     "opts": [("Very consistent",0),("Consistent",1),("Sometimes",2),("Inconsistent",3),("No routine",4)]},

    {"q": "How often do you review weak topics?",
     "opts": [("Always",0),("Often",1),("Sometimes",2),("Rarely",3),("Never",4)]},

    {"q": "How confident are you solving exam questions?",
     "opts": [("Very confident",0),("Confident",1),("Neutral",2),("Not confident",3),("Very weak",4)]},

    {"q": "How well do you manage your time?",
     "opts": [("Excellent",0),("Good",1),("Average",2),("Poor",3),("Very poor",4)]},

    {"q": "How often do you feel overwhelmed?",
     "opts": [("Never",0),("Rarely",1),("Sometimes",2),("Often",3),("Always",4)]},

    {"q": "How motivated are you to study?",
     "opts": [("Highly motivated",0),("Motivated",1),("Average",2),("Low",3),("No motivation",4)]},

    {"q": "How prepared do you feel?",
     "opts": [("Fully prepared",0),("Prepared",1),("Somewhat",2),("Not ready",3),("Not at all",4)]}
]

# ---------------- LOAD EXISTING ----------------
if option == "Load existing result":
    file = st.file_uploader("Upload JSON file", type=["json"])

    if file is not None:
        data = json.load(file)

        st.success("Loaded successfully")

        st.write("Name:", data["name"])
        st.write("Surname:", data["surname"])
        st.write("DOB:", data["dob"])
        st.write("Student ID:", data["student_id"])
        st.write("Score:", data["score"])
        st.write("Result:", data["result"])

        st.write("Answers:")
        for item in data["answers"]:
            st.write("-", item["question"])
            st.write("Answer:", item["answer"])

# ---------------- NEW QUESTIONNAIRE ----------------
if option == "Start new questionnaire":

    name = st.text_input("Given Name")
    surname = st.text_input("Surname")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    sid = st.text_input("Student ID")

    # session state
    if "start" not in st.session_state:
        st.session_state.start = False

    # start button
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

    # show questions
    if st.session_state.start:

        total = 0
        answers = []

        for i in range(len(questions)):
            opts = []
            for opt in questions[i]["opts"]:
                opts.append(opt[0])

            choice = st.radio(
                "Q" + str(i+1) + ": " + questions[i]["q"],
                opts,
                key="q"+str(i)
            )

            for opt in questions[i]["opts"]:
                if opt[0] == choice:
                    total += opt[1]
                    answers.append({
                        "question": questions[i]["q"],
                        "answer": choice,
                        "score": opt[1]
                    })

        # submit button
        if st.button("Submit"):

            if total <= 10:
                state = "Excellent Planning"
                msg = "You have outstanding revision habits and strong confidence."
            elif total <= 20:
                state = "Very Good Preparation"
                msg = "You are well-prepared and confident."
            elif total <= 30:
                state = "Good Preparation"
                msg = "Your preparation is good with minor improvements needed."
            elif total <= 40:
                state = "Moderate Planning"
                msg = "Your revision is inconsistent."
            elif total <= 50:
                state = "Low Confidence"
                msg = "You may struggle in exams."
            else:
                state = "Very Low Confidence"
                msg = "You need serious improvement and support."

            st.success("Result: " + state)
            st.write("Score:", total)
            st.info(msg)

            data = {
                "name": name,
                "surname": surname,
                "dob": dob,
                "student_id": sid,
                "score": total,
                "result": state,
                "answers": answers
            }

            # JSON download
            st.download_button(
                "Download JSON",
                json.dumps(data, indent=2),
                file_name=sid + "_result.json"
            )

            # TXT download
            txt = "Exam Revision Survey Result\n\n"
            txt += "Name: " + name + "\n"
            txt += "Surname: " + surname + "\n"
            txt += "DOB: " + dob + "\n"
            txt += "Student ID: " + sid + "\n"
            txt += "Score: " + str(total) + "\n"
            txt += "Result: " + state + "\n\n"

            txt += "Answers:\n"
            for a in answers:
                txt += a["question"] + "\n"
                txt += "Answer: " + a["answer"] + "\n\n"

            st.download_button(
                "Download TXT",
                txt,
                file_name=sid + "_result.txt"
            )