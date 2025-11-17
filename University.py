import streamlit as st
import os, random
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

# Set Groq API key
#os.environ['GROQ_API_KEY'] = groq_api_key
groq_api_key = os.getenv('GROQ_API_KEY')

# Create Groq chat model
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.8
)

# Streamlit app
st.set_page_config(page_title="🌐 Universities of the World ", layout="centered")
st.title("🏛️ Best Universities")
st.write("Give the country name and I'll suggest one of the best Universities of it and courses from there!")

# Dropdown for cuisine selection
cuisine_type = st.selectbox(
    "Choose a country:",
    ["United States of America", "China", "India", "Australia", "Germany", "Russia", "Singapore", "United Kingdom", "France", "Canada"]
)
# User input
# cuisine_type = st.text_input("Enter the cuisine type (e.g., Italian, Japanese, Mexican):")

if st.button("Suggest"):
    if cuisine_type.strip() == "":
        st.warning("⚠️ Please enter a country.")
    else:
        with st.spinner("Preparing list..."):
            # Prompt for University name
            name_template = f"""
            I want to find a top university in {cuisine_type} that is strong in STEM. Suggest exactly 10 universities.  
            - Provide only the **university names**, one per line.  
            - Do NOT add any numbering, bullets, labels, or extra words like "University:" at the start.  
            - Do NOT include any explanation, text, or punctuation except the university name.  
            - Pick universities that are well-known in STEM.
            """
            name_prompt = PromptTemplate(input_variables=['country'], template=name_template)
            result = llm.invoke(name_prompt.format(country=cuisine_type))
            universities = [line for line in result.content.split('\n')]
            chosen_uni = random.choice(universities)
            university_name = chosen_uni

        st.success(f"🏛️ University: **{university_name}**")

        with st.spinner("Preparing the course lists..."):
            # Prompt for menu
            menu_template = "Suggest 10 major undergraduate courses that are related to STEM subjects from {university_name}. Provide just names and a short description. Also include major subjects"
            menu_prompt = PromptTemplate(input_variables=['university_name','country'], template=menu_template)
            result = llm.invoke(menu_prompt.format(university_name=university_name, country=cuisine_type))

        st.subheader("📜 Subjects")
        st.write(result.content)
