import streamlit as st
from typing import Dict, Any, Optional
from database.connection import get_db_session
from database.queries import (
    UserQueries, ProjectQueries, ExperienceQueries, AcademicCollaborationQueries,
    EducationQueries, SkillsQueries, CertificationQueries
)
from utils.validators import DataValidator
from ai_integration.groq_client import GroqClient
from utils.auth import hash_password, show_password_dialog
from config.settings import settings

def get_user_api_key():
    """Get Groq API key from user input if not in environment"""
    if settings.groq_api_key:
        return settings.groq_api_key
    
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input(
            "Enter your Groq API Key",
            type="password",
            help="Get your free API key from https://console.groq.com/keys",
            key="user_groq_api_key"
        )
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your Groq API key to use AI features")
        
        st.markdown("---")
    return api_key

def get_api_key_from_session():
    """Get API key from session state without rendering widget"""
    if settings.groq_api_key:
        return settings.groq_api_key
    return st.session_state.get('user_groq_api_key', '')

def render_sidebar() -> bool:
    """
    Render the sidebar with user data input forms
    Returns: True if data was changed, False otherwise
    """
    data_changed = False
    
    # Initialize session state for current user
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    
    # User management section
    st.subheader("User Profile")
    data_changed |= render_user_section()
    
    # Only show other sections if user is selected/created
    if st.session_state.current_user_id:
        st.markdown("---")
        st.subheader("Projects")
        data_changed |= render_projects_section()
        
        st.markdown("---")
        st.subheader("Professional Experience")
        data_changed |= render_professional_experience_section()
        
        st.markdown("---")
        st.subheader("Research Experience")
        data_changed |= render_research_experience_section()

        st.markdown("---")
        st.subheader("Academic Collaborations")
        data_changed |= render_academic_collaborations_section()

        st.markdown("---")
        st.subheader("Education")
        data_changed |= render_education_section()
        
        st.markdown("---")
        st.subheader("Technical Skills")
        data_changed |= render_skills_section()
        
        st.markdown("---")
        st.subheader("Certifications")
        data_changed |= render_certifications_section()
    
    return data_changed

def render_user_section() -> bool:
    """Render user profile section"""
    data_changed = False
    
    # User selection/creation
    with st.expander("Select or Create User", expanded=True):
        email = st.text_input("Email", key="user_email")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load User", disabled=not email, key="load_user_btn"):
                if DataValidator.validate_email(email):
                    # Check if user exists
                    user = load_user_by_email(email)
                    if user:
                        # Set the email for authentication and show dialog
                        st.session_state.auth_email = email
                        st.session_state.show_login_dialog = True
                    else:
                        st.error("User not found")
                else:
                    st.error("Invalid email format")
        
        # Show login dialog outside of button context
        if st.session_state.get('show_login_dialog', False) and st.session_state.get('auth_email'):
            st.markdown("### Enter Password to Access Account")
            
            with st.form("login_form_persistent"):
                password_input = st.text_input("Password", type="password")
                
                col1_auth, col2_auth = st.columns(2)
                with col1_auth:
                    login_submitted = st.form_submit_button("Login")
                with col2_auth:
                    cancel_submitted = st.form_submit_button("Cancel")
                
                if login_submitted:
                    if password_input:
                        st.write("🔥 Authenticating...")
                        authenticated_user = authenticate_user_simple(st.session_state.auth_email, password_input)
                        if authenticated_user:
                            st.session_state.current_user_id = authenticated_user.id
                            st.session_state.show_login_dialog = False
                            st.session_state.auth_email = None
                            st.success(f"Welcome back, {authenticated_user.name}!")
                            st.rerun()
                        else:
                            st.error("Invalid password")
                    else:
                        st.error("Please enter a password")
                
                if cancel_submitted:
                    st.session_state.show_login_dialog = False
                    st.session_state.auth_email = None
                    st.rerun()
        
        with col2:
            if st.button("Create New User", disabled=not email, key="create_user_btn"):
                if DataValidator.validate_email(email):
                    # Check if user already exists
                    existing_user = load_user_by_email(email)
                    if existing_user:
                        st.error("User with this email already exists")
                    else:
                        # Set the email for account creation and show dialog
                        st.session_state.create_email = email
                        st.session_state.show_create_dialog = True
                else:
                    st.error("Invalid email format")
    
    # Show create account dialog outside of button context
    if st.session_state.get('show_create_dialog', False) and st.session_state.get('create_email'):
        st.markdown("### Create New Account")
        
        with st.form("create_form_persistent"):
            password_input = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1_create, col2_create = st.columns(2)
            with col1_create:
                create_submitted = st.form_submit_button("Create Account")
            with col2_create:
                cancel_submitted = st.form_submit_button("Cancel")
            
            if create_submitted:
                if password_input and confirm_password:
                    if password_input == confirm_password:
                        if len(password_input) >= 6:
                            st.write("🔥 Creating account...")
                            success = create_new_user_with_password(st.session_state.create_email, password_input)
                            if success:
                                st.session_state.show_create_dialog = False
                                st.session_state.create_email = None
                                st.rerun()
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in both password fields")
            
            if cancel_submitted:
                st.session_state.show_create_dialog = False
                st.session_state.create_email = None
                st.rerun()
    
    # User data form (if user is selected)
    if st.session_state.current_user_id:
        data_changed |= render_user_form()
    
    return data_changed

def render_user_form() -> bool:
    """Render user information form"""
    data_changed = False
    
    # Load current user data
    user_data = load_current_user_data()
    
    # Clear form keys if user changed
    if 'last_user_id' not in st.session_state or st.session_state.last_user_id != st.session_state.current_user_id:
        form_keys = ['profile_name', 'profile_phone', 'profile_location', 'profile_linkedin', 'profile_github']
        for key in form_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.last_user_id = st.session_state.current_user_id
    
    with st.expander("Edit Profile Information", expanded=True):
        name = st.text_input("Full Name", value=user_data.get('name', ''), key="profile_name")
        phone = st.text_input("Phone Number", value=user_data.get('phone', ''), key="profile_phone")
        location = st.text_input("Location", value=user_data.get('location', ''), key="profile_location")
        linkedin_url = st.text_input("LinkedIn URL", value=user_data.get('linkedin_url', ''), key="profile_linkedin")
        github_url = st.text_input("GitHub URL", value=user_data.get('github_url', ''), key="profile_github")
        
        if st.button("Update Profile", key="update_profile"):
            update_data = {
                'name': name,
                'phone': phone,
                'location': location,
                'linkedin_url': linkedin_url,
                'github_url': github_url
            }
            
            is_valid, errors = DataValidator.validate_user_data(update_data)
            if is_valid:
                if update_user_profile(update_data):
                    st.success("Profile updated successfully!")
                    data_changed = True
                else:
                    st.error("Failed to update profile")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_projects_section() -> bool:
    """Render projects management section"""
    data_changed = False
    
    # Load projects
    projects = load_user_projects()
    
    # Display existing projects with AI reframing
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
                        data_changed = True
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_project_{i}"):
                        st.session_state[f'editing_project_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_project_title = project.get('title', '')
                        st.session_state.edit_project_description = project.get('description', '')
                        st.session_state.edit_project_technologies = project.get('technologies', '')
                        st.session_state.edit_project_start = project.get('start_date', '')
                        st.session_state.edit_project_end = project.get('end_date', '')
                        st.session_state.edit_project_url = project.get('project_url', '')
                        st.session_state.edit_project_id = project['id']
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_project_{i}"):
                        if delete_project(project['id']):
                            st.success("Project deleted!")
                            data_changed = True
                            st.rerun()
                
                # Show reframed version if available
                if f'reframed_project_{i}' in st.session_state:
                    st.markdown("**✨ AI Reframed Description:**")
                    st.info(st.session_state[f'reframed_project_{i}'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Use This Version", key=f"accept_reframe_{i}"):
                            update_project_description(project['id'], st.session_state[f'reframed_project_{i}'])
                            del st.session_state[f'reframed_project_{i}']
                            st.success("Project updated!")
                            data_changed = True
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Keep Original", key=f"reject_reframe_{i}"):
                            del st.session_state[f'reframed_project_{i}']
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_project_{i}', False):
                    st.markdown("**✏️ Edit Project:**")

                    edit_title = st.text_input(
                        "Project Title",
                        value=st.session_state.get('edit_project_title', ''),
                        key=f"edit_project_title_{i}"
                    )
                    edit_description = st.text_area(
                        "Description",
                        value=st.session_state.get('edit_project_description', ''),
                        key=f"edit_project_description_{i}"
                    )
                    edit_technologies = st.text_input(
                        "Technologies (comma-separated)",
                        value=st.session_state.get('edit_project_technologies', ''),
                        key=f"edit_project_technologies_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        edit_start_date = st.text_input(
                            "Start Date",
                            value=st.session_state.get('edit_project_start', ''),
                            key=f"edit_project_start_{i}"
                        )
                    with col2:
                        edit_end_date = st.text_input(
                            "End Date",
                            value=st.session_state.get('edit_project_end', ''),
                            key=f"edit_project_end_{i}"
                        )

                    edit_project_url = st.text_input(
                        "Project URL (optional)",
                        value=st.session_state.get('edit_project_url', ''),
                        key=f"edit_project_url_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_project_{i}"):
                            updated_data = {
                                'title': edit_title,
                                'description': edit_description,
                                'technologies': edit_technologies,
                                'start_date': edit_start_date,
                                'end_date': edit_end_date,
                                'project_url': edit_project_url
                            }

                            is_valid, errors = DataValidator.validate_project_data(updated_data)
                            if is_valid:
                                if update_project(st.session_state.get('edit_project_id'), updated_data):
                                    st.success("Project updated successfully!")
                                    # Clear edit mode
                                    st.session_state[f'editing_project_{i}'] = False
                                    clear_edit_project_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update project")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_project_{i}"):
                            st.session_state[f'editing_project_{i}'] = False
                            clear_edit_project_session_state()
                            st.rerun()
    
    # Add new project form
    with st.expander("Add New Project", expanded=False):
        data_changed |= render_add_project_form()
    
    return data_changed

def render_add_project_form() -> bool:
    """Render add project form - always empty for new projects"""
    # Initialize form counter for unique keys
    if 'project_form_counter' not in st.session_state:
        st.session_state.project_form_counter = 0

    # Use counter in keys to ensure fresh form
    counter = st.session_state.project_form_counter

    title = st.text_input("Project Title", key=f"new_project_title_{counter}")
    description = st.text_area("Description", key=f"new_project_description_{counter}")
    technologies = st.text_input("Technologies (comma-separated)", key=f"new_project_technologies_{counter}")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.text_input("Start Date (e.g., Jan 2024)", key=f"new_project_start_{counter}")
    with col2:
        end_date = st.text_input("End Date (or 'Present')", key=f"new_project_end_{counter}")

    project_url = st.text_input("Project URL (optional)", key=f"new_project_url_{counter}")
    
    if st.button("Add Project", key="add_project"):
        project_data = {
            'title': title,
            'description': description,
            'technologies': technologies,
            'start_date': start_date,
            'end_date': end_date,
            'project_url': project_url
        }

        is_valid, errors = DataValidator.validate_project_data(project_data)
        if is_valid:
            if add_project(project_data):
                st.success("Project added successfully!")
                # Increment counter to create fresh form
                st.session_state.project_form_counter += 1
                st.rerun()
                return True
            else:
                st.error("Failed to add project")
        else:
            for error in errors:
                st.error(error)

    return False

def render_professional_experience_section() -> bool:
    """Render professional experience section"""
    data_changed = False
    
    # Similar structure to projects
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
                        data_changed = True
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_exp_{i}"):
                        st.session_state[f'editing_exp_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_exp_company = exp.get('company', '')
                        st.session_state.edit_exp_position = exp.get('position', '')
                        st.session_state.edit_exp_description = exp.get('description', '')
                        st.session_state.edit_exp_start = exp.get('start_date', '')
                        st.session_state.edit_exp_end = exp.get('end_date', '')
                        st.session_state.edit_exp_id = exp['id']
                        st.rerun()
                
                # Show reframed version if available
                if f'reframed_exp_{i}' in st.session_state:
                    st.markdown("**✨ AI Reframed Description:**")
                    st.info(st.session_state[f'reframed_exp_{i}'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Use This Version", key=f"accept_exp_reframe_{i}"):
                            update_experience_description(exp['id'], st.session_state[f'reframed_exp_{i}'])
                            del st.session_state[f'reframed_exp_{i}']
                            st.success("Experience updated!")
                            data_changed = True
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Keep Original", key=f"reject_exp_reframe_{i}"):
                            del st.session_state[f'reframed_exp_{i}']
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_exp_{i}', False):
                    st.markdown("**✏️ Edit Experience:**")

                    edit_company = st.text_input(
                        "Company",
                        value=st.session_state.get('edit_exp_company', ''),
                        key=f"edit_exp_company_{i}"
                    )
                    edit_position = st.text_input(
                        "Position",
                        value=st.session_state.get('edit_exp_position', ''),
                        key=f"edit_exp_position_{i}"
                    )
                    edit_description = st.text_area(
                        "Description",
                        value=st.session_state.get('edit_exp_description', ''),
                        key=f"edit_exp_description_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        edit_start_date = st.text_input(
                            "Start Date",
                            value=st.session_state.get('edit_exp_start', ''),
                            key=f"edit_exp_start_{i}"
                        )
                    with col2:
                        edit_end_date = st.text_input(
                            "End Date",
                            value=st.session_state.get('edit_exp_end', ''),
                            key=f"edit_exp_end_{i}"
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_exp_{i}"):
                            updated_data = {
                                'company': edit_company,
                                'position': edit_position,
                                'description': edit_description,
                                'start_date': edit_start_date,
                                'end_date': edit_end_date
                            }

                            is_valid, errors = DataValidator.validate_experience_data(updated_data, "professional")
                            if is_valid:
                                if update_experience(st.session_state.get('edit_exp_id'), updated_data):
                                    st.success("Experience updated successfully!")
                                    # Clear edit mode
                                    st.session_state[f'editing_exp_{i}'] = False
                                    clear_edit_experience_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update experience")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_exp_{i}"):
                            st.session_state[f'editing_exp_{i}'] = False
                            clear_edit_experience_session_state()
                            st.rerun()
    
    # Add new experience form
    with st.expander("Add Professional Experience", expanded=False):
        data_changed |= render_add_professional_experience_form()
    
    return data_changed

def render_add_professional_experience_form() -> bool:
    """Render add professional experience form - always empty for new experiences"""
    # Initialize form counter for unique keys
    if 'experience_form_counter' not in st.session_state:
        st.session_state.experience_form_counter = 0

    # Use counter in keys to ensure fresh form
    counter = st.session_state.experience_form_counter

    company = st.text_input("Company", key=f"new_exp_company_{counter}")
    position = st.text_input("Position", key=f"new_exp_position_{counter}")
    description = st.text_area("Description", key=f"new_exp_description_{counter}")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.text_input("Start Date", key=f"new_exp_start_{counter}")
    with col2:
        end_date = st.text_input("End Date (or 'Present')", key=f"new_exp_end_{counter}")
    
    if st.button("Add Experience", key="add_experience"):
        exp_data = {
            'company': company,
            'position': position,
            'description': description,
            'start_date': start_date,
            'end_date': end_date
        }
        
        is_valid, errors = DataValidator.validate_experience_data(exp_data, "professional")
        if is_valid:
            if add_professional_experience(exp_data):
                st.success("Experience added successfully!")
                # Increment counter to create fresh form
                st.session_state.experience_form_counter += 1
                st.rerun()
                return True
            else:
                st.error("Failed to add experience")
        else:
            for error in errors:
                st.error(error)

    return False

def render_research_experience_section() -> bool:
    """Render research experience section (similar to professional)"""
    data_changed = False

    # Load and display existing research experiences
    research_experiences = load_user_research_experience()

    if research_experiences:
        st.write(f"**Current Research Experience ({len(research_experiences)}):**")
        for i, research in enumerate(research_experiences):
            with st.expander(f"{research.get('title', 'Research Project')}", expanded=False):
                st.write(f"**Period:** {research.get('start_date', '')} - {research.get('end_date', 'Present')}")
                st.write(f"**Description:** {research.get('description', 'No description')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_research_{i}"):
                        st.session_state[f'editing_research_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_research_title = research.get('title', '')
                        st.session_state.edit_research_description = research.get('description', '')
                        st.session_state.edit_research_start = research.get('start_date', '')
                        st.session_state.edit_research_end = research.get('end_date', '')
                        st.session_state.edit_research_id = research['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_research_{i}"):
                        if delete_research_experience(research['id']):
                            st.success("Research experience deleted!")
                            data_changed = True
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_research_{i}', False):
                    st.markdown("**✏️ Edit Research Experience:**")

                    edit_title = st.text_input(
                        "Research Title",
                        value=st.session_state.get('edit_research_title', ''),
                        key=f"edit_research_title_{i}"
                    )
                    edit_description = st.text_area(
                        "Description",
                        value=st.session_state.get('edit_research_description', ''),
                        key=f"edit_research_description_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        edit_start_date = st.text_input(
                            "Start Date",
                            value=st.session_state.get('edit_research_start', ''),
                            key=f"edit_research_start_{i}"
                        )
                    with col2:
                        edit_end_date = st.text_input(
                            "End Date",
                            value=st.session_state.get('edit_research_end', ''),
                            key=f"edit_research_end_{i}"
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_research_{i}"):
                            updated_data = {
                                'title': edit_title,
                                'description': edit_description,
                                'start_date': edit_start_date,
                                'end_date': edit_end_date
                            }

                            is_valid, errors = DataValidator.validate_experience_data(updated_data, "research")
                            if is_valid:
                                if update_research_experience(st.session_state.get('edit_research_id'), updated_data):
                                    st.success("Research experience updated successfully!")
                                    st.session_state[f'editing_research_{i}'] = False
                                    clear_edit_research_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update research experience")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_research_{i}"):
                            st.session_state[f'editing_research_{i}'] = False
                            clear_edit_research_session_state()
                            st.rerun()

    # Add new research experience form
    with st.expander("Add Research Experience", expanded=False):
        # Initialize form counter for unique keys
        if 'research_form_counter' not in st.session_state:
            st.session_state.research_form_counter = 0

        counter = st.session_state.research_form_counter

        title = st.text_input("Research Title", key=f"new_research_title_{counter}")
        description = st.text_area("Description", key=f"new_research_description_{counter}")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.text_input("Start Date", key=f"new_research_start_{counter}")
        with col2:
            end_date = st.text_input("End Date", key=f"new_research_end_{counter}")

        if st.button("Add Research Experience", key="add_research"):
            research_data = {
                'title': title,
                'description': description,
                'start_date': start_date,
                'end_date': end_date
            }

            is_valid, errors = DataValidator.validate_experience_data(research_data, "research")
            if is_valid:
                if add_research_experience(research_data):
                    st.success("Research experience added successfully!")
                    # Increment counter to create fresh form
                    st.session_state.research_form_counter += 1
                    data_changed = True
                    st.rerun()
                else:
                    st.error("Failed to add research experience")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_academic_collaborations_section() -> bool:
    """Render academic collaborations section"""
    data_changed = False

    # Load and display existing academic collaborations
    collaborations = load_user_academic_collaborations()

    if collaborations:
        st.write(f"**Current Academic Collaborations ({len(collaborations)}):**")
        for i, collab in enumerate(collaborations):
            with st.expander(f"{collab.get('project_title', 'Collaboration')} ({collab.get('collaboration_type', 'N/A')})", expanded=False):
                st.write(f"**Type:** {collab.get('collaboration_type', 'N/A')}")
                st.write(f"**Institution:** {collab.get('institution', 'N/A')}")
                st.write(f"**Role:** {collab.get('role', 'N/A')}")
                st.write(f"**Period:** {collab.get('start_date', '')} - {collab.get('end_date', 'Present')}")
                if collab.get('collaborators'):
                    st.write(f"**Collaborators:** {collab.get('collaborators', 'N/A')}")
                st.write(f"**Description:** {collab.get('description', 'No description')}")
                if collab.get('publication_url'):
                    st.write(f"**Publication/URL:** {collab.get('publication_url', 'N/A')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_collab_{i}"):
                        st.session_state[f'editing_collab_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_collab_title = collab.get('project_title', '')
                        st.session_state.edit_collab_type = collab.get('collaboration_type', '')
                        st.session_state.edit_collab_institution = collab.get('institution', '')
                        st.session_state.edit_collab_collaborators = collab.get('collaborators', '')
                        st.session_state.edit_collab_role = collab.get('role', '')
                        st.session_state.edit_collab_description = collab.get('description', '')
                        st.session_state.edit_collab_start = collab.get('start_date', '')
                        st.session_state.edit_collab_end = collab.get('end_date', '')
                        st.session_state.edit_collab_url = collab.get('publication_url', '')
                        st.session_state.edit_collab_id = collab['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_collab_{i}"):
                        if delete_academic_collaboration(collab['id']):
                            st.success("Academic collaboration deleted!")
                            data_changed = True
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_collab_{i}', False):
                    st.markdown("**✏️ Edit Academic Collaboration:**")

                    edit_title = st.text_input(
                        "Project Title",
                        value=st.session_state.get('edit_collab_title', ''),
                        key=f"edit_collab_title_{i}"
                    )
                    edit_type = st.selectbox(
                        "Collaboration Type",
                        ["Research", "Publication", "Conference", "Workshop", "Grant", "Other"],
                        index=["Research", "Publication", "Conference", "Workshop", "Grant", "Other"].index(
                            st.session_state.get('edit_collab_type', 'Research')
                        ) if st.session_state.get('edit_collab_type', 'Research') in ["Research", "Publication", "Conference", "Workshop", "Grant", "Other"] else 0,
                        key=f"edit_collab_type_{i}"
                    )
                    edit_institution = st.text_input(
                        "Institution",
                        value=st.session_state.get('edit_collab_institution', ''),
                        key=f"edit_collab_institution_{i}"
                    )
                    edit_role = st.text_input(
                        "Your Role",
                        value=st.session_state.get('edit_collab_role', ''),
                        key=f"edit_collab_role_{i}"
                    )
                    edit_collaborators = st.text_area(
                        "Collaborators",
                        value=st.session_state.get('edit_collab_collaborators', ''),
                        key=f"edit_collab_collaborators_{i}"
                    )
                    edit_description = st.text_area(
                        "Description",
                        value=st.session_state.get('edit_collab_description', ''),
                        key=f"edit_collab_description_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        edit_start_date = st.text_input(
                            "Start Date",
                            value=st.session_state.get('edit_collab_start', ''),
                            key=f"edit_collab_start_{i}"
                        )
                    with col2:
                        edit_end_date = st.text_input(
                            "End Date",
                            value=st.session_state.get('edit_collab_end', ''),
                            key=f"edit_collab_end_{i}"
                        )

                    edit_url = st.text_input(
                        "Publication/URL (optional)",
                        value=st.session_state.get('edit_collab_url', ''),
                        key=f"edit_collab_url_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_collab_{i}"):
                            updated_data = {
                                'project_title': edit_title,
                                'collaboration_type': edit_type,
                                'institution': edit_institution,
                                'role': edit_role,
                                'collaborators': edit_collaborators,
                                'description': edit_description,
                                'start_date': edit_start_date,
                                'end_date': edit_end_date,
                                'publication_url': edit_url
                            }

                            is_valid, errors = DataValidator.validate_academic_collaboration_data(updated_data)
                            if is_valid:
                                if update_academic_collaboration(st.session_state.get('edit_collab_id'), updated_data):
                                    st.success("Academic collaboration updated successfully!")
                                    st.session_state[f'editing_collab_{i}'] = False
                                    clear_edit_collaboration_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update academic collaboration")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_collab_{i}"):
                            st.session_state[f'editing_collab_{i}'] = False
                            clear_edit_collaboration_session_state()
                            st.rerun()

    # Add new academic collaboration form
    with st.expander("Add Academic Collaboration", expanded=False):
        # Initialize form counter for unique keys
        if 'collaboration_form_counter' not in st.session_state:
            st.session_state.collaboration_form_counter = 0

        counter = st.session_state.collaboration_form_counter

        project_title = st.text_input("Project Title", key=f"new_collab_title_{counter}")
        collaboration_type = st.selectbox(
            "Collaboration Type",
            ["Research", "Publication", "Conference", "Workshop", "Grant", "Other"],
            key=f"new_collab_type_{counter}"
        )
        institution = st.text_input("Institution", key=f"new_collab_institution_{counter}")
        role = st.text_input("Your Role", key=f"new_collab_role_{counter}")
        collaborators = st.text_area("Collaborators (list names)", key=f"new_collab_collaborators_{counter}")
        description = st.text_area("Description", key=f"new_collab_description_{counter}")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.text_input("Start Date", key=f"new_collab_start_{counter}")
        with col2:
            end_date = st.text_input("End Date", key=f"new_collab_end_{counter}")

        publication_url = st.text_input("Publication/URL (optional)", key=f"new_collab_url_{counter}")

        if st.button("Add Academic Collaboration", key="add_collaboration"):
            collab_data = {
                'project_title': project_title,
                'collaboration_type': collaboration_type,
                'institution': institution,
                'role': role,
                'collaborators': collaborators,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'publication_url': publication_url
            }

            is_valid, errors = DataValidator.validate_academic_collaboration_data(collab_data)
            if is_valid:
                if add_academic_collaboration(collab_data):
                    st.success("Academic collaboration added successfully!")
                    # Increment counter to create fresh form
                    st.session_state.collaboration_form_counter += 1
                    data_changed = True
                    st.rerun()
                else:
                    st.error("Failed to add academic collaboration")
            else:
                for error in errors:
                    st.error(error)

    return data_changed

def render_education_section() -> bool:
    """Render education section"""
    data_changed = False

    # Load and display existing education
    education_records = load_user_education()

    if education_records:
        st.write(f"**Current Education ({len(education_records)}):**")
        for i, edu in enumerate(education_records):
            with st.expander(f"{edu.get('degree', 'Degree')} at {edu.get('institution', 'Institution')}", expanded=False):
                st.write(f"**Graduation:** {edu.get('graduation_date', 'N/A')}")
                if edu.get('gpa_percentage'):
                    st.write(f"**GPA/Percentage:** {edu.get('gpa_percentage', 'N/A')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_edu_{i}"):
                        st.session_state[f'editing_edu_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_edu_degree = edu.get('degree', '')
                        st.session_state.edit_edu_institution = edu.get('institution', '')
                        st.session_state.edit_edu_grad_date = edu.get('graduation_date', '')
                        st.session_state.edit_edu_gpa = edu.get('gpa_percentage', '')
                        st.session_state.edit_edu_id = edu['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_edu_{i}"):
                        if delete_education(edu['id']):
                            st.success("Education deleted!")
                            data_changed = True
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_edu_{i}', False):
                    st.markdown("**✏️ Edit Education:**")

                    edit_degree = st.text_input(
                        "Degree",
                        value=st.session_state.get('edit_edu_degree', ''),
                        key=f"edit_edu_degree_{i}"
                    )
                    edit_institution = st.text_input(
                        "Institution",
                        value=st.session_state.get('edit_edu_institution', ''),
                        key=f"edit_edu_institution_{i}"
                    )
                    edit_graduation_date = st.text_input(
                        "Graduation Date",
                        value=st.session_state.get('edit_edu_grad_date', ''),
                        key=f"edit_edu_grad_date_{i}"
                    )
                    edit_gpa_percentage = st.text_input(
                        "GPA/Percentage",
                        value=st.session_state.get('edit_edu_gpa', ''),
                        key=f"edit_edu_gpa_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_edu_{i}"):
                            updated_data = {
                                'degree': edit_degree,
                                'institution': edit_institution,
                                'graduation_date': edit_graduation_date,
                                'gpa_percentage': edit_gpa_percentage
                            }

                            is_valid, errors = DataValidator.validate_education_data(updated_data)
                            if is_valid:
                                if update_education(st.session_state.get('edit_edu_id'), updated_data):
                                    st.success("Education updated successfully!")
                                    st.session_state[f'editing_edu_{i}'] = False
                                    clear_edit_education_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update education")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_edu_{i}"):
                            st.session_state[f'editing_edu_{i}'] = False
                            clear_edit_education_session_state()
                            st.rerun()

    # Add new education form
    with st.expander("Add Education", expanded=False):
        # Initialize form counter for unique keys
        if 'education_form_counter' not in st.session_state:
            st.session_state.education_form_counter = 0

        counter = st.session_state.education_form_counter

        degree = st.text_input("Degree", key=f"new_edu_degree_{counter}")
        institution = st.text_input("Institution", key=f"new_edu_institution_{counter}")
        graduation_date = st.text_input("Graduation Date", key=f"new_edu_grad_date_{counter}")
        gpa_percentage = st.text_input("GPA/Percentage", key=f"new_edu_gpa_{counter}")

        if st.button("Add Education", key="add_education"):
            edu_data = {
                'degree': degree,
                'institution': institution,
                'graduation_date': graduation_date,
                'gpa_percentage': gpa_percentage
            }

            is_valid, errors = DataValidator.validate_education_data(edu_data)
            if is_valid:
                if add_education(edu_data):
                    st.success("Education added successfully!")
                    # Increment counter to create fresh form
                    st.session_state.education_form_counter += 1
                    data_changed = True
                    st.rerun()
                else:
                    st.error("Failed to add education")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_skills_section() -> bool:
    """Render technical skills section"""
    data_changed = False

    # Load and display existing skills
    skills_records = load_user_technical_skills()

    if skills_records:
        st.write(f"**Current Technical Skills ({len(skills_records)}):**")
        for i, skill in enumerate(skills_records):
            with st.expander(f"{skill.get('category', 'Skills Category')}", expanded=False):
                st.write(f"**Skills:** {skill.get('skills', 'No skills listed')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_skill_{i}"):
                        st.session_state[f'editing_skill_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_skill_category = skill.get('category', '')
                        st.session_state.edit_skill_skills = skill.get('skills', '')
                        st.session_state.edit_skill_id = skill['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_skill_{i}"):
                        if delete_technical_skills(skill['id']):
                            st.success("Skills deleted!")
                            data_changed = True
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_skill_{i}', False):
                    st.markdown("**✏️ Edit Skills:**")

                    edit_category = st.text_input(
                        "Skill Category",
                        value=st.session_state.get('edit_skill_category', ''),
                        key=f"edit_skill_category_{i}"
                    )
                    edit_skills = st.text_input(
                        "Skills (comma-separated)",
                        value=st.session_state.get('edit_skill_skills', ''),
                        key=f"edit_skill_skills_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_skill_{i}"):
                            updated_data = {
                                'category': edit_category,
                                'skills': edit_skills
                            }

                            is_valid, errors = DataValidator.validate_skill_data(updated_data)
                            if is_valid:
                                if update_technical_skills(st.session_state.get('edit_skill_id'), updated_data):
                                    st.success("Skills updated successfully!")
                                    st.session_state[f'editing_skill_{i}'] = False
                                    clear_edit_skills_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update skills")
                            else:
                                for error in errors:
                                    st.error(error)

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_skill_{i}"):
                            st.session_state[f'editing_skill_{i}'] = False
                            clear_edit_skills_session_state()
                            st.rerun()

    # Add new skills form
    with st.expander("Add Technical Skills", expanded=False):
        # Initialize form counter for unique keys
        if 'skills_form_counter' not in st.session_state:
            st.session_state.skills_form_counter = 0

        counter = st.session_state.skills_form_counter

        category = st.text_input("Skill Category (e.g., Programming Languages)", key=f"new_skill_category_{counter}")
        skills = st.text_input("Skills (comma-separated)", key=f"new_skill_list_{counter}")

        if st.button("Add Skills Category", key="add_skills"):
            skill_data = {
                'category': category,
                'skills': skills
            }

            is_valid, errors = DataValidator.validate_skill_data(skill_data)
            if is_valid:
                if add_technical_skills(skill_data):
                    st.success("Skills added successfully!")
                    # Increment counter to create fresh form
                    st.session_state.skills_form_counter += 1
                    data_changed = True
                    st.rerun()
                else:
                    st.error("Failed to add skills")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_certifications_section() -> bool:
    """Render certifications section"""
    data_changed = False

    # Load and display existing certifications
    certifications = load_user_certifications()

    if certifications:
        st.write(f"**Current Certifications ({len(certifications)}):**")
        for i, cert in enumerate(certifications):
            with st.expander(f"{cert.get('title', 'Certification')}", expanded=False):
                st.write(f"**Issuer:** {cert.get('issuer', 'N/A')}")
                st.write(f"**Date Obtained:** {cert.get('date_obtained', 'N/A')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_cert_{i}"):
                        st.session_state[f'editing_cert_{i}'] = True
                        # Populate edit form with current data
                        st.session_state.edit_cert_title = cert.get('title', '')
                        st.session_state.edit_cert_issuer = cert.get('issuer', '')
                        st.session_state.edit_cert_date = cert.get('date_obtained', '')
                        st.session_state.edit_cert_id = cert['id']
                        st.rerun()

                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_cert_{i}"):
                        if delete_certification(cert['id']):
                            st.success("Certification deleted!")
                            data_changed = True
                            st.rerun()

                # Show edit form if in edit mode
                if st.session_state.get(f'editing_cert_{i}', False):
                    st.markdown("**✏️ Edit Certification:**")

                    edit_title = st.text_input(
                        "Certification Title",
                        value=st.session_state.get('edit_cert_title', ''),
                        key=f"edit_cert_title_{i}"
                    )
                    edit_issuer = st.text_input(
                        "Issuer",
                        value=st.session_state.get('edit_cert_issuer', ''),
                        key=f"edit_cert_issuer_{i}"
                    )
                    edit_date_obtained = st.text_input(
                        "Date Obtained",
                        value=st.session_state.get('edit_cert_date', ''),
                        key=f"edit_cert_date_{i}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_cert_{i}"):
                            updated_data = {
                                'title': edit_title,
                                'issuer': edit_issuer,
                                'date_obtained': edit_date_obtained
                            }

                            if edit_title:  # Only title is required
                                if update_certification(st.session_state.get('edit_cert_id'), updated_data):
                                    st.success("Certification updated successfully!")
                                    st.session_state[f'editing_cert_{i}'] = False
                                    clear_edit_certification_session_state()
                                    data_changed = True
                                    st.rerun()
                                else:
                                    st.error("Failed to update certification")
                            else:
                                st.error("Certification title is required")

                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_edit_cert_{i}"):
                            st.session_state[f'editing_cert_{i}'] = False
                            clear_edit_certification_session_state()
                            st.rerun()

    # Add new certification form
    with st.expander("Add Certification", expanded=False):
        # Initialize form counter for unique keys
        if 'certification_form_counter' not in st.session_state:
            st.session_state.certification_form_counter = 0

        counter = st.session_state.certification_form_counter

        title = st.text_input("Certification Title", key=f"new_cert_title_{counter}")
        issuer = st.text_input("Issuer", key=f"new_cert_issuer_{counter}")
        date_obtained = st.text_input("Date Obtained", key=f"new_cert_date_{counter}")

        if st.button("Add Certification", key="add_certification"):
            cert_data = {
                'title': title,
                'issuer': issuer,
                'date_obtained': date_obtained
            }

            if title:  # Only title is required
                if add_certification(cert_data):
                    st.success("Certification added successfully!")
                    # Increment counter to create fresh form
                    st.session_state.certification_form_counter += 1
                    data_changed = True
                    st.rerun()
                else:
                    st.error("Failed to add certification")
            else:
                st.error("Certification title is required")
    
    return data_changed

# Database helper functions
def load_user_by_email(email: str):
    """Load user by email"""
    try:
        session = next(get_db_session())
        return UserQueries.get_user_by_email(session, email)
    except Exception as e:
        st.error(f"Error loading user: {e}")
        return None

def authenticate_user_simple(email: str, password: str):
    """Simple authentication using direct SQL"""
    try:
        import psycopg2
        from utils.auth import verify_password
        
        # Use SQLAlchemy instead of raw SQL
        session = next(get_db_session())
        user = UserQueries.get_user_by_email(session, email)
        
        if user and user.password_hash:
            if verify_password(password, user.password_hash):
                return type('User', (), {
                    'id': user.id, 
                    'name': user.name or 'User', 
                    'email': user.email
                })()
        
        return None
        
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def create_new_user_with_password(email: str, password: str) -> bool:
    """Create new user with password"""
    try:
        session = next(get_db_session())
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Create user with basic info
        user_data = {
            "email": email,
            "name": email.split("@")[0].title()  # Default name from email
        }
        
        user = UserQueries.create_user(session, user_data, password_hash)
        session.commit()
        
        # Set as current user
        st.session_state.current_user_id = user.id
        st.success(f"Account created successfully! Welcome, {user.name}!")
        
        session.close()
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def create_new_user(email: str) -> bool:
    """Create new user"""
    try:
        session = next(get_db_session())
        user_data = {'email': email, 'name': 'New User'}
        user = UserQueries.create_user(session, user_data)
        st.session_state.current_user_id = user.id
        st.success(f"Created new user with email: {email}")
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def load_current_user_data() -> Dict[str, Any]:
    """Load current user data"""
    if not st.session_state.current_user_id:
        return {}
    
    try:
        session = next(get_db_session())
        user = UserQueries.get_user_by_id(session, st.session_state.current_user_id)
        session.close()
        
        return {
            'name': user.name or '',
            'email': user.email or '',
            'phone': user.phone or '',
            'location': user.location or '',
            'linkedin_url': user.linkedin_url or '',
            'github_url': user.github_url or ''
        } if user else {}
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return {}

def update_user_profile(user_data: Dict[str, Any]) -> bool:
    """Update user profile"""
    try:
        session = next(get_db_session())
        UserQueries.update_user(session, st.session_state.current_user_id, user_data)
        return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False

def load_user_projects() -> list:
    """Load user projects"""
    if not st.session_state.current_user_id:
        return []
    
    try:
        session = next(get_db_session())
        projects = ProjectQueries.get_user_projects(session, st.session_state.current_user_id)
        return [
            {
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'technologies': p.technologies,
                'start_date': p.start_date,
                'end_date': p.end_date,
                'project_url': p.project_url
            } for p in projects
        ]
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        return []

def add_project(project_data: Dict[str, Any]) -> bool:
    """Add new project"""
    try:
        session = next(get_db_session())
        ProjectQueries.create_project(session, st.session_state.current_user_id, project_data)
        return True
    except Exception as e:
        st.error(f"Error adding project: {e}")
        return False

def delete_project(project_id: int) -> bool:
    """Delete project"""
    try:
        session = next(get_db_session())
        ProjectQueries.delete_project(session, project_id)
        return True
    except Exception as e:
        st.error(f"Error deleting project: {e}")
        return False

def load_user_professional_experience() -> list:
    """Load user professional experience"""
    if not st.session_state.current_user_id:
        return []
    
    try:
        session = next(get_db_session())
        experiences = ExperienceQueries.get_professional_experience(session, st.session_state.current_user_id)
        return [
            {
                'id': e.id,
                'company': e.company,
                'position': e.position,
                'description': e.description,
                'start_date': e.start_date,
                'end_date': e.end_date
            } for e in experiences
        ]
    except Exception as e:
        st.error(f"Error loading experience: {e}")
        return []

def add_professional_experience(exp_data: Dict[str, Any]) -> bool:
    """Add professional experience"""
    try:
        session = next(get_db_session())
        ExperienceQueries.create_professional_experience(session, st.session_state.current_user_id, exp_data)
        return True
    except Exception as e:
        st.error(f"Error adding experience: {e}")
        return False

def add_research_experience(research_data: Dict[str, Any]) -> bool:
    """Add research experience"""
    try:
        session = next(get_db_session())
        ExperienceQueries.create_research_experience(session, st.session_state.current_user_id, research_data)
        return True
    except Exception as e:
        st.error(f"Error adding research experience: {e}")
        return False

def add_education(edu_data: Dict[str, Any]) -> bool:
    """Add education"""
    try:
        session = next(get_db_session())
        EducationQueries.create_education(session, st.session_state.current_user_id, edu_data)
        return True
    except Exception as e:
        st.error(f"Error adding education: {e}")
        return False

def add_technical_skills(skill_data: Dict[str, Any]) -> bool:
    """Add technical skills"""
    try:
        session = next(get_db_session())
        SkillsQueries.create_technical_skill(session, st.session_state.current_user_id, skill_data)
        return True
    except Exception as e:
        st.error(f"Error adding skills: {e}")
        return False

def add_certification(cert_data: Dict[str, Any]) -> bool:
    """Add certification"""
    try:
        session = next(get_db_session())
        CertificationQueries.create_certification(session, st.session_state.current_user_id, cert_data)
        return True
    except Exception as e:
        st.error(f"Error adding certification: {e}")
        return False

# AI Reframing Functions
def reframe_project_description(project: Dict[str, Any], index: int):
    """Reframe project description using AI"""
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("AI is reframing your project description..."):
            reframed = groq_client.reframe_content(
                project.get('description', ''),
                'project',
                'make it more impactful and highlight technical achievements'
            )
            
            if reframed and reframed != project.get('description', ''):
                st.session_state[f'reframed_project_{index}'] = reframed
                st.success("✨ AI has reframed your project description!")
                st.rerun()
            else:
                st.warning("AI couldn't improve the description significantly.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

def reframe_experience_description(experience: Dict[str, Any], index: int):
    """Reframe experience description using AI"""
    groq_client = GroqClient()
    if groq_client.is_available():
        with st.spinner("AI is reframing your experience description..."):
            reframed = groq_client.reframe_content(
                experience.get('description', ''),
                'professional experience',
                'emphasize achievements and quantifiable results'
            )
            
            if reframed and reframed != experience.get('description', ''):
                st.session_state[f'reframed_exp_{index}'] = reframed
                st.success("✨ AI has reframed your experience description!")
                st.rerun()
            else:
                st.warning("AI couldn't improve the description significantly.")
    else:
        st.error("AI service not available. Please check your Groq API key.")

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

def update_project(project_id: int, project_data: Dict[str, Any]) -> bool:
    """Update project in database"""
    try:
        session = next(get_db_session())
        ProjectQueries.update_project(session, project_id, project_data)
        return True
    except Exception as e:
        st.error(f"Error updating project: {e}")
        return False

def clear_new_project_form():
    """Clear new project form session state"""
    form_keys = [
        'new_project_title', 'new_project_description', 'new_project_technologies',
        'new_project_start', 'new_project_end', 'new_project_url'
    ]
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_edit_project_session_state():
    """Clear edit project session state"""
    edit_keys = [
        'edit_project_title', 'edit_project_description', 'edit_project_technologies',
        'edit_project_start', 'edit_project_end', 'edit_project_url', 'edit_project_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_new_experience_form():
    """Clear new experience form session state"""
    form_keys = [
        'new_exp_company', 'new_exp_position', 'new_exp_description',
        'new_exp_start', 'new_exp_end'
    ]
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_edit_experience_session_state():
    """Clear edit experience session state"""
    edit_keys = [
        'edit_exp_company', 'edit_exp_position', 'edit_exp_description',
        'edit_exp_start', 'edit_exp_end', 'edit_exp_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def update_experience(experience_id: int, exp_data: Dict[str, Any]) -> bool:
    """Update experience in database"""
    try:
        session = next(get_db_session())
        ExperienceQueries.update_professional_experience(session, experience_id, exp_data)
        return True
    except Exception as e:
        st.error(f"Error updating experience: {e}")
        return False

# Additional data loading functions
def load_user_research_experience() -> list:
    """Load user research experience"""
    if not st.session_state.current_user_id:
        return []

    try:
        session = next(get_db_session())
        experiences = ExperienceQueries.get_research_experience(session, st.session_state.current_user_id)
        return [
            {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'start_date': e.start_date,
                'end_date': e.end_date
            } for e in experiences
        ]
    except Exception as e:
        st.error(f"Error loading research experience: {e}")
        return []

def load_user_education() -> list:
    """Load user education"""
    if not st.session_state.current_user_id:
        return []

    try:
        session = next(get_db_session())
        education = EducationQueries.get_user_education(session, st.session_state.current_user_id)
        return [
            {
                'id': e.id,
                'degree': e.degree,
                'institution': e.institution,
                'graduation_date': e.graduation_date,
                'gpa_percentage': e.gpa_percentage
            } for e in education
        ]
    except Exception as e:
        st.error(f"Error loading education: {e}")
        return []

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

def load_user_certifications() -> list:
    """Load user certifications"""
    if not st.session_state.current_user_id:
        return []

    try:
        session = next(get_db_session())
        certifications = CertificationQueries.get_user_certifications(session, st.session_state.current_user_id)
        return [
            {
                'id': c.id,
                'title': c.title,
                'issuer': c.issuer,
                'date_obtained': c.date_obtained
            } for c in certifications
        ]
    except Exception as e:
        st.error(f"Error loading certifications: {e}")
        return []

# Additional update and delete functions
def update_research_experience(research_id: int, research_data: Dict[str, Any]) -> bool:
    """Update research experience in database"""
    try:
        session = next(get_db_session())
        ExperienceQueries.update_research_experience(session, research_id, research_data)
        return True
    except Exception as e:
        st.error(f"Error updating research experience: {e}")
        return False

def delete_research_experience(research_id: int) -> bool:
    """Delete research experience"""
    try:
        session = next(get_db_session())
        ExperienceQueries.delete_research_experience(session, research_id)
        return True
    except Exception as e:
        st.error(f"Error deleting research experience: {e}")
        return False

def update_education(education_id: int, education_data: Dict[str, Any]) -> bool:
    """Update education in database"""
    try:
        session = next(get_db_session())
        EducationQueries.update_education(session, education_id, education_data)
        return True
    except Exception as e:
        st.error(f"Error updating education: {e}")
        return False

def delete_education(education_id: int) -> bool:
    """Delete education"""
    try:
        session = next(get_db_session())
        EducationQueries.delete_education(session, education_id)
        return True
    except Exception as e:
        st.error(f"Error deleting education: {e}")
        return False

def update_technical_skills(skills_id: int, skills_data: Dict[str, Any]) -> bool:
    """Update technical skills in database"""
    try:
        session = next(get_db_session())
        SkillsQueries.update_technical_skill(session, skills_id, skills_data)
        return True
    except Exception as e:
        st.error(f"Error updating skills: {e}")
        return False

def delete_technical_skills(skills_id: int) -> bool:
    """Delete technical skills"""
    try:
        session = next(get_db_session())
        SkillsQueries.delete_technical_skill(session, skills_id)
        return True
    except Exception as e:
        st.error(f"Error deleting skills: {e}")
        return False

def update_certification(cert_id: int, cert_data: Dict[str, Any]) -> bool:
    """Update certification in database"""
    try:
        session = next(get_db_session())
        CertificationQueries.update_certification(session, cert_id, cert_data)
        return True
    except Exception as e:
        st.error(f"Error updating certification: {e}")
        return False

def delete_certification(cert_id: int) -> bool:
    """Delete certification"""
    try:
        session = next(get_db_session())
        CertificationQueries.delete_certification(session, cert_id)
        return True
    except Exception as e:
        st.error(f"Error deleting certification: {e}")
        return False

# Additional session state clearing functions
def clear_edit_research_session_state():
    """Clear edit research session state"""
    edit_keys = [
        'edit_research_title', 'edit_research_description',
        'edit_research_start', 'edit_research_end', 'edit_research_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_edit_education_session_state():
    """Clear edit education session state"""
    edit_keys = [
        'edit_edu_degree', 'edit_edu_institution',
        'edit_edu_grad_date', 'edit_edu_gpa', 'edit_edu_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_edit_skills_session_state():
    """Clear edit skills session state"""
    edit_keys = [
        'edit_skill_category', 'edit_skill_skills', 'edit_skill_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_edit_certification_session_state():
    """Clear edit certification session state"""
    edit_keys = [
        'edit_cert_title', 'edit_cert_issuer', 'edit_cert_date', 'edit_cert_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

# Academic Collaboration Helper Functions
def load_user_academic_collaborations() -> list:
    """Load user academic collaborations"""
    if not st.session_state.current_user_id:
        return []

    try:
        session = next(get_db_session())
        collaborations = AcademicCollaborationQueries.get_user_academic_collaborations(session, st.session_state.current_user_id)
        return [
            {
                'id': c.id,
                'project_title': c.project_title,
                'collaboration_type': c.collaboration_type,
                'institution': c.institution,
                'collaborators': c.collaborators,
                'role': c.role,
                'description': c.description,
                'start_date': c.start_date,
                'end_date': c.end_date,
                'publication_url': c.publication_url
            } for c in collaborations
        ]
    except Exception as e:
        st.error(f"Error loading academic collaborations: {e}")
        return []

def add_academic_collaboration(collab_data: Dict[str, Any]) -> bool:
    """Add academic collaboration"""
    try:
        session = next(get_db_session())
        AcademicCollaborationQueries.create_academic_collaboration(session, st.session_state.current_user_id, collab_data)
        return True
    except Exception as e:
        st.error(f"Error adding academic collaboration: {e}")
        return False

def update_academic_collaboration(collab_id: int, collab_data: Dict[str, Any]) -> bool:
    """Update academic collaboration in database"""
    try:
        session = next(get_db_session())
        AcademicCollaborationQueries.update_academic_collaboration(session, collab_id, collab_data)
        return True
    except Exception as e:
        st.error(f"Error updating academic collaboration: {e}")
        return False

def delete_academic_collaboration(collab_id: int) -> bool:
    """Delete academic collaboration"""
    try:
        session = next(get_db_session())
        AcademicCollaborationQueries.delete_academic_collaboration(session, collab_id)
        return True
    except Exception as e:
        st.error(f"Error deleting academic collaboration: {e}")
        return False

def clear_edit_collaboration_session_state():
    """Clear edit academic collaboration session state"""
    edit_keys = [
        'edit_collab_title', 'edit_collab_type', 'edit_collab_institution',
        'edit_collab_collaborators', 'edit_collab_role', 'edit_collab_description',
        'edit_collab_start', 'edit_collab_end', 'edit_collab_url', 'edit_collab_id'
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]