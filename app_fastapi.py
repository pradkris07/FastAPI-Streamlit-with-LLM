import os, re, random
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Groq API
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.8
)

app = FastAPI()

# Templates & static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Languages and countries
languages = ["Hindi", "Spanish", "Thai", "Chinese", "Malayalam", "Mexican", "English", "Tamil", "French", "Korean"]
countries = ["United States of America", "China", "India", "Australia", "Germany", "Russia", "Singapore", "United Kingdom", "France", "Canada"]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    apps = {
        "Movies": {"name": "Movies App", "url": "/movies"},
        "University": {"name": "University App", "url": "/universities"},
    }
    return templates.TemplateResponse("index.html", {"request": request, "apps": apps})

@app.get("/movies", response_class=HTMLResponse)
def movies_home(request: Request):
    return templates.TemplateResponse("movies.html", {"request": request, "languages": languages, "top_10_movies": None})

@app.post("/movies/generate", response_class=HTMLResponse)
def movies_generate(request: Request, language: str = Form(...)):
    # Generate top 10 movies
    name_template = f"""
        I want to watch a movie in {language} language. Suggest 15-20 popular, interesting, blockbuster movies in {language} language.
        Provide only the movie names and release year in this format: Movie Name - Year.
        Arrange in descending order of year.
        Do not include any extra explanation or text.
    """
    prompt = PromptTemplate(input_variables=['cuisine'], template=name_template)
    menu_text = llm.invoke(prompt.format(cuisine=language)).content
    movies = re.findall(r"(.*) - (\d{4})", menu_text)
    filtered = [(name, int(year)) for name, year in movies if 2014 <= int(year) <= 2025]
    top_10 = filtered[:10]
    top_10_formatted = [f"{name} - {year}" for name, year in top_10]
    menu_items = [line.split('-')[0].strip() for line in top_10_formatted]

    return templates.TemplateResponse("movies.html", {
        "request": request,
        "languages": languages,
        "top_10_movies": top_10_formatted,
        "menu_items": menu_items,
        "selected_language": language,
        "selected_movie": None,
        "movie_desc": None
    })

@app.post("/movies/details", response_class=HTMLResponse)
def movies_details(request: Request, selected_movie: str = Form(...), selected_language: str = Form(...), top_10_movies: list[str] = Form(...)):
    menu_items = [line.split('-')[0].strip() for line in top_10_movies]

    # Generate description
    desc_template = "Provide a short, appealing storyline of the movie: {dish} in English language. Also name the main actors of the movie"
    desc_prompt = PromptTemplate(input_variables=['dish','cuisine'], template=desc_template)
    desc_result = llm.invoke(desc_prompt.format(dish=selected_movie, cuisine=selected_language))
    movie_desc = desc_result.content

    return templates.TemplateResponse("movies.html", {
        "request": request,
        "languages": languages,
        "top_10_movies": top_10_movies,
        "menu_items": menu_items,
        "selected_language": selected_language,
        "selected_movie": selected_movie,
        "movie_desc": movie_desc
    })

@app.get("/universities", response_class=HTMLResponse)
def uni_home(request: Request):
    return templates.TemplateResponse("universities.html", {"request": request, "countries": countries, "chosen_uni": None})

@app.post("/universities/generate", response_class=HTMLResponse)
def uni_generate(request: Request, country: str = Form(...)):
    name_template = f"""
        I want to find a top university in {country} that is strong in STEM. Suggest exactly 10 universities.  
        - Provide only the university names, one per line.
        - Do NOT add numbering or extra text.
    """
    prompt = PromptTemplate(input_variables=['country'], template=name_template)
    result = llm.invoke(prompt.format(country=country))
    universities = [line.strip() for line in result.content.split('\n')]
    chosen_uni = random.choice(universities)

    menu_template = "Suggest 10 major undergraduate courses that are related to STEM subjects from {university_name}. Provide just names and a short description. Also include major subjects"
    menu_prompt = PromptTemplate(input_variables=['university_name','country'], template=menu_template)
    courses_result = llm.invoke(menu_prompt.format(university_name=chosen_uni, country=country)).content

    return templates.TemplateResponse("universities.html", {
        "request": request,
        "countries": countries,
        "chosen_uni": chosen_uni,
        "courses": courses_result
    })

