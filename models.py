from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 관계 설정: 한 유저는 여러 메모를 가질 수 있음 (1:N)
    memos = relationship("Memo", back_populates="author", cascade="all, delete")

class Memo(Base):
    __tablename__ = "memos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 관계 설정: 메모는 한 명의 작성자에게 속함
    author = relationship("User", back_populates="memos")
    reactions = relationship("MemoReaction", back_populates="memo", cascade="all, delete")

class MemoReaction(Base):
    __tablename__ = "memo_reactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # 어떤 메모에 대한 반응인가? (CASCADE 설정으로 메모 삭제 시 함께 삭제)
    memo_id = Column(BigInteger, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False)
    # 누가 반응을 남겼는가?
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # 반응 종류: 'like' 또는 'dislike' (과제 규격상 Text/String으로 처리)
    reaction = Column(Text, nullable=False) 
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # [내실 포인트] 한 유저가 한 메모에 1개의 반응만 남기도록 물리적으로 강제 (UPSERT의 근거)
    __table_args__ = (
        UniqueConstraint('memo_id', 'user_id', name='idx_memo_user_reaction_unique'),
        # 인덱스 추가로 조회 성능 향상
        Index("idx_reactions_memo_id", "memo_id"),
    )

    # 관계 설정 (필요 시 조회용)
    memo = relationship("Memo", back_populates="reactions")


# 인덱스 설정 (요구사항 반영)
# 1. 특정 유저의 메모를 최신순으로 조회할 때 사용
Index("idx_memos_user_created_at", Memo.user_id, Memo.created_at.desc())
# 2. 모든 메모를 최신순으로 조회할 때 사용
Index("idx_memos_created_at", Memo.created_at.desc())