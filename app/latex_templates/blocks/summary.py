from typing import Dict, Any

class SummaryBlock:
    """Professional summary block"""
    
    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style
    
    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate professional summary LaTeX code"""
        summary_data = user_data.get('professional_summaries', [])
        
        # Get the most recent summary or default text
        if summary_data:
            summary_text = summary_data[0].get('generated_summary', self._get_default_summary())
        else:
            summary_text = self._get_default_summary()
        
        if self.template_style == "arpan":
            return self._generate_arpan_summary(summary_text)
        else:
            return self._generate_simple_summary(summary_text)
    
    def _generate_arpan_summary(self, summary_text: str) -> str:
        """Generate Arpan style summary"""
        summary_parts = []

        summary_parts.append("\\section{Professional Summary}")
        summary_parts.append(f"{self._escape_latex(summary_text)}")
        summary_parts.append("\\vspace{8pt}")
        summary_parts.append("")

        return "\n".join(summary_parts)
    
    def _generate_simple_summary(self, summary_text: str) -> str:
        """Generate simple style summary"""
        summary_parts = []

        summary_parts.append("\\section{Professional Summary}")
        summary_parts.append(f"{self._escape_latex(summary_text)}")
        summary_parts.append("\\vspace{8pt}")
        summary_parts.append("")

        return "\n".join(summary_parts)
    
    def _get_default_summary(self) -> str:
        """Get default professional summary"""
        return ("Computer Science enthusiast with expertise in AI/ML, cybersecurity, and software development. "
                "Passionate about creating innovative solutions that bridge technology gaps and enhance system "
                "performance through advanced algorithms and cutting-edge technologies.")
    
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