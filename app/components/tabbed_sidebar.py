import streamlit as st
from typing import Dict, Any, Optional
from database.connection import get_db_session
from database.queries import (
    UserQueries, ProjectQueries, ExperienceQueries, 
    EducationQueries, SkillsQueries, CertificationQueries
)
from utils.validators import DataValidator
from ai_integration.groq_client import GroqClient
from streamlit_ace import st_ace
from utils.pdf_generator import PDFGenerator

def render_tabbed_sidebar() -> bool:
    """
    Render the new tabbed sidebar with Details and LaTeX Editor tabs
    Returns: True if data was changed, False otherwise
    """
    data_changed = False
    
    # Create tabs
    tab1, tab2 = st.tabs(["📋 Details", "📝 LaTeX Editor"])
    
    with tab1:
        data_changed |= render_details_tab()
    
    with tab2:
        data_changed |= render_latex_editor_tab()
    
    return data_changed

def render_details_tab() -> bool:
    """Render the Details tab with all data entry forms and AI reframing"""
    data_changed = False
    
    # Initialize session state for current user
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    
    # User management section
    st.subheader("👤 User Profile")
    data_changed |= render_user_section()
    
    # Only show other sections if user is selected/created
    if st.session_state.current_user_id:
        st.markdown("---")
        st.subheader("💼 Projects")
        data_changed |= render_projects_section_with_ai()
        
        st.markdown("---")
        st.subheader("🏢 Professional Experience")
        data_changed |= render_professional_experience_section_with_ai()
        
        st.markdown("---")
        st.subheader("🔬 Research Experience")
        data_changed |= render_research_experience_section()
        
        st.markdown("---")
        st.subheader("🎓 Education")
        data_changed |= render_education_section()
        
        st.markdown("---")
        st.subheader("⚡ Technical Skills")
        data_changed |= render_skills_section()
        
        st.markdown("---")
        st.subheader("🏆 Certifications")
        data_changed |= render_certifications_section()
    
    return data_changed

def render_latex_editor_tab() -> bool:
    """Render the LaTeX Editor tab with job posting integration and AI features"""
    data_changed = False
    
    # Job posting section
    st.subheader("🎯 Job Posting Analysis")
    job_description = st.text_area(
        "Paste the job posting here to optimize your resume:",
        height=150,
        key="job_posting_input",
        placeholder="Paste the job description here to get AI-powered resume optimization..."
    )
    
    if job_description:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Optimize Resume for Job", key="optimize_for_job"):
                optimize_resume_for_job(job_description)
                data_changed = True
        
        with col2:
            if st.button("📊 Analyze Job Posting", key="analyze_job"):
                analyze_job_posting(job_description)
    
    st.markdown("---")
    
    # Professional Summary Generation Section
    st.subheader("✨ AI Professional Summary")
    data_changed |= render_professional_summary_section(job_description)
    
    st.markdown("---")
    
    # LaTeX Editor Section
    st.subheader("📝 LaTeX Code Editor")
    data_changed |= render_latex_editor_section()
    
    return data_changed

def render_projects_section_with_ai() -> bool:
    """Render projects section with AI reframing capabilities"""
    data_changed = False
    
    # Load projects
    projects = load_user_projects()
    
    # Display existing projects with AI reframe buttons
    if projects:
        st.write(f"**Current Projects ({len(projects)}):**")
        for i, project in enumerate(projects):
            with st.expander(f"{project.get('title', 'Untitled Project')}", expanded=False):
                st.write(f"**Technologies:** {project.get('technologies', 'N/A')}")
                st.write(f"**Period:** {project.get('start_date', '')} - {project.get('end_date', 'Present')}")
                
                # Current description
                st.write("**Current Description:**")
                st.write(project.get('description', 'No description'))
                
                # AI Reframe section
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"✨ Reframe with AI", key=f"reframe_project_{i}"):
                        reframe_project_description(project, i)
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_project_{i}"):
                        st.session_state[f'editing_project_{i}'] = True
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_project_{i}"):
                        if delete_project(project['id']):
                            st.success("Project deleted!")
                            data_changed = True
                            st.rerun()
    
    # Add new project form
    with st.expander("Add New Project", expanded=False):
        data_changed |= render_add_project_form()
    
    return data_changed

def render_professional_experience_section_with_ai() -> bool:
    """Render professional experience section with AI reframing"""
    data_changed = False
    
    experiences = load_user_professional_experience()
    
    if experiences:
        st.write(f"**Current Experience ({len(experiences)}):**")
        for i, exp in enumerate(experiences):
            with st.expander(f"{exp.get('position', 'Position')} at {exp.get('company', 'Company')}", expanded=False):
                st.write(f"**Period:** {exp.get('start_date', '')} - {exp.get('end_date', 'Present')}")
                
                # Current description
                st.write("**Current Description:**")
                st.write(exp.get('description', 'No description'))
                
                # AI Reframe section
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✨ Reframe with AI", key=f"reframe_exp_{i}"):
                        reframe_experience_description(exp, i)
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_exp_{i}"):
                        st.session_state[f'editing_exp_{i}'] = True
    
    # Add new experience form
    with st.expander("Add Professional Experience", expanded=False):
        data_changed |= render_add_professional_experience_form()
    
    return data_changed

def render_professional_summary_section(job_description: str) -> bool:
    """Render professional summary generation and refinement section"""
    data_changed = False
    
    # Initialize session state for professional summary
    if 'ai_generated_summary' not in st.session_state:
        st.session_state.ai_generated_summary = ""
    if 'summary_generation_count' not in st.session_state:
        st.session_state.summary_generation_count = 0
    
    # Show current summary if exists
    if st.session_state.ai_generated_summary:
        st.write("**Current AI-Generated Summary:**")
        st.info(st.session_state.ai_generated_summary)
        
        # Feedback and regeneration
        col1, col2 = st.columns([2, 1])
        with col1:
            user_feedback = st.text_input(
                "Feedback for improvement:",
                key="summary_feedback",
                placeholder="e.g., Make it more technical, focus on leadership, add specific skills..."
            )
        
        with col2:
            if st.button("🔄 Regenerate Summary", key="regenerate_summary"):
                regenerate_professional_summary(job_description, user_feedback)
                data_changed = True
    
    # Generate new summary button
    if not st.session_state.ai_generated_summary or st.session_state.summary_generation_count == 0:
        if st.button("✨ Generate Professional Summary", key="generate_summary"):
            generate_professional_summary(job_description)
            data_changed = True
    
    # Show generation tips
    if not st.session_state.ai_generated_summary:
        st.info("💡 **Tip:** Add a job posting above and your personal details in the Details tab to get a tailored professional summary!")
    
    return data_changed

def render_latex_editor_section() -> bool:
    """Render the LaTeX editor with enhanced features"""
    latex_changed = False
    
    # Template selection
    template_style = st.selectbox(
        "Choose Template Style",
        ["arpan", "simple"],
        index=0 if st.session_state.get('template_style', 'arpan') == "arpan" else 1,
        key="template_selector"
    )
    
    if template_style != st.session_state.get('template_style', 'arpan'):
        st.session_state.template_style = template_style
        latex_changed = True
    
    # Editor options
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        auto_update = st.checkbox("Auto-update PDF", value=True, key="auto_update_pdf")
    
    with col2:
        show_line_numbers = st.checkbox("Show line numbers", value=True, key="show_line_numbers")
    
    with col3:
        editor_theme = st.selectbox(
            "Editor theme",
            ["github", "monokai", "tomorrow", "twilight"],
            key="editor_theme"
        )
    
    # Initialize LaTeX code if empty
    if not st.session_state.get('latex_code'):
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        st.session_state.latex_code = pdf_generator.get_latex_template(
            template_style=st.session_state.get('template_style', 'arpan'),
            active_sections=st.session_state.get('active_sections', [])
        )
        latex_changed = True
    
    # LaTeX editor
    new_latex_code = st_ace(
        value=st.session_state.get('latex_code', ''),
        language='latex',
        theme=editor_theme,
        key="latex_editor",
        height=400,
        auto_update=True,
        wrap=True,
        show_gutter=show_line_numbers,
        show_print_margin=True
    )
    
    # Check if LaTeX code changed
    if new_latex_code != st.session_state.get('latex_code', ''):
        st.session_state.latex_code = new_latex_code
        latex_changed = True
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Compile PDF", key="manual_compile"):
            compile_latex_to_pdf()
            latex_changed = True
    
    with col2:
        if st.button("💾 Save LaTeX", key="save_latex"):
            save_latex_code()
    
    with col3:
        if st.button("🔄 Reset Template", key="reset_latex"):
            reset_to_default_template()
            latex_changed = True
            st.rerun()
    
    return latex_changed

# AI Integration Functions
def reframe_project_description(project: Dict[str, Any], index: int):
    """Reframe project description using AI"""
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is reframing your project description..."):
            reframed = groq_client.reframe_content(
                project.get('description', ''),
                'project',
                'make it more impactful and highlight technical achievements'
            )
            
            if reframed and reframed != project.get('description', ''):
                st.session_state[f'reframed_project_{index}'] = reframed
                
                # Show the reframed version
                st.success("✨ AI Reframed Description:")
                st.write(reframed)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Use This Version", key=f"accept_reframe_{index}"):
                        # Update the project in database
                        update_project_description(project['id'], reframed)
                        st.success("Project updated!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Keep Original", key=f"reject_reframe_{index}"):
                        if f'reframed_project_{index}' in st.session_state:
                            del st.session_state[f'reframed_project_{index}']
                        st.rerun()
            else:
                st.warning("AI couldn't improve the description significantly.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def reframe_experience_description(experience: Dict[str, Any], index: int):
    """Reframe experience description using AI"""
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is reframing your experience description..."):
            reframed = groq_client.reframe_content(
                experience.get('description', ''),
                'professional experience',
                'emphasize achievements and quantifiable results'
            )
            
            if reframed and reframed != experience.get('description', ''):
                st.session_state[f'reframed_exp_{index}'] = reframed
                
                st.success("✨ AI Reframed Description:")
                st.write(reframed)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Use This Version", key=f"accept_exp_reframe_{index}"):
                        # Update experience in database
                        update_experience_description(experience['id'], reframed)
                        st.success("Experience updated!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Keep Original", key=f"reject_exp_reframe_{index}"):
                        if f'reframed_exp_{index}' in st.session_state:
                            del st.session_state[f'reframed_exp_{index}']
                        st.rerun()
            else:
                st.warning("AI couldn't improve the description significantly.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def generate_professional_summary(job_description: str):
    """Generate professional summary using AI"""
    if not st.session_state.current_user_id:
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is generating your professional summary..."):
            # Gather user data
            user_data = gather_user_data()
            
            summary = groq_client.generate_professional_summary(user_data, job_description)
            
            if summary:
                st.session_state.ai_generated_summary = summary
                st.session_state.summary_generation_count += 1
                st.success("✨ Professional summary generated!")
                st.rerun()
            else:
                st.error("Failed to generate professional summary.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def regenerate_professional_summary(job_description: str, user_feedback: str):
    """Regenerate professional summary with user feedback"""
    if not st.session_state.current_user_id:
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is improving your professional summary..."):
            user_data = gather_user_data()
            
            improved_summary = groq_client.generate_professional_summary_with_feedback(
                user_data,
                job_description,
                st.session_state.ai_generated_summary,
                user_feedback
            )
            
            if improved_summary:
                st.session_state.ai_generated_summary = improved_summary
                st.session_state.summary_generation_count += 1
                st.success("✨ Professional summary improved!")
                # Clear feedback
                if 'summary_feedback' in st.session_state:
                    st.session_state.summary_feedback = ""
                st.rerun()
            else:
                st.error("Failed to improve professional summary.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def optimize_resume_for_job(job_description: str):
    """Optimize entire resume for specific job posting"""
    if not st.session_state.current_user_id:
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is optimizing your resume for this job..."):
            # Analyze job posting
            job_analysis = groq_client.analyze_job_posting(job_description)
            
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
            st.info("Check the Professional Summary section and PDF preview for optimized content.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def analyze_job_posting(job_description: str):
    """Analyze and display job posting insights"""
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("📊 Analyzing job posting..."):
            analysis = groq_client.analyze_job_posting(job_description)
            
            if analysis:
                st.success("📊 Job Analysis Complete!")
                
                with st.expander("📋 Job Analysis Results", expanded=True):
                    if analysis.get('technical_skills'):
                        st.write("**🔧 Required Technical Skills:**")
                        for skill in analysis['technical_skills'][:5]:
                            st.write(f"• {skill}")
                    
                    if analysis.get('qualifications'):
                        st.write("**🎓 Preferred Qualifications:**")
                        for qual in analysis['qualifications'][:5]:
                            st.write(f"• {qual}")
                    
                    if analysis.get('keywords'):
                        st.write("**🔑 Important Keywords:**")
                        keywords_text = ", ".join(analysis['keywords'][:10])
                        st.write(keywords_text)
            else:
                st.warning("Could not analyze the job posting.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

# Helper Functions (Import from original sidebar.py)
def gather_user_data() -> Dict[str, Any]:
    """Gather all user data for AI processing"""
    if not st.session_state.current_user_id:
        return {}
    
    return {
        'user': load_current_user_data(),
        'projects': load_user_projects(),
        'professional_experience': load_user_professional_experience(),
        'technical_skills': load_user_technical_skills(),
        # Add other data as needed
    }

def regenerate_latex_with_optimization():
    """Regenerate LaTeX code with AI optimizations"""
    try:
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        
        user_data = gather_user_data()
        
        # Use optimized projects if available
        if 'optimized_projects' in st.session_state:
            user_data['projects'] = st.session_state.optimized_projects
        
        # Generate LaTeX with optimized data
        pdf_path, latex_code = pdf_generator.generate_pdf_from_data(
            user_data,
            st.session_state.get('template_style', 'arpan'),
            st.session_state.get('active_sections', [])
        )
        
        if latex_code:
            st.session_state.latex_code = latex_code
            if pdf_path:
                st.session_state.pdf_path = pdf_path
                
    except Exception as e:
        st.error(f"Error regenerating LaTeX: {e}")

# Import helper functions from original sidebar
from components.sidebar import (
    render_user_section, render_add_project_form, render_add_professional_experience_form,
    render_research_experience_section, render_education_section, render_skills_section,
    render_certifications_section, load_user_projects, load_user_professional_experience,
    load_current_user_data, delete_project
)

# Import LaTeX functions from latex_editor
from components.latex_editor import compile_latex_to_pdf, save_latex_code, reset_to_default_template

# Additional helper functions for database updates
def update_project_description(project_id: int, new_description: str) -> bool:
    """Update project description in database"""
    try:
        session = next(get_db_session())
        ProjectQueries.update_project(session, project_id, {'description': new_description})
        return True
    except Exception as e:
        st.error(f"Error updating project: {e}")
        return False

def update_experience_description(experience_id: int, new_description: str) -> bool:
    """Update experience description in database"""
    try:
        session = next(get_db_session())
        ExperienceQueries.update_professional_experience(session, experience_id, {'description': new_description})
        return True
    except Exception as e:
        st.error(f"Error updating experience: {e}")
        return False

def load_user_technical_skills() -> list:
    """Load user technical skills"""
    if not st.session_state.current_user_id:
        return []
    
    try:
        session = next(get_db_session())
        skills = SkillsQueries.get_user_skills(session, st.session_state.current_user_id)
        return [
            {
                'id': s.id,
                'category': s.category,
                'skills': s.skills
            } for s in skills
        ]
    except Exception as e:
        st.error(f"Error loading skills: {e}")
        return []