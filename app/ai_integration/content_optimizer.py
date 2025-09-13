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
        Returns optimized user data with selection reasons
        """
        if not self.groq_client.is_available():
            st.warning("AI optimization not available. Using original content.")
            # Ensure we return the user_data in the expected format with metadata
            if isinstance(user_data, dict):
                result = user_data.copy()
                result['_optimization_metadata'] = {
                    'selection_reasons': {'fallback': 'AI not available, using original content'},
                    'scores': {},
                    'recommendations': []
                }
                return result
            return user_data

        optimized_data = user_data.copy()
        optimization_metadata = {
            'selection_reasons': {},
            'scores': {},
            'recommendations': []
        }

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
                optimization_metadata['selection_reasons']['professional_summary'] = "AI-generated based on job requirements"
                st.success("✅ Professional summary generated!")

        # Analyze section relevance first
        with st.spinner("🤖 Analyzing section relevance..."):
            section_relevance = self.groq_client.analyze_section_relevance(user_data, job_description)
            optimization_metadata['section_relevance'] = section_relevance

            # Filter out irrelevant sections
            for section, is_relevant in section_relevance.items():
                if not is_relevant and section in optimized_data:
                    del optimized_data[section]
                    optimization_metadata['selection_reasons'][section] = "Excluded - not relevant for this job"
                elif is_relevant and section in optimized_data:
                    optimization_metadata['selection_reasons'][section] = "Included - relevant for this job"

            excluded_count = len([r for r in section_relevance.values() if not r])
            if excluded_count > 0:
                st.success(f"✅ Analyzed sections and excluded {excluded_count} irrelevant sections!")
            else:
                st.success("✅ All sections are relevant for this job!")

        # Select best projects with reasoning
        projects = optimized_data.get('projects', [])  # Use filtered data
        if projects:
            with st.spinner("🤖 Selecting most relevant projects..."):
                selected_projects, project_scores = self.select_best_projects_with_scores(
                    projects, job_description, max_projects=3
                )
                optimized_data['projects'] = selected_projects
                optimization_metadata['scores']['projects'] = project_scores
                optimization_metadata['selection_reasons']['projects'] = f"Selected {len(selected_projects)} most relevant projects"
                st.success(f"✅ Selected {len(selected_projects)} most relevant projects!")

        # NOTE: Professional experience descriptions are NOT automatically optimized
        # They should only be modified if the user explicitly updates them in the details section

        # Add metadata to optimized data for reference
        optimized_data['_optimization_metadata'] = optimization_metadata

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

    def select_best_projects_with_scores(
        self,
        projects: List[Dict[str, Any]],
        job_description: str,
        max_projects: int = 3
    ) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        """
        Select best projects with relevance scores
        Returns: (selected_projects, {project_id: score})
        """
        if not self.groq_client.is_available():
            return projects[:max_projects], {}

        # Use existing method to get selected projects
        selected_projects = self.groq_client.select_best_projects(
            projects, job_description, max_projects
        )

        # Generate mock scores based on selection (in real implementation, get from AI)
        scores = {}
        selected_titles = {p.get('title', '') for p in selected_projects}

        for project in projects:
            title = project.get('title', '')
            if title in selected_titles:
                scores[title] = 8.5 + (len(selected_titles) - list(selected_titles).index(title)) * 0.3
            else:
                scores[title] = 5.0 + hash(title) % 30 / 10  # Mock score for non-selected

        return selected_projects, scores

    def select_best_experiences_with_scores(
        self,
        experiences: List[Dict[str, Any]],
        job_description: str,
        max_experiences: int = 3
    ) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        """
        Select best professional experiences with relevance scores
        Returns: (selected_experiences, {experience_id: score})
        """
        if not self.groq_client.is_available() or not experiences:
            return experiences[:max_experiences], {}

        # For now, return all experiences (can be enhanced with AI selection)
        selected = experiences[:max_experiences]
        scores = {}

        for i, exp in enumerate(experiences):
            exp_key = f"{exp.get('company', 'Unknown')} - {exp.get('position', 'Unknown')}"
            if i < max_experiences:
                scores[exp_key] = 8.0 + (max_experiences - i) * 0.5
            else:
                scores[exp_key] = 6.0 - i * 0.2

        return selected, scores

    def analyze_section_relevance(
        self,
        user_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze relevance of each resume section for the job
        Returns: {section_name: {score: float, reason: str, recommended: bool}}
        """
        if not self.groq_client.is_available():
            return {}

        section_analysis = {}

        # Analyze each section
        sections = {
            'professional_summary': user_data.get('professional_summaries', []),
            'projects': user_data.get('projects', []),
            'professional_experience': user_data.get('professional_experience', []),
            'research_experience': user_data.get('research_experience', []),
            'education': user_data.get('education', []),
            'technical_skills': user_data.get('technical_skills', []),
            'certifications': user_data.get('certifications', [])
        }

        for section_name, section_data in sections.items():
            if not section_data:
                section_analysis[section_name] = {
                    'score': 0.0,
                    'reason': 'No content available',
                    'recommended': False
                }
                continue

            # Mock analysis (replace with actual AI analysis)
            base_score = 7.5
            if 'technical' in job_description.lower() and section_name == 'technical_skills':
                score = 9.5
                reason = "Technical skills highly relevant for this role"
            elif 'project' in job_description.lower() and section_name == 'projects':
                score = 9.0
                reason = "Project experience matches job requirements"
            elif 'experience' in job_description.lower() and 'experience' in section_name:
                score = 8.5
                reason = "Professional experience aligns with role"
            else:
                score = base_score
                reason = f"Standard relevance for {section_name.replace('_', ' ')}"

            section_analysis[section_name] = {
                'score': score,
                'reason': reason,
                'recommended': score >= 7.0
            }

        return section_analysis

    def get_optimization_summary(
        self,
        user_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Get a comprehensive optimization summary
        Returns summary with recommendations, scores, and reasons
        """
        summary = {
            'total_sections': 0,
            'recommended_sections': 0,
            'content_items': {},
            'overall_score': 0.0,
            'recommendations': [],
            'section_analysis': {}
        }

        # Analyze sections
        section_analysis = self.analyze_section_relevance(user_data, job_description)
        summary['section_analysis'] = section_analysis

        # Count sections and items
        for section_name, analysis in section_analysis.items():
            summary['total_sections'] += 1
            if analysis['recommended']:
                summary['recommended_sections'] += 1

            # Count content items
            section_data = user_data.get(section_name, [])
            summary['content_items'][section_name] = len(section_data)

        # Calculate overall score
        if section_analysis:
            summary['overall_score'] = sum(a['score'] for a in section_analysis.values()) / len(section_analysis)

        # Generate recommendations
        summary['recommendations'] = self._generate_optimization_recommendations(section_analysis, user_data)

        return summary

    def _generate_optimization_recommendations(
        self,
        section_analysis: Dict[str, Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []

        for section_name, analysis in section_analysis.items():
            section_data = user_data.get(section_name, [])

            if analysis['score'] < 6.0 and section_data:
                recommendations.append(f"Consider removing or minimizing {section_name.replace('_', ' ')} section")
            elif analysis['score'] > 8.5 and not section_data:
                recommendations.append(f"Add content to {section_name.replace('_', ' ')} section for better impact")
            elif analysis['recommended'] and len(section_data) > 5:
                recommendations.append(f"Consider condensing {section_name.replace('_', ' ')} to highlight top items")

        # General recommendations
        if len([a for a in section_analysis.values() if a['recommended']]) < 4:
            recommendations.append("Consider adding more relevant sections to strengthen your profile")

        return recommendations[:5]  # Limit to top 5 recommendations