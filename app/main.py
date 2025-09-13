import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import settings
from database.connection import get_db_connection, get_db_session
from database.queries import UserQueries
from components.pdf_preview import render_pdf_preview
from components.latex_editor import render_latex_editor
from components.sidebar import render_sidebar
from components.visual_resume_builder import VisualResumeBuilder
from utils.pdf_generator import PDFGenerator
from ai_integration.groq_client import GroqClient

# Settings are automatically loaded from Pydantic Settings

# Configure Streamlit page
st.set_page_config(
    page_title="CV Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #1E6B4F;
        border-bottom: 2px solid #2E8B57;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #2E8B57;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #1E6B4F;
    }
    .preview-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        margin-top: 1rem;
        width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E8B57 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())[:8]  # Short unique ID
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'latex_code' not in st.session_state:
        st.session_state.latex_code = ""
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None
    if 'template_style' not in st.session_state:
        st.session_state.template_style = "arpan"
    if 'active_sections' not in st.session_state:
        st.session_state.active_sections = [
            "professional_summary",
            "projects", 
            "professional_experience",
            "research_experience",
            "education",
            "technical_skills"
        ]
    if 'ai_generated_summary' not in st.session_state:
        st.session_state.ai_generated_summary = ""
    if 'summary_generation_count' not in st.session_state:
        st.session_state.summary_generation_count = 0
    if 'job_posting_input' not in st.session_state:
        st.session_state.job_posting_input = ""
    if 'font_size' not in st.session_state:
        st.session_state.font_size = "10pt"

def check_database_connection():
    """Check if database is connected"""
    try:
        db_conn = get_db_connection()
        if not db_conn.test_connection():
            st.error("❌ Database connection failed. Please make sure PostgreSQL is running.")
            st.info("Run: `docker-compose up -d` to start the database")
            return False
        return True
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return False

def render_visual_builder_tab():
    """Render the visual resume builder tab"""
    try:
        # Get current user ID from session state (from sidebar component)
        current_user_id = st.session_state.get('current_user_id')

        if not current_user_id:
            st.warning("⚠️ Please select a user in the Details tab first to use the Visual Builder.")
            st.info("👈 Go to the **Details** tab and select a user to get started.")
            return

        # Initialize visual builder
        visual_builder = VisualResumeBuilder()

        # Render the visual builder interface
        layout_changed = visual_builder.render_visual_builder(current_user_id)

        # Generate PDF button and preview
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("🚀 Generate Resume PDF", key="generate_visual_pdf", use_container_width=True):
                with st.spinner("🎨 Generating your personalized resume..."):
                    pdf_path = visual_builder.generate_optimized_pdf(current_user_id)

                    if pdf_path:
                        st.success("✅ Resume generated successfully!")
                        st.session_state.pdf_path = pdf_path

                        # Show PDF preview
                        st.markdown("### 📄 Generated Resume Preview")
                        render_pdf_preview(force_update=True)
                    else:
                        st.error("❌ Failed to generate PDF. Please check your content and try again.")

    except Exception as e:
        st.error(f"Error in Visual Builder: {e}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

def optimize_resume_for_job(job_description: str):
    """Optimize resume for specific job posting using AI"""
    from components.tabbed_sidebar import gather_user_data, regenerate_latex_with_optimization
    
    if not st.session_state.current_user_id:
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is optimizing your resume for this job..."):
            try:
                # Gather user data
                user_data = gather_user_data()
                
                # Select best projects
                projects = user_data.get('projects', [])
                if projects:
                    selected_projects = groq_client.select_best_projects(projects, job_description, max_projects=3)
                    st.session_state.optimized_projects = selected_projects
                
                # Generate optimized professional summary
                summary = groq_client.generate_professional_summary(user_data, job_description)
                if summary:
                    st.session_state.ai_generated_summary = summary
                
                # Update LaTeX with optimized content
                regenerate_latex_with_optimization()
                
                st.success("🎯 Resume optimized for the job posting!")
                st.info("Switch to LaTeX Editor tab to see the optimized resume.")
                
            except Exception as e:
                st.error(f"Error optimizing resume: {e}")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("<h1 class='main-header'>🎯 AI-Powered CV Resume Builder</h1>", unsafe_allow_html=True)
    
    # Check database connection
    if not check_database_connection():
        st.stop()
    
    # Check for Groq API key
    if not settings.is_groq_available:
        st.warning("⚠️ Groq API key not found in settings. Please add it to your .env file for AI features.")
    
    # Initialize active tab in session state
    if 'active_main_tab' not in st.session_state:
        st.session_state.active_main_tab = 'details'
    
    # Left sidebar with simple tab selection
    with st.sidebar:
        st.markdown("<h2 class='section-header'>📝 Resume Builder</h2>", unsafe_allow_html=True)
        
        # Tab selection buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Details", key="details_tab", use_container_width=True):
                st.session_state.active_main_tab = 'details'
        with col2:
            if st.button("🎨 Visual Builder", key="visual_tab", use_container_width=True):
                st.session_state.active_main_tab = 'visual'
        with col3:
            if st.button("📝 LaTeX Editor", key="latex_tab", use_container_width=True):
                st.session_state.active_main_tab = 'latex'
        
        # Show current active tab
        st.markdown(f"**Active:** {st.session_state.active_main_tab.title()}")
        
        # Job posting input (always available)
        st.markdown("---")
        st.subheader("🎯 Job Posting")
        job_description = st.text_area(
            "Paste job posting for AI optimization:",
            height=120,
            key="job_posting_input",
            placeholder="Paste job description here..."
        )
        
        if job_description:
            if st.button("🎯 Optimize Resume for Job", key="optimize_for_job"):
                optimize_resume_for_job(job_description)
                st.rerun()
    
    # Main content area - changes based on active tab
    if st.session_state.active_main_tab == 'details':
        # Show data entry forms
        st.markdown("<h2 class='section-header'>📋 Resume Details</h2>", unsafe_allow_html=True)
        user_data_changed = render_sidebar()

    elif st.session_state.active_main_tab == 'visual':
        # Show visual resume builder
        render_visual_builder_tab()

    elif st.session_state.active_main_tab == 'latex':
        # Show LaTeX editor + PDF preview (two columns)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("<h2 class='section-header'>📝 LaTeX Editor</h2>", unsafe_allow_html=True)
            latex_changed = render_latex_editor()

        with col2:
            st.markdown("<h2 class='section-header'>📄 PDF Preview</h2>", unsafe_allow_html=True)
            render_pdf_preview(force_update=latex_changed)
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit, PostgreSQL, and Groq AI*")

if __name__ == "__main__":
    main()