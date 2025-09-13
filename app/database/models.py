from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    phone = Column(String(50))
    linkedin_url = Column(String(255))
    github_url = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    professional_experience = relationship("ProfessionalExperience", back_populates="user", cascade="all, delete-orphan")
    research_experience = relationship("ResearchExperience", back_populates="user", cascade="all, delete-orphan")
    academic_collaborations = relationship("AcademicCollaboration", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    technical_skills = relationship("TechnicalSkill", back_populates="user", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="user", cascade="all, delete-orphan")
    professional_summaries = relationship("ProfessionalSummary", back_populates="user", cascade="all, delete-orphan")
    resume_configurations = relationship("ResumeConfiguration", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    technologies = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    project_url = Column(String(255))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")

class ProfessionalExperience(Base):
    __tablename__ = "professional_experience"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="professional_experience")

class ResearchExperience(Base):
    __tablename__ = "research_experience"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="research_experience")

class AcademicCollaboration(Base):
    __tablename__ = "academic_collaborations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_title = Column(String(255), nullable=False)
    collaboration_type = Column(String(100))  # Research, Publication, Conference, Workshop
    institution = Column(String(255))
    collaborators = Column(Text)  # Names of collaborators
    role = Column(String(255))  # User's role in the collaboration
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    publication_url = Column(String(255))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="academic_collaborations")

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    graduation_date = Column(String(50))
    gpa_percentage = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="education")

class TechnicalSkill(Base):
    __tablename__ = "technical_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(255), nullable=False)
    skills = Column(Text, nullable=False)  # comma-separated skills
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="technical_skills")

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255))
    date_obtained = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="certifications")

class ProfessionalSummary(Base):
    __tablename__ = "professional_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_description = Column(Text)
    generated_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="professional_summaries")

class ResumeConfiguration(Base):
    __tablename__ = "resume_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    template_style = Column(String(50), default='arpan')  # 'arpan' or 'simple'
    section_order = Column(Text)  # JSON array of section names in order
    active_sections = Column(Text)  # JSON array of active section names
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resume_configurations")
    
    def get_section_order(self) -> List[str]:
        """Get section order as list"""
        if self.section_order:
            return json.loads(self.section_order)
        return []
    
    def set_section_order(self, order: List[str]):
        """Set section order from list"""
        self.section_order = json.dumps(order)
    
    def get_active_sections(self) -> List[str]:
        """Get active sections as list"""
        if self.active_sections:
            return json.loads(self.active_sections)
        return []
    
    def set_active_sections(self, sections: List[str]):
        """Set active sections from list"""
        self.active_sections = json.dumps(sections)