"""
Resume management service module for handling resume customization and storage.
"""
from .manager import ResumeManager
from .generator import ResumeGenerator

class ResumePriority:
    """Priority levels for resume customization."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2

# Resume file formats supported
SUPPORTED_FORMATS = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

__all__ = [
    'ResumeManager',
    'ResumeGenerator',
    'ResumePriority',
    'SUPPORTED_FORMATS'
]
