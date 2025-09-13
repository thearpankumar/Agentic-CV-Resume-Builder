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
    page_title="Professional Resume Builder",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23333333'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z'/><polyline points='14,2 14,8 20,8'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
st.markdown("""
<style>
    /* Root and App Background */
    .stApp {
        background-color: #0F0F0F;
        color: #E8E8E8;
    }

    /* Main Header */
    .main-header {
        text-align: center;
        color: #E8E8E8;
        margin-bottom: 2rem;
        font-weight: 600;
    }

    /* Section Headers */
    .section-header {
        color: #E8E8E8;
        border-bottom: 2px solid #404040;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Specific styling for Resume Details header */
    .resume-details-header {
        color: #E8E8E8;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    /* Buttons - Professional Grey Theme */
    .stButton > button {
        background-color: #404040;
        color: #E8E8E8;
        border-radius: 6px;
        border: 1px solid #606060;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #505050;
        border-color: #707070;
        box-shadow: 0 2px 8px rgba(96, 96, 96, 0.2);
    }

    /* Success/Info/Warning Messages */
    .stSuccess {
        background-color: #1A2E1A;
        border: 1px solid #2E5E2E;
        color: #90EE90;
    }
    .stInfo {
        background-color: #1A1A2E;
        border: 1px solid #2E2E5E;
        color: #87CEEB;
    }
    .stWarning {
        background-color: #2E2E1A;
        border: 1px solid #5E5E2E;
        color: #FFE55C;
    }
    .stError {
        background-color: #2E1A1A;
        border: 1px solid #5E2E2E;
        color: #FF6B6B;
    }

    /* Input Fields and Widgets */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #1A1A1A;
        color: #E8E8E8;
        border: 1px solid #404040;
    }

    /* Tabs - Professional Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        background-color: #1A1A1A;
        border: 1px solid #404040;
        border-radius: 6px;
        color: #B0B0B0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #404040 !important;
        color: #E8E8E8 !important;
        border-color: #606060 !important;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #1A1A1A;
    }

    /* Professional Navigation Tabs */
    .sidebar-nav-tabs {
        margin-bottom: 1rem;
    }
    .nav-tab-active {
        background-color: #404040 !important;
        color: #E8E8E8 !important;
        border: 2px solid #606060 !important;
        font-weight: 600;
    }
    .nav-tab-inactive {
        background-color: #1A1A1A !important;
        color: #B0B0B0 !important;
        border: 2px solid #2A2A2A !important;
        font-weight: 400;
    }

    /* Preview Container */
    .preview-container {
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 1rem;
        background-color: #1A1A1A;
        width: 100%;
    }

    /* Code Editor Styling */
    .stCodeBlock {
        background-color: #1A1A1A;
        border: 1px solid #404040;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1A1A1A;
        color: #E8E8E8;
        border: 1px solid #404040;
    }

    /* Metrics and Stats */
    .metric-container {
        background-color: #1A1A1A;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #404040;
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
            st.error("Database connection failed. Please make sure PostgreSQL is running.")
            st.info("Run: `docker-compose up -d` to start the database")
            return False
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def render_visual_builder_tab():
    """Render the visual resume builder tab"""
    try:
        # Get current user ID from session state (from sidebar component)
        current_user_id = st.session_state.get('current_user_id')

        if not current_user_id:
            st.warning("Please select a user in the Details tab first to use the Visual Builder.")
            st.info("Go to the **Details** tab and select a user to get started.")
            return

        # Initialize visual builder
        visual_builder = VisualResumeBuilder()

        # Render the visual builder interface (now includes PDF generation at the end)
        layout_changed = visual_builder.render_visual_builder(current_user_id)

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
        with st.spinner("AI is optimizing your resume for this job..."):
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
    st.markdown("<h1 class='main-header'>AI-Powered CV Resume Builder</h1>", unsafe_allow_html=True)
    
    # Check database connection
    if not check_database_connection():
        st.stop()
    
    # Check for Groq API key
    if not settings.is_groq_available:
        st.warning("Groq API key not found in settings. Please add it to your .env file for AI features.")
    
    # Initialize active tab in session state
    if 'active_main_tab' not in st.session_state:
        st.session_state.active_main_tab = 'details'
    
    # Left sidebar with horizontal tab navigation
    with st.sidebar:
        st.markdown("<h2 class='section-header'>Resume Builder</h2>", unsafe_allow_html=True)

        # Tab selection buttons - stacked horizontally (one below the other)
        st.markdown('<div class="sidebar-nav-tabs">', unsafe_allow_html=True)

        # Details tab
        details_style = "nav-tab-active" if st.session_state.active_main_tab == 'details' else "nav-tab-inactive"
        if st.button("Details", key="details_tab", use_container_width=True):
            st.session_state.active_main_tab = 'details'
            st.rerun()

        # Visual Builder tab
        visual_style = "nav-tab-active" if st.session_state.active_main_tab == 'visual' else "nav-tab-inactive"
        if st.button("Visual Builder", key="visual_tab", use_container_width=True):
            st.session_state.active_main_tab = 'visual'
            st.rerun()

        # LaTeX Editor tab
        latex_style = "nav-tab-active" if st.session_state.active_main_tab == 'latex' else "nav-tab-inactive"
        if st.button("LaTeX Editor", key="latex_tab", use_container_width=True):
            st.session_state.active_main_tab = 'latex'
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        
    
    # Main content area - changes based on active tab
    if st.session_state.active_main_tab == 'details':
        # Show data entry forms
        st.markdown("<h2 class='resume-details-header'>📋 Resume Details</h2>", unsafe_allow_html=True)
        user_data_changed = render_sidebar()

    elif st.session_state.active_main_tab == 'visual':
        # Show visual resume builder
        render_visual_builder_tab()

    elif st.session_state.active_main_tab == 'latex':
        # Show LaTeX editor + PDF preview (two columns)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("<h2 class='section-header'>LaTeX Editor</h2>", unsafe_allow_html=True)
            latex_changed = render_latex_editor()

        with col2:
            st.markdown("<h2 class='section-header'>PDF Preview</h2>", unsafe_allow_html=True)
            render_pdf_preview(force_update=latex_changed)
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit, PostgreSQL, and Groq AI*")

if __name__ == "__main__":
    main()