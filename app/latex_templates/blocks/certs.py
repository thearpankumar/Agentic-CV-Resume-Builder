from typing import Dict, Any, List

class CertificationsBlock:
    """Certifications section block"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate certifications LaTeX code"""
        certs_data = user_data.get('certifications', [])
        
        # Only generate if there are certifications
        if not certs_data:
            return ""
        
        if self.template_style == "arpan":
            return self._generate_arpan_certs(certs_data)
        else:
            return self._generate_simple_certs(certs_data)
    
    def _generate_arpan_certs(self, certifications: List[Dict[str, Any]]) -> str:
        """Generate Arpan style certifications (sidebar format)"""
        cert_parts = []
        
        cert_parts.append("\\subsection*{Certifications}")
        
        for cert in certifications:
            title = cert.get('title', 'Certification Title')
            issuer = cert.get('issuer', '')
            date_obtained = cert.get('date_obtained', '')
            
            cert_parts.append(f"\\textbf{{{self._escape_latex(title)}}} \\\\")
            
            if issuer:
                cert_parts.append(f"{self._escape_latex(issuer)} \\\\")
            
            if date_obtained:
                cert_parts.append(f"\\textit{{{date_obtained}}} \\\\")
            
            cert_parts.append("\\vspace{5pt}")
        
        cert_parts.append("")
        
        return "\n".join(cert_parts)
    
    def _generate_simple_certs(self, certifications: List[Dict[str, Any]]) -> str:
        """Generate simple style certifications"""
        cert_parts = []
        
        cert_parts.append("\\section{Certifications}")
        
        for cert in certifications:
            title = cert.get('title', 'Certification Title')
            issuer = cert.get('issuer', '')
            date_obtained = cert.get('date_obtained', '')
            
            # Format header line
            header = f"\\textbf{{{self._escape_latex(title)}}}"
            if date_obtained:
                header += f" \\hfill {date_obtained}"
            
            cert_parts.append(header)
            
            if issuer:
                cert_parts.append(f"\\textit{{{self._escape_latex(issuer)}}}")
            
            cert_parts.append("")
        
        return "\n".join(cert_parts)
    
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