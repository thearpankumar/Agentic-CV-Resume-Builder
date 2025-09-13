from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://cv_user:cv_password@localhost:5432/cv_builder",
        description="PostgreSQL database connection URL"
    )

    # AI/Groq Configuration
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Groq API key for AI functionality"
    )
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Groq model to use for AI operations"
    )
    groq_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for Groq API responses"
    )
    groq_temperature: float = Field(
        default=0.7,
        description="Temperature setting for Groq model creativity"
    )

    # Application Configuration
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    streamlit_server_port: int = Field(
        default=8501,
        description="Streamlit server port"
    )

    # PDF Generation Configuration
    latex_timeout: int = Field(
        default=30,
        description="Timeout for LaTeX compilation in seconds"
    )
    pdf_temp_dir: Optional[str] = Field(
        default=None,
        description="Temporary directory for PDF generation"
    )

    # Session Configuration
    session_timeout: int = Field(
        default=3600,
        description="Session timeout in seconds"
    )

    @property
    def is_groq_available(self) -> bool:
        """Check if Groq API is configured and available."""
        return self.groq_api_key is not None and len(self.groq_api_key.strip()) > 0

    @property
    def database_config(self) -> dict:
        """Get database configuration for SQLAlchemy."""
        return {
            "url": self.database_url,
            "echo": self.debug,
        }

    def get_groq_config(self) -> dict:
        """Get Groq configuration dictionary."""
        if not self.is_groq_available:
            return {}

        return {
            "api_key": self.groq_api_key,
            "model": self.groq_model,
            "max_tokens": self.groq_max_tokens,
            "temperature": self.groq_temperature,
        }


# Global settings instance
settings = Settings()