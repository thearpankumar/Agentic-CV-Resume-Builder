from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from .models import (
    User, Project, ProfessionalExperience, ResearchExperience,
    Education, TechnicalSkill, Certification, ProfessionalSummary,
    ResumeConfiguration
)

class UserQueries:
    @staticmethod
    def create_user(session: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return session.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return session.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(session: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            session.commit()
            session.refresh(user)
        return user

class ProjectQueries:
    @staticmethod
    def create_project(session: Session, user_id: int, project_data: Dict[str, Any]) -> Project:
        """Create a new project"""
        project_data['user_id'] = user_id
        project = Project(**project_data)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project
    
    @staticmethod
    def get_user_projects(session: Session, user_id: int) -> List[Project]:
        """Get all projects for a user ordered by display_order"""
        return session.query(Project).filter(
            Project.user_id == user_id
        ).order_by(Project.display_order, Project.created_at.desc()).all()
    
    @staticmethod
    def update_project(session: Session, project_id: int, project_data: Dict[str, Any]) -> Optional[Project]:
        """Update project information"""
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            for key, value in project_data.items():
                setattr(project, key, value)
            session.commit()
            session.refresh(project)
        return project
    
    @staticmethod
    def delete_project(session: Session, project_id: int) -> bool:
        """Delete a project"""
        project = session.query(Project).filter(Project.id == project_id).first()
        if project:
            session.delete(project)
            session.commit()
            return True
        return False

class ExperienceQueries:
    @staticmethod
    def create_professional_experience(session: Session, user_id: int, exp_data: Dict[str, Any]) -> ProfessionalExperience:
        """Create professional experience"""
        exp_data['user_id'] = user_id
        experience = ProfessionalExperience(**exp_data)
        session.add(experience)
        session.commit()
        session.refresh(experience)
        return experience
    
    @staticmethod
    def create_research_experience(session: Session, user_id: int, exp_data: Dict[str, Any]) -> ResearchExperience:
        """Create research experience"""
        exp_data['user_id'] = user_id
        experience = ResearchExperience(**exp_data)
        session.add(experience)
        session.commit()
        session.refresh(experience)
        return experience
    
    @staticmethod
    def get_professional_experience(session: Session, user_id: int) -> List[ProfessionalExperience]:
        """Get all professional experience for a user"""
        return session.query(ProfessionalExperience).filter(
            ProfessionalExperience.user_id == user_id
        ).order_by(ProfessionalExperience.display_order, ProfessionalExperience.created_at.desc()).all()
    
    @staticmethod
    def get_research_experience(session: Session, user_id: int) -> List[ResearchExperience]:
        """Get all research experience for a user"""
        return session.query(ResearchExperience).filter(
            ResearchExperience.user_id == user_id
        ).order_by(ResearchExperience.display_order, ResearchExperience.created_at.desc()).all()
    
    @staticmethod
    def update_professional_experience(session: Session, experience_id: int, exp_data: Dict[str, Any]) -> Optional[ProfessionalExperience]:
        """Update professional experience information"""
        experience = session.query(ProfessionalExperience).filter(ProfessionalExperience.id == experience_id).first()
        if experience:
            for key, value in exp_data.items():
                setattr(experience, key, value)
            session.commit()
            session.refresh(experience)
        return experience

class EducationQueries:
    @staticmethod
    def create_education(session: Session, user_id: int, edu_data: Dict[str, Any]) -> Education:
        """Create education entry"""
        edu_data['user_id'] = user_id
        education = Education(**edu_data)
        session.add(education)
        session.commit()
        session.refresh(education)
        return education
    
    @staticmethod
    def get_user_education(session: Session, user_id: int) -> List[Education]:
        """Get all education for a user"""
        return session.query(Education).filter(
            Education.user_id == user_id
        ).order_by(Education.display_order, Education.created_at.desc()).all()

class SkillsQueries:
    @staticmethod
    def create_technical_skill(session: Session, user_id: int, skill_data: Dict[str, Any]) -> TechnicalSkill:
        """Create technical skill category"""
        skill_data['user_id'] = user_id
        skill = TechnicalSkill(**skill_data)
        session.add(skill)
        session.commit()
        session.refresh(skill)
        return skill
    
    @staticmethod
    def get_user_skills(session: Session, user_id: int) -> List[TechnicalSkill]:
        """Get all technical skills for a user"""
        return session.query(TechnicalSkill).filter(
            TechnicalSkill.user_id == user_id
        ).order_by(TechnicalSkill.display_order, TechnicalSkill.created_at.desc()).all()

class CertificationQueries:
    @staticmethod
    def create_certification(session: Session, user_id: int, cert_data: Dict[str, Any]) -> Certification:
        """Create certification"""
        cert_data['user_id'] = user_id
        certification = Certification(**cert_data)
        session.add(certification)
        session.commit()
        session.refresh(certification)
        return certification
    
    @staticmethod
    def get_user_certifications(session: Session, user_id: int) -> List[Certification]:
        """Get all certifications for a user"""
        return session.query(Certification).filter(
            Certification.user_id == user_id
        ).order_by(Certification.display_order, Certification.created_at.desc()).all()

class SummaryQueries:
    @staticmethod
    def create_professional_summary(session: Session, user_id: int, summary_data: Dict[str, Any]) -> ProfessionalSummary:
        """Create professional summary"""
        summary_data['user_id'] = user_id
        summary = ProfessionalSummary(**summary_data)
        session.add(summary)
        session.commit()
        session.refresh(summary)
        return summary
    
    @staticmethod
    def get_user_summaries(session: Session, user_id: int) -> List[ProfessionalSummary]:
        """Get all professional summaries for a user"""
        return session.query(ProfessionalSummary).filter(
            ProfessionalSummary.user_id == user_id
        ).order_by(ProfessionalSummary.created_at.desc()).all()

class ResumeConfigurationQueries:
    @staticmethod
    def create_resume_config(session: Session, user_id: int, config_data: Dict[str, Any]) -> ResumeConfiguration:
        """Create resume configuration"""
        config_data['user_id'] = user_id
        config = ResumeConfiguration(**config_data)
        session.add(config)
        session.commit()
        session.refresh(config)
        return config
    
    @staticmethod
    def get_user_configs(session: Session, user_id: int) -> List[ResumeConfiguration]:
        """Get all resume configurations for a user"""
        return session.query(ResumeConfiguration).filter(
            ResumeConfiguration.user_id == user_id
        ).order_by(ResumeConfiguration.updated_at.desc()).all()
    
    @staticmethod
    def get_default_config(session: Session, user_id: int) -> Optional[ResumeConfiguration]:
        """Get default resume configuration for a user"""
        return session.query(ResumeConfiguration).filter(
            and_(ResumeConfiguration.user_id == user_id, ResumeConfiguration.name == "Default")
        ).first()