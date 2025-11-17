import streamlit as st
import os, re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

# Set Groq API key
groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.8
)

st.set_page_config(page_title="Best Movies 🎥", layout="centered")
st.title("🎞️ Movie Recommender")
st.write("Select a language and I'll suggest a classic movie from the past 10 years!")

# Initialize session state variables
for key in ["generated", "menu_items", "menu_text", "descriptions"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Cuisine selection
cuisine_type = st.selectbox(
    "Choose a language:",
    ["Hindi", "Spanish", "Thai", "Chinese", "Malayalam", "Mexican", "English", "Tamil", "French", "Korean"]
)

# Generate button
if st.button("Suggest"):
    # --- Generate Restaurant Name ---
    with st.spinner("Searching movies..."):
        name_template = f"""
        I want to watch a movie in {cuisine_type} language. Suggest 15-20 popular, interesting, blockbuster movies in {cuisine_type} language.
        Provide only the movie names and release year in this format: Movie Name - Year.
        Arrange in descending order of year.
        Do not include any extra explanation or text.
        """
        name_prompt = PromptTemplate(input_variables=['cuisine'], template=name_template)
        menu_text = llm.invoke(name_prompt.format(cuisine=cuisine_type)).content
        movies = re.findall(r"(.*) - (\d{4})", menu_text)
        filtered_movies = [(name, int(year)) for name, year in movies if 2014 <= int(year) <= 2025]
        
        top_10_movies = filtered_movies[:10]
        top_10_movies_formatted = [f"{name} - {year}" for name, year in top_10_movies]
        st.session_state.menu_text = top_10_movies_formatted

        # Extract menu items
        menu_items = [line.split('-')[0].strip() for line in st.session_state.menu_text if '-' in line]
        st.session_state.menu_items = menu_items

    # --- Generate Descriptions for ALL items ---
    st.session_state.descriptions = {}
    with st.spinner("Generating movie descriptions..."):
        for dish in st.session_state.menu_items:
            desc_template = "Provide a short, appealing storyline of the movie: {dish} in English language. Also name the main actors of the movie"
            desc_prompt = PromptTemplate(input_variables=['dish','cuisine'], template=desc_template)
            desc_result = llm.invoke(desc_prompt.format(dish=dish, cuisine=cuisine_type))
            st.session_state.descriptions[dish] = desc_result.content

    st.session_state.generated = True

# --- Display results if generated ---
if st.session_state.generated:
    #st.success(f"🍴 Restaurant Name: **{st.session_state.restaurant_name}**")
    st.subheader("📜 Best Movies")
    st.write("\n\n".join(st.session_state.menu_text))

    # Dropdown to select a menu item
    selected_item = st.selectbox("Select a movie to see its details:", st.session_state.menu_items)
    if selected_item:
        st.info(f"📖 **{selected_item}**:\n{st.session_state.descriptions[selected_item]}")
