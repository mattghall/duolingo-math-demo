import streamlit as st
import os
import requests
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

st.set_page_config(page_title="Matt's Duolingo Math Assistant Demo", page_icon="🧮")
st.title("Matt's Duolingo Math Assistant Demo")

st.write("""
Enter a premise (e.g., a name, topic, or idea) and select a math category. The AI will generate a creative math problem for you!
""")

# Add a session state variable to track if a problem is being generated
if 'generating' not in st.session_state:
    st.session_state['generating'] = False
if 'show_solution' not in st.session_state:
    st.session_state['show_solution'] = False

premise = st.text_input("Premise", "Taylor Swift")
category = st.selectbox("Category", ["Algebra", "Geometry", "Logarithms", "Sequences"])
age_category = st.selectbox("Age Category", ["Elementary", "Middle School", "High School", "College"])

# Add custom CSS to fully gray out and disable the button, including hover
st.markdown(
    """
    <style>
    .element-container button[disabled], .element-container button[disabled]:hover, .element-container button[disabled]:focus {
        background-color: #cccccc !important;
        color: #888888 !important;
        border: 1px solid #bbbbbb !important;
        cursor: not-allowed !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Track previous prompt values to enable/disable generate button
if 'prev_premise' not in st.session_state:
    st.session_state['prev_premise'] = premise
if 'prev_category' not in st.session_state:
    st.session_state['prev_category'] = category
if 'prev_age_category' not in st.session_state:
    st.session_state['prev_age_category'] = age_category

# Enable generate button only if prompts have changed or not generating
prompts_changed = (
    premise != st.session_state['prev_premise'] or
    category != st.session_state['prev_category'] or
    age_category != st.session_state['prev_age_category']
)

can_generate = (not st.session_state['generating']) and prompts_changed

generate_btn = st.button("Generate Math Problem", key="generate_btn", disabled=not can_generate)

problem_text = None
solution_text = None

# Immediately set generating state if button is pressed
if generate_btn and not st.session_state['generating']:
    st.session_state['generating'] = True
    st.session_state['prev_premise'] = premise
    st.session_state['prev_category'] = category
    st.session_state['prev_age_category'] = age_category
    st.rerun()

if st.session_state['generating']:
    st.session_state['show_solution'] = False
    with st.spinner('Generating problem...'):
        if not OPENROUTER_API_KEY:
            st.error("OpenRouter API key not set. Please set the OPENROUTER_API_KEY environment variable or .env file.")
        else:
            prompt = (
                f"Generate a creative, high-quality {category} math problem for a {age_category} student based on the following premise: '{premise}'. "
                "The problem should be engaging and context-rich, suitable for a learner. "
                "After the problem, provide a clear, step-by-step solution.\n\n"
                "Format all equations and math expressions using LaTeX in dollar signs (e.g., $x^2+1$ for inline, $$x^2+1$$ for display math) so they render correctly in Streamlit.\n"
                "Format your response as:\nProblem: <problem statement>\nSolution: <solution>"
            )
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful math teacher who creates fun, real-world math problems."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.8
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    # Extract problem and solution using regex
                    match = re.search(r"Problem:(.*?)(?:Solution:|$)(.*)", content, re.DOTALL)
                    if match:
                        problem_text = match.group(1).strip()
                        solution_text = match.group(2).strip()
                    else:
                        problem_text = content
                        solution_text = None
                    st.session_state['problem_text'] = problem_text
                    st.session_state['solution_text'] = solution_text
                else:
                    st.error(f"Error from OpenRouter: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error generating problem: {e}")
    st.session_state['generating'] = False
    st.rerun()

# Display the problem if available
if 'problem_text' in st.session_state and st.session_state['problem_text']:
    st.markdown(f"**Problem:**\n\n")
    st.markdown(st.session_state['problem_text'])
    if st.session_state.get('solution_text'):
        if st.session_state['show_solution']:
            if st.button("Hide Solution"):
                st.session_state['show_solution'] = False
                st.rerun()
            st.markdown(f"**Solution:**\n\n")
            st.markdown(st.session_state['solution_text'])
        else:
            if st.button("See Solution"):
                st.session_state['show_solution'] = True
                st.rerun()
