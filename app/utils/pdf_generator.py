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
                text=True, 
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
        if not self.ensure_latex_installed():
            return None, "LaTeX not installed. Please install texlive-full or similar package."
        
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
                text=True,
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
                # Log compilation errors for debugging
                error_log = result.stderr + result.stdout
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
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()