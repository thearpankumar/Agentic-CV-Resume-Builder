from typing import Dict, Any

class SocialLinksBlock:
    """Social links block for sidebar - LinkedIn and GitHub"""

    def __init__(self, template_style: str = "arpan"):
        self.template_style = template_style

    def generate(self, user_data: Dict[str, Any]) -> str:
        """Generate social links LaTeX code"""
        user_info = user_data.get('user', {})
        linkedin = user_info.get('linkedin_url', '')
        github = user_info.get('github_url', '')

        if not linkedin and not github:
            return ""  # Don't show section if no links

        if self.template_style == "arpan":
            return self._generate_arpan_social_links(linkedin, github)
        else:
            return self._generate_simple_social_links(linkedin, github)

    def _generate_arpan_social_links(self, linkedin: str, github: str) -> str:
        """Generate Arpan style social links for sidebar"""
        social_parts = []

        social_parts.append("\\subsection{Social Links}")

        if linkedin:
            # Clean LinkedIn URL
            linkedin_clean = self._clean_linkedin_url(linkedin)
            social_parts.append(f"\\textbf{{LinkedIn:}} \\\\")
            social_parts.append(f"\\href{{{linkedin}}}{{linkedin.com/in/{linkedin_clean}}}")
            social_parts.append("")

        if github:
            # Clean GitHub URL
            github_clean = self._clean_github_url(github)
            social_parts.append(f"\\textbf{{GitHub:}} \\\\")
            social_parts.append(f"\\href{{{github}}}{{github.com/{github_clean}}}")
            social_parts.append("")

        return "\n".join(social_parts)

    def _generate_simple_social_links(self, linkedin: str, github: str) -> str:
        """Generate simple style social links"""
        social_parts = []

        social_parts.append("\\section{Social Links}")

        if linkedin:
            linkedin_clean = self._clean_linkedin_url(linkedin)
            social_parts.append(f"\\textbf{{LinkedIn:}} \\href{{{linkedin}}}{{linkedin.com/in/{linkedin_clean}}}")

        if github:
            github_clean = self._clean_github_url(github)
            social_parts.append(f"\\textbf{{GitHub:}} \\href{{{github}}}{{github.com/{github_clean}}}")

        social_parts.append("")
        return "\n".join(social_parts)

    def _clean_linkedin_url(self, linkedin_url: str) -> str:
        """Clean LinkedIn URL to get username"""
        linkedin_clean = linkedin_url.strip()
        prefixes_to_remove = [
            'https://www.linkedin.com/in/',
            'https://linkedin.com/in/',
            'http://www.linkedin.com/in/',
            'http://linkedin.com/in/',
            'www.linkedin.com/in/',
            'linkedin.com/in/'
        ]
        for prefix in prefixes_to_remove:
            linkedin_clean = linkedin_clean.replace(prefix, '')
        # Remove any remaining https:// or http://
        linkedin_clean = linkedin_clean.replace('https://', '').replace('http://', '')
        return linkedin_clean

    def _clean_github_url(self, github_url: str) -> str:
        """Clean GitHub URL to get username"""
        github_clean = github_url.strip()
        prefixes_to_remove = [
            'https://github.com/',
            'https://www.github.com/',
            'http://github.com/',
            'http://www.github.com/',
            'www.github.com/',
            'github.com/'
        ]
        for prefix in prefixes_to_remove:
            github_clean = github_clean.replace(prefix, '')
        # Remove any remaining https:// or http://
        github_clean = github_clean.replace('https://', '').replace('http://', '')
        return github_clean