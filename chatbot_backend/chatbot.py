from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
# LangChain imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_community.tools import BraveSearch
from langchain.schema.runnable import RunnableBranch, RunnableLambda
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import BaseMessage
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import make_response
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
# Load once
summarizer = pipeline("summarization", model="t5-small")


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["asha_db"]
user_sessions = db["user_sessions"]
users_collection = db["users"]
app = Flask(__name__)
CORS(app, supports_credentials=True)

# ====== Tools and Utilities ======

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
JOB_API_KEY = os.getenv("JOB_API_KEY")
UDEMY_API=os.getenv("UDEMY_API")

def get_session_history(session_id: str):
    return ChatMessageHistory()

def generate_full_summary(messages):
    full_text = " ".join(msg.content for msg in messages if hasattr(msg, 'content'))

    if len(full_text) > 4000:
        full_text = full_text[:4000]  # To avoid too large input

    num_words = len(full_text.split())

    if num_words < 20:
        # Very small conversation, don't even summarize, return as it is
        return full_text

    max_length = min(100, int(num_words * 0.7))  # 70% of words

    # Never let it be too tiny
    max_length = max(max_length, 10)

    summary = summarizer(
        full_text,
        max_length=max_length,
        min_length=max(5, int(max_length * 0.5)),
        do_sample=False
    )
    return summary[0]['summary_text']

def update_session_summary(session_id, new_summary):
    user_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"summary": new_summary}}
    )

def maybe_update_summary(session_id, all_messages):
    if len(all_messages)%10==0:  # 10 user+bot pairs
        new_summary = generate_full_summary(all_messages)
        update_session_summary(session_id, new_summary)

def get_session_summary(session_id):
    """
    Fetch the saved conversation summary from MongoDB for the given session ID.
    """
    session_data = user_sessions.find_one({"session_id": session_id})
    if session_data and "summary" in session_data:
        return session_data["summary"]
    return None

@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello {name}, I'm Asha! 🌸 I'm here to help you explore jobs, careers, mentorships, and events."

from langchain_core.tools import tool


@tool
def fetch_learning_resources(query: str) -> str:
    """
    Search for free Udemy courses with detailed information including ratings, duration, and expiry dates.
    
    Args:
        query (str): The search term for courses (e.g., "python", "AI", "web development").
        
    Returns:
        str: A beautifully formatted list of courses with all key details or an error message.
    """
    url = "https://paid-udemy-course-for-free.p.rapidapi.com/search"
    
    headers = {
        "x-rapidapi-key": UDEMY_API,  # Defined elsewhere
        "x-rapidapi-host": "paid-udemy-course-for-free.p.rapidapi.com"
    }
    
    params = {"s": query}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        courses = response.json()
        
        if not courses:
            return f"🔍 No courses found for '{query}'. Try a different search term."
        
        formatted_courses = []
        for course in courses[:5]:  # Show top 5 results         
            # Build course card
            card = [
                f"🎯 {course['title']}",
                f"⭐ Rating: {course['rating']}/5 | ⏳ Duration: {course['duration']} hours",
                f"📚 Category: {course['category']} | 🌐 Language: {course['language']}",
                f"📝 Description: {course['desc_text'][:100]}...",
                "──────────────────────────"
            ]
            formatted_courses.append("\n".join(card))
        
        return "\n\n".join(formatted_courses)
    
    except requests.exceptions.RequestException as e:
        return f"⚠️ API Error: {str(e)}"
    except ValueError as e:
        return f"⚠️ Data Error: {str(e)}"
    except KeyError as e:
        return f"⚠️ Missing expected data field: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

@tool
def search_jobs(query: str, country: str = "india", page: int = 1, num_pages: int = 1, date_posted: str = "all", work_from_home: bool = False) -> str:
    """
    Search for jobs using a query and optional filters like country, pagination, and remote.
    
    Args:
        query (str): Free-form job search query (e.g. 'developer jobs in chicago').
        country (str): Country code (default 'us').
        page (int): Page number to return.
        num_pages (int): Number of pages to return (max 20).
        date_posted (str): One of ['all', 'today', '3days', 'week', 'month'].
        work_from_home (bool): Whether to return only remote jobs.

    Returns:
        str: Top matching job listings or an error message.
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": JOB_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": query,
        "page": str(page),
        "num_pages": str(num_pages),
        "country": country,
        "date_posted": date_posted,
        "radius": "10000000"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        jobs = response.json().get("data", [])[:3]
        if not jobs:
            return "No jobs found for your search."
        result = "\n\n".join(
            f"📌 {job.get('job_title')} at {job.get('employer_name')}\n"
            f"Publisher: {job.get('job_publisher')}, {job.get('job_country')}\n"
            f"🔗 {job.get('job_apply_link')}\n{job.get('job_city')}"
            for job in jobs
        )
        return result
    else:
        return f"❌ Request failed with status {response.status_code}: {response.text}"



bravetool = BraveSearch.from_api_key(api_key=BRAVE_API_KEY, search_kwargs={"count": 3})

tools = [greet, bravetool, search_jobs,fetch_learning_resources]
tool_map = {tool.name: tool for tool in tools}

llmh = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # or "gemini-1.5-pro", depending on what you want
    temperature=0.2
)

# Bind tools to Gemini
llm = llmh.bind_tools(tools)
def get_user_details(email):
    user = users_collection.find_one({"email": email})
    if user:
        return user  # Returns user data like name, age, domain, etc.
    return None
from flask import make_response

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists!"}), 409  # Conflict

    hashed_pw = generate_password_hash(password)

    user_data = {
        "name": data.get("name"),
        "email": email,
        "password": hashed_pw,
        "role": data.get("role"),
        "age": data.get("age"),
        "domain": data.get("domain")
    }

    users_collection.insert_one(user_data)

    # Create a response with cookie
    response = make_response(jsonify({"message": "User registered successfully!"}))
    response.set_cookie("user_email", email)
    response.set_cookie("user_name", user_data["name"])

    return response, 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create a response with cookies
    response = make_response(jsonify({
        "message": "Login successful!",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "age": user["age"],
            "domain": user["domain"]
        }
    }))
    response.set_cookie("user_email", user["email"])
    response.set_cookie("user_name", user["name"])

    return response, 200


@app.route("/logout")
def logout():
    resp = make_response(jsonify({"message": "Logged out"}))
    # Clear all user-related cookies
    resp.set_cookie("user_id", "", expires=0)
    resp.set_cookie("user_email", "", expires=0)
    resp.set_cookie("user_name", "", expires=0)
    return resp, 200


def prompt_with_tool_call(response):
    for call in response.tool_calls:
        tool_name = call["name"]
        args = call["args"]
        tool_result = tool_map[tool_name].invoke(args)
    return str(tool_result)

branches = RunnableBranch(
    (
        lambda x: hasattr(x, "tool_calls") and x.tool_calls,
        RunnableLambda(lambda x: prompt_with_tool_call(x))
    ),
    RunnableLambda(lambda x: x)
)

chain = llm
chain2 = chain | branches

chain_with_memory = chain2
# 1️⃣ Define your system prompt template with placeholders for user info
system_template = SystemMessagePromptTemplate.from_template(
    "You are Asha, an inclusive career assistant for women.\n"
    "You provide personalized career guidance based on each user's information.\n"
    "Current user:\n"
    "- Name: {name}\n"
    "- Domain: {domain}\n"
    "- Age: {age}\n"
    "Always be empathetic and helpful."
)

# 2️⃣ Define your human prompt template (summary + recent messages + input)
human_template = HumanMessagePromptTemplate.from_template(
    "Summary of previous conversation:\n"
    "{summary}\n\n"
    "Recent conversation:\n"
    "{recent_messages}\n\n"
    "User’s latest question:\n"
    "{input}"
)
def get_session_history(session_id: str):
    session_data = user_sessions.find_one({"session_id": session_id})
    history = ChatMessageHistory()
    if session_data and "messages" in session_data:
        for msg in session_data["messages"]:
            if msg["type"] == "human":
                history.add_user_message(msg["content"])
            else:
                history.add_ai_message(msg["content"])
    return history
# 3️⃣ Combine into a single ChatPromptTemplate
chat_prompt = ChatPromptTemplate.from_messages([
    system_template,
    human_template
])
def create_system_prompt(user_details):
    if user_details:
        # Dynamically customize system prompt with user info
        user_name = user_details.get("name", "User")
        user_domain = user_details.get("domain", "the industry")
        user_age = user_details.get("age", "unknown age")
        
        # Create a string-based system prompt template
        system_prompt_str = f"""
        You are Asha, an inclusive career assistant for women. You provide personalized career guidance based on each user's information.
        User details:
        Name: {user_name}
        Domain: {user_domain}
        Age: {user_age}
        Be empathetic and helpful, tailoring your advice to their career needs.
        """
        
        # Now, create a SystemMessagePromptTemplate with the string
        system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_str)
        return system_prompt
    return None

from langchain.schema import SystemMessage, HumanMessage

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    session_id = request.cookies.get("user_email")
    if not session_id:
        return jsonify({"error": "No session ID in cookies"}), 401

    user = users_collection.find_one({"email": session_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    name = user.get("name", "User")
    domain = user.get("domain", "the industry")
    age = user.get("age", "unknown age")

    history = get_session_history(session_id).messages
    maybe_update_summary(session_id, history)
    saved_summary = get_session_summary(session_id) or "No prior summary."
    recent_msgs = history[-10:]
    recent_text = "\n".join(
        f"{'User' if m.type == 'human' else 'Asha'}: {m.content}"
        for m in recent_msgs
    )

    # Format prompt
    pv = chat_prompt.format_prompt(
        name=name,
        domain=domain,
        age=age,
        summary=saved_summary,
        recent_messages=recent_text,
        input=user_input
    )
    messages = pv.to_messages()

    # Get LLM response
    llm_response = chain.invoke(messages)

    if hasattr(llm_response, "tool_calls") and llm_response.tool_calls:
        reply_text = prompt_with_tool_call(llm_response)
        # Store as simple string
        reply_content = "tool called"
        res=reply_text
    else:
        reply_text = llm_response
        # Extract just the content if it's an AIMessage
        reply_content = reply_text.content if hasattr(reply_text, 'content') else str(reply_text)
        res=reply_content

    # Save conversation (simplified format)
    user_sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "$each": [
                        {"type": "human", "content": user_input},
                        {"type": "ai", "content": reply_content}
                    ]
                }
            }
        },
        upsert=True
    )

    return jsonify({"response": res})
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
