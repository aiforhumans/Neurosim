"""
Input validation utilities for NeuroSim.

This module provides comprehensive input validation for user messages,
configuration parameters, and API inputs to ensure data integrity
and security.
"""

import re
from typing import Any, Dict, List, Optional
from pathlib import Path

from neurosim.core.error_handling import ValidationError


def validate_user_message(message: str) -> str:
    """
    Validate and sanitize user input message.
    
    Args:
        message: Raw user message
        
    Returns:
        Sanitized message
        
    Raises:
        ValidationError: If message is invalid
    """
    if not isinstance(message, str):
        raise ValidationError("Message must be a string")
    
    # Strip whitespace
    message = message.strip()
    
    # Check for empty message
    if not message:
        raise ValidationError("Message cannot be empty")
    
    # Check message length
    if len(message) > 10000:  # 10k character limit
        raise ValidationError("Message too long (max 10,000 characters)")
    
    # Check for null bytes and other control characters
    if '\x00' in message or any(ord(c) < 32 and c not in '\n\r\t' for c in message):
        raise ValidationError("Message contains invalid characters")
    
    return message


def validate_emotion_values(mood: float, trust: float, energy: float) -> None:
    """
    Validate emotion state values.
    
    Args:
        mood: Mood value
        trust: Trust value  
        energy: Energy value
        
    Raises:
        ValidationError: If any value is invalid
    """
    for name, value in [("mood", mood), ("trust", trust), ("energy", energy)]:
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number")
        if not -1.0 <= value <= 1.0:
            raise ValidationError(f"{name} must be between -1.0 and 1.0")


def validate_model_name(model_name: str) -> str:
    """
    Validate model name format.
    
    Args:
        model_name: Model identifier
        
    Returns:
        Validated model name
        
    Raises:
        ValidationError: If model name is invalid
    """
    if not isinstance(model_name, str):
        raise ValidationError("Model name must be a string")
    
    model_name = model_name.strip()
    if not model_name:
        raise ValidationError("Model name cannot be empty")
    
    # Allow alphanumeric, hyphens, underscores, forward slashes, and dots
    if not re.match(r'^[a-zA-Z0-9/_.-]+$', model_name):
        raise ValidationError("Model name contains invalid characters")
    
    if len(model_name) > 100:
        raise ValidationError("Model name too long (max 100 characters)")
    
    return model_name


def validate_api_key(api_key: str) -> str:
    """
    Validate API key format.
    
    Args:
        api_key: API key string
        
    Returns:
        Validated API key
        
    Raises:
        ValidationError: If API key is invalid
    """
    if not isinstance(api_key, str):
        raise ValidationError("API key must be a string")
    
    api_key = api_key.strip()
    if not api_key:
        raise ValidationError("API key cannot be empty")
    
    # Basic format validation - should be reasonable length and no obvious issues
    if len(api_key) < 10:
        raise ValidationError("API key appears too short")
    
    if len(api_key) > 200:
        raise ValidationError("API key too long")
    
    # Check for whitespace or newlines
    if any(c.isspace() for c in api_key):
        raise ValidationError("API key cannot contain whitespace")
    
    return api_key


def validate_url(url: str) -> str:
    """
    Validate URL format.
    
    Args:
        url: URL string
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError("URL must be a string")
    
    url = url.strip()
    if not url:
        raise ValidationError("URL cannot be empty")
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*'  # domain
        r'[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?'  # host
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValidationError("Invalid URL format")
    
    return url


def validate_file_path(file_path: str, must_exist: bool = False, must_be_writable: bool = False) -> Path:
    """
    Validate file path.
    
    Args:
        file_path: File path string
        must_exist: Whether file must already exist
        must_be_writable: Whether path must be writable
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(file_path, str):
        raise ValidationError("File path must be a string")
    
    try:
        path = Path(file_path)
    except (ValueError, OSError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    if must_exist and not path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    if must_be_writable:
        try:
            # Check if parent directory is writable
            parent = path.parent
            if not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
            
            # Try to create a temporary file
            test_file = parent / f".neurosim_write_test_{id(path)}"
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise ValidationError(f"Path not writable: {e}")
    
    return path


def validate_temperature(temperature: float) -> float:
    """
    Validate temperature parameter.
    
    Args:
        temperature: Temperature value
        
    Returns:
        Validated temperature
        
    Raises:
        ValidationError: If temperature is invalid
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError("Temperature must be a number")
    
    if not 0.0 <= temperature <= 2.0:
        raise ValidationError("Temperature must be between 0.0 and 2.0")
    
    return float(temperature)


def validate_max_tokens(max_tokens: int) -> int:
    """
    Validate max tokens parameter.
    
    Args:
        max_tokens: Maximum tokens value
        
    Returns:
        Validated max tokens
        
    Raises:
        ValidationError: If max tokens is invalid
    """
    if not isinstance(max_tokens, int):
        raise ValidationError("Max tokens must be an integer")
    
    if max_tokens < 1:
        raise ValidationError("Max tokens must be positive")
    
    if max_tokens > 100000:  # Reasonable upper limit
        raise ValidationError("Max tokens too large (max 100,000)")
    
    return max_tokens


def validate_config_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary")
    
    validated_config = {}
    
    # Validate common configuration keys
    if 'model' in config:
        validated_config['model'] = validate_model_name(config['model'])
    
    if 'api_key' in config:
        validated_config['api_key'] = validate_api_key(config['api_key'])
    
    if 'base_url' in config:
        validated_config['base_url'] = validate_url(config['base_url'])
    
    if 'temperature' in config:
        validated_config['temperature'] = validate_temperature(config['temperature'])
    
    if 'max_tokens' in config:
        validated_config['max_tokens'] = validate_max_tokens(config['max_tokens'])
    
    # Copy other valid keys (basic validation)
    for key, value in config.items():
        if key not in validated_config:
            if not isinstance(key, str):
                raise ValidationError("Configuration keys must be strings")
            if len(key) > 100:
                raise ValidationError("Configuration key too long")
            validated_config[key] = value
    
    return validated_config


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return "unnamed_file"
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    
    # Ensure it's not empty
    if not filename.strip():
        filename = "unnamed_file"
    
    return filename.strip()
