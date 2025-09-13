# 🚀 Quick Setup Guide

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- LaTeX distribution (texlive-full)
- Groq API key

## Installation Steps

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   nano .env
   ```

2. **Start Database**
   ```bash
   docker-compose up -d
   ```

3. **Install LaTeX**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install texlive-full
   
   # macOS
   brew install mactex
   ```

4. **Run Application**
   ```bash
   # From project root
   streamlit run app/main.py
   
   # Or from app directory
   cd app && streamlit run main.py
   ```

## First Run

1. Open browser to `http://localhost:8501`
2. Enter your email in the sidebar
3. Click "Create New User"
4. Start building your resume!

## Environment Variables

Required in `.env` file:
```bash
DATABASE_URL=postgresql://cv_user:cv_password@localhost:5432/cv_builder
GROQ_API_KEY=your_groq_api_key_here
DEBUG=True
STREAMLIT_SERVER_PORT=8501
```

## Troubleshooting

- **Database connection failed**: Run `docker-compose up -d`
- **LaTeX compilation errors**: Install `texlive-full`
- **AI features disabled**: Check `GROQ_API_KEY` in `.env`
- **Port conflicts**: Change `STREAMLIT_SERVER_PORT` in `.env`

## Features Overview

- 🤖 **AI Optimization**: Generate summaries, select projects
- 📝 **LaTeX Editor**: Real-time editing with syntax highlighting
- 📄 **PDF Preview**: Live PDF generation and preview
- 💾 **Data Persistence**: PostgreSQL storage for all user data
- 🎨 **Templates**: Arpan (modern) and Simple (classic) styles

Ready to build professional resumes! 🎯