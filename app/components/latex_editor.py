import streamlit as st
from streamlit_ace import st_ace
from typing import Optional
from utils.pdf_generator import PDFGenerator
from utils.validators import DataValidator
from ai_integration.groq_client import GroqClient

def render_latex_editor() -> bool:
    """
    Render LaTeX editor with syntax highlighting
    Returns: True if LaTeX code was changed, False otherwise
    """
    latex_changed = False
    
    # Template selection
    template_style = st.selectbox(
        "Choose Template Style",
        ["arpan", "simple"],
        index=0 if st.session_state.template_style == "arpan" else 1,
        key="template_selector"
    )
    
    if template_style != st.session_state.template_style:
        st.session_state.template_style = template_style
        latex_changed = True
    
    # Section management
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔧 Section Configuration")
    
    with col2:
        if st.button("Reset to Default", key="reset_latex"):
            reset_to_default_template()
            latex_changed = True
            st.rerun()
    
    # Section ordering and visibility
    latex_changed |= render_section_manager()
    
    # AI Professional Summary Section
    st.subheader("✨ AI Professional Summary")
    latex_changed |= render_professional_summary_section()
    
    st.markdown("---")
    
    # LaTeX code editor
    st.subheader("📝 LaTeX Code Editor")
    
    # Initialize LaTeX code if empty
    if not st.session_state.latex_code:
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        st.session_state.latex_code = pdf_generator.get_latex_template(
            template_style=st.session_state.template_style,
            active_sections=st.session_state.active_sections
        )
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
    
    # LaTeX editor
    new_latex_code = st_ace(
        value=st.session_state.latex_code,
        language='latex',
        theme=editor_theme,
        key="latex_editor",
        height=400,
        auto_update=True,
        wrap=True,
        show_gutter=show_line_numbers,
        show_print_margin=True,
        annotations=validate_latex_code(st.session_state.latex_code)
    )
    
    # Check if LaTeX code changed
    if new_latex_code != st.session_state.latex_code:
        st.session_state.latex_code = new_latex_code
        latex_changed = True
    
    # Manual compile button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Compile PDF", key="manual_compile"):
            compile_latex_to_pdf()
            latex_changed = True
    
    with col2:
        if st.button("💾 Save LaTeX", key="save_latex"):
            save_latex_code()
    
    with col3:
        if st.button("📥 Download LaTeX", key="download_latex"):
            download_latex_code()
    
    # LaTeX validation messages
    render_latex_validation()
    
    return latex_changed

def render_section_manager() -> bool:
    """Render section ordering and visibility manager"""
    section_changed = False
    
    with st.expander("Section Management", expanded=False):
        # Available sections
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        template = pdf_generator.get_sample_data()  # This will be replaced with actual template
        available_sections = {
            "professional_summary": "Professional Summary",
            "projects": "Projects",
            "professional_experience": "Professional Experience",
            "research_experience": "Research Experience",
            "education": "Education",
            "technical_skills": "Technical Skills",
            "certifications": "Certifications"
        }
        
        st.write("**Select Active Sections:**")
        
        # Create checkboxes for each section
        new_active_sections = []
        for section_key, section_name in available_sections.items():
            if st.checkbox(
                section_name, 
                value=section_key in st.session_state.active_sections,
                key=f"section_{section_key}"
            ):
                new_active_sections.append(section_key)
        
        if new_active_sections != st.session_state.active_sections:
            st.session_state.active_sections = new_active_sections
            section_changed = True
        
        # Section ordering
        st.write("**Section Order:**")
        if st.session_state.active_sections:
            st.info("Drag and drop functionality will be added in future updates. Current order:")
            for i, section in enumerate(st.session_state.active_sections):
                st.write(f"{i+1}. {available_sections.get(section, section)}")
    
    return section_changed

def validate_latex_code(latex_code: str) -> list:
    """Validate LaTeX code and return annotations for editor"""
    annotations = []
    
    if not latex_code:
        return annotations
    
    is_valid, errors = DataValidator.validate_latex_syntax(latex_code)
    
    if not is_valid:
        for error in errors:
            annotations.append({
                "row": 0,
                "column": 0,
                "type": "error",
                "text": error
            })
    
    return annotations

def render_latex_validation():
    """Render LaTeX validation messages"""
    if st.session_state.latex_code:
        is_valid, errors = DataValidator.validate_latex_syntax(st.session_state.latex_code)
        
        if not is_valid:
            st.error("⚠️ LaTeX Validation Issues:")
            for error in errors:
                st.write(f"• {error}")
        else:
            st.success("✅ LaTeX syntax looks good!")

def compile_latex_to_pdf():
    """Manually compile LaTeX to PDF"""
    if not st.session_state.latex_code:
        st.error("No LaTeX code to compile")
        return
    
    with st.spinner("Compiling LaTeX to PDF..."):
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        pdf_path = pdf_generator.generate_pdf_from_latex(st.session_state.latex_code)
        
        if pdf_path:
            st.session_state.pdf_path = pdf_path
            st.success("✅ PDF compiled successfully!")
        else:
            st.error("❌ PDF compilation failed")

def save_latex_code():
    """Save LaTeX code to session state"""
    if st.session_state.latex_code:
        st.success("LaTeX code saved to session!")
    else:
        st.warning("No LaTeX code to save")

def download_latex_code():
    """Provide download button for LaTeX code"""
    if st.session_state.latex_code:
        st.download_button(
            label="📥 Download LaTeX File",
            data=st.session_state.latex_code,
            file_name="resume.tex",
            mime="text/plain",
            key="download_latex_button"
        )
    else:
        st.warning("No LaTeX code to download")

def reset_to_default_template():
    """Reset LaTeX code to default template"""
    session_id = st.session_state.get('session_id', 'default')
    pdf_generator = PDFGenerator(session_id=session_id)
    st.session_state.latex_code = pdf_generator.get_latex_template(
        template_style=st.session_state.template_style,
        active_sections=st.session_state.active_sections
    )
    st.success("Reset to default template!")

def update_latex_from_data():
    """Update LaTeX code based on current user data"""
    if not st.session_state.current_user_id:
        return
    
    # This function will be called when user data changes
    # to regenerate LaTeX code from database
    try:
        from components.sidebar import (
            load_current_user_data, 
            load_user_projects,
            load_user_professional_experience
        )
        
        # Gather all user data
        user_data = {
            'user': load_current_user_data(),
            'projects': load_user_projects(),
            'professional_experience': load_user_professional_experience(),
            # Add other data sources as needed
        }
        
        # Generate new LaTeX
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        new_latex = pdf_generator.generate_pdf_from_data(
            user_data,
            st.session_state.template_style,
            st.session_state.active_sections
        )
        
        if new_latex[1]:  # If LaTeX was generated successfully
            st.session_state.latex_code = new_latex[1]
        
    except Exception as e:
        st.error(f"Error updating LaTeX from data: {e}")

def render_professional_summary_section() -> bool:
    """Render professional summary generation and refinement section"""
    summary_changed = False
    
    # Show current summary if exists
    if st.session_state.get('ai_generated_summary'):
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
                regenerate_professional_summary(user_feedback)
                summary_changed = True
    
    # Generate new summary button
    if not st.session_state.get('ai_generated_summary'):
        if st.button("✨ Generate Professional Summary", key="generate_summary"):
            generate_professional_summary()
            summary_changed = True
    
    # Show generation tips
    if not st.session_state.get('ai_generated_summary'):
        st.info("💡 **Tip:** Add a job posting in the sidebar and your personal details in the Details tab to get a tailored professional summary!")
    
    return summary_changed

def generate_professional_summary():
    """Generate professional summary using AI"""
    if not st.session_state.get('current_user_id'):
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is generating your professional summary..."):
            # Gather user data
            user_data = gather_user_data()
            job_description = st.session_state.get('job_posting_input', '')
            
            summary = groq_client.generate_professional_summary(user_data, job_description)
            
            if summary:
                st.session_state.ai_generated_summary = summary
                st.session_state.summary_generation_count = st.session_state.get('summary_generation_count', 0) + 1
                st.success("✨ Professional summary generated!")
                st.rerun()
            else:
                st.error("Failed to generate professional summary.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def regenerate_professional_summary(user_feedback: str):
    """Regenerate professional summary with user feedback"""
    if not st.session_state.get('current_user_id'):
        st.error("Please select a user first!")
        return
    
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("🤖 AI is improving your professional summary..."):
            user_data = gather_user_data()
            job_description = st.session_state.get('job_posting_input', '')
            
            improved_summary = groq_client.generate_professional_summary_with_feedback(
                user_data,
                job_description,
                st.session_state.ai_generated_summary,
                user_feedback
            )
            
            if improved_summary:
                st.session_state.ai_generated_summary = improved_summary
                st.session_state.summary_generation_count = st.session_state.get('summary_generation_count', 0) + 1
                st.success("✨ Professional summary improved!")
                # Clear feedback
                if 'summary_feedback' in st.session_state:
                    st.session_state.summary_feedback = ""
                st.rerun()
            else:
                st.error("Failed to improve professional summary.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def gather_user_data():
    """Gather all user data for AI processing"""
    from components.sidebar import load_current_user_data, load_user_projects, load_user_professional_experience
    
    if not st.session_state.get('current_user_id'):
        return {}
    
    return {
        'user': load_current_user_data(),
        'projects': load_user_projects(),
        'professional_experience': load_user_professional_experience(),
        # Add other data as needed
    }

def get_latex_preview() -> str:
    """Get a short preview of the LaTeX code"""
    if not st.session_state.latex_code:
        return "No LaTeX code generated yet"
    
    lines = st.session_state.latex_code.split('\n')
    preview_lines = lines[:10]  # First 10 lines
    
    preview = '\n'.join(preview_lines)
    if len(lines) > 10:
        preview += f"\n... ({len(lines) - 10} more lines)"
    
    return preview