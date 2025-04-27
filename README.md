# ASHA AI Chatbot

Asha is an inclusive AI-powered career guidance chatbot built for the JobsForHer platform. It provides personalized support for women exploring job opportunities, career paths, mentorship programs, and skill-building resources. Asha leverages LangChain, Hugging Face, and Google’s Generative AI models, along with an extensible toolset (job search, course recommendations, web search). The backend is powered by Flask and MongoDB, and the frontend is built with React.

---

## 🚀 Features

- **Personalized Chat**: Context-aware conversation with session memory and summaries.
- **Tool Integrations**:
  - Job search via RapidAPI’s JSearch
  - Free course recommendations from Udemy API
  - Web search using Brave Search API
- **Summarization**: Automatic conversation summarization using a T5-based pipeline.
- **User Authentication**: Register, login, logout with secure password hashing and cookie-based sessions.
- **Full-Stack Deployment**: Single Dockerfile builds React frontend and Flask backend into one production container.

---

## 📦 Prerequisites

- **Node.js** (v18+)
- **npm** or **yarn**
- **Python** (3.9+)
- **pip**
- **MongoDB Atlas** or local MongoDB instance
- (Optional) **Docker** and **Docker Compose** for containerized deployment

---

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pq36/ASHA_AI_Chatbot.git
   cd ASHA_AI_Chatbot
   ```

2. **Frontend Setup**
   ```bash
   cd client
   npm ci
   # or yarn install
   ```

3. **Backend Setup**
   ```bash
   cd ../chatbot_backend
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate     # Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Environment Variables**

   Create a `.env` file in the `chatbot_backend/` folder with the following keys:
   ```ini
   MONGO_URI=<Your MongoDB connection string>
   BRAVE_API_KEY=<Your Brave Search API key>
   JOB_API_KEY=<Your RapidAPI JSearch key>
   UDEMY_API=<Your Udemy RapidAPI key>
   GOOGLE_API_KEY=<(Optional) Google API key for Gemini>
   ```

---

## 🏃‍♂️ Running Locally

1. **Start MongoDB** (if local)
2. **Run Flask Backend**
   ```bash
   cd chatbot_backend
   flask run --host=0.0.0.0 --port=5000
   ```

3. **Run React Frontend**
   ```bash
   cd client
   npm start
   ```

4. **Visit** `http://localhost:3000` and interact with Asha. Backend APIs are at `http://localhost:5000`.

---

## 🐳 Docker Deployment

A multi-stage Dockerfile builds the React frontend and bundles it with the Flask backend.

1. **Build the image**
   ```bash
   docker build -t asha-chatbot .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 asha-chatbot
   ```

3. **Open** `http://localhost:5000` to use the app.

---

## 📁 Project Structure

```
ASHA_AI_Chatbot/
├── client/               # React frontend
│   ├── public/
│   ├── src/
│   └── package.json
├── chatbot_backend/      # Flask backend
│   ├── chatbot.py        # Main application
│   ├── requirements.txt
│   └── ...
├── Dockerfile            # Multi-stage build
└── README.md
```

---
