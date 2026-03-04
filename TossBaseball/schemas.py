from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# 1. 유저 관련 규격
class UserCreate(BaseModel):
    email: EmailStr  # Pydantic이 이메일 형식을 자동으로 검사합니다
    name: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 Pydantic 모델로 변환 허용

# 2. 메모 관련 규격
class MemoCreate(BaseModel):
    title: str
    content: str

class MemoOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    # JOIN 조회를 위해 작성자 정보를 포함 (Optional)
    user: Optional[UserOut] = None 

    class Config:
        from_attributes = True

# 3. 공통 에러 응답 규격 (요구사항 반영)
class ErrorResponse(BaseModel):
    error: str

# step2

# 1. 반응 요청용 스키마 (POST /memos/{memo_id}/reactions 에서 사용)
class ReactionRequest(BaseModel):
    user_id: int
    reaction: str  # "like", "dislike", "cancel" 중 하나가 들어옴

# 2. 2단계 메모 출력용 스키마 (GET /memos 에서 사용)
class MemoOutV2(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    like_count: int      # 집계된 좋아요 개수
    dislike_count: int   # 집계된 싫어요 개수

    class Config:
        from_attributes = True # SQLAlchemy 모델을 Pydantic으로 변환 허용