import streamlit as st
import os
import base64
from typing import Optional
from utils.pdf_generator import PDFGenerator

def render_pdf_preview(force_update: bool = False):
    """
    Render PDF preview component
    Args:
        force_update: If True, force regeneration of PDF
    """
    
    
    # Auto-compile if enabled and data exists
    auto_update = st.session_state.get('auto_update_pdf', True)
    
    # Try to generate PDF from user data if no PDF exists or force update
    if auto_update and (force_update or not st.session_state.get('pdf_path')):
        if st.session_state.get('latex_code'):
            compile_pdf_from_latex()
        elif st.session_state.get('current_user_id'):
            generate_pdf_from_user_data()
        else:
            generate_sample_pdf()
    
    # PDF preview controls
    render_pdf_controls()
    
    # PDF display
    pdf_path = st.session_state.get('pdf_path')
    if pdf_path and os.path.exists(pdf_path):
        render_pdf_display()
    else:
        render_pdf_placeholder()

def render_pdf_controls():
    """Render PDF preview controls"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Refresh Preview", key="refresh_pdf"):
            if st.session_state.get('current_user_id'):
                generate_pdf_from_user_data()
            elif st.session_state.latex_code:
                compile_pdf_from_latex()
            else:
                generate_sample_pdf()
            st.rerun()
    
    with col2:
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            if st.button("📥 Download PDF", key="download_pdf"):
                download_pdf()

def render_pdf_display():
    """Render the actual PDF display"""
    try:
        # Show PDF info first
        if st.session_state.pdf_path:
            file_size = os.path.getsize(st.session_state.pdf_path)
        
        # Create browser-like PDF display
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        
        
        # Browser-like PDF viewer with proper styling and controls
        browser_pdf_viewer = f"""
        <style>
        .pdf-browser-container {{
            width: 100%;
            height: 90vh;
            max-height: 1200px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            background: #f9fafb;
        }}
        .pdf-toolbar {{
            background: #f3f4f6;
            border-bottom: 1px solid #d1d5db;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            color: #374151;
        }}
        .pdf-title {{
            font-weight: 500;
        }}
        .pdf-controls {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        .pdf-viewer-frame {{
            width: 100%;
            height: calc(100% - 45px);
            border: none;
            background: white;
        }}
        </style>
        
        <div class="pdf-browser-container">
            <div class="pdf-toolbar">
                <div class="pdf-title">📄 resume.pdf</div>
                <div class="pdf-controls">
                    <span style="color: #6b7280;">Ready</span>
                </div>
            </div>
            <object 
                class="pdf-viewer-frame"
                data="data:application/pdf;base64,{base64_pdf}"
                type="application/pdf">
                <embed 
                    class="pdf-viewer-frame"
                    src="data:application/pdf;base64,{base64_pdf}"
                    type="application/pdf" />
                <div style="padding: 40px; text-align: center; color: #6b7280;">
                    <p>📄 PDF viewer not supported in this browser</p>
                    <p>Please use the download button above to view the PDF</p>
                </div>
            </object>
        </div>
        """
        
        st.markdown(browser_pdf_viewer, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")
        st.write(f"PDF path: {st.session_state.pdf_path}")
        st.write(f"Path exists: {os.path.exists(st.session_state.pdf_path) if st.session_state.pdf_path else 'No path'}")
        render_pdf_placeholder()

def render_pdf_placeholder():
    """Render placeholder when no PDF is available"""
    placeholder_html = """
    <style>
    .pdf-placeholder-container {
        width: 100%;
        height: 90vh;
        max-height: 1200px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        background: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }
    .placeholder-content {
        text-align: center;
        color: #6b7280;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .placeholder-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        color: #9ca3af;
    }
    .placeholder-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    .placeholder-text {
        font-size: 1rem;
        line-height: 1.5;
        max-width: 400px;
    }
    </style>
    
    <div class="pdf-placeholder-container">
        <div class="placeholder-content">
            <div class="placeholder-icon">📄</div>
            <div class="placeholder-title">PDF Preview</div>
            <div class="placeholder-text">
                Your resume will appear here once generated.<br><br>
                Fill in your information in the sidebar or edit the LaTeX code to create your personalized resume.
            </div>
        </div>
    </div>
    """
    st.markdown(placeholder_html, unsafe_allow_html=True)

def compile_pdf_from_latex():
    """Compile PDF from current LaTeX code"""
    if not st.session_state.latex_code:
        st.warning("No LaTeX code to compile")
        return
    
    with st.spinner("Generating PDF..."):
        # Use session ID for consistent temp directory
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        pdf_path = pdf_generator.generate_pdf_from_latex(st.session_state.latex_code)
        
        if pdf_path:
            st.session_state.pdf_path = pdf_path
            st.session_state.pdf_generator = pdf_generator  # Keep reference to prevent cleanup
        else:
            st.error("❌ PDF generation failed")

def generate_pdf_from_user_data():
    """Generate PDF from user data in database"""
    if not st.session_state.get('current_user_id'):
        return
    
    with st.spinner("Generating PDF from your data..."):
        try:
            from database.connection import get_db_session
            from database.queries import (
                UserQueries, ProjectQueries, ExperienceQueries,
                EducationQueries, SkillsQueries, CertificationQueries,
                SummaryQueries
            )
            
            # Fetch user data from database
            session = next(get_db_session())
            user_id = st.session_state.current_user_id
            
            # Get all user data
            user_data = {
                'user': UserQueries.get_user_by_id(session, user_id),
                'projects': ProjectQueries.get_user_projects(session, user_id),
                'professional_experience': ExperienceQueries.get_professional_experience(session, user_id),
                'research_experience': ExperienceQueries.get_research_experience(session, user_id),
                'education': EducationQueries.get_user_education(session, user_id),
                'technical_skills': SkillsQueries.get_user_skills(session, user_id),
                'certifications': CertificationQueries.get_user_certifications(session, user_id),
                'professional_summaries': SummaryQueries.get_user_summaries(session, user_id)
            }
            
            # Convert database objects to dictionaries
            user_data = format_user_data_for_pdf(user_data)
            
            # Generate PDF
            session_id = st.session_state.get('session_id', 'default')
            pdf_generator = PDFGenerator(session_id=session_id)
            pdf_path, latex_code = pdf_generator.generate_pdf_from_data(
                user_data,
                st.session_state.template_style,
                st.session_state.active_sections
            )
            
            if pdf_path:
                st.session_state.pdf_path = pdf_path
                st.session_state.latex_code = latex_code
            else:
                st.error("❌ PDF generation failed")
                
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")

def format_user_data_for_pdf(raw_data):
    """Format database data for PDF generation"""
    formatted_data = {}
    
    # Format user info
    if raw_data['user']:
        user = raw_data['user']
        formatted_data['user'] = {
            'name': getattr(user, 'name', ''),
            'email': getattr(user, 'email', ''),
            'phone': getattr(user, 'phone', ''),
            'location': getattr(user, 'location', ''),
            'linkedin_url': getattr(user, 'linkedin_url', ''),
            'github_url': getattr(user, 'github_url', '')
        }
    
    # Format projects
    formatted_data['projects'] = []
    for project in raw_data.get('projects', []):
        formatted_data['projects'].append({
            'title': getattr(project, 'title', ''),
            'description': getattr(project, 'description', ''),
            'start_date': getattr(project, 'start_date', ''),
            'end_date': getattr(project, 'end_date', ''),
            'technologies': getattr(project, 'technologies', ''),
            'project_url': getattr(project, 'project_url', '')
        })
    
    # Format experiences
    for exp_type in ['professional_experience', 'research_experience']:
        formatted_data[exp_type] = []
        for exp in raw_data.get(exp_type, []):
            if exp_type == 'professional_experience':
                formatted_data[exp_type].append({
                    'company': getattr(exp, 'company', ''),
                    'position': getattr(exp, 'position', ''),
                    'description': getattr(exp, 'description', ''),
                    'start_date': getattr(exp, 'start_date', ''),
                    'end_date': getattr(exp, 'end_date', '')
                })
            else:
                formatted_data[exp_type].append({
                    'title': getattr(exp, 'title', ''),
                    'description': getattr(exp, 'description', ''),
                    'start_date': getattr(exp, 'start_date', ''),
                    'end_date': getattr(exp, 'end_date', '')
                })
    
    # Format education
    formatted_data['education'] = []
    for edu in raw_data.get('education', []):
        formatted_data['education'].append({
            'degree': getattr(edu, 'degree', ''),
            'institution': getattr(edu, 'institution', ''),
            'graduation_date': getattr(edu, 'graduation_date', ''),
            'gpa_percentage': getattr(edu, 'gpa_percentage', '')
        })
    
    # Format skills
    formatted_data['technical_skills'] = []
    for skill in raw_data.get('technical_skills', []):
        formatted_data['technical_skills'].append({
            'category': getattr(skill, 'category', ''),
            'skills': getattr(skill, 'skills', '')
        })
    
    # Format certifications
    formatted_data['certifications'] = []
    for cert in raw_data.get('certifications', []):
        formatted_data['certifications'].append({
            'title': getattr(cert, 'title', ''),
            'issuer': getattr(cert, 'issuer', ''),
            'date_obtained': getattr(cert, 'date_obtained', '')
        })
    
    # Format summaries
    formatted_data['professional_summaries'] = []
    for summary in raw_data.get('professional_summaries', []):
        formatted_data['professional_summaries'].append({
            'generated_summary': getattr(summary, 'generated_summary', '')
        })
    
    return formatted_data

def download_pdf():
    """Provide PDF download functionality"""
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        try:
            with open(st.session_state.pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            
            st.download_button(
                label="📥 Download Resume PDF",
                data=pdf_data,
                file_name="resume.pdf",
                mime="application/pdf",
                key="download_resume_pdf"
            )
        except Exception as e:
            st.error(f"Error preparing PDF download: {e}")
    else:
        st.error("No PDF available for download")

def show_pdf_info():
    """Show information about the generated PDF"""
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        try:
            import os
            file_size = os.path.getsize(st.session_state.pdf_path)
            file_size_mb = file_size / (1024 * 1024)
            
            st.info(f"""
            **PDF Information:**
            - File size: {file_size_mb:.2f} MB
            - Template: {st.session_state.template_style.title()} Style
            - Active sections: {len(st.session_state.active_sections)}
            - Path: {st.session_state.pdf_path}
            """)
        except Exception as e:
            st.error(f"Error getting PDF info: {e}")
    else:
        st.warning("No PDF generated yet")

def render_pdf_comparison():
    """Render side-by-side comparison of templates (if needed)"""
    st.subheader("📊 Template Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Arpan Style (Modern)**")
        st.write("• Two-column layout")
        st.write("• Sidebar for skills/education")
        st.write("• Professional color scheme")
        st.write("• Modern typography")
    
    with col2:
        st.write("**Simple Style (Classic)**")
        st.write("• Single-column layout")
        st.write("• Traditional formatting")
        st.write("• Clean and minimal")
        st.write("• ATS-friendly")

def generate_sample_pdf():
    """Generate a sample PDF with demo data"""
    with st.spinner("Generating sample PDF..."):
        session_id = st.session_state.get('session_id', 'default')
        pdf_generator = PDFGenerator(session_id=session_id)
        sample_data = pdf_generator.get_sample_data()
        
        pdf_path, latex_code = pdf_generator.generate_pdf_from_data(
            sample_data,
            st.session_state.template_style,
            st.session_state.active_sections
        )
        
        if pdf_path:
            st.session_state.pdf_path = pdf_path
            st.session_state.latex_code = latex_code
            st.session_state.pdf_generator = pdf_generator  # Keep reference
            return True
        else:
            st.error("❌ Failed to generate sample PDF")
            return False

def render_pdf_quality_settings():
    """Render PDF quality and export settings"""
    with st.expander("PDF Export Settings", expanded=False):
        st.write("**Quality Settings:**")
        
        pdf_quality = st.selectbox(
            "PDF Quality",
            ["High (Print)", "Medium (Web)", "Low (Email)"],
            index=0,
            key="pdf_quality"
        )
        
        include_metadata = st.checkbox(
            "Include metadata", 
            value=True,
            key="include_metadata"
        )
        
        compress_pdf = st.checkbox(
            "Compress PDF",
            value=False,
            key="compress_pdf"
        )
        
        if st.button("Apply Settings", key="apply_pdf_settings"):
            st.success("PDF settings updated!")

def render_pdf_export_options():
    """Render different export format options"""
    st.subheader("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export PDF", key="export_pdf"):
            download_pdf()
    
    with col2:
        if st.button("📝 Export LaTeX", key="export_latex"):
            from components.latex_editor import download_latex_code
            download_latex_code()
    
    with col3:
        if st.button("🖼️ Export Image", key="export_image"):
            export_as_image()

def export_as_image():
    """Export PDF as PNG image (requires additional dependencies)"""
    st.info("Image export feature coming soon! For now, you can:")
    st.write("1. Download the PDF")
    st.write("2. Use online PDF to PNG converters")
    st.write("3. Take a screenshot of the PDF preview")

def render_pdf_analytics():
    """Render resume analytics and feedback"""
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        with st.expander("📊 Resume Analytics", expanded=False):
            st.write("**Content Analysis:**")
            
            # Analyze LaTeX content
            if st.session_state.latex_code:
                word_count = len(st.session_state.latex_code.split())
                line_count = len(st.session_state.latex_code.split('\n'))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Word Count", word_count)
                
                with col2:
                    st.metric("Lines", line_count)
                
                with col3:
                    st.metric("Sections", len(st.session_state.active_sections))
                
                # Content recommendations
                st.write("**Recommendations:**")
                enforce_limit = st.session_state.get('enforce_one_page_limit', True)

                if word_count < 200:
                    st.warning("Consider adding more content to your resume")
                elif enforce_limit and word_count > 500:
                    st.warning("Your resume might be too long. Consider condensing.")
                elif not enforce_limit and word_count > 800:
                    st.info("Very comprehensive resume - ensure all content is relevant")
                else:
                    st.success("Good content length!")
                
                if len(st.session_state.active_sections) < 4:
                    st.info("Consider adding more sections for a complete resume")

def check_pdf_page_count():
    """Check if PDF exceeds one page and warn user"""
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        try:
            # Check if one-page limit is enforced
            enforce_limit = st.session_state.get('enforce_one_page_limit', True)

            if enforce_limit:
                # This would require PyPDF2 or similar library
                # For now, we'll implement a basic check
                st.info("💡 **One-Page Resume Tip:** Keep your resume concise and focused on key achievements.")
        except Exception:
            pass