from typing import Dict, Any, List

class CollaborationBlock:
    """Academic collaboration section block"""

    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style

    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate LaTeX for academic collaborations"""
        collaborations = user_data.get('academic_collaborations', [])

        if not collaborations:
            return ""

        latex_parts = []
        latex_parts.append("\\section{Academic Collaborations}")

        for collaboration in collaborations:
            if not isinstance(collaboration, dict):
                continue

            title = collaboration.get('project_title', '')
            institution = collaboration.get('institution', '')
            collaboration_type = collaboration.get('collaboration_type', '')
            collaborators = collaboration.get('collaborators', '')
            role = collaboration.get('role', '')
            description = collaboration.get('description', '')
            start_date = collaboration.get('start_date', '')
            end_date = collaboration.get('end_date', '')
            url = collaboration.get('publication_url', '')

            # Format header with title and dates
            header_parts = []
            if title:
                if url:
                    header_parts.append(f"\\textbf{{\\href{{{url}}}{{{title}}}}}")
                else:
                    header_parts.append(f"\\textbf{{{title}}}")

            # Add dates if available
            if start_date or end_date:
                if end_date and end_date.lower() != 'present':
                    date_str = f"{start_date} -- {end_date}"
                else:
                    date_str = f"{start_date} -- Present"
                header_parts.append(f"\\hfill {date_str}")

            if header_parts:
                latex_parts.append(" ".join(header_parts))

            # Add collaboration type and institution
            if collaboration_type or institution:
                type_inst_parts = []
                if collaboration_type:
                    type_inst_parts.append(f"\\textit{{{collaboration_type}}}")
                if institution:
                    type_inst_parts.append(f"at {institution}")
                if type_inst_parts:
                    latex_parts.append(" ".join(type_inst_parts))

            # Add role if specified
            if role:
                latex_parts.append(f"\\textbf{{Role:}} {role}")

            # Add collaborators if specified
            if collaborators:
                latex_parts.append(f"\\textbf{{Collaborators:}} {collaborators}")

            # Add description as bullet points
            if description:
                latex_parts.append("\\begin{itemize}")
                # Split description into bullet points if it contains newlines
                desc_lines = description.split('\n')
                for line in desc_lines:
                    line = line.strip()
                    if line:
                        latex_parts.append(f"    \\item {line}")
                latex_parts.append("\\end{itemize}")

            latex_parts.append("")  # Add spacing between collaborations

        return "\n".join(latex_parts)