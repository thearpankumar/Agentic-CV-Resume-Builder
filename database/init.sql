-- Initialize CV Builder Database Schema

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table (user can have multiple projects)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    technologies VARCHAR(255),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    project_url VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Professional Experience table
CREATE TABLE professional_experience (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    description TEXT,
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research Experience table
CREATE TABLE research_experience (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Education table
CREATE TABLE education (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    graduation_date VARCHAR(50),
    gpa_percentage VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Technical Skills table
CREATE TABLE technical_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(255) NOT NULL, -- e.g., "Programming Languages", "Frameworks"
    skills TEXT NOT NULL, -- comma-separated skills
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Certifications table
CREATE TABLE certifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    issuer VARCHAR(255),
    date_obtained VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Professional Summaries (job-specific)
CREATE TABLE professional_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_description TEXT,
    generated_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume Configurations (for saving different resume layouts)
CREATE TABLE resume_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    template_style VARCHAR(50) DEFAULT 'arpan', -- 'arpan' or 'simple'
    section_order TEXT, -- JSON array of section names in order
    active_sections TEXT, -- JSON array of active section names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_professional_experience_user_id ON professional_experience(user_id);
CREATE INDEX idx_research_experience_user_id ON research_experience(user_id);
CREATE INDEX idx_education_user_id ON education(user_id);
CREATE INDEX idx_technical_skills_user_id ON technical_skills(user_id);
CREATE INDEX idx_certifications_user_id ON certifications(user_id);
CREATE INDEX idx_professional_summaries_user_id ON professional_summaries(user_id);
CREATE INDEX idx_resume_configurations_user_id ON resume_configurations(user_id);