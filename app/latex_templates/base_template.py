from typing import Dict, List, Any
from .blocks.header import HeaderBlock
from .blocks.summary import SummaryBlock
from .blocks.projects import ProjectsBlock
from .blocks.experience import ExperienceBlock
from .blocks.research import ResearchBlock
from .blocks.education import EducationBlock
from .blocks.skills import SkillsBlock
from .blocks.certs import CertificationsBlock
from .blocks.social_links import SocialLinksBlock
from .blocks.collaboration import CollaborationBlock

class BaseTemplate:
    """Base class for LaTeX resume templates"""
    
    def __init__(self, template_style: str = "arpan", font_size: str = "10pt", enforce_one_page_limit: bool = True):
        self.template_style = template_style
        self.font_size = font_size
        self.enforce_one_page_limit = enforce_one_page_limit
        self.blocks = {
            "header": HeaderBlock(template_style),
            "professional_summary": SummaryBlock(template_style),
            "projects": ProjectsBlock(template_style),
            "professional_experience": ExperienceBlock(template_style, "professional"),
            "research_experience": ResearchBlock(template_style),
            "education": EducationBlock(template_style),
            "technical_skills": SkillsBlock(template_style),
            "certifications": CertificationsBlock(template_style),
            "academic_collaborations": CollaborationBlock(template_style),
            "social_links": SocialLinksBlock(template_style)
        }
    
    def get_document_preamble(self) -> str:
        """Get LaTeX document preamble based on template style"""
        if self.template_style == "arpan":
            return self._get_arpan_preamble()
        else:
            return self._get_simple_preamble()
    
    def _get_arpan_preamble(self) -> str:
        """Arpan style preamble (modern, responsive layout)"""
        # Adjust margins based on page limit enforcement
        if self.enforce_one_page_limit:
            margin_settings = r"""margin=0.5in,
    top=0.5in,
    bottom=0.6in"""
        else:
            margin_settings = r"""margin=0.75in,
    top=0.75in,
    bottom=0.75in"""

        preamble = f"""
\\documentclass[FONT_SIZE,a4paper]{{article}}

% --- PACKAGES ---
\\usepackage[utf8]{{inputenc}}
\\usepackage[
    {margin_settings}
]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage[explicit]{{titlesec}}
\\usepackage{{hyperref}}
\\usepackage{{xcolor}}
\\usepackage{{helvet}}
\\usepackage{{fontawesome5}}
\\usepackage{{needspace}}
\\usepackage{{paracol}}

% --- COLOR & HYPERLINK DEFINITION ---
\\definecolor{{darkblue}}{{RGB}}{{0, 51, 102}}
\\definecolor{{graytext}}{{RGB}}{{80, 80, 80}}
\\hypersetup{{
    colorlinks=true,
    linkcolor=darkblue,
    urlcolor=darkblue,
    citecolor=darkblue,
    pdftitle={{Resume}},
    pdfauthor={{Resume Builder}}
}}

% --- PAGE & FONT SETUP ---
\\pagestyle{{empty}}
\\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\setlength{{\\parindent}}{{0pt}}

% --- ROBUST SECTION FORMATTING ---
% Main sections (medium size headings)
\\titleformat{{\\section}}
  {{\\normalsize\\bfseries\\sffamily\\color{{darkblue}}}}
  {{}}
  {{0em}}
  {{#1}}
  [\\vspace{{2pt}}\\noindent\\rule{{\\linewidth}}{{0.8pt}}]
\\titlespacing*{{\\section}}{{0pt}}{{8pt}}{{6pt}}

% Sidebar Sections (smaller headings)
\\titleformat{{\\subsection}}
  {{\\small\\sffamily\\bfseries\\color{{black}}}}
  {{}}
  {{0em}}
  {{}}
\\titlespacing*{{\\subsection}}{{0pt}}{{6pt}}{{3pt}}

% --- LIST SPACING ---
\\setlist[itemize]{{
    noitemsep,
    topsep=2pt,
    leftmargin=*,
    itemsep=2pt,
    parsep=2pt
}}

% --- CUSTOM ENVIRONMENTS ---
% Sidebar environment with smaller font
\\newenvironment{{sidebarenv}}
  {{\\small}}
  {{}}
"""
        return preamble.replace("FONT_SIZE", self.font_size)
    
    def _get_simple_preamble(self) -> str:
        """Simple style preamble (single column, clean)"""
        return r"""
\documentclass[11pt,a4paper]{article}

% --- PACKAGES ---
\usepackage[utf8]{inputenc}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{xcolor}

% --- COLOR DEFINITION ---
\definecolor{darkblue}{RGB}{0, 51, 102}
\hypersetup{
    colorlinks=true,
    linkcolor=darkblue,
    urlcolor=darkblue,
    citecolor=darkblue
}

% --- PAGE SETUP ---
\pagestyle{empty}
\setlength{\parindent}{0pt}

% --- SECTION FORMATTING ---
\titleformat{\section}
  {\large\bfseries\color{darkblue}}
  {}
  {0em}
  {#1}
  [\vspace{2pt}\noindent\rule{\linewidth}{0.5pt}]
\titlespacing*{\section}{0pt}{15pt}{10pt}

% --- LIST SPACING ---
\setlist[itemize]{
    noitemsep,
    topsep=3pt,
    leftmargin=15pt,
    itemsep=3pt
}
"""
    
    def generate_latex(self, user_data: Dict[str, Any], active_sections: List[str], section_order: List[str]) -> str:
        """Generate complete LaTeX document"""
        latex_parts = []
        
        # Add preamble
        latex_parts.append(self.get_document_preamble())
        
        # Begin document
        latex_parts.append("\\begin{document}")
        
        # Always include header
        latex_parts.append(self.blocks["header"].generate(user_data))
        
        # Handle layout based on template style
        if self.template_style == "arpan":
            latex_parts.append(self._generate_arpan_layout(user_data, active_sections, section_order))
        else:
            latex_parts.append(self._generate_simple_layout(user_data, active_sections, section_order))
        
        # End document
        latex_parts.append("\\end{document}")
        
        return "\n".join(latex_parts)
    
    def _generate_arpan_layout(self, user_data: Dict[str, Any], active_sections: List[str], section_order: List[str]) -> str:
        """Generate Arpan style layout (two-column for single page, single-column for multi-page)"""
        latex_parts = []

        if self.enforce_one_page_limit:
            # Single-page mode: Use minipage two-column layout like docs/main.tex
            latex_parts.append("% --- TWO-COLUMN LAYOUT (SINGLE PAGE) ---")
            latex_parts.append("\\needspace{4cm}")
            latex_parts.append("\\noindent")
            latex_parts.append("\\begin{minipage}[t]{0.3\\textwidth}")
            latex_parts.append("\\begin{sidebarenv}")
            latex_parts.append("    \\sffamily")

            # Left sidebar sections
            sidebar_sections = ["education", "technical_skills", "certifications"]
            for section in sidebar_sections:
                if section in active_sections and section in self.blocks:
                    latex_parts.append(self.blocks[section].generate(user_data))

            # Always add social links to sidebar
            latex_parts.append(self.blocks["social_links"].generate(user_data))

            latex_parts.append("\\end{sidebarenv}")
            latex_parts.append("\\end{minipage}")
            latex_parts.append("\\hspace{0.05\\textwidth}")
            latex_parts.append("\\begin{minipage}[t]{0.65\\textwidth}")
            latex_parts.append("    \\sffamily")

            # Right main sections
            main_sections = [s for s in section_order if s not in sidebar_sections and s in active_sections]
            for section in main_sections:
                if section in self.blocks:
                    latex_parts.append(self.blocks[section].generate(user_data))

            latex_parts.append("\\end{minipage}")
        else:
            # Multi-page mode: Use two-column layout that can flow across pages (matching docs/main.tex exactly)
            latex_parts.append("% --- TWO-COLUMN LAYOUT (MULTI-PAGE FLOW) ---")
            latex_parts.append("\\columnratio{0.3,0.65}")  # Set column ratios: 30% left, 65% right
            latex_parts.append("\\setlength{\\columnsep}{0.05\\textwidth}")  # 5% separation between columns
            latex_parts.append("\\begin{paracol}{2}")

            # Left sidebar sections (column 1) - 30% width like docs/main.tex
            latex_parts.append("% Left column - sidebar sections (30% width)")
            latex_parts.append("\\begin{sloppypar}")  # Better line breaking
            latex_parts.append("\\sffamily % Use sans-serif font for the entire sidebar")
            latex_parts.append("\\raggedright % Prevent text justification that could cause overflow")
            latex_parts.append("\\hsize=0.3\\textwidth % Explicitly set column width")

            sidebar_sections = ["education", "technical_skills", "certifications"]
            for section in sidebar_sections:
                if section in active_sections and section in self.blocks:
                    latex_parts.append(self.blocks[section].generate(user_data))

            # Always add social links to sidebar
            latex_parts.append(self.blocks["social_links"].generate(user_data))
            latex_parts.append("\\end{sloppypar}")

            # Right main sections (column 2) - 65% width like docs/main.tex
            latex_parts.append("% Right column - main sections (65% width)")
            latex_parts.append("\\switchcolumn")
            latex_parts.append("\\begin{sloppypar}")  # Better line breaking
            latex_parts.append("\\sffamily")
            latex_parts.append("\\raggedright % Prevent text justification that could cause overflow")
            latex_parts.append("\\hsize=0.65\\textwidth % Explicitly set column width")

            main_sections = [s for s in section_order if s not in sidebar_sections and s in active_sections]
            for section in main_sections:
                if section in self.blocks:
                    latex_parts.append(self.blocks[section].generate(user_data))

            latex_parts.append("\\end{sloppypar}")

            latex_parts.append("\\end{paracol}")

        return "\n".join(latex_parts)
    
    def _generate_simple_layout(self, user_data: Dict[str, Any], active_sections: List[str], section_order: List[str]) -> str:
        """Generate simple single-column layout"""
        latex_parts = []
        
        # Single column - follow section order
        for section in section_order:
            if section in active_sections and section in self.blocks:
                latex_parts.append(self.blocks[section].generate(user_data))
        
        return "\n".join(latex_parts)
    
    def get_default_section_order(self) -> List[str]:
        """Get default section order for template"""
        return [
            "professional_summary",
            "projects",
            "professional_experience",
            "research_experience",
            "academic_collaborations",
            "education",
            "technical_skills",
            "certifications"
        ]
    
    def get_available_sections(self) -> Dict[str, str]:
        """Get available sections with display names"""
        return {
            "professional_summary": "Professional Summary",
            "projects": "Projects",
            "professional_experience": "Professional Experience",
            "research_experience": "Research Experience", 
            "education": "Education",
            "technical_skills": "Technical Skills",
            "certifications": "Certifications"
        }