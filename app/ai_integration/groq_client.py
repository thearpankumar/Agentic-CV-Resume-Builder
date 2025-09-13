import os
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client"""
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                st.error(f"Failed to initialize Groq client: {e}")
        else:
            st.warning("Groq API key not found. AI features will be disabled.")
    
    def is_available(self) -> bool:
        """Check if Groq client is available"""
        return self.client is not None
    
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
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Use Llama 3 model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer with expertise in creating compelling professional summaries. Create concise, impactful summaries that highlight key strengths and align with job requirements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
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
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor expert at matching projects to job requirements. Analyze projects and select the most relevant ones based on the job description."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.3
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
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume optimizer. Enhance content to better align with job requirements while maintaining truthfulness and impact."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.5
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
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor. Analyze job descriptions and recommend relevant skills that would strengthen a candidate's profile."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.4
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
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer. Reframe content to be more impactful, professional, and ATS-friendly while maintaining truthfulness."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.6
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
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer. Create compelling professional summaries that can be iteratively improved based on user feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
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
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a job market analyst. Extract key requirements, skills, and priorities from job descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return self._parse_job_analysis(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error analyzing job posting: {e}")
            return {}
    
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