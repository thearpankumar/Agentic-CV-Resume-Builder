from typing import Dict, Any, List

class EducationBlock:
    """Education section block"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate education LaTeX code"""
        education_data = user_data.get('education', [])
        
        if not education_data:
            education_data = self._get_default_education()
        
        if self.template_style == "arpan":
            return self._generate_arpan_education(education_data)
        else:
            return self._generate_simple_education(education_data)
    
    def _generate_arpan_education(self, education: List[Dict[str, Any]]) -> str:
        """Generate Arpan style education (sidebar format)"""
        edu_parts = []
        
        edu_parts.append("\\subsection*{Education}")
        
        for edu in education:
            degree = edu.get('degree', 'Degree')
            institution = edu.get('institution', 'Institution')
            graduation_date = edu.get('graduation_date', '')
            gpa_percentage = edu.get('gpa_percentage', '')
            
            edu_parts.append(f"\\textbf{{{self._escape_latex(degree)}}} \\\\")
            edu_parts.append(f"{self._escape_latex(institution)} \\\\")
            
            # Add graduation info
            grad_info = []
            if gpa_percentage:
                grad_info.append(f"{gpa_percentage}")
            if graduation_date:
                grad_info.append(graduation_date)
            
            if grad_info:
                edu_parts.append(f"\\textit{{{' | '.join(grad_info)}}}")
            
            edu_parts.append("\\vspace{10pt}")
            edu_parts.append("")
        
        return "\n".join(edu_parts)
    
    def _generate_simple_education(self, education: List[Dict[str, Any]]) -> str:
        """Generate simple style education"""
        edu_parts = []
        
        edu_parts.append("\\section{Education}")
        
        for edu in education:
            degree = edu.get('degree', 'Degree')
            institution = edu.get('institution', 'Institution')
            graduation_date = edu.get('graduation_date', '')
            gpa_percentage = edu.get('gpa_percentage', '')
            
            # Format header line
            header = f"\\textbf{{{self._escape_latex(degree)}}}"
            if graduation_date:
                header += f" \\hfill {graduation_date}"
            
            edu_parts.append(header)
            edu_parts.append(f"\\textit{{{self._escape_latex(institution)}}}")
            
            if gpa_percentage:
                edu_parts.append(f"GPA/Percentage: {gpa_percentage}")
            
            edu_parts.append("")
        
        return "\n".join(edu_parts)
    
    def _get_default_education(self) -> List[Dict[str, Any]]:
        """Get default education for demonstration"""
        return [
            {
                'degree': 'Bachelor of Technology in Computer Science',
                'institution': 'Your University',
                'graduation_date': 'Expected 2025',
                'gpa_percentage': '8.5/10'
            }
        ]
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # Basic LaTeX escaping - backslash must be first
        text = text.replace('\\', '\\textbackslash{}')
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('^', '\\textasciicircum{}')
        text = text.replace('_', '\\_')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('~', '\\textasciitilde{}')
        
        return text