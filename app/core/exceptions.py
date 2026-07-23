class BusinessPlanException(Exception):
    """Base exception for Business Plan AI."""
    pass


class LLMException(BusinessPlanException):
    """Raised when there is an issue with LLM generation."""
    pass


class ValidationError(BusinessPlanException):
    """Raised when input validation fails."""
    pass


class SearchException(BusinessPlanException):
    """Raised when web search fails."""
    pass
