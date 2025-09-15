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

    
    # AI Professional Summary Section
    st.subheader("AI Professional Summary")
    latex_changed |= render_professional_summary_section()

    # Auto-sync AI data changes
    latex_changed |= check_and_sync_ai_data()

    st.markdown("---")
    
    # LaTeX code editor
    st.subheader("LaTeX Code Editor")
    
    # Initialize LaTeX code if empty
    if not st.session_state.latex_code:
        # Try to use real user data with AI optimization first
        if st.session_state.get('current_user_id'):
            try:
                update_latex_from_data()
                latex_changed = True
            except Exception:
                # Fall back to template if real data fails
                session_id = st.session_state.get('session_id', 'default')
                pdf_generator = PDFGenerator(session_id=session_id)
                st.session_state.latex_code = pdf_generator.get_latex_template(
                    template_style=st.session_state.template_style,
                    active_sections=st.session_state.active_sections
                )
                latex_changed = True
        else:
            # No user selected, use template
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
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Compile PDF", key="manual_compile"):
            compile_latex_to_pdf()
            latex_changed = True

    with col2:
        if st.button("Manual Sync", key="sync_ai_data", help="Manually refresh LaTeX with current data (auto-sync is active)"):
            update_latex_from_data()
            latex_changed = True
            # Update sync timestamp to prevent immediate auto-sync message
            current_optimization_timestamp = st.session_state.get('ai_optimization_timestamp', 0)
            st.session_state.latex_ai_sync_timestamp = current_optimization_timestamp
            st.success("Manually synced with current data!")

    with col3:
        if st.button("Save LaTeX", key="save_latex"):
            save_latex_code()

    with col4:
        if st.button("Download LaTeX", key="download_latex"):
            download_latex_code()
    
    # LaTeX validation messages
    render_latex_validation()
    
    return latex_changed


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
            st.error("LaTeX Validation Issues:")
            for error in errors:
                st.write(f"• {error}")

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


def update_latex_from_data():
    """Update LaTeX code based on current user data with AI optimization"""
    if not st.session_state.current_user_id:
        return

    try:
        from database.queries import UserQueries
        from database.connection import get_db_session

        # Get complete user data from database
        session = next(get_db_session())
        user_data = UserQueries.get_user_with_all_data(session, st.session_state.current_user_id)

        if not user_data:
            st.error("Could not load user data")
            return

        # Apply AI optimization if available (same logic as visual builder)
        ai_optimized_data = st.session_state.get('ai_optimized_data')
        if ai_optimized_data and isinstance(ai_optimized_data, dict):
            # Merge AI optimized content with original data
            user_data = _merge_ai_optimized_data_latex(user_data, ai_optimized_data)

        # Get section organization
        sidebar_sections = st.session_state.get('sidebar_sections', ["education", "technical_skills", "certifications"])
        main_sections = st.session_state.get('main_sections', ["professional_summary", "projects", "professional_experience", "research_experience"])
        active_sections = st.session_state.get('active_sections', {})

        # User manual selections always take priority over AI suggestions
        # AI filtering is only for initial suggestions - user can override manually
        # No need to filter based on AI if user has made manual selections

        # Filter to only active sections
        active_sidebar = [s for s in sidebar_sections if active_sections.get(s, False)]
        active_main = [s for s in main_sections if active_sections.get(s, False)]
        all_active_sections = active_sidebar + active_main

        # Generate new LaTeX
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        font_size = st.session_state.get('font_size', '10pt')

        pdf_path, new_latex = pdf_generator.generate_pdf_from_data(
            user_data,
            template_style=st.session_state.template_style,
            active_sections=all_active_sections,
            section_order=all_active_sections,
            font_size=font_size
        )

        if new_latex:
            st.session_state.latex_code = new_latex

    except Exception as e:
        st.error(f"Error updating LaTeX from data: {e}")

def _merge_ai_optimized_data_latex(original_data: dict, ai_data: dict) -> dict:
    """Merge AI-optimized data with original data (same logic as visual builder)"""
    merged_data = original_data.copy()

    # List of sections that AI can optimize automatically
    ai_optimizable_sections = [
        'projects', 'professional_summaries'
    ]

    for section in ai_optimizable_sections:
        if section in ai_data and ai_data[section]:
            # Use AI-optimized content for this section
            merged_data[section] = ai_data[section]

    return merged_data

def check_and_sync_ai_data() -> bool:
    """Check if AI-optimized data has changed and auto-sync LaTeX if needed"""
    if not st.session_state.get('current_user_id'):
        return False

    # Get current AI optimization timestamp
    current_optimization_timestamp = st.session_state.get('ai_optimization_timestamp', 0)

    # Get last known timestamp when LaTeX was synced
    last_synced_timestamp = st.session_state.get('latex_ai_sync_timestamp', 0)

    # Check if AI data has been updated since last sync
    if current_optimization_timestamp > last_synced_timestamp:
        try:
            # Auto-sync the LaTeX with new AI data
            update_latex_from_data()

            # Update the sync timestamp
            st.session_state.latex_ai_sync_timestamp = current_optimization_timestamp

            # Show a subtle success message
            st.success("LaTeX automatically updated with latest AI optimization")

            return True
        except Exception as e:
            st.warning(f"Auto-sync failed: {e}")
            return False

    return False

def render_professional_summary_section() -> bool:
    """Render professional summary generation and refinement section"""
    summary_changed = False

    # Get the most current AI summary - prioritize Visual Builder's AI optimization
    current_summary = None

    # First check Visual Builder's AI-optimized data (most recent)
    ai_optimized_data = st.session_state.get('ai_optimized_data', {})
    if ai_optimized_data and isinstance(ai_optimized_data, dict):
        summaries = ai_optimized_data.get('professional_summaries', [])
        if summaries and len(summaries) > 0:
            current_summary = summaries[0].get('generated_summary')

    # Fallback to LaTeX editor's own summary
    if not current_summary:
        current_summary = st.session_state.get('ai_generated_summary')

    # Show current summary if exists
    if current_summary:
        st.write("**Current AI-Generated Summary:**")
        st.info(current_summary)
        
        # Feedback and regeneration
        col1, col2 = st.columns([2, 1])
        with col1:
            user_feedback = st.text_input(
                "Feedback for improvement:",
                key="summary_feedback",
                placeholder="e.g., Make it more technical, focus on leadership, add specific skills..."
            )
        
        with col2:
            if st.button("Regenerate Summary", key="regenerate_summary"):
                regenerate_professional_summary(user_feedback)
                summary_changed = True
    
    # Generate new summary button
    if not current_summary:
        if st.button("Generate Professional Summary", key="generate_summary"):
            generate_professional_summary()
            summary_changed = True
    
    # Show generation tips
    if not current_summary:
        st.info("💡 **Tip:** Add a job posting in the sidebar and your personal details in the Details tab to get a tailored professional summary!")
    
    return summary_changed

def generate_professional_summary():
    """Generate professional summary using AI"""
    if not st.session_state.get('current_user_id'):
        st.error("Please select a user first!")
        return
    
    from components.sidebar import get_api_key_from_session
    user_api_key = get_api_key_from_session()
    groq_client = GroqClient(user_api_key=user_api_key)
    if groq_client.is_available():
        with st.spinner("AI is generating your professional summary..."):
            # Gather user data
            user_data = gather_user_data()
            job_description = st.session_state.get('job_posting_input', '')
            
            summary = groq_client.generate_professional_summary(user_data, job_description)
            
            if summary:
                # Update both storage locations for consistency
                st.session_state.ai_generated_summary = summary

                # Also update Visual Builder's AI-optimized data if it exists
                ai_optimized_data = st.session_state.get('ai_optimized_data', {})
                if ai_optimized_data and isinstance(ai_optimized_data, dict):
                    # Update the professional summaries in AI-optimized data
                    ai_optimized_data['professional_summaries'] = [
                        {'generated_summary': summary, 'job_description': job_description}
                    ]
                    st.session_state.ai_optimized_data = ai_optimized_data

                st.session_state.summary_generation_count = st.session_state.get('summary_generation_count', 0) + 1

                # Update AI optimization timestamp to trigger auto-sync
                st.session_state.ai_optimization_timestamp = st.session_state.get('summary_generation_count', 0)

                st.success("Professional summary generated!")
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
    
    from components.sidebar import get_api_key_from_session
    user_api_key = get_api_key_from_session()
    groq_client = GroqClient(user_api_key=user_api_key)
    if groq_client.is_available():
        with st.spinner("AI is improving your professional summary..."):
            user_data = gather_user_data()
            job_description = st.session_state.get('job_posting_input', '')
            
            improved_summary = groq_client.generate_professional_summary_with_feedback(
                user_data,
                job_description,
                st.session_state.ai_generated_summary,
                user_feedback
            )
            
            if improved_summary:
                # Update both storage locations for consistency
                st.session_state.ai_generated_summary = improved_summary

                # Also update Visual Builder's AI-optimized data if it exists
                ai_optimized_data = st.session_state.get('ai_optimized_data', {})
                if ai_optimized_data and isinstance(ai_optimized_data, dict):
                    # Update the professional summaries in AI-optimized data
                    ai_optimized_data['professional_summaries'] = [
                        {'generated_summary': improved_summary, 'job_description': job_description}
                    ]
                    st.session_state.ai_optimized_data = ai_optimized_data

                st.session_state.summary_generation_count = st.session_state.get('summary_generation_count', 0) + 1

                # Update AI optimization timestamp to trigger auto-sync
                st.session_state.ai_optimization_timestamp = st.session_state.get('summary_generation_count', 0)

                st.success("Professional summary improved!")
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