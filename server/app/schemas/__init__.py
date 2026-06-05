"""
Pydantic schemas for API validation.
Separate from ORM models (app/models/).

These define request/response formats for FastAPI endpoints.
Use for:
  - Request body validation
  - Response serialization
  - OpenAPI/Swagger documentation
  - Type hints

Example:
    from app.schemas import UserCreate, UserResponse
    
    @app.post("/users", response_model=UserResponse)
    def create_user(user: UserCreate):
        ...
"""

from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserRoleEnum,
    ErrorResponse,
)

from .exam import (
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ExamListResponse,
    ExamDetailResponse,
    ExamStatusEnum,
)

from .rubric import (
    RubricCreate,
    RubricUpdate,
    RubricResponse,
    CriterionBase,
)

from .submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
    SubmissionListResponse,
    SubmissionStatusEnum,
)

from .answer_region import (
    AnswerRegionCreate,
    AnswerRegionUpdate,
    AnswerRegionResponse,
    AnswerRegionListResponse,
)

from .grade import (
    GradeCreate,
    GradeUpdate,
    GradeResponse,
    GradeApprove,
    GradeOverride,
    GradeQueueResponse,
    GradeQueueListResponse,
    TAStatusEnum,
    CriterionResultBase,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "UserRoleEnum",
    "ErrorResponse",
    # Exam
    "ExamCreate",
    "ExamUpdate",
    "ExamResponse",
    "ExamListResponse",
    "ExamDetailResponse",
    "ExamStatusEnum",
    # Rubric
    "RubricCreate",
    "RubricUpdate",
    "RubricResponse",
    "CriterionBase",
    # Submission
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionResponse",
    "SubmissionListResponse",
    "SubmissionStatusEnum",
    # AnswerRegion
    "AnswerRegionCreate",
    "AnswerRegionUpdate",
    "AnswerRegionResponse",
    "AnswerRegionListResponse",
    # Grade
    "GradeCreate",
    "GradeUpdate",
    "GradeResponse",
    "GradeApprove",
    "GradeOverride",
    "GradeQueueResponse",
    "GradeQueueListResponse",
    "TAStatusEnum",
    "CriterionResultBase",
]