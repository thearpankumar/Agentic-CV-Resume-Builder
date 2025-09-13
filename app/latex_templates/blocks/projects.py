from typing import Dict, Any, List

class ProjectsBlock:
    """Projects section block"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate projects LaTeX code"""
        projects_data = user_data.get('projects', [])
        
        if not projects_data:
            projects_data = self._get_default_projects()
        
        if self.template_style == "arpan":
            return self._generate_arpan_projects(projects_data)
        else:
            return self._generate_simple_projects(projects_data)
    
    def _generate_arpan_projects(self, projects: List[Dict[str, Any]]) -> str:
        """Generate Arpan style projects"""
        project_parts = []
        
        project_parts.append("\\section{Projects}")
        
        for project in projects:
            title = project.get('title', 'Project Title')
            description = project.get('description', 'Project description')
            start_date = project.get('start_date', '')
            end_date = project.get('end_date', 'Present')
            technologies = project.get('technologies', '')
            
            # Format date range
            date_range = self._format_date_range(start_date, end_date)
            
            project_parts.append(f"\\textbf{{{self._escape_latex(title)}}} \\hfill {date_range}")
            project_parts.append("\\begin{itemize}")
            
            # Split description into bullet points if it contains multiple sentences
            descriptions = self._split_description(description)
            for desc in descriptions:
                project_parts.append(f"    \\item {self._escape_latex(desc)}")
            
            project_parts.append("\\end{itemize}")
            project_parts.append("")
        
        return "\n".join(project_parts)
    
    def _generate_simple_projects(self, projects: List[Dict[str, Any]]) -> str:
        """Generate simple style projects"""
        project_parts = []
        
        project_parts.append("\\section{Projects}")
        
        for project in projects:
            title = project.get('title', 'Project Title')
            description = project.get('description', 'Project description')
            start_date = project.get('start_date', '')
            end_date = project.get('end_date', 'Present')
            technologies = project.get('technologies', '')
            project_url = project.get('project_url', '')
            
            # Format date range
            date_range = self._format_date_range(start_date, end_date)
            
            # Project header with title and dates
            if project_url:
                project_parts.append(f"\\textbf{{\\href{{{project_url}}}{{{self._escape_latex(title)}}}}} \\hfill {date_range}")
            else:
                project_parts.append(f"\\textbf{{{self._escape_latex(title)}}} \\hfill {date_range}")
            
            if technologies:
                project_parts.append(f"\\textit{{Technologies: {self._escape_latex(technologies)}}}")
            
            project_parts.append("\\begin{itemize}")
            
            # Split description into bullet points
            descriptions = self._split_description(description)
            for desc in descriptions:
                project_parts.append(f"    \\item {self._escape_latex(desc)}")
            
            project_parts.append("\\end{itemize}")
            project_parts.append("")
        
        return "\n".join(project_parts)
    
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
            return ["Project description"]
        
        # If description already contains bullet points or line breaks, split on them
        if '•' in description:
            return [desc.strip() for desc in description.split('•') if desc.strip()]
        elif '\n' in description:
            return [desc.strip() for desc in description.split('\n') if desc.strip()]
        else:
            # For single description, return as single bullet point
            return [description.strip()]
    
    def _get_default_projects(self) -> List[Dict[str, Any]]:
        """Get default projects for demonstration"""
        return [
            {
                'title': 'Sample Project 1',
                'description': 'Developed a comprehensive solution using modern technologies and best practices.',
                'start_date': 'Jan 2024',
                'end_date': 'Present',
                'technologies': 'Python, React, PostgreSQL'
            },
            {
                'title': 'Sample Project 2', 
                'description': 'Built an innovative platform that addresses real-world challenges.',
                'start_date': 'Sep 2023',
                'end_date': 'Dec 2023',
                'technologies': 'Node.js, MongoDB, Docker'
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