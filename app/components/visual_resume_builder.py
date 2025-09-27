from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from .interactive_section_manager import InteractiveSectionManager
from ai_integration.content_optimizer import ContentOptimizer
from database.queries import UserQueries
from database.connection import get_db_session
from latex_templates.base_template import BaseTemplate
from utils.pdf_generator import PDFGenerator

class VisualResumeBuilder:
    """Main visual interface for building resumes with drag-drop and AI optimization"""

    def __init__(self):
        self.section_manager = InteractiveSectionManager()
        # ContentOptimizer will be initialized when needed with user API key
        self.content_optimizer = None
        self.session_id = st.session_state.get('session_id', 'default')

    def render_visual_builder(self, user_id: Optional[int] = None) -> bool:
        """
        Render the complete visual resume builder interface
        Returns: True if layout changed and PDF needs regeneration
        """
        if not user_id:
            st.warning("Please select a user to start building your resume.")
            return False

        st.markdown("# Visual Resume Builder")
        st.markdown("---")

        # Create single tab for integrated experience
        tab1 = st.tabs(["Resume Builder"])[0]

        layout_changed = False

        try:
            with tab1:
                # Render AI Optimizer first (job posting and optimization)
                self._render_ai_optimizer(user_id)

                st.markdown("---")

                # Then render Layout Designer
                layout_changed = self._render_layout_designer(user_id)

                # Generate PDF section at the bottom
                st.markdown("---")

                # Informational message
                enforce_one_page_limit = st.session_state.get('enforce_one_page_limit', True)
                ai_optimized = st.session_state.get('ai_optimized_data')

                if not ai_optimized:
                    if not enforce_one_page_limit:
                        st.info("**Multi-page mode:** Resume will include ALL your data from the database for a comprehensive document.")
                    else:
                        st.info("**Tip:** Run AI optimization above to get a tailored resume with selected projects and optimized content!")
                else:
                    st.success("Your resume will include optimized content and selected projects.")

                # Generate PDF button
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    if st.button("Generate Resume PDF", key="generate_visual_pdf", use_container_width=True):
                        with st.spinner("Generating your personalized resume..."):
                            pdf_path = self.generate_optimized_pdf(user_id)

                            if pdf_path:
                                st.success("Resume generated successfully!")
                                st.session_state.pdf_path = pdf_path
                            else:
                                st.error("❌ Failed to generate PDF. Please check your content and try again.")

                # Show PDF preview full width (outside column layout)
                if st.session_state.get('pdf_path'):
                    st.markdown("---")
                    self._render_pdf_preview()

        except Exception as e:
            st.error(f"Error in Visual Builder: {e}")
            st.error(f"Error type: {type(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

        return layout_changed

    def _render_layout_designer(self, user_id: int) -> bool:
        """Render the layout designer with drag-drop functionality"""
        layout_changed = False

        # Section organization interface - full width
        # Main drag-drop interface
        old_sidebar = st.session_state.get('sidebar_sections', []).copy()
        old_main = st.session_state.get('main_sections', []).copy()

        sidebar_sections, main_sections = self.section_manager.render_section_organizer(user_id)

        # Check if layout changed
        if (sidebar_sections != old_sidebar or main_sections != old_main):
            layout_changed = True

        st.markdown("---")

        # Section toggles
        active_sections = self.section_manager.render_section_toggles(user_id)

        # Template style selector
        self._render_template_selector()

        return layout_changed

    def _render_ai_optimizer(self, user_id: int):
        """Render AI optimization interface"""
        st.header("🤖 AI Content Optimizer")
        st.write("Let AI help you select and optimize content for specific job applications.")

        # Job posting input
        job_description = st.text_area(
            "📄 Job Description",
            placeholder="Paste the job description here for AI optimization...",
            height=150,
            key="ai_job_description"
        )

        if job_description and st.button("Optimize Content for Job", key="optimize_content"):
            self._run_ai_optimization(user_id, job_description)

        # Display current AI recommendations if available
        self._display_ai_recommendations(user_id)


    def _render_template_selector(self):
        """Render template style selector"""
        st.subheader("Template Settings")

        # Full width template settings
        col1, col2 = st.columns(2)

        with col1:
            template_style = st.selectbox(
                "Choose template style:",
                options=["arpan", "simple"],
                index=0 if st.session_state.get('template_style', 'arpan') == 'arpan' else 1,
                help="Arpan: Modern two-column layout | Simple: Clean single-column layout"
            )

            if template_style != st.session_state.get('template_style'):
                st.session_state.template_style = template_style
                st.rerun()

        with col2:
            # Font size selector
            font_size = st.selectbox(
                "Font size:",
                options=["9pt", "10pt", "11pt", "12pt"],
                index=1,  # Default to 10pt
                key="font_size_selector",
                help="Choose the font size for the resume text"
            )

            if font_size != st.session_state.get('font_size', '10pt'):
                st.session_state.font_size = font_size

    def _run_ai_optimization(self, user_id: int, job_description: str):
        """Run AI optimization and update session state"""
        try:
            session = next(get_db_session())
            user_data = UserQueries.get_user_with_all_data(session, user_id)

            if not user_data:
                st.error("Could not load user data for optimization.")
                return

            with st.spinner("AI is analyzing and optimizing your content..."):
                # Initialize content optimizer with user API key
                from components.sidebar import get_api_key_from_session
                user_api_key = get_api_key_from_session()
                self.content_optimizer = ContentOptimizer(api_key=user_api_key)
                
                # Run optimization
                optimized_data = self.content_optimizer.optimize_resume_for_job(
                    user_data, job_description, user_id
                )

                # Debug: Check what we got back
                if not isinstance(optimized_data, dict):
                    st.error(f"Error: AI optimization returned {type(optimized_data)} instead of dict")
                    return

                # Store optimization results in session state
                st.session_state.ai_optimized_data = optimized_data
                st.session_state.ai_job_description_stored = job_description
                st.session_state.ai_optimization_timestamp = st.session_state.get('summary_generation_count', 0) + 1

                # Apply AI section filtering automatically
                metadata = optimized_data.get('_optimization_metadata', {})
                section_relevance = metadata.get('section_relevance', {})
                if section_relevance:
                    # Update active sections based on AI analysis
                    st.session_state.ai_filtered_sections = section_relevance
                    
                    # Also update active_sections to reflect AI recommendations
                    if 'active_sections' not in st.session_state:
                        st.session_state.active_sections = {}
                    
                    # Update active sections based on AI relevance
                    for section, is_relevant in section_relevance.items():
                        if not is_relevant:
                            # AI says this section is not relevant, uncheck it
                            st.session_state.active_sections[section] = False
                        # If AI says it's relevant, keep current user preference or default to True

                st.success("AI optimization completed!")

        except Exception as e:
            st.error(f"Error during AI optimization: {e}")

    def _display_ai_recommendations(self, user_id: int):
        """Display AI recommendations and allow user to apply them"""
        if 'ai_optimized_data' not in st.session_state:
            st.info("Run AI optimization to see personalized recommendations.")
            return

        st.subheader("AI Recommendations")

        # Show optimization summary
        optimized_data = st.session_state.ai_optimized_data

        # Debug: Check if optimized_data is the right type
        if not isinstance(optimized_data, dict):
            st.error(f"Error: Expected dictionary, got {type(optimized_data)}. Please try running optimization again.")
            return

        job_desc = st.session_state.get('ai_job_description_stored', '')

        if job_desc:
            st.write(f"**Optimized for:** {job_desc[:100]}..." if len(job_desc) > 100 else job_desc)

        # Section relevance analysis
        metadata = optimized_data.get('_optimization_metadata', {})
        section_relevance = metadata.get('section_relevance', {})

        if section_relevance:
            excluded_sections = [section.replace('_', ' ').title() for section, relevant in section_relevance.items() if not relevant]
            included_sections = [section.replace('_', ' ').title() for section, relevant in section_relevance.items() if relevant]

            if excluded_sections:
                with st.expander("Excluded Sections", expanded=False):
                    st.write("**The following sections were excluded as not relevant for this job:**")
                    for section in excluded_sections:
                        st.write(f"• {section}")
                    st.info("These sections won't appear in the optimized resume to keep it focused and relevant.")

            if included_sections:
                with st.expander("Included Sections", expanded=False):
                    st.write("**The following sections are relevant for this job:**")
                    for section in included_sections:
                        st.write(f"• {section}")

        # Project recommendations
        projects = optimized_data.get('projects', [])
        if projects and isinstance(projects, list):
            with st.expander("Selected Projects", expanded=False):
                for i, project in enumerate(projects, 1):
                    if isinstance(project, dict):
                        st.write(f"**{i}. {project.get('title', 'Untitled Project')}**")
                        st.write(f"_{project.get('technologies', 'No technologies listed')}_")
                        if project.get('description'):
                            st.write(project['description'][:150] + "..." if len(project['description']) > 150 else project['description'])
                        st.markdown("---")

        # Professional summary
        summaries = optimized_data.get('professional_summaries', [])
        if summaries and isinstance(summaries, list) and len(summaries) > 0:
            with st.expander("Generated Summary", expanded=False):
                summary_item = summaries[0]
                if isinstance(summary_item, dict):
                    summary = summary_item.get('generated_summary', 'No summary available')
                    st.write(summary)

        # Show impact summary
        if section_relevance:
            total_sections = len(section_relevance)
            excluded_count = len([r for r in section_relevance.values() if not r])
            included_count = total_sections - excluded_count

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sections", total_sections)
            with col2:
                st.metric("Included", included_count, delta=f"{included_count}/{total_sections}")
            with col3:
                st.metric("Excluded", excluded_count, delta=f"-{excluded_count}" if excluded_count > 0 else "0")

        # Regenerate button
        if st.button("Generate New Optimization", key="regenerate_optimization"):
            if st.session_state.get('ai_job_description_stored'):
                self._run_ai_optimization(user_id, st.session_state.ai_job_description_stored)



    def generate_optimized_pdf(self, user_id: int) -> Optional[str]:
        """Generate PDF with current visual configuration"""
        try:
            session = next(get_db_session())
            user_data = UserQueries.get_user_with_all_data(session, user_id)

            if not user_data:
                st.error("Could not load user data for PDF generation.")
                return None

            # Use AI-optimized data if available, otherwise use original database data
            ai_optimized_data = st.session_state.get('ai_optimized_data')
            if ai_optimized_data and isinstance(ai_optimized_data, dict):

                # Merge AI optimized content with original data
                user_data = self._merge_ai_optimized_data(user_data, ai_optimized_data)
            else:
                pass  # Use original data without notification

            # Get current section organization
            sidebar_sections, main_sections, active_sections = self.section_manager.get_organized_sections()

            # Check if one-page limit is enforced and if AI optimization was used
            enforce_one_page_limit = st.session_state.get('enforce_one_page_limit', True)
            ai_was_used = ai_optimized_data and isinstance(ai_optimized_data, dict)

            # User manual selections always take priority over AI suggestions
            # AI filtering is only for initial suggestions - user can override manually

            if not enforce_one_page_limit and not ai_was_used:
                # Multi-page mode without AI: Include ALL sections from database
                all_available_sections = [
                    "professional_summary",
                    "projects",
                    "professional_experience",
                    "research_experience",
                    "academic_collaborations",
                    "education",
                    "technical_skills",
                    "certifications"
                ]
                # Use the default section order from the template for consistency
                from latex_templates.base_template import BaseTemplate
                template = BaseTemplate()
                all_active_sections = template.get_default_section_order()
            else:
                # Single-page mode OR AI was used: Respect user's manual selections
                active_sidebar = [s for s in sidebar_sections if active_sections.get(s, False)]
                active_main = [s for s in main_sections if active_sections.get(s, False)]
                all_active_sections = active_sidebar + active_main

            # Generate PDF
            pdf_generator = PDFGenerator(self.session_id)
            template_style = st.session_state.get('template_style', 'arpan')
            font_size = st.session_state.get('font_size', '10pt')

            pdf_path, latex_code = pdf_generator.generate_pdf_from_data(
                user_data,
                template_style=template_style,
                active_sections=all_active_sections,
                section_order=all_active_sections,
                font_size=font_size
            )

            if pdf_path:
                # Update session state with generated LaTeX
                st.session_state.latex_code = latex_code
                st.session_state.pdf_path = pdf_path

            return pdf_path

        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            return None

    def _merge_ai_optimized_data(self, original_data: Dict[str, Any], ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge AI-optimized data with original data
        AI data takes precedence for optimized sections
        """
        merged_data = original_data.copy()

        # List of sections that AI can optimize automatically
        # NOTE: professional_experience is excluded - only optimize if user modified it in details
        ai_optimizable_sections = [
            'projects', 'professional_summaries'
        ]

        for section in ai_optimizable_sections:
            if section in ai_data and ai_data[section]:
                # Use AI-optimized content for this section
                merged_data[section] = ai_data[section]

        return merged_data

    def _render_pdf_preview(self):
        """Render PDF preview if available"""
        try:
            from components.pdf_preview import render_pdf_preview
            render_pdf_preview(force_update=True)
        except ImportError:
            st.info("PDF preview will be shown in the LaTeX Editor tab.")