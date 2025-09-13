from typing import Dict, Any, List

class SkillsBlock:
    """Technical skills section block"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate technical skills LaTeX code"""
        skills_data = user_data.get('technical_skills', [])
        
        if not skills_data:
            skills_data = self._get_default_skills()
        
        if self.template_style == "arpan":
            return self._generate_arpan_skills(skills_data)
        else:
            return self._generate_simple_skills(skills_data)
    
    def _generate_arpan_skills(self, skills: List[Dict[str, Any]]) -> str:
        """Generate Arpan style skills (sidebar format)"""
        skills_parts = []
        
        skills_parts.append("\\subsection*{Technical Skills}")
        
        for skill_category in skills:
            category = skill_category.get('category', 'Skills')
            skills_list = skill_category.get('skills', '')
            
            skills_parts.append(f"\\textbf{{{self._escape_latex(category)}:}} \\\\")
            skills_parts.append(f"{self._escape_latex(skills_list)} \\\\[5pt]")
        
        skills_parts.append("\\vspace{10pt}")
        skills_parts.append("")
        
        return "\n".join(skills_parts)
    
    def _generate_simple_skills(self, skills: List[Dict[str, Any]]) -> str:
        """Generate simple style skills"""
        skills_parts = []
        
        skills_parts.append("\\section{Technical Skills}")
        
        # Group all skills into categories
        for skill_category in skills:
            category = skill_category.get('category', 'Skills')
            skills_list = skill_category.get('skills', '')
            
            skills_parts.append(f"\\textbf{{{self._escape_latex(category)}:}} {self._escape_latex(skills_list)}")
            skills_parts.append("")
        
        return "\n".join(skills_parts)
    
    def _get_default_skills(self) -> List[Dict[str, Any]]:
        """Get default skills for demonstration"""
        return [
            {
                'category': 'Programming Languages',
                'skills': 'Python, JavaScript, Java, C++, SQL'
            },
            {
                'category': 'Frameworks & Libraries',
                'skills': 'React, Node.js, Django, FastAPI, TensorFlow'
            },
            {
                'category': 'Tools & Technologies',
                'skills': 'Git, Docker, AWS, PostgreSQL, MongoDB'
            },
            {
                'category': 'AI & Machine Learning',
                'skills': 'Machine Learning, Deep Learning, NLP, Computer Vision'
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