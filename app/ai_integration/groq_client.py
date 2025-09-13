from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from groq import Groq
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

class GroqClient:
    """Client for interacting with Groq API using Pydantic settings"""

    def __init__(self):
        self.config = settings.get_groq_config()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Groq client"""
        if settings.is_groq_available:
            try:
                self.client = Groq(api_key=self.config["api_key"])
            except Exception as e:
                st.error(f"Failed to initialize Groq client: {e}")
        else:
            st.warning("Groq API key not found in settings. AI features will be disabled.")

    def is_available(self) -> bool:
        """Check if Groq client is available"""
        return self.client is not None and settings.is_groq_available
    
    def generate_professional_summary(
        self, 
        user_data: Dict[str, Any], 
        job_description: str = ""
    ) -> Optional[str]:
        """
        Generate professional summary based on user data and job description
        """
        if not self.is_available():
            return None
        
        try:
            # Build context from user data
            context = self._build_user_context(user_data)
            
            # Create prompt
            prompt = self._create_summary_prompt(context, job_description)
            
            # Call Groq API with retries for word count compliance
            max_attempts = 3
            for attempt in range(max_attempts):
                response = self.client.chat.completions.create(
                    model=self.config.get("model", "openai/gpt-oss-120b"),
                    max_tokens=self.config.get("max_tokens", 2000),
                    temperature=self.config.get("temperature", 0.7),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional resume writer with expertise in creating compelling professional summaries. Create concise, impactful summaries that highlight key strengths and align with job requirements. ALWAYS follow the exact word count requirements."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                generated_summary = response.choices[0].message.content.strip()
                word_count = len(generated_summary.split())

                # Validate word count (80-90 words)
                if 80 <= word_count <= 90:
                    return generated_summary
                elif attempt < max_attempts - 1:
                    # Modify prompt for retry
                    if word_count < 80:
                        prompt = prompt.replace("EXACTLY 80-90 words", f"EXACTLY 80-90 words (current draft was {word_count} words - ADD more content)")
                    else:
                        prompt = prompt.replace("EXACTLY 80-90 words", f"EXACTLY 80-90 words (current draft was {word_count} words - REDUCE content)")

            # If all attempts failed, return the last attempt
            return generated_summary
            
        except Exception as e:
            st.error(f"Error generating professional summary: {e}")
            return None
    
    def select_best_projects(
        self, 
        projects: List[Dict[str, Any]], 
        job_description: str,
        max_projects: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select and rank the best projects based on job description
        """
        if not self.is_available() or not projects:
            return projects[:max_projects]  # Return first N projects if AI not available
        
        try:
            # Create prompt for project selection
            prompt = self._create_project_selection_prompt(projects, job_description, max_projects)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor expert at matching projects to job requirements. Analyze projects and select the most relevant ones based on the job description."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response to get project indices
            selected_indices = self._parse_project_selection_response(
                response.choices[0].message.content,
                len(projects)
            )
            
            # Return selected projects in order
            return [projects[i] for i in selected_indices[:max_projects]]
            
        except Exception as e:
            st.error(f"Error selecting projects: {e}")
            return projects[:max_projects]
    
    def optimize_content_for_job(
        self,
        content: str,
        content_type: str,
        job_description: str
    ) -> Optional[str]:
        """
        Optimize content (experience descriptions, project descriptions) for specific job
        """
        if not self.is_available():
            return content
        
        try:
            prompt = self._create_content_optimization_prompt(content, content_type, job_description)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume optimizer. Enhance content to better align with job requirements while maintaining truthfulness and impact."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error optimizing content: {e}")
            return content
    
    def generate_skills_recommendations(
        self,
        current_skills: List[str],
        job_description: str
    ) -> List[str]:
        """
        Recommend additional skills based on job description
        """
        if not self.is_available():
            return []
        
        try:
            prompt = self._create_skills_recommendation_prompt(current_skills, job_description)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor. Analyze job descriptions and recommend relevant skills that would strengthen a candidate's profile."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse skills from response
            return self._parse_skills_recommendations(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error generating skills recommendations: {e}")
            return []
    
    def reframe_content(
        self,
        content: str,
        content_type: str,
        improvement_focus: str = "make it more professional and impactful"
    ) -> Optional[str]:
        """
        Reframe content to make it more professional and impactful
        """
        if not self.is_available():
            return content
        
        try:
            prompt = self._create_reframe_prompt(content, content_type, improvement_focus)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer. Reframe content to be more impactful, professional, and ATS-friendly while maintaining truthfulness."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error reframing content: {e}")
            return content
    
    def generate_professional_summary_with_feedback(
        self,
        user_data: Dict[str, Any],
        job_description: str,
        previous_summary: str = "",
        user_feedback: str = ""
    ) -> Optional[str]:
        """
        Generate professional summary with iterative improvement based on feedback
        """
        if not self.is_available():
            return None
        
        try:
            context = self._build_user_context(user_data)
            prompt = self._create_iterative_summary_prompt(
                context, job_description, previous_summary, user_feedback
            )

            # Call Groq API with retries for word count compliance
            max_attempts = 3
            for attempt in range(max_attempts):
                response = self.client.chat.completions.create(
                    model=self.config.get("model", "openai/gpt-oss-120b"),
                    max_tokens=self.config.get("max_tokens", 2000),
                    temperature=self.config.get("temperature", 0.7),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional resume writer. Create compelling professional summaries that can be iteratively improved based on user feedback. ALWAYS follow the exact word count requirements."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                generated_summary = response.choices[0].message.content.strip()
                word_count = len(generated_summary.split())

                # Validate word count (80-90 words)
                if 80 <= word_count <= 90:
                    return generated_summary
                elif attempt < max_attempts - 1:
                    # Modify prompt for retry
                    if word_count < 80:
                        prompt = prompt.replace("EXACTLY 80-90 words", f"EXACTLY 80-90 words (current draft was {word_count} words - ADD more content)")
                    else:
                        prompt = prompt.replace("EXACTLY 80-90 words", f"EXACTLY 80-90 words (current draft was {word_count} words - REDUCE content)")

            # If all attempts failed, return the last attempt
            return generated_summary
            
        except Exception as e:
            st.error(f"Error generating professional summary: {e}")
            return None
    
    def analyze_job_posting(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job posting to extract key requirements and skills
        """
        if not self.is_available():
            return {}

        try:
            prompt = self._create_job_analysis_prompt(job_description)

            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a job market analyst. Extract key requirements, skills, and priorities from job descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return self._parse_job_analysis(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error analyzing job posting: {e}")
            return {}

    def analyze_section_relevance(self, user_data: Dict[str, Any], job_description: str) -> Dict[str, bool]:
        """
        Analyze whether each resume section is relevant for the job posting
        Returns: {section_name: should_include_boolean}
        """
        if not self.is_available():
            # Fallback: include all sections with content
            sections_to_check = [
                'professional_summaries', 'projects', 'professional_experience',
                'research_experience', 'education', 'technical_skills', 'certifications'
            ]
            return {section: bool(user_data.get(section, [])) for section in sections_to_check}

        try:
            prompt = self._create_section_relevance_prompt(user_data, job_description)

            response = self.client.chat.completions.create(
                model=self.config.get("model", "openai/gpt-oss-120b"),
                max_tokens=self.config.get("max_tokens", 2000),
                temperature=self.config.get("temperature", 0.7),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume advisor. Analyze which resume sections are relevant for a specific job and should be included or excluded."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return self._parse_section_relevance_response(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error analyzing section relevance: {e}")
            # Fallback: include all sections with content
            sections_to_check = [
                'professional_summaries', 'projects', 'professional_experience',
                'research_experience', 'education', 'technical_skills', 'certifications'
            ]
            return {section: bool(user_data.get(section, [])) for section in sections_to_check}
    
    def _build_user_context(self, user_data: Dict[str, Any]) -> str:
        """Build context string from user data"""
        context_parts = []
        
        # User basic info
        user_info = user_data.get('user', {})
        if user_info.get('name'):
            context_parts.append(f"Name: {user_info['name']}")
        
        # Projects
        projects = user_data.get('projects', [])
        if projects:
            context_parts.append("Projects:")
            for project in projects[:3]:  # Limit to top 3
                context_parts.append(f"- {project.get('title', '')}: {project.get('description', '')}")
        
        # Experience
        experience = user_data.get('professional_experience', [])
        if experience:
            context_parts.append("Experience:")
            for exp in experience[:2]:  # Limit to top 2
                context_parts.append(f"- {exp.get('position', '')} at {exp.get('company', '')}: {exp.get('description', '')}")
        
        # Skills
        skills = user_data.get('technical_skills', [])
        if skills:
            context_parts.append("Skills:")
            for skill_cat in skills:
                context_parts.append(f"- {skill_cat.get('category', '')}: {skill_cat.get('skills', '')}")
        
        return "\n".join(context_parts)
    
    def _create_summary_prompt(self, user_context: str, job_description: str) -> str:
        """Create prompt for professional summary generation"""
        prompt = f"""
Based on the following user information, create a compelling professional summary for their resume:

USER INFORMATION:
{user_context}

"""
        
        if job_description:
            prompt += f"""
TARGET JOB DESCRIPTION:
{job_description}

Please tailor the summary to align with this specific role.
"""
        
        prompt += """
Requirements:
- EXACTLY 80-90 words (this is mandatory)
- 2-3 sentences maximum
- Highlight key strengths and expertise
- Use action-oriented language
- Make it ATS-friendly
- Focus on value proposition

Professional Summary:"""
        
        return prompt
    
    def _create_project_selection_prompt(
        self, 
        projects: List[Dict[str, Any]], 
        job_description: str,
        max_projects: int
    ) -> str:
        """Create prompt for project selection"""
        prompt = f"""
Analyze these projects and select the {max_projects} most relevant ones for the following job description.

JOB DESCRIPTION:
{job_description}

AVAILABLE PROJECTS:
"""
        
        for i, project in enumerate(projects):
            prompt += f"""
{i}. Title: {project.get('title', 'Untitled')}
   Technologies: {project.get('technologies', 'N/A')}
   Description: {project.get('description', 'No description')}

"""
        
        prompt += f"""
Please respond with only the indices (0-{len(projects)-1}) of the {max_projects} most relevant projects, ranked by relevance to the job. 
Format: 0,2,1 (comma-separated, no spaces)
"""
        
        return prompt
    
    def _create_content_optimization_prompt(
        self,
        content: str,
        content_type: str,
        job_description: str
    ) -> str:
        """Create prompt for content optimization"""
        return f"""
Optimize this {content_type} description to better align with the job requirements:

JOB DESCRIPTION:
{job_description}

CURRENT {content_type.upper()}:
{content}

Requirements:
- Keep it truthful and accurate
- Emphasize relevant skills and achievements
- Use keywords from job description naturally
- Maintain professional tone
- Keep similar length

OPTIMIZED {content_type.upper()}:"""
    
    def _create_skills_recommendation_prompt(
        self,
        current_skills: List[str],
        job_description: str
    ) -> str:
        """Create prompt for skills recommendations"""
        skills_text = ", ".join(current_skills)
        
        return f"""
Based on this job description, recommend additional skills that would strengthen the candidate's profile:

JOB DESCRIPTION:
{job_description}

CURRENT SKILLS:
{skills_text}

Please suggest 3-5 relevant skills that:
- Are mentioned or implied in the job description
- Would complement current skills
- Are realistic to acquire/highlight

Respond with only the skill names, comma-separated:"""
    
    def _parse_project_selection_response(self, response: str, total_projects: int) -> List[int]:
        """Parse project selection response"""
        try:
            # Extract numbers from response
            import re
            numbers = re.findall(r'\d+', response)
            indices = [int(n) for n in numbers if 0 <= int(n) < total_projects]
            return indices
        except Exception:
            # Fallback to first projects
            return list(range(min(3, total_projects)))
    
    def _parse_skills_recommendations(self, response: str) -> List[str]:
        """Parse skills recommendations from response"""
        try:
            # Split by comma and clean up
            skills = [skill.strip() for skill in response.split(',')]
            # Filter out empty strings and limit to reasonable length
            return [skill for skill in skills if skill and len(skill) < 50][:5]
        except Exception:
            return []
    
    def _create_reframe_prompt(self, content: str, content_type: str, improvement_focus: str) -> str:
        """Create prompt for content reframing"""
        return f"""
Improve this {content_type} description to be more professional, impactful, and ATS-friendly:

CURRENT {content_type.upper()}:
{content}

IMPROVEMENT FOCUS:
{improvement_focus}

Requirements:
- Keep it truthful and accurate
- Use stronger action verbs
- Quantify achievements where possible
- Make it more compelling to recruiters
- Ensure ATS keyword optimization
- Maintain similar length

IMPROVED {content_type.upper()}:"""
    
    def _create_iterative_summary_prompt(
        self,
        user_context: str,
        job_description: str,
        previous_summary: str,
        user_feedback: str
    ) -> str:
        """Create prompt for iterative summary generation"""
        prompt = f"""
Based on the user information and job description, create a compelling professional summary:

USER INFORMATION:
{user_context}

TARGET JOB DESCRIPTION:
{job_description}
"""
        
        if previous_summary:
            prompt += f"""
PREVIOUS SUMMARY:
{previous_summary}

USER FEEDBACK:
{user_feedback}

Please improve the summary based on the feedback while maintaining alignment with the job requirements.
"""
        
        prompt += """
Requirements:
- EXACTLY 80-90 words (this is mandatory)
- 2-3 sentences maximum
- Highlight key strengths relevant to the job
- Use action-oriented language
- Make it ATS-friendly
- Focus on value proposition
- Address any specific feedback provided

PROFESSIONAL SUMMARY:"""
        
        return prompt
    
    def _create_job_analysis_prompt(self, job_description: str) -> str:
        """Create prompt for job analysis"""
        return f"""
Analyze this job posting and extract key information:

JOB DESCRIPTION:
{job_description}

Please identify:
1. Required technical skills
2. Preferred qualifications
3. Key responsibilities
4. Company culture/values mentioned
5. Experience level required
6. Important keywords for ATS

Format your response as a structured analysis with clear sections.

ANALYSIS:"""
    
    def _parse_job_analysis(self, response: str) -> Dict[str, Any]:
        """Parse job analysis response"""
        try:
            # Simple parsing - in a real implementation, you might use more sophisticated NLP
            analysis = {
                'technical_skills': [],
                'qualifications': [],
                'responsibilities': [],
                'keywords': [],
                'experience_level': 'Unknown'
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Identify sections
                if 'technical skills' in line.lower():
                    current_section = 'technical_skills'
                elif 'qualifications' in line.lower():
                    current_section = 'qualifications'
                elif 'responsibilities' in line.lower():
                    current_section = 'responsibilities'
                elif 'keywords' in line.lower():
                    current_section = 'keywords'
                elif line.startswith('-') or line.startswith('•'):
                    # Extract bullet point content
                    content = line[1:].strip()
                    if current_section and content:
                        analysis[current_section].append(content)
            
            return analysis

        except Exception:
            return {'technical_skills': [], 'qualifications': [], 'responsibilities': [], 'keywords': [], 'experience_level': 'Unknown'}

    def _create_section_relevance_prompt(self, user_data: Dict[str, Any], job_description: str) -> str:
        """Create prompt for section relevance analysis"""
        # Build summary of user's sections
        sections_info = []

        sections_to_analyze = {
            'professional_summaries': 'Professional Summary',
            'projects': 'Projects',
            'professional_experience': 'Professional Experience',
            'research_experience': 'Research Experience',
            'education': 'Education',
            'technical_skills': 'Technical Skills',
            'certifications': 'Certifications'
        }

        for section_key, section_name in sections_to_analyze.items():
            section_data = user_data.get(section_key, [])
            if section_data:
                count = len(section_data)
                # Get brief content summary
                if section_key == 'projects':
                    titles = [p.get('title', 'Untitled') for p in section_data[:3]]
                    preview = f"Projects: {', '.join(titles)}"
                elif section_key == 'professional_experience':
                    positions = [f"{exp.get('position', '')} at {exp.get('company', '')}" for exp in section_data[:2]]
                    preview = f"Experience: {', '.join(positions)}"
                elif section_key == 'technical_skills':
                    categories = [skill.get('category', '') for skill in section_data[:3]]
                    preview = f"Skills: {', '.join(categories)}"
                else:
                    preview = f"{count} items"

                sections_info.append(f"- {section_name}: {preview}")
            else:
                sections_info.append(f"- {section_name}: No content")

        return f"""
Analyze which resume sections should be INCLUDED or EXCLUDED for this specific job posting.

JOB DESCRIPTION:
{job_description}

AVAILABLE RESUME SECTIONS:
{chr(10).join(sections_info)}

For each section, determine if it's RELEVANT for this job posting. Consider:
1. Does the section content align with job requirements?
2. Would recruiters find this section valuable for this role?
3. Does the section demonstrate relevant skills/experience?
4. Is the content strong enough to add value?

If a section has no content or weak/irrelevant content, mark it as EXCLUDE.
If a section is highly relevant and adds value, mark it as INCLUDE.

Respond with ONLY a simple list format:
professional_summaries: INCLUDE/EXCLUDE
projects: INCLUDE/EXCLUDE
professional_experience: INCLUDE/EXCLUDE
research_experience: INCLUDE/EXCLUDE
education: INCLUDE/EXCLUDE
technical_skills: INCLUDE/EXCLUDE
certifications: INCLUDE/EXCLUDE"""

    def _parse_section_relevance_response(self, response: str) -> Dict[str, bool]:
        """Parse section relevance analysis response"""
        try:
            section_decisions = {}
            lines = response.strip().split('\n')

            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        section = parts[0].strip()
                        decision = parts[1].strip().upper()
                        section_decisions[section] = decision == 'INCLUDE'

            # Ensure all expected sections are present
            expected_sections = [
                'professional_summaries', 'projects', 'professional_experience',
                'research_experience', 'education', 'technical_skills', 'certifications'
            ]

            for section in expected_sections:
                if section not in section_decisions:
                    section_decisions[section] = True  # Default to include if unclear

            return section_decisions

        except Exception:
            # Fallback: include all sections
            return {
                'professional_summaries': True,
                'projects': True,
                'professional_experience': True,
                'research_experience': True,
                'education': True,
                'technical_skills': True,
                'certifications': True
            }