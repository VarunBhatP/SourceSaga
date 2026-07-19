# SourceSage 🚀

**Find Your Perfect Open Source Contribution with AI**

SourceSage is an AI-powered intelligent assistant that helps developers find "good first issues" on GitHub, analyzes them, and drafts professional GSOC proposals instantly.
 

---

## ✨ Features

- **Smart Issue Search**: Find beginner-friendly GitHub issues based on your specific skills (e.g., "Python, React, FastAPI").
- **AI Analysis**: Uses **Grok via xAI API** to analyze issue context and generate a step-by-step technical solution plan.
- **Auto-Draft Proposals**: Generates professional, download-ready GSOC proposals in `.docx` format.
- **Real-Time Insights**: Powered by **FastAPI** and **LangGraph** for agentic workflows.
- **Premium UI**: Stunning, responsive frontend built with **React**, **Tailwind CSS**, and **Shadcn UI**.
- **Dark Mode**: Fully supported dark mode for late-night coding sessions.

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python)
- **AI/LLM**: xAI Grok API (`grok-3-mini`, `grok-4.1-fast`)
- **Orchestration**: LangGraph (Agentic workflow)
- **Database**: MongoDB (Caching analyses)
- **Tools**: `crewai`, `python-docx`

### **Frontend**
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **Components**: Shadcn UI, Lucide React
- **Animations**: Framer Motion
- **State Management**: React Hooks

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (Local or Atlas)
- xAI API Key for Grok (Get one at [xAI Console](https://console.x.ai))

### 1. Clone the Repository
git clone https://github.com/VarunBhatP/sourcesage.git
cd sourcesage


### 2. Backend Setup
cd backend

#### 2.1. Create virtual environment
python -m venv venv

#### 2.2. Activate it (Windows)
venv\Scripts\activate

#### 2.2. Activate it (Mac/Linux)
source venv/bin/activate

#### 2.3. Install dependencies
pip install -r requirements.txt

#### 2.4. Set up environment variables
##### Create a .env file in /backend with:
XAI_API_KEY=your_key_here
MONGODB_URL=mongodb://localhost:27017
#### 2.5. Run the server
python run.py

text
*Backend will run at `http://localhost:8000`*

### 3. Frontend Setup
cd frontend

#### 3.1. Create virtual environment
python -m venv venv

#### 3.2.Install dependencies
npm install

#### 3.3.Start the dev server
npm run dev

text
*Frontend will run at `http://localhost:5173` (or `8080`)*

---

## 📂 Project Structure

### sourcesage/
### ├── backend/
### │ ├── agents/ # AI Agents (Analysis, Report Drafter)
### │ ├── api/ # FastAPI Routes & Models
### │ ├── database/ # MongoDB Connection & Caching
### │ ├── graph/ # LangGraph State & Workflow
### │ ├── utils/ # Helper functions
### │ ├── app.py # Main Application Entry
### │ └── run.py # Server Runner
### │
### └── frontend/
### ├── src/
### │ ├── components/ # React Components (Hero, IssuesList, AnalysisView)
### │ ├── lib/ # Utilities (Tailwind merge, API client)
### │ ├── pages/ # Main Pages (Index)
### │ └── App.jsx # Main App Component
### └── package.json

text

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<p align="center">
  Built by <a href="https://github.com/VarunBhatP">Varun Bhat P</a> using <b>Grok</b>
</p>
