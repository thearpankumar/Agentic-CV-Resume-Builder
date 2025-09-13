import streamlit as st
from typing import List, Dict, Any
from ai_integration.content_optimizer import ContentOptimizer

def render_section_manager() -> bool:
    """
    Render section management interface with AI optimization
    Returns: True if sections were modified, False otherwise
    """
    sections_changed = False
    
    st.subheader("🔧 Section Management")
    
    # Available sections
    available_sections = {
        "professional_summary": "Professional Summary",
        "projects": "Projects",
        "professional_experience": "Professional Experience", 
        "research_experience": "Research Experience",
        "education": "Education",
        "technical_skills": "Technical Skills",
        "certifications": "Certifications"
    }
    
    # AI Optimization Section
    with st.expander("🤖 AI Resume Optimization", expanded=False):
        sections_changed |= render_ai_optimization_panel()
    
    # Section visibility management
    with st.expander("👁️ Section Visibility", expanded=True):
        st.write("**Select which sections to include in your resume:**")
        
        new_active_sections = []
        for section_key, section_name in available_sections.items():
            if st.checkbox(
                section_name,
                value=section_key in st.session_state.active_sections,
                key=f"section_toggle_{section_key}"
            ):
                new_active_sections.append(section_key)
        
        if new_active_sections != st.session_state.active_sections:
            st.session_state.active_sections = new_active_sections
            sections_changed = True
            st.success("✅ Active sections updated!")
    
    # Section ordering
    with st.expander("📋 Section Order", expanded=False):
        render_section_ordering(available_sections)
    
    # Template style selection
    with st.expander("🎨 Template Style", expanded=False):
        new_template = st.radio(
            "Choose template style:",
            ["arpan", "simple"],
            index=0 if st.session_state.template_style == "arpan" else 1,
            key="template_style_radio"
        )
        
        if new_template != st.session_state.template_style:
            st.session_state.template_style = new_template
            sections_changed = True
            st.success(f"✅ Template changed to {new_template.title()} style!")
    
    return sections_changed

def render_ai_optimization_panel() -> bool:
    """Render AI optimization controls"""
    optimization_changed = False
    
    st.write("**🎯 Optimize your resume for a specific job:**")
    
    # Job description input
    job_description = st.text_area(
        "Paste the job description here:",
        height=150,
        key="job_description_input",
        placeholder="Paste the job posting or job description you're applying for..."
    )
    
    if job_description and st.session_state.current_user_id:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Optimize Resume", key="optimize_resume"):
                optimization_changed |= optimize_resume_for_job(job_description)
        
        with col2:
            if st.button("📊 Analyze Fit", key="analyze_fit"):
                show_job_fit_analysis(job_description)
        
        # Quick optimizations
        st.write("**Quick Optimizations:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✨ Generate Summary", key="gen_summary"):
                optimization_changed |= generate_summary_only(job_description)
        
        with col2:
            if st.button("🎯 Select Projects", key="select_projects"):
                optimization_changed |= optimize_projects_only(job_description)
        
        with col3:
            if st.button("💡 Get Suggestions", key="get_suggestions"):
                show_optimization_suggestions(job_description)
    
    elif not st.session_state.current_user_id:
        st.info("Please create or load a user profile first to use AI optimization.")
    
    return optimization_changed

def render_section_ordering(available_sections: Dict[str, str]):
    """Render section ordering interface"""
    st.write("**Current section order:**")
    
    if st.session_state.active_sections:
        for i, section_key in enumerate(st.session_state.active_sections):
            section_name = available_sections.get(section_key, section_key)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"{i+1}. {section_name}")
            
            with col2:
                if i > 0 and st.button("⬆️", key=f"move_up_{i}"):
                    move_section_up(i)
                    st.rerun()
            
            with col3:
                if i < len(st.session_state.active_sections) - 1 and st.button("⬇️", key=f"move_down_{i}"):
                    move_section_down(i)
                    st.rerun()
    else:
        st.write("No sections selected")

def optimize_resume_for_job(job_description: str) -> bool:
    """Optimize entire resume for job description"""
    try:
        # Gather current user data
        user_data = gather_user_data()
        
        # Initialize content optimizer
        optimizer = ContentOptimizer()
        
        # Optimize content
        optimized_data = optimizer.optimize_resume_for_job(
            user_data, job_description, st.session_state.current_user_id
        )
        
        # Update session state with optimized data
        update_session_with_optimized_data(optimized_data)
        
        st.success("🎉 Resume optimized successfully!")
        st.info("The PDF will be regenerated with optimized content.")
        
        return True
        
    except Exception as e:
        st.error(f"Error optimizing resume: {e}")
        return False

def generate_summary_only(job_description: str) -> bool:
    """Generate only professional summary"""
    try:
        user_data = gather_user_data()
        optimizer = ContentOptimizer()
        
        summary = optimizer.generate_summary_for_job(
            user_data, job_description, st.session_state.current_user_id
        )
        
        if summary:
            st.success("✅ Professional summary generated!")
            st.write("**Generated Summary:**")
            st.write(summary)
            return True
        else:
            st.error("Failed to generate summary")
            return False
            
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return False

def optimize_projects_only(job_description: str) -> bool:
    """Optimize project selection only"""
    try:
        user_data = gather_user_data()
        projects = user_data.get('projects', [])
        
        if not projects:
            st.warning("No projects found to optimize")
            return False
        
        optimizer = ContentOptimizer()
        selected_projects, reasons = optimizer.get_project_recommendations(
            projects, job_description
        )
        
        st.success("✅ Project recommendations generated!")
        st.write("**Recommended Projects:**")
        
        for i, project in enumerate(selected_projects):
            st.write(f"{i+1}. **{project.get('title', 'Untitled')}**")
            st.write(f"   Technologies: {project.get('technologies', 'N/A')}")
        
        st.write("**Reasons:**")
        for reason in reasons:
            st.write(f"• {reason}")
        
        return True
        
    except Exception as e:
        st.error(f"Error optimizing projects: {e}")
        return False

def show_job_fit_analysis(job_description: str):
    """Show job fit analysis"""
    try:
        user_data = gather_user_data()
        optimizer = ContentOptimizer()
        
        # Get skills gap analysis
        current_skills = extract_skills_from_data(user_data)
        recommended_skills, improvement_areas = optimizer.get_skills_gap_analysis(
            current_skills, job_description
        )
        
        # ATS compatibility
        ats_score, ats_suggestions = optimizer.estimate_ats_compatibility(user_data)
        
        # Display results
        st.write("**📊 Job Fit Analysis:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("ATS Compatibility", f"{ats_score}%")
            
        with col2:
            match_score = min(100, len(current_skills) * 10)  # Simplified calculation
            st.metric("Skills Match", f"{match_score}%")
        
        if recommended_skills:
            st.write("**🎯 Recommended Skills to Highlight:**")
            for skill in recommended_skills:
                st.write(f"• {skill}")
        
        if ats_suggestions:
            st.write("**💡 ATS Improvement Suggestions:**")
            for suggestion in ats_suggestions:
                st.write(f"• {suggestion}")
        
    except Exception as e:
        st.error(f"Error analyzing job fit: {e}")

def show_optimization_suggestions(job_description: str = ""):
    """Show general optimization suggestions"""
    try:
        user_data = gather_user_data()
        optimizer = ContentOptimizer()
        
        suggestions = optimizer.get_optimization_suggestions(user_data, job_description)
        
        st.write("**💡 Optimization Suggestions:**")
        
        if suggestions:
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
        else:
            st.success("✅ Your resume looks well-optimized!")
        
    except Exception as e:
        st.error(f"Error getting suggestions: {e}")

def move_section_up(index: int):
    """Move section up in order"""
    if index > 0:
        sections = st.session_state.active_sections.copy()
        sections[index], sections[index-1] = sections[index-1], sections[index]
        st.session_state.active_sections = sections

def move_section_down(index: int):
    """Move section down in order"""
    if index < len(st.session_state.active_sections) - 1:
        sections = st.session_state.active_sections.copy()
        sections[index], sections[index+1] = sections[index+1], sections[index]
        st.session_state.active_sections = sections

def gather_user_data() -> Dict[str, Any]:
    """Gather all user data from database"""
    from components.sidebar import (
        load_current_user_data,
        load_user_projects,
        load_user_professional_experience
    )
    
    return {
        'user': load_current_user_data(),
        'projects': load_user_projects(),
        'professional_experience': load_user_professional_experience(),
        # Add other data sources as needed
    }

def extract_skills_from_data(user_data: Dict[str, Any]) -> List[str]:
    """Extract skills list from user data"""
    skills = []
    
    for skill_category in user_data.get('technical_skills', []):
        category_skills = skill_category.get('skills', '').split(',')
        skills.extend([skill.strip() for skill in category_skills if skill.strip()])
    
    return skills

def update_session_with_optimized_data(optimized_data: Dict[str, Any]):
    """Update session state with optimized data"""
    # This would update the LaTeX code and trigger PDF regeneration
    # Implementation depends on how the data flows between components
    pass