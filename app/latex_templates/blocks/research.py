from typing import Dict, Any
from .experience import ExperienceBlock

class ResearchBlock(ExperienceBlock):
    """Research experience section block (inherits from ExperienceBlock)"""
    
    def __init__(self, template_style: str = "arpan"):
        super().__init__(template_style, experience_type="research")