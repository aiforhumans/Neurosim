"""
Error handling utilities for NeuroSim.

This module provides centralized error handling and exception management
for the NeuroSim application. It includes custom exceptions, error
recovery strategies, and consistent error reporting.
"""

import functools
import logging
import traceback
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union
from datetime import datetime

F = TypeVar('F', bound=Callable[..., Any])


class NeuroSimError(Exception):
    """Base exception for NeuroSim-specific errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.cause = cause


class AgentError(NeuroSimError):
    """Raised when an agent encounters an error during operation."""
    pass


class ConfigurationError(NeuroSimError):
    """Raised when there's a configuration-related error."""
    pass


class MemoryError(NeuroSimError):
    """Raised when memory operations fail."""
    pass


class UIError(NeuroSimError):
    """Raised when UI operations fail."""
    pass


class ValidationError(NeuroSimError):
    """Raised when input validation fails."""
    pass


def handle_exceptions(
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False
) -> Callable[[F], F]:
    """
    Decorator to handle exceptions in functions.
    
    Args:
        exception_types: Tuple of exception types to catch
        default_return: Value to return if an exception occurs
        log_errors: Whether to log caught exceptions
        reraise: Whether to reraise the exception after handling
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                if log_errors:
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"Exception in {func.__name__}: {e}")
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                
                return default_return
        return wrapper
    return decorator


def safe_call(func: Callable, *args, default=None, log_errors=True, **kwargs):
    """
    Safely call a function with error handling.
    
    Args:
        func: Function to call
        *args: Arguments to pass to function
        default: Default value to return on error
        log_errors: Whether to log errors
        **kwargs: Keyword arguments to pass to function
        
    Returns:
        Function result or default value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger = logging.getLogger(func.__module__)
            logger.error(f"Safe call failed for {func.__name__}: {e}")
        return default


class ErrorContext:
    """Context manager for handling errors with additional context."""
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        self.operation = operation
        self.logger = logger or logging.getLogger(__name__)
        self.error: Optional[Exception] = None
    
    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            self.logger.error(f"Operation '{self.operation}' failed: {exc_val}")
            # Don't suppress the exception
        else:
            self.logger.debug(f"Operation completed successfully: {self.operation}")
        return False


def validate_input(value: Any, validator: Callable[[Any], bool], error_msg: str) -> None:
    """
    Validate input using a validator function.
    
    Args:
        value: Value to validate
        validator: Function that returns True if value is valid
        error_msg: Error message to raise if validation fails
        
    Raises:
        ValidationError: If validation fails
    """
    if not validator(value):
        raise ValidationError(error_msg)


def format_error_for_user(error: Exception) -> str:
    """
    Format an error message for display to users.
    
    Args:
        error: Exception to format
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, NeuroSimError):
        return f"NeuroSim Error: {error.message}"
    elif isinstance(error, (ConnectionError, TimeoutError)):
        return "Connection error: Unable to reach the AI service. Please check your network connection and try again."
    elif isinstance(error, FileNotFoundError):
        return "File not found: A required file is missing. Please check your configuration."
    elif isinstance(error, PermissionError):
        return "Permission error: Unable to access a required resource. Please check file permissions."
    else:
        return f"An unexpected error occurred: {str(error)}"


def create_error_response(error: Exception, request_id: Optional[str] = None) -> dict:
    """
    Create a standardized error response dictionary.
    
    Args:
        error: Exception that occurred
        request_id: Optional request identifier
        
    Returns:
        Dictionary containing error details
    """
    response = {
        "error": True,
        "error_type": type(error).__name__,
        "message": format_error_for_user(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if request_id:
        response["request_id"] = request_id
    
    if isinstance(error, NeuroSimError) and error.error_code:
        response["error_code"] = error.error_code
    
    return response
