from typing import Dict, List, Any, Tuple, Optional
import streamlit as st
from streamlit_sortables import sort_items
from database.queries import UserQueries
from database.connection import get_db_session

class InteractiveSectionManager:
    """Manages interactive drag-and-drop section organization for resume building"""

    def __init__(self):
        self.available_sections = {
            "professional_summary": "Professional Summary",
            "projects": "Projects",
            "professional_experience": "Professional Experience",
            "research_experience": "Research Experience",
            "education": "Education",
            "technical_skills": "Technical Skills",
            "certifications": "Certifications"
        }

        # Default organization for two-column layout
        self.default_sidebar_sections = ["education", "technical_skills", "certifications"]
        self.default_main_sections = ["professional_summary", "projects", "professional_experience", "research_experience"]

        # Initialize session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state for section management"""
        if 'sidebar_sections' not in st.session_state:
            st.session_state.sidebar_sections = self.default_sidebar_sections.copy()
        if 'main_sections' not in st.session_state:
            st.session_state.main_sections = self.default_main_sections.copy()
        if 'section_organization_changed' not in st.session_state:
            st.session_state.section_organization_changed = False

    def render_section_organizer(self, user_id: Optional[int] = None) -> Tuple[List[str], List[str]]:
        """
        Render the interactive section organizer interface
        Returns: (sidebar_sections, main_sections)
        """
        st.subheader("📋 Resume Layout Organizer")
        st.write("Drag sections between containers to organize your resume layout:")

        # Get current content counts for each section
        content_counts = self._get_content_counts(user_id) if user_id else {}

        # Prepare container data with content indicators
        containers = [
            {
                'header': '📄 Sidebar (30% width)',
                'items': [self._format_section_item(section, content_counts)
                         for section in st.session_state.sidebar_sections]
            },
            {
                'header': '📝 Main Content (70% width)',
                'items': [self._format_section_item(section, content_counts)
                         for section in st.session_state.main_sections]
            }
        ]

        # Custom styling for the sortable interface
        custom_style = """
        .sortable-component {
            border: 2px solid #2E8B57;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
        .sortable-container {
            background-color: #F8F9FA;
            border-radius: 8px;
            margin: 5px 0;
        }
        .sortable-container-header {
            background-color: #2E8B57;
            color: white;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        .sortable-container-body {
            background-color: #FFFFFF;
            padding: 5px;
            border-radius: 0 0 8px 8px;
        }
        .sortable-item {
            background-color: #E3F2FD;
            border: 1px solid #1976D2;
            color: #1976D2;
            padding: 8px 12px;
            margin: 2px;
            border-radius: 5px;
            font-weight: 500;
        }
        .sortable-item:hover {
            background-color: #BBDEFB;
            cursor: grab;
        }
        """

        # Render the sortable interface
        result = sort_items(
            containers,
            multi_containers=True,
            custom_style=custom_style,
            key="section_organizer"
        )

        # Process the result and update session state
        if result:
            new_sidebar = [self._extract_section_key(item) for item in result[0]['items']]
            new_main = [self._extract_section_key(item) for item in result[1]['items']]

            # Check if organization changed
            if (new_sidebar != st.session_state.sidebar_sections or
                new_main != st.session_state.main_sections):

                st.session_state.sidebar_sections = new_sidebar
                st.session_state.main_sections = new_main
                st.session_state.section_organization_changed = True
                st.rerun()

        return st.session_state.sidebar_sections, st.session_state.main_sections

    def render_section_toggles(self, user_id: Optional[int] = None) -> Dict[str, bool]:
        """
        Render toggles for enabling/disabling sections
        Returns: dict of section_key -> enabled status
        """
        st.subheader("⚙️ Section Controls")

        # Get content counts
        content_counts = self._get_content_counts(user_id) if user_id else {}

        # Initialize active sections in session state, ensuring it's a dictionary
        if 'active_sections' not in st.session_state or not isinstance(st.session_state.active_sections, dict):
            # Convert from list to dict if necessary
            if isinstance(st.session_state.get('active_sections'), list):
                old_list = st.session_state.active_sections
                st.session_state.active_sections = {section: True for section in old_list}
            else:
                st.session_state.active_sections = {
                    section: True for section in
                    (st.session_state.sidebar_sections + st.session_state.main_sections)
                }

        active_sections = {}

        col1, col2 = st.columns(2)

        # Get AI filtered sections
        ai_filtered_sections = st.session_state.get('ai_filtered_sections', {})

        with col1:
            st.write("**Sidebar Sections:**")
            for section in st.session_state.sidebar_sections:
                section_name = self.available_sections.get(section, section)
                count = content_counts.get(section, 0)
                ai_relevant = ai_filtered_sections.get(section, True)

                # Show content count and AI status
                label = f"{section_name}"
                if count > 0:
                    label += f" ({count} items)"
                else:
                    label += " (no content)"

                if not ai_relevant:
                    label += " ❌"

                # Disable if no content or AI excluded
                disabled = count == 0
                checkbox_value = st.session_state.active_sections.get(section, True) and ai_relevant

                active_sections[section] = st.checkbox(
                    label,
                    value=checkbox_value,
                    key=f"toggle_{section}",
                    disabled=disabled,
                    help="AI excluded this section for this job posting" if not ai_relevant else None
                )

        with col2:
            st.write("**Main Content Sections:**")
            for section in st.session_state.main_sections:
                section_name = self.available_sections.get(section, section)
                count = content_counts.get(section, 0)
                ai_relevant = ai_filtered_sections.get(section, True)

                label = f"{section_name}"
                if count > 0:
                    label += f" ({count} items)"
                else:
                    label += " (no content)"

                if not ai_relevant:
                    label += " ❌"

                # Disable if no content
                disabled = count == 0
                checkbox_value = st.session_state.active_sections.get(section, True) and ai_relevant

                active_sections[section] = st.checkbox(
                    label,
                    value=checkbox_value,
                    key=f"toggle_{section}",
                    disabled=disabled,
                    help="AI excluded this section for this job posting" if not ai_relevant else None
                )

        # Update session state
        st.session_state.active_sections = active_sections

        return active_sections

    def _format_section_item(self, section_key: str, content_counts: Dict[str, int]) -> str:
        """Format section item for display with content count"""
        section_name = self.available_sections.get(section_key, section_key)
        count = content_counts.get(section_key, 0)

        if count > 0:
            return f"{section_name} ({count})"
        else:
            return f"{section_name} (empty)"

    def _extract_section_key(self, formatted_item: str) -> str:
        """Extract the section key from formatted item display"""
        # Remove the count suffix and find the matching section
        for key, name in self.available_sections.items():
            if formatted_item.startswith(name):
                return key
        return formatted_item  # Fallback

    def _get_content_counts(self, user_id: int) -> Dict[str, int]:
        """Get count of content items for each section"""
        if not user_id:
            return {}

        try:
            session = next(get_db_session())
            user_data = UserQueries.get_user_with_all_data(session, user_id)

            if not user_data:
                return {}

            counts = {
                'professional_summary': len(user_data.get('professional_summaries', [])),
                'projects': len(user_data.get('projects', [])),
                'professional_experience': len(user_data.get('professional_experience', [])),
                'research_experience': len(user_data.get('research_experience', [])),
                'education': len(user_data.get('education', [])),
                'technical_skills': len(user_data.get('technical_skills', [])),
                'certifications': len(user_data.get('certifications', []))
            }

            return counts

        except Exception as e:
            st.error(f"Error getting content counts: {e}")
            return {}

    def get_organized_sections(self) -> Tuple[List[str], List[str], Dict[str, bool]]:
        """
        Get the current section organization and active status
        Returns: (sidebar_sections, main_sections, active_sections)
        """
        return (
            st.session_state.sidebar_sections,
            st.session_state.main_sections,
            st.session_state.get('active_sections', {})
        )

    def reset_to_default(self):
        """Reset section organization to default layout"""
        st.session_state.sidebar_sections = self.default_sidebar_sections.copy()
        st.session_state.main_sections = self.default_main_sections.copy()
        st.session_state.active_sections = {
            section: True for section in
            (self.default_sidebar_sections + self.default_main_sections)
        }
        st.session_state.section_organization_changed = True

    def render_layout_preview(self):
        """Render a visual preview of the current layout"""
        st.subheader("📐 Layout Preview")

        # Ensure active_sections is a dictionary
        if not isinstance(st.session_state.get('active_sections', {}), dict):
            # Convert list to dictionary format
            if isinstance(st.session_state.get('active_sections'), list):
                old_list = st.session_state.active_sections
                st.session_state.active_sections = {section: True for section in old_list}
            else:
                st.session_state.active_sections = {}

        # Get AI filtered sections
        ai_filtered_sections = st.session_state.get('ai_filtered_sections', {})

        col1, col2 = st.columns([0.3, 0.7])

        with col1:
            st.markdown("**Sidebar (30%)**")
            for section in st.session_state.sidebar_sections:
                section_name = self.available_sections.get(section, section)
                active = st.session_state.active_sections.get(section, True)
                ai_relevant = ai_filtered_sections.get(section, True)  # Default to True if no AI analysis

                if active and ai_relevant:
                    st.info(f"✅ {section_name}")
                elif active and not ai_relevant:
                    st.warning(f"❌ {section_name}")
                elif not active:
                    st.error(f"❌ {section_name} (disabled)")
                else:
                    st.error(f"❌ {section_name}")

        with col2:
            st.markdown("**Main Content (70%)**")
            for section in st.session_state.main_sections:
                section_name = self.available_sections.get(section, section)
                active = st.session_state.active_sections.get(section, True)
                ai_relevant = ai_filtered_sections.get(section, True)

                if active and ai_relevant:
                    st.success(f"✅ {section_name}")
                elif active and not ai_relevant:
                    st.warning(f"❌ {section_name}")
                elif not active:
                    st.error(f"❌ {section_name} (disabled)")
                else:
                    st.error(f"❌ {section_name}")

        # Show AI exclusion summary if available
        if ai_filtered_sections:
            excluded_count = sum(1 for relevant in ai_filtered_sections.values() if not relevant)
            if excluded_count > 0:
                st.info(f"🤖 AI Analysis: {excluded_count} section(s) excluded for this job posting")

        # Reset button
        if st.button("🔄 Reset to Default Layout", key="reset_layout"):
            self.reset_to_default()
            st.rerun()