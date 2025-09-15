import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import streamlit as st
from latex_templates.base_template import BaseTemplate
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

# Alternative PDF generation imports
try:
    from weasyprint import HTML, CSS
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    ALTERNATIVE_PDF_AVAILABLE = True
except ImportError:
    ALTERNATIVE_PDF_AVAILABLE = False

class PDFGenerator:
    """Handles LaTeX to PDF conversion"""
    
    def __init__(self, session_id: str = None):
        # Use configured temp directory or fallback to system temp
        if settings.pdf_temp_dir:
            temp_base = settings.pdf_temp_dir
            os.makedirs(temp_base, exist_ok=True)
        elif session_id:
            temp_base = tempfile.gettempdir()
        else:
            temp_base = tempfile.gettempdir()

        if session_id:
            self.temp_dir = os.path.join(temp_base, f"cv_builder_{session_id}")
            os.makedirs(self.temp_dir, exist_ok=True)
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="cv_builder_")
        print(f"PDFGenerator using temp directory: {self.temp_dir}")
        self.ensure_latex_installed()
    
    def ensure_latex_installed(self) -> bool:
        """Check if LaTeX is installed and available"""
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=False,  # Handle as bytes to avoid UTF-8 decoding errors
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def generate_pdf_from_data(
        self,
        user_data: Dict[str, Any],
        template_style: str = "arpan",
        active_sections: List[str] = None,
        section_order: List[str] = None,
        font_size: str = "10pt"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate PDF from user data
        Returns: (pdf_path, latex_code) or (None, error_message)
        """
        # Try LaTeX first, fallback to alternative methods
        if self.ensure_latex_installed():
            try:
                # Create template instance with font size
                template = BaseTemplate(template_style, font_size)

                # Set defaults if not provided
                if active_sections is None:
                    active_sections = template.get_default_section_order()
                if section_order is None:
                    section_order = template.get_default_section_order()

                # Generate LaTeX code
                latex_code = template.generate_latex(user_data, active_sections, section_order)

                # Convert to PDF
                pdf_path = self.compile_latex_to_pdf(latex_code)

                if pdf_path:
                    return pdf_path, latex_code
                else:
                    return None, "PDF compilation failed"

            except Exception as e:
                return None, f"Error generating PDF: {str(e)}"

        # Fallback to alternative PDF generation
        if ALTERNATIVE_PDF_AVAILABLE:
            try:
                pdf_path = self.generate_pdf_with_reportlab(user_data, active_sections, section_order)
                if pdf_path:
                    return pdf_path, "Generated using ReportLab (LaTeX alternative)"
                else:
                    return None, "Alternative PDF generation failed"
            except Exception as e:
                return None, f"Error with alternative PDF generation: {str(e)}"

        return None, "No PDF generation methods available. Please install LaTeX or required Python packages."
    
    def generate_pdf_from_latex(self, latex_code: str) -> Optional[str]:
        """
        Generate PDF from LaTeX code
        Returns: pdf_path or None if failed
        """
        if not self.ensure_latex_installed():
            try:
                st.error("LaTeX not installed. Please install texlive-full or similar package.")
            except:
                print("LaTeX not installed. Please install texlive-full or similar package.")
            return None
        
        return self.compile_latex_to_pdf(latex_code)
    
    def compile_latex_to_pdf(self, latex_code: str) -> Optional[str]:
        """
        Compile LaTeX code to PDF
        Returns: path to generated PDF or None if failed
        """
        try:
            # Use consistent filename instead of timestamp
            filename = "current_resume"
            
            # Write LaTeX to temp file
            tex_path = os.path.join(self.temp_dir, f"{filename}.tex")
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            # Debug: Check if tex file was written
            print(f"LaTeX file written to: {tex_path}")
            print(f"LaTeX file exists: {os.path.exists(tex_path)}")
            print(f"LaTeX file size: {os.path.getsize(tex_path) if os.path.exists(tex_path) else 'N/A'}")
            
            # Compile LaTeX to PDF
            result = subprocess.run(
                [
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', self.temp_dir,
                    tex_path
                ],
                capture_output=True,
                text=False,  # Handle as bytes to avoid UTF-8 decoding errors
                timeout=settings.latex_timeout,
                cwd=self.temp_dir
            )
            
            pdf_path = os.path.join(self.temp_dir, f"{filename}.pdf")
            
            # Debug: Check compilation results
            print(f"LaTeX compilation return code: {result.returncode}")
            print(f"Expected PDF path: {pdf_path}")
            print(f"PDF file exists after compilation: {os.path.exists(pdf_path)}")
            if os.path.exists(pdf_path):
                print(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
            
            # List all files in temp directory for debugging
            print(f"Files in temp directory: {os.listdir(self.temp_dir)}")
            
            # Check if PDF was created (sometimes LaTeX returns error code but still creates PDF)
            if os.path.exists(pdf_path):
                return pdf_path
            else:
                # Log compilation errors for debugging - safely decode bytes
                try:
                    stderr_text = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
                    stdout_text = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
                    error_log = stderr_text + stdout_text
                except Exception as decode_error:
                    error_log = f"Could not decode LaTeX output: {decode_error}"

                print(f"LaTeX compilation failed: {error_log[-1000:]}")  # Last 1000 chars
                try:
                    st.error(f"LaTeX compilation failed. Check the LaTeX syntax.")
                    with st.expander("Compilation Errors"):
                        st.code(error_log)
                except:
                    # If streamlit is not available, just print
                    print(f"LaTeX compilation failed: {error_log}")
                return None
                
        except subprocess.TimeoutExpired:
            try:
                st.error("LaTeX compilation timed out")
            except:
                print("LaTeX compilation timed out")
            return None
        except Exception as e:
            try:
                st.error(f"Error during PDF compilation: {str(e)}")
            except:
                print(f"Error during PDF compilation: {str(e)}")
            return None
    
    def get_latex_template(
        self,
        template_style: str = "arpan",
        active_sections: List[str] = None,
        section_order: List[str] = None,
        font_size: str = "10pt"
    ) -> str:
        """
        Get LaTeX template with sample data
        """
        # Sample data for template
        sample_data = self.get_sample_data()
        
        # Create template instance with font size
        template = BaseTemplate(template_style, font_size)
        
        # Set defaults if not provided
        if active_sections is None:
            active_sections = template.get_default_section_order()
        if section_order is None:
            section_order = template.get_default_section_order()
        
        return template.generate_latex(sample_data, active_sections, section_order)
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample data for template demonstration"""
        return {
            'user': {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1 (555) 123-4567',
                'location': 'San Francisco, CA',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'github_url': 'https://github.com/johndoe'
            },
            'professional_summaries': [
                {
                    'generated_summary': 'Experienced software engineer with expertise in full-stack development, machine learning, and cloud technologies. Passionate about building scalable solutions and leading technical teams.'
                }
            ],
            'projects': [
                {
                    'title': 'E-commerce Platform',
                    'description': 'Built a full-stack e-commerce platform with React frontend and Node.js backend. Implemented secure payment processing and real-time inventory management.',
                    'start_date': 'Jan 2024',
                    'end_date': 'Present',
                    'technologies': 'React, Node.js, PostgreSQL, AWS'
                },
                {
                    'title': 'ML Recommendation Engine',
                    'description': 'Developed machine learning recommendation system using collaborative filtering and content-based algorithms. Improved user engagement by 40%.',
                    'start_date': 'Sep 2023',
                    'end_date': 'Dec 2023',
                    'technologies': 'Python, TensorFlow, Redis, Docker'
                }
            ],
            'professional_experience': [
                {
                    'company': 'Tech Solutions Inc.',
                    'position': 'Senior Software Engineer',
                    'description': 'Led development of microservices architecture. Mentored junior developers and improved code quality through comprehensive testing.',
                    'start_date': 'Jun 2022',
                    'end_date': 'Present'
                }
            ],
            'research_experience': [
                {
                    'title': 'Natural Language Processing Research',
                    'description': 'Researched advanced NLP techniques for sentiment analysis. Published findings in peer-reviewed conference.',
                    'start_date': 'Jan 2022',
                    'end_date': 'May 2022'
                }
            ],
            'education': [
                {
                    'degree': 'Master of Science in Computer Science',
                    'institution': 'Stanford University',
                    'graduation_date': 'May 2022',
                    'gpa_percentage': '3.8/4.0'
                }
            ],
            'technical_skills': [
                {
                    'category': 'Programming Languages',
                    'skills': 'Python, JavaScript, Java, C++, Go'
                },
                {
                    'category': 'Frameworks & Libraries',
                    'skills': 'React, Node.js, Django, TensorFlow, PyTorch'
                },
                {
                    'category': 'Cloud & DevOps',
                    'skills': 'AWS, Docker, Kubernetes, CI/CD, Terraform'
                }
            ],
            'certifications': [
                {
                    'title': 'AWS Solutions Architect',
                    'issuer': 'Amazon Web Services',
                    'date_obtained': 'Dec 2023'
                }
            ]
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
    
    def _map_section_names(self, sections: List[str]) -> List[str]:
        """Map section names from UI to data structure names"""
        section_mapping = {
            'professional_summary': 'professional_summaries',
            'professional_summaries': 'professional_summaries',
            'projects': 'projects',
            'professional_experience': 'professional_experience',
            'research_experience': 'research_experience',
            'education': 'education',
            'technical_skills': 'technical_skills',
            'certifications': 'certifications'
        }
        return [section_mapping.get(section, section) for section in sections]

    def generate_pdf_with_reportlab(
        self,
        user_data: Dict[str, Any],
        active_sections: List[str] = None,
        section_order: List[str] = None
    ) -> Optional[str]:
        """
        Generate PDF using ReportLab as fallback when LaTeX is not available
        """
        try:
            filename = "current_resume_reportlab.pdf"
            pdf_path = os.path.join(self.temp_dir, filename)

            # Create document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                alignment=1  # Center alignment
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6,
                textColor=colors.darkblue
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )

            story = []

            # Header section
            user = user_data.get('user', {})
            if user.get('name'):
                story.append(Paragraph(user['name'], title_style))

            contact_info = []
            if user.get('email'):
                contact_info.append(user['email'])
            if user.get('phone'):
                contact_info.append(user['phone'])
            if user.get('location'):
                contact_info.append(user['location'])

            if contact_info:
                story.append(Paragraph(' | '.join(contact_info), normal_style))

            # Social links
            social_links = []
            if user.get('linkedin_url'):
                social_links.append(f"LinkedIn: {user['linkedin_url']}")
            if user.get('github_url'):
                social_links.append(f"GitHub: {user['github_url']}")

            if social_links:
                story.append(Paragraph(' | '.join(social_links), normal_style))

            story.append(Spacer(1, 12))

            # Handle different active_sections formats
            if isinstance(active_sections, dict):
                # Dictionary format: {section_name: True/False}
                # Map section names and filter active ones
                mapped_active = {}
                for section_key, is_active in active_sections.items():
                    mapped_key = self._map_section_names([section_key])[0]
                    mapped_active[mapped_key] = is_active
                active_section_list = [k for k, v in mapped_active.items() if v]
            elif isinstance(active_sections, list):
                # List format: [section_name1, section_name2, ...]
                active_section_list = self._map_section_names(active_sections)
            else:
                # Default to all sections
                active_section_list = ['professional_summaries', 'professional_experience', 'projects',
                                     'education', 'technical_skills', 'certifications', 'research_experience']

            # Define section order if not provided
            if not section_order:
                if isinstance(active_sections, dict):
                    # Use mapped active sections as order
                    section_order = active_section_list
                else:
                    section_order = ['professional_summaries', 'professional_experience', 'projects',
                                   'education', 'technical_skills', 'certifications', 'research_experience']
            else:
                section_order = self._map_section_names(section_order)

            # Process each section - strictly follow active sections
            for section in section_order:
                # Skip section if it's not in active_section_list
                if section not in active_section_list:
                    continue

                if section == 'professional_summaries' and user_data.get('professional_summaries'):
                    story.append(Paragraph("Professional Summary", heading_style))
                    for summary in user_data['professional_summaries']:
                        if summary.get('generated_summary'):
                            story.append(Paragraph(summary['generated_summary'], normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'professional_experience' and user_data.get('professional_experience'):
                    story.append(Paragraph("Professional Experience", heading_style))
                    for exp in user_data['professional_experience']:
                        title = f"<b>{exp.get('position', '')}</b> - {exp.get('company', '')}"
                        if exp.get('start_date') or exp.get('end_date'):
                            title += f" ({exp.get('start_date', '')} - {exp.get('end_date', '')})"
                        story.append(Paragraph(title, normal_style))
                        if exp.get('description'):
                            story.append(Paragraph(exp['description'], normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'projects' and user_data.get('projects'):
                    story.append(Paragraph("Projects", heading_style))
                    for project in user_data['projects']:
                        title = f"<b>{project.get('title', '')}</b>"
                        if project.get('start_date') or project.get('end_date'):
                            title += f" ({project.get('start_date', '')} - {project.get('end_date', '')})"
                        story.append(Paragraph(title, normal_style))
                        if project.get('description'):
                            story.append(Paragraph(project['description'], normal_style))
                        if project.get('technologies'):
                            story.append(Paragraph(f"<i>Technologies: {project['technologies']}</i>", normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'education' and user_data.get('education'):
                    story.append(Paragraph("Education", heading_style))
                    for edu in user_data['education']:
                        title = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}"
                        if edu.get('graduation_date'):
                            title += f" ({edu['graduation_date']})"
                        story.append(Paragraph(title, normal_style))
                        if edu.get('gpa_percentage'):
                            story.append(Paragraph(f"GPA: {edu['gpa_percentage']}", normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'technical_skills' and user_data.get('technical_skills'):
                    story.append(Paragraph("Technical Skills", heading_style))
                    for skill in user_data['technical_skills']:
                        if skill.get('category') and skill.get('skills'):
                            story.append(Paragraph(f"<b>{skill['category']}:</b> {skill['skills']}", normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'certifications' and user_data.get('certifications'):
                    story.append(Paragraph("Certifications", heading_style))
                    for cert in user_data['certifications']:
                        title = f"<b>{cert.get('title', '')}</b>"
                        if cert.get('issuer'):
                            title += f" - {cert['issuer']}"
                        if cert.get('date_obtained'):
                            title += f" ({cert['date_obtained']})"
                        story.append(Paragraph(title, normal_style))
                    story.append(Spacer(1, 6))

                elif section == 'research_experience' and user_data.get('research_experience'):
                    story.append(Paragraph("Research Experience", heading_style))
                    for research in user_data['research_experience']:
                        title = f"<b>{research.get('title', '')}</b>"
                        if research.get('start_date') or research.get('end_date'):
                            title += f" ({research.get('start_date', '')} - {research.get('end_date', '')})"
                        story.append(Paragraph(title, normal_style))
                        if research.get('description'):
                            story.append(Paragraph(research['description'], normal_style))
                    story.append(Spacer(1, 6))

            # Build PDF
            doc.build(story)

            if os.path.exists(pdf_path):
                print(f"ReportLab PDF generated successfully: {pdf_path}")
                return pdf_path
            else:
                print("ReportLab PDF generation failed")
                return None

        except Exception as e:
            print(f"Error in ReportLab PDF generation: {str(e)}")
            return None

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()