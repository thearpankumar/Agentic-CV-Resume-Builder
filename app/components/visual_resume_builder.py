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
        self.content_optimizer = ContentOptimizer()
        self.session_id = st.session_state.get('session_id', 'default')

    def render_visual_builder(self, user_id: Optional[int] = None) -> bool:
        """
        Render the complete visual resume builder interface
        Returns: True if layout changed and PDF needs regeneration
        """
        if not user_id:
            st.warning("⚠️ Please select a user to start building your resume.")
            return False

        st.markdown("# 🎨 Visual Resume Builder")
        st.markdown("---")

        # Create tabs for different aspects of resume building
        tab1, tab2, tab3 = st.tabs(["📋 Layout Designer", "🤖 AI Optimizer", "🎯 Content Manager"])

        layout_changed = False

        try:
            with tab1:
                layout_changed = self._render_layout_designer(user_id)

            with tab2:
                self._render_ai_optimizer(user_id)

            with tab3:
                self._render_content_manager(user_id)

        except Exception as e:
            st.error(f"Error in Visual Builder: {e}")
            st.error(f"Error type: {type(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

        return layout_changed

    def _render_layout_designer(self, user_id: int) -> bool:
        """Render the layout designer with drag-drop functionality"""
        st.header("📋 Layout Designer")
        st.write("Design your resume layout by dragging sections between sidebar and main content areas.")

        layout_changed = False

        # Section organization interface
        col1, col2 = st.columns([2, 1])

        with col1:
            # Main drag-drop interface
            old_sidebar = st.session_state.get('sidebar_sections', []).copy()
            old_main = st.session_state.get('main_sections', []).copy()

            sidebar_sections, main_sections = self.section_manager.render_section_organizer(user_id)

            # Check if layout changed
            if (sidebar_sections != old_sidebar or main_sections != old_main):
                layout_changed = True

        with col2:
            # Layout preview and controls
            self.section_manager.render_layout_preview()

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

        if job_description and st.button("🚀 Optimize Content for Job", key="optimize_content"):
            self._run_ai_optimization(user_id, job_description)

        # Display current AI recommendations if available
        self._display_ai_recommendations(user_id)

    def _render_content_manager(self, user_id: int):
        """Render content management interface"""
        st.header("🎯 Content Manager")
        st.write("Review and manage the content that will appear in your resume.")

        try:
            session = next(get_db_session())
            user_data = UserQueries.get_user_with_all_data(session, user_id)

            if not user_data:
                st.error("Could not load user data.")
                return

            # Get current section organization
            sidebar_sections, main_sections, active_sections = self.section_manager.get_organized_sections()

            # Display content for each active section
            self._render_section_content_preview(user_data, sidebar_sections + main_sections, active_sections)

        except Exception as e:
            st.error(f"Error loading content: {e}")

    def _render_template_selector(self):
        """Render template style selector"""
        st.subheader("🎨 Template Settings")

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

        with col2:
            # Template preview info
            if template_style == "arpan":
                st.info("🏛️ **Arpan Style**: Professional two-column layout with sidebar for skills and main content for experience.")
            else:
                st.info("📄 **Simple Style**: Clean single-column layout suitable for traditional formats.")

            # Font size info
            font_size_current = st.session_state.get('font_size', '10pt')
            st.info(f"📝 **Font Size**: {font_size_current} - Headings are medium size (fixed)")

    def _run_ai_optimization(self, user_id: int, job_description: str):
        """Run AI optimization and update session state"""
        try:
            session = next(get_db_session())
            user_data = UserQueries.get_user_with_all_data(session, user_id)

            if not user_data:
                st.error("Could not load user data for optimization.")
                return

            with st.spinner("🤖 AI is analyzing and optimizing your content..."):
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

                st.success("✅ AI optimization completed!")

        except Exception as e:
            st.error(f"Error during AI optimization: {e}")

    def _display_ai_recommendations(self, user_id: int):
        """Display AI recommendations and allow user to apply them"""
        if 'ai_optimized_data' not in st.session_state:
            st.info("💡 Run AI optimization to see personalized recommendations.")
            return

        st.subheader("🎯 AI Recommendations")

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
                with st.expander("🚫 Excluded Sections", expanded=False):
                    st.write("**The following sections were excluded as not relevant for this job:**")
                    for section in excluded_sections:
                        st.write(f"• {section}")
                    st.info("These sections won't appear in the optimized resume to keep it focused and relevant.")

            if included_sections:
                with st.expander("✅ Included Sections", expanded=False):
                    st.write("**The following sections are relevant for this job:**")
                    for section in included_sections:
                        st.write(f"• {section}")

        # Project recommendations
        projects = optimized_data.get('projects', [])
        if projects and isinstance(projects, list):
            with st.expander("📊 Selected Projects", expanded=True):
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
            with st.expander("📝 Generated Summary", expanded=True):
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
        if st.button("🔄 Generate New Optimization", key="regenerate_optimization"):
            if st.session_state.get('ai_job_description_stored'):
                self._run_ai_optimization(user_id, st.session_state.ai_job_description_stored)


    def _render_section_content_preview(self, user_data: Dict[str, Any], sections: List[str], active_sections: Dict[str, bool]):
        """Render preview of content for each section"""
        for section in sections:
            if not active_sections.get(section, False):
                continue

            section_name = self.section_manager.available_sections.get(section, section)
            section_data = user_data.get(section, [])

            # Ensure section_data is a list
            if not isinstance(section_data, list):
                st.error(f"Invalid data format for section '{section_name}': expected list, got {type(section_data)}")
                continue

            with st.expander(f"📋 {section_name} ({len(section_data)} items)", expanded=False):
                if not section_data:
                    st.info("No content available for this section.")
                    continue

                # Display section content based on type
                self._display_section_content(section, section_data)

    def _display_section_content(self, section: str, data: List[Dict[str, Any]]):
        """Display content for a specific section"""
        if section == "projects":
            for i, project in enumerate(data, 1):
                if not isinstance(project, dict):
                    st.warning(f"Project {i}: Invalid data format")
                    continue
                st.write(f"**{i}. {project.get('title', 'Untitled')}**")
                st.write(f"*{project.get('start_date', '')} - {project.get('end_date', '')}*")
                if project.get('technologies'):
                    st.write(f"**Technologies:** {project['technologies']}")
                if project.get('description'):
                    st.write(project['description'])
                st.markdown("---")

        elif section in ["professional_experience", "research_experience"]:
            for i, exp in enumerate(data, 1):
                if not isinstance(exp, dict):
                    st.warning(f"Experience {i}: Invalid data format")
                    continue
                if section == "professional_experience":
                    st.write(f"**{i}. {exp.get('position', 'Position')} at {exp.get('company', 'Company')}**")
                else:
                    st.write(f"**{i}. {exp.get('title', 'Research Title')}**")
                st.write(f"*{exp.get('start_date', '')} - {exp.get('end_date', '')}*")
                if exp.get('description'):
                    st.write(exp['description'])
                st.markdown("---")

        elif section == "education":
            for i, edu in enumerate(data, 1):
                if not isinstance(edu, dict):
                    st.warning(f"Education {i}: Invalid data format")
                    continue
                st.write(f"**{i}. {edu.get('degree', 'Degree')}**")
                st.write(f"*{edu.get('institution', 'Institution')} - {edu.get('graduation_date', '')}*")
                if edu.get('gpa_percentage'):
                    st.write(f"**GPA:** {edu['gpa_percentage']}")
                st.markdown("---")

        elif section == "technical_skills":
            for i, skill in enumerate(data, 1):
                if not isinstance(skill, dict):
                    st.warning(f"Skill {i}: Invalid data format")
                    continue
                st.write(f"**{skill.get('category', 'Category')}:**")
                st.write(skill.get('skills', 'No skills listed'))
                st.markdown("---")

        elif section == "certifications":
            for i, cert in enumerate(data, 1):
                if not isinstance(cert, dict):
                    st.warning(f"Certification {i}: Invalid data format")
                    continue
                st.write(f"**{i}. {cert.get('title', 'Certification')}**")
                st.write(f"*{cert.get('issuer', 'Issuer')} - {cert.get('date_obtained', '')}*")
                st.markdown("---")

        elif section == "professional_summaries":
            for i, summary in enumerate(data, 1):
                if not isinstance(summary, dict):
                    st.warning(f"Summary {i}: Invalid data format")
                    continue
                st.write(f"**Summary {i}:**")
                st.write(summary.get('generated_summary', 'No summary available'))
                if summary.get('job_description'):
                    st.write(f"*Optimized for:* {summary['job_description'][:100]}...")
                st.markdown("---")

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
                # Debug: Show what AI data contains
                original_project_count = len(user_data.get('projects', []))
                ai_project_count = len(ai_optimized_data.get('projects', []))
                st.info(f"🤖 Using AI-optimized data: {original_project_count} → {ai_project_count} projects")
                st.info("📝 Professional experience uses original content (not AI-modified)")

                # Merge AI optimized content with original data
                user_data = self._merge_ai_optimized_data(user_data, ai_optimized_data)
            else:
                st.info("📄 Using original database data (no AI optimization applied)")

            # Get current section organization
            sidebar_sections, main_sections, active_sections = self.section_manager.get_organized_sections()

            # Apply AI filtering if available
            ai_filtered_sections = st.session_state.get('ai_filtered_sections')
            if ai_filtered_sections:
                # Filter sections based on AI analysis
                filtered_active_sections = {}
                for section, is_active in active_sections.items():
                    ai_relevant = ai_filtered_sections.get(section, True)  # Default to True if not in AI analysis
                    filtered_active_sections[section] = is_active and ai_relevant
                active_sections = filtered_active_sections

            # Filter to only active sections
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
                print(f"Using AI-optimized data for {section}: {len(ai_data[section])} items")

        return merged_data