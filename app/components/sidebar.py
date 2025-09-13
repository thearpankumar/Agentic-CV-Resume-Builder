import streamlit as st
from typing import Dict, Any, Optional
from database.connection import get_db_session
from database.queries import (
    UserQueries, ProjectQueries, ExperienceQueries, 
    EducationQueries, SkillsQueries, CertificationQueries
)
from utils.validators import DataValidator
from ai_integration.groq_client import GroqClient

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
    st.subheader("👤 User Profile")
    data_changed |= render_user_section()
    
    # Only show other sections if user is selected/created
    if st.session_state.current_user_id:
        st.markdown("---")
        st.subheader("💼 Projects")
        data_changed |= render_projects_section()
        
        st.markdown("---")
        st.subheader("🏢 Professional Experience")
        data_changed |= render_professional_experience_section()
        
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

def render_user_section() -> bool:
    """Render user profile section"""
    data_changed = False
    
    # User selection/creation
    with st.expander("Select or Create User", expanded=True):
        email = st.text_input("Email", key="user_email")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load User", disabled=not email):
                if DataValidator.validate_email(email):
                    user = load_user_by_email(email)
                    if user:
                        st.session_state.current_user_id = user.id
                        st.success(f"Loaded user: {user.name}")
                        data_changed = True
                    else:
                        st.error("User not found")
                else:
                    st.error("Invalid email format")
        
        with col2:
            if st.button("Create New User", disabled=not email):
                if DataValidator.validate_email(email):
                    data_changed |= create_new_user(email)
                else:
                    st.error("Invalid email format")
    
    # User data form (if user is selected)
    if st.session_state.current_user_id:
        data_changed |= render_user_form()
    
    return data_changed

def render_user_form() -> bool:
    """Render user information form"""
    data_changed = False
    
    # Load current user data
    user_data = load_current_user_data()
    
    with st.expander("Edit Profile Information", expanded=False):
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
                        if st.button("✅ Use This Version", key=f"accept_reframe_{i}"):
                            update_project_description(project['id'], st.session_state[f'reframed_project_{i}'])
                            del st.session_state[f'reframed_project_{i}']
                            st.success("Project updated!")
                            data_changed = True
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Keep Original", key=f"reject_reframe_{i}"):
                            del st.session_state[f'reframed_project_{i}']
                            st.rerun()
    
    # Add new project form
    with st.expander("Add New Project", expanded=False):
        data_changed |= render_add_project_form()
    
    return data_changed

def render_add_project_form() -> bool:
    """Render add project form"""
    title = st.text_input("Project Title", key="new_project_title")
    description = st.text_area("Description", key="new_project_description")
    technologies = st.text_input("Technologies (comma-separated)", key="new_project_technologies")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.text_input("Start Date (e.g., Jan 2024)", key="new_project_start")
    with col2:
        end_date = st.text_input("End Date (or 'Present')", key="new_project_end")
    
    project_url = st.text_input("Project URL (optional)", key="new_project_url")
    
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
                
                # Show reframed version if available
                if f'reframed_exp_{i}' in st.session_state:
                    st.markdown("**✨ AI Reframed Description:**")
                    st.info(st.session_state[f'reframed_exp_{i}'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Use This Version", key=f"accept_exp_reframe_{i}"):
                            update_experience_description(exp['id'], st.session_state[f'reframed_exp_{i}'])
                            del st.session_state[f'reframed_exp_{i}']
                            st.success("Experience updated!")
                            data_changed = True
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Keep Original", key=f"reject_exp_reframe_{i}"):
                            del st.session_state[f'reframed_exp_{i}']
                            st.rerun()
    
    # Add new experience form
    with st.expander("Add Professional Experience", expanded=False):
        data_changed |= render_add_professional_experience_form()
    
    return data_changed

def render_add_professional_experience_form() -> bool:
    """Render add professional experience form"""
    company = st.text_input("Company", key="new_exp_company")
    position = st.text_input("Position", key="new_exp_position")
    description = st.text_area("Description", key="new_exp_description")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.text_input("Start Date", key="new_exp_start")
    with col2:
        end_date = st.text_input("End Date (or 'Present')", key="new_exp_end")
    
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
    
    with st.expander("Add Research Experience", expanded=False):
        title = st.text_input("Research Title", key="new_research_title")
        description = st.text_area("Description", key="new_research_description")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.text_input("Start Date", key="new_research_start")
        with col2:
            end_date = st.text_input("End Date", key="new_research_end")
        
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
                    data_changed = True
                else:
                    st.error("Failed to add research experience")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_education_section() -> bool:
    """Render education section"""
    data_changed = False
    
    with st.expander("Add Education", expanded=False):
        degree = st.text_input("Degree", key="new_edu_degree")
        institution = st.text_input("Institution", key="new_edu_institution")
        graduation_date = st.text_input("Graduation Date", key="new_edu_grad_date")
        gpa_percentage = st.text_input("GPA/Percentage", key="new_edu_gpa")
        
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
                    data_changed = True
                else:
                    st.error("Failed to add education")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_skills_section() -> bool:
    """Render technical skills section"""
    data_changed = False
    
    with st.expander("Add Technical Skills", expanded=False):
        category = st.text_input("Skill Category (e.g., Programming Languages)", key="new_skill_category")
        skills = st.text_input("Skills (comma-separated)", key="new_skill_list")
        
        if st.button("Add Skills Category", key="add_skills"):
            skill_data = {
                'category': category,
                'skills': skills
            }
            
            is_valid, errors = DataValidator.validate_skill_data(skill_data)
            if is_valid:
                if add_technical_skills(skill_data):
                    st.success("Skills added successfully!")
                    data_changed = True
                else:
                    st.error("Failed to add skills")
            else:
                for error in errors:
                    st.error(error)
    
    return data_changed

def render_certifications_section() -> bool:
    """Render certifications section"""
    data_changed = False
    
    with st.expander("Add Certification", expanded=False):
        title = st.text_input("Certification Title", key="new_cert_title")
        issuer = st.text_input("Issuer", key="new_cert_issuer")
        date_obtained = st.text_input("Date Obtained", key="new_cert_date")
        
        if st.button("Add Certification", key="add_certification"):
            cert_data = {
                'title': title,
                'issuer': issuer,
                'date_obtained': date_obtained
            }
            
            if title:  # Only title is required
                if add_certification(cert_data):
                    st.success("Certification added successfully!")
                    data_changed = True
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
        with st.spinner("🤖 AI is reframing your project description..."):
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
        with st.spinner("🤖 AI is reframing your experience description..."):
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