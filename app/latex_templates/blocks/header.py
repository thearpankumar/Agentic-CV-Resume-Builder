from typing import Dict, Any

class HeaderBlock:
    """Header block for resume - name and contact information"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate header LaTeX code"""
        user_info = user_data.get('user', {})
        name = user_info.get('name', 'Your Name')
        email = user_info.get('email', 'your.email@example.com')
        phone = user_info.get('phone', 'Your Phone')
        location = user_info.get('location', 'Your Location')
        linkedin = user_info.get('linkedin_url', '')
        github = user_info.get('github_url', '')
        
        if self.template_style == "arpan":
            return self._generate_arpan_header(name, email, phone, location, linkedin, github)
        else:
            return self._generate_simple_header(name, email, phone, location, linkedin, github)
    
    def _generate_arpan_header(self, name: str, email: str, phone: str, location: str, linkedin: str, github: str) -> str:
        """Generate Arpan style header with clean design"""
        header_parts = []
        
        header_parts.append("% --- CLEAN & SIMPLE HEADER ---")
        header_parts.append("\\begin{center}")
        header_parts.append(f"    {{\\Huge\\bfseries\\sffamily {self._escape_latex(name)}}}")
        header_parts.append("    \\vspace{4pt}")
        header_parts.append("    \\noindent\\rule{\\linewidth}{0.8pt}")
        header_parts.append("\\end{center}")
        header_parts.append("\\vspace{16pt}")
        
        return "\n".join(header_parts)
    
    def _generate_simple_header(self, name: str, email: str, phone: str, location: str, linkedin: str, github: str) -> str:
        """Generate simple style header with contact info"""
        header_parts = []
        
        # Name
        header_parts.append("\\begin{center}")
        header_parts.append(f"    {{\\LARGE\\bfseries {self._escape_latex(name)}}}")
        header_parts.append("\\end{center}")
        header_parts.append("\\vspace{8pt}")
        
        # Contact information
        contact_info = []
        if email:
            contact_info.append(f"\\href{{mailto:{email}}}{{{email}}}")
        if phone:
            contact_info.append(phone)
        if location:
            contact_info.append(location)
        
        if contact_info:
            bullet_sep = ' $\\bullet$ '
            header_parts.append("\\begin{center}")
            header_parts.append(f"    {bullet_sep.join(contact_info)}")
            header_parts.append("\\end{center}")
        
        # Social links
        social_links = []
        if linkedin:
            linkedin_text = linkedin.replace('https://www.linkedin.com/in/', '').replace('https://linkedin.com/in/', '')
            social_links.append(f"\\href{{{linkedin}}}{{LinkedIn: {linkedin_text}}}")
        if github:
            github_text = github.replace('https://github.com/', '').replace('https://www.github.com/', '')
            social_links.append(f"\\href{{{github}}}{{GitHub: {github_text}}}")
        
        if social_links:
            bullet_sep = ' $\\bullet$ '
            header_parts.append("\\begin{center}")
            header_parts.append(f"    {bullet_sep.join(social_links)}")
            header_parts.append("\\end{center}")
        
        header_parts.append("\\vspace{12pt}")
        
        return "\n".join(header_parts)
    
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