from typing import Dict, Any, List, Optional, Tuple
import streamlit as st
from .groq_client import GroqClient
from database.queries import SummaryQueries
from database.connection import get_db_session

class ContentOptimizer:
    """Handles AI-powered content optimization for resumes"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def optimize_resume_for_job(
        self,
        user_data: Dict[str, Any],
        job_description: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Optimize entire resume content for a specific job
        Returns optimized user data
        """
        if not self.groq_client.is_available():
            st.warning("AI optimization not available. Using original content.")
            return user_data
        
        optimized_data = user_data.copy()
        
        # Generate professional summary
        with st.spinner("🤖 Generating professional summary..."):
            summary = self.groq_client.generate_professional_summary(
                user_data, job_description
            )
            
            if summary:
                # Save to database
                self._save_professional_summary(user_id, job_description, summary)
                optimized_data['professional_summaries'] = [
                    {'generated_summary': summary, 'job_description': job_description}
                ]
                st.success("✅ Professional summary generated!")
        
        # Select best projects
        projects = user_data.get('projects', [])
        if projects:
            with st.spinner("🤖 Selecting most relevant projects..."):
                selected_projects = self.groq_client.select_best_projects(
                    projects, job_description, max_projects=3
                )
                optimized_data['projects'] = selected_projects
                st.success(f"✅ Selected {len(selected_projects)} most relevant projects!")
        
        # Optimize experience descriptions
        if user_data.get('professional_experience'):
            with st.spinner("🤖 Optimizing experience descriptions..."):
                optimized_experience = self._optimize_experience_descriptions(
                    user_data['professional_experience'], job_description
                )
                optimized_data['professional_experience'] = optimized_experience
                st.success("✅ Experience descriptions optimized!")
        
        return optimized_data
    
    def generate_summary_for_job(
        self,
        user_data: Dict[str, Any],
        job_description: str,
        user_id: int
    ) -> Optional[str]:
        """Generate professional summary for specific job"""
        if not self.groq_client.is_available():
            return None
        
        summary = self.groq_client.generate_professional_summary(
            user_data, job_description
        )
        
        if summary and user_id:
            self._save_professional_summary(user_id, job_description, summary)
        
        return summary
    
    def get_project_recommendations(
        self,
        projects: List[Dict[str, Any]],
        job_description: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Get project recommendations and explanations
        Returns: (selected_projects, reasons)
        """
        if not self.groq_client.is_available():
            return projects[:3], ["AI not available"]
        
        selected_projects = self.groq_client.select_best_projects(
            projects, job_description, max_projects=3
        )
        
        # Generate simple reasons (this could be enhanced)
        reasons = [
            f"Selected {len(selected_projects)} most relevant projects based on job requirements",
            "Projects ranked by technology stack alignment",
            "Focused on projects demonstrating required skills"
        ]
        
        return selected_projects, reasons
    
    def get_skills_gap_analysis(
        self,
        current_skills: List[str],
        job_description: str
    ) -> Tuple[List[str], List[str]]:
        """
        Analyze skills gap and provide recommendations
        Returns: (recommended_skills, improvement_areas)
        """
        if not self.groq_client.is_available():
            return [], []
        
        recommended_skills = self.groq_client.generate_skills_recommendations(
            current_skills, job_description
        )
        
        # Analyze improvement areas (simplified)
        improvement_areas = self._analyze_skill_improvements(
            current_skills, recommended_skills
        )
        
        return recommended_skills, improvement_areas
    
    def optimize_single_project(
        self,
        project: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """Optimize a single project description for job alignment"""
        if not self.groq_client.is_available():
            return project
        
        optimized_project = project.copy()
        
        # Optimize description
        if project.get('description'):
            optimized_description = self.groq_client.optimize_content_for_job(
                project['description'],
                "project description",
                job_description
            )
            
            if optimized_description:
                optimized_project['description'] = optimized_description
        
        return optimized_project
    
    def optimize_experience_item(
        self,
        experience: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """Optimize a single experience item for job alignment"""
        if not self.groq_client.is_available():
            return experience
        
        optimized_exp = experience.copy()
        
        # Optimize description
        if experience.get('description'):
            optimized_description = self.groq_client.optimize_content_for_job(
                experience['description'],
                "professional experience",
                job_description
            )
            
            if optimized_description:
                optimized_exp['description'] = optimized_description
        
        return optimized_exp
    
    def _optimize_experience_descriptions(
        self,
        experiences: List[Dict[str, Any]],
        job_description: str
    ) -> List[Dict[str, Any]]:
        """Optimize all experience descriptions"""
        optimized_experiences = []
        
        for exp in experiences:
            optimized_exp = self.optimize_experience_item(exp, job_description)
            optimized_experiences.append(optimized_exp)
        
        return optimized_experiences
    
    def _save_professional_summary(
        self,
        user_id: int,
        job_description: str,
        summary: str
    ) -> bool:
        """Save professional summary to database"""
        try:
            session = next(get_db_session())
            summary_data = {
                'job_description': job_description,
                'generated_summary': summary
            }
            SummaryQueries.create_professional_summary(session, user_id, summary_data)
            return True
        except Exception as e:
            st.error(f"Error saving summary: {e}")
            return False
    
    def _analyze_skill_improvements(
        self,
        current_skills: List[str],
        recommended_skills: List[str]
    ) -> List[str]:
        """Analyze and suggest skill improvement areas"""
        improvement_areas = []
        
        # Simple analysis based on recommended skills
        for skill in recommended_skills:
            if skill.lower() not in [s.lower() for s in current_skills]:
                improvement_areas.append(f"Consider learning {skill}")
        
        return improvement_areas[:3]  # Limit to top 3
    
    def get_optimization_suggestions(
        self,
        user_data: Dict[str, Any],
        job_description: str = ""
    ) -> List[str]:
        """Get general optimization suggestions for the resume"""
        suggestions = []
        
        # Check for missing sections
        if not user_data.get('professional_summaries'):
            suggestions.append("📝 Add a professional summary to highlight your key strengths")
        
        projects = user_data.get('projects', [])
        if len(projects) < 2:
            suggestions.append("🚀 Add more projects to showcase your technical skills")
        
        experience = user_data.get('professional_experience', [])
        if not experience:
            suggestions.append("💼 Add professional experience to strengthen your profile")
        
        skills = user_data.get('technical_skills', [])
        if len(skills) < 3:
            suggestions.append("⚡ Add more technical skill categories")
        
        # Content quality suggestions
        if projects:
            for project in projects:
                if not project.get('technologies'):
                    suggestions.append("🔧 Add technology stacks to your projects")
                    break
        
        # AI-specific suggestions if available
        if self.groq_client.is_available() and job_description:
            suggestions.append("🤖 Use AI optimization to tailor your resume for this job")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def estimate_ats_compatibility(self, user_data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Estimate ATS (Applicant Tracking System) compatibility
        Returns: (score_out_of_100, improvement_suggestions)
        """
        score = 0
        suggestions = []
        
        # Check for required sections
        if user_data.get('user', {}).get('name'):
            score += 20
        else:
            suggestions.append("Add your full name")
        
        if user_data.get('user', {}).get('email'):
            score += 15
        else:
            suggestions.append("Add your email address")
        
        if user_data.get('technical_skills'):
            score += 20
        else:
            suggestions.append("Add technical skills section")
        
        if user_data.get('professional_experience'):
            score += 25
        else:
            suggestions.append("Add professional experience")
        
        if user_data.get('projects'):
            score += 15
        else:
            suggestions.append("Add projects section")
        
        # Additional checks
        if user_data.get('education'):
            score += 5
        
        return min(score, 100), suggestions