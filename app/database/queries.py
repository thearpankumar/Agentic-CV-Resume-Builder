from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from .models import (
    User, Project, ProfessionalExperience, ResearchExperience, AcademicCollaboration,
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

    @staticmethod
    def update_research_experience(session: Session, research_id: int, research_data: Dict[str, Any]) -> Optional[ResearchExperience]:
        """Update research experience information"""
        research = session.query(ResearchExperience).filter(ResearchExperience.id == research_id).first()
        if research:
            for key, value in research_data.items():
                setattr(research, key, value)
            session.commit()
            session.refresh(research)
        return research

    @staticmethod
    def delete_research_experience(session: Session, research_id: int) -> bool:
        """Delete a research experience"""
        research = session.query(ResearchExperience).filter(ResearchExperience.id == research_id).first()
        if research:
            session.delete(research)
            session.commit()
            return True
        return False

class AcademicCollaborationQueries:
    @staticmethod
    def create_academic_collaboration(session: Session, user_id: int, collab_data: Dict[str, Any]) -> AcademicCollaboration:
        """Create academic collaboration"""
        collab_data['user_id'] = user_id
        collaboration = AcademicCollaboration(**collab_data)
        session.add(collaboration)
        session.commit()
        session.refresh(collaboration)
        return collaboration

    @staticmethod
    def get_user_academic_collaborations(session: Session, user_id: int) -> List[AcademicCollaboration]:
        """Get all academic collaborations for a user"""
        return session.query(AcademicCollaboration).filter(
            AcademicCollaboration.user_id == user_id
        ).order_by(AcademicCollaboration.display_order, AcademicCollaboration.created_at.desc()).all()

    @staticmethod
    def update_academic_collaboration(session: Session, collaboration_id: int, collab_data: Dict[str, Any]) -> Optional[AcademicCollaboration]:
        """Update academic collaboration information"""
        collaboration = session.query(AcademicCollaboration).filter(AcademicCollaboration.id == collaboration_id).first()
        if collaboration:
            for key, value in collab_data.items():
                setattr(collaboration, key, value)
            session.commit()
            session.refresh(collaboration)
        return collaboration

    @staticmethod
    def delete_academic_collaboration(session: Session, collaboration_id: int) -> bool:
        """Delete an academic collaboration"""
        collaboration = session.query(AcademicCollaboration).filter(AcademicCollaboration.id == collaboration_id).first()
        if collaboration:
            session.delete(collaboration)
            session.commit()
            return True
        return False

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

    @staticmethod
    def update_education(session: Session, education_id: int, edu_data: Dict[str, Any]) -> Optional[Education]:
        """Update education information"""
        education = session.query(Education).filter(Education.id == education_id).first()
        if education:
            for key, value in edu_data.items():
                setattr(education, key, value)
            session.commit()
            session.refresh(education)
        return education

    @staticmethod
    def delete_education(session: Session, education_id: int) -> bool:
        """Delete an education record"""
        education = session.query(Education).filter(Education.id == education_id).first()
        if education:
            session.delete(education)
            session.commit()
            return True
        return False

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

    @staticmethod
    def update_technical_skill(session: Session, skill_id: int, skill_data: Dict[str, Any]) -> Optional[TechnicalSkill]:
        """Update technical skill information"""
        skill = session.query(TechnicalSkill).filter(TechnicalSkill.id == skill_id).first()
        if skill:
            for key, value in skill_data.items():
                setattr(skill, key, value)
            session.commit()
            session.refresh(skill)
        return skill

    @staticmethod
    def delete_technical_skill(session: Session, skill_id: int) -> bool:
        """Delete a technical skill record"""
        skill = session.query(TechnicalSkill).filter(TechnicalSkill.id == skill_id).first()
        if skill:
            session.delete(skill)
            session.commit()
            return True
        return False

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

    @staticmethod
    def update_certification(session: Session, certification_id: int, cert_data: Dict[str, Any]) -> Optional[Certification]:
        """Update certification information"""
        certification = session.query(Certification).filter(Certification.id == certification_id).first()
        if certification:
            for key, value in cert_data.items():
                setattr(certification, key, value)
            session.commit()
            session.refresh(certification)
        return certification

    @staticmethod
    def delete_certification(session: Session, certification_id: int) -> bool:
        """Delete a certification record"""
        certification = session.query(Certification).filter(Certification.id == certification_id).first()
        if certification:
            session.delete(certification)
            session.commit()
            return True
        return False

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