import re
from typing import Dict, Any, List, Tuple, Optional

class DataValidator:
    """Validates user input data for resume generation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return True  # Optional field
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format (basic validation)"""
        if not phone:
            return True  # Optional field
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
        # Check if it contains only digits and + (for international)
        return re.match(r'^[\+]?[\d]{7,15}$', cleaned) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return True  # Optional field
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
        """Validate required field"""
        if not value or not value.strip():
            return False, f"{field_name} is required"
        return True, ""
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete user data"""
        errors = []
        
        # Validate required fields
        name = user_data.get('name', '')
        if not name or not name.strip():
            errors.append("Name is required")
        
        # Validate optional fields format
        email = user_data.get('email', '')
        if email and not DataValidator.validate_email(email):
            errors.append("Invalid email format")
        
        phone = user_data.get('phone', '')
        if phone and not DataValidator.validate_phone(phone):
            errors.append("Invalid phone number format")
        
        linkedin_url = user_data.get('linkedin_url', '')
        if linkedin_url and 'linkedin.com' not in linkedin_url:
            errors.append("Invalid LinkedIn URL format")

        github_url = user_data.get('github_url', '')
        if github_url and 'github.com' not in github_url:
            errors.append("Invalid GitHub URL format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_project_data(project_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate project data"""
        errors = []
        
        # Title is required
        title = project_data.get('title', '')
        if not title or not title.strip():
            errors.append("Project title is required")
        
        # Description is required
        description = project_data.get('description', '')
        if not description or not description.strip():
            errors.append("Project description is required")
        
        # Validate project URL if provided
        project_url = project_data.get('project_url', '')
        if project_url and not DataValidator.validate_url(project_url):
            errors.append("Invalid project URL format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_experience_data(exp_data: Dict[str, Any], exp_type: str = "professional") -> Tuple[bool, List[str]]:
        """Validate experience data"""
        errors = []
        
        if exp_type == "professional":
            # Company and position are required
            company = exp_data.get('company', '')
            if not company or not company.strip():
                errors.append("Company name is required")
            
            position = exp_data.get('position', '')
            if not position or not position.strip():
                errors.append("Position title is required")
        else:  # research
            # Title is required for research
            title = exp_data.get('title', '')
            if not title or not title.strip():
                errors.append("Research title is required")
        
        # Description is required
        description = exp_data.get('description', '')
        if not description or not description.strip():
            errors.append("Experience description is required")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_education_data(edu_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate education data"""
        errors = []
        
        # Degree is required
        degree = edu_data.get('degree', '')
        if not degree or not degree.strip():
            errors.append("Degree is required")
        
        # Institution is required
        institution = edu_data.get('institution', '')
        if not institution or not institution.strip():
            errors.append("Institution is required")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_skill_data(skill_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate technical skill data"""
        errors = []
        
        # Category is required
        category = skill_data.get('category', '')
        if not category or not category.strip():
            errors.append("Skill category is required")
        
        # Skills list is required
        skills = skill_data.get('skills', '')
        if not skills or not skills.strip():
            errors.append("Skills list is required")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input for LaTeX"""
        if not text:
            return ""
        
        # Remove potentially dangerous LaTeX commands
        text = re.sub(r'\\(?:input|include|usepackage|documentclass|begin|end)', '', text)
        
        # Limit length to prevent overly long content
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
    
    @staticmethod
    def validate_latex_syntax(latex_code: str) -> Tuple[bool, List[str]]:
        """Basic LaTeX syntax validation"""
        errors = []
        
        # Check for balanced braces
        open_braces = latex_code.count('{')
        close_braces = latex_code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening vs {close_braces} closing")
        
        # Check for required document structure
        if '\\begin{document}' not in latex_code:
            errors.append("Missing \\begin{document}")
        
        if '\\end{document}' not in latex_code:
            errors.append("Missing \\end{document}")
        
        # Check for potentially problematic commands
        dangerous_commands = ['\\input', '\\include', '\\write', '\\immediate']
        for cmd in dangerous_commands:
            if cmd in latex_code:
                errors.append(f"Potentially dangerous command found: {cmd}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_academic_collaboration_data(collab_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate academic collaboration data"""
        errors = []

        # Required fields
        if not collab_data.get('project_title', '').strip():
            errors.append("Project title is required")

        # Optional but validated fields
        if collab_data.get('publication_url'):
            if not DataValidator.validate_url(collab_data['publication_url']):
                errors.append("Invalid publication URL format")

        # Text length validation
        max_lengths = {
            'project_title': 255,
            'collaboration_type': 100,
            'institution': 255,
            'role': 255,
            'collaborators': 1000,
            'description': 2000,
            'start_date': 50,
            'end_date': 50,
            'publication_url': 255
        }

        for field, max_length in max_lengths.items():
            value = collab_data.get(field, '')
            if value and len(value) > max_length:
                errors.append(f"{field.replace('_', ' ').title()} must be less than {max_length} characters")

        # Validate collaboration type
        valid_types = ['Research', 'Publication', 'Conference', 'Workshop', 'Grant', 'Other']
        if collab_data.get('collaboration_type') and collab_data['collaboration_type'] not in valid_types:
            errors.append(f"Collaboration type must be one of: {', '.join(valid_types)}")

        return len(errors) == 0, errors