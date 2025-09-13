from typing import Dict, Any, List

class ExperienceBlock:
    """Professional experience section block"""
    
    def __init__(self, template_style: str = "arpan", experience_type: str = "professional"):
        self.template_style = template_style
        self.experience_type = experience_type  # "professional" or "research"
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate experience LaTeX code"""
        if self.experience_type == "professional":
            experience_data = user_data.get('professional_experience', [])
            section_title = "Professional Experience"
        else:
            experience_data = user_data.get('research_experience', [])
            section_title = "Research Experience"
        
        if not experience_data:
            experience_data = self._get_default_experience()
        
        if self.template_style == "arpan":
            return self._generate_arpan_experience(experience_data, section_title)
        else:
            return self._generate_simple_experience(experience_data, section_title)
    
    def _generate_arpan_experience(self, experiences: List[Dict[str, Any]], section_title: str) -> str:
        """Generate Arpan style experience"""
        exp_parts = []
        
        exp_parts.append(f"\\section{{{section_title}}}")
        
        for exp in experiences:
            if self.experience_type == "professional":
                title = f"{exp.get('position', 'Position')} -- {exp.get('company', 'Company')}"
            else:
                title = exp.get('title', 'Research Title')
            
            description = exp.get('description', 'Experience description')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', 'Present')
            
            # Format date range
            date_range = self._format_date_range(start_date, end_date)
            
            exp_parts.append(f"\\textbf{{{self._escape_latex(title)}}} \\hfill {date_range}")
            exp_parts.append("\\begin{itemize}")
            
            # Split description into bullet points
            descriptions = self._split_description(description)
            for desc in descriptions:
                exp_parts.append(f"    \\item {self._escape_latex(desc)}")
            
            exp_parts.append("\\end{itemize}")
            exp_parts.append("")
        
        return "\n".join(exp_parts)
    
    def _generate_simple_experience(self, experiences: List[Dict[str, Any]], section_title: str) -> str:
        """Generate simple style experience"""
        exp_parts = []
        
        exp_parts.append(f"\\section{{{section_title}}}")
        
        for exp in experiences:
            if self.experience_type == "professional":
                position = exp.get('position', 'Position')
                company = exp.get('company', 'Company')
                exp_parts.append(f"\\textbf{{{self._escape_latex(position)}}} \\hfill {self._format_date_range(exp.get('start_date', ''), exp.get('end_date', 'Present'))}")
                exp_parts.append(f"\\textit{{{self._escape_latex(company)}}}")
            else:
                title = exp.get('title', 'Research Title')
                exp_parts.append(f"\\textbf{{{self._escape_latex(title)}}} \\hfill {self._format_date_range(exp.get('start_date', ''), exp.get('end_date', 'Present'))}")
            
            description = exp.get('description', 'Experience description')
            
            exp_parts.append("\\begin{itemize}")
            
            # Split description into bullet points
            descriptions = self._split_description(description)
            for desc in descriptions:
                exp_parts.append(f"    \\item {self._escape_latex(desc)}")
            
            exp_parts.append("\\end{itemize}")
            exp_parts.append("")
        
        return "\n".join(exp_parts)
    
    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format date range for display"""
        if not start_date and not end_date:
            return ""
        elif not start_date:
            return end_date
        elif not end_date or end_date.lower() == 'present':
            return f"{start_date} -- Present"
        else:
            return f"{start_date} -- {end_date}"
    
    def _split_description(self, description: str) -> List[str]:
        """Split description into bullet points"""
        if not description:
            return ["Experience description"]
        
        # If description already contains bullet points or line breaks, split on them
        if '•' in description:
            return [desc.strip() for desc in description.split('•') if desc.strip()]
        elif '\n' in description:
            return [desc.strip() for desc in description.split('\n') if desc.strip()]
        else:
            # For single description, return as single bullet point
            return [description.strip()]
    
    def _get_default_experience(self) -> List[Dict[str, Any]]:
        """Get default experience for demonstration"""
        if self.experience_type == "professional":
            return [
                {
                    'company': 'Sample Company',
                    'position': 'Software Engineer',
                    'description': 'Developed and maintained software applications using modern technologies.',
                    'start_date': 'Jun 2023',
                    'end_date': 'Present'
                }
            ]
        else:
            return [
                {
                    'title': 'Sample Research Project',
                    'description': 'Conducted research on innovative solutions and published findings.',
                    'start_date': 'Jan 2023',
                    'end_date': 'May 2023'
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