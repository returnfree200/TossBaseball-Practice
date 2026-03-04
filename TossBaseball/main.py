from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# [추가] 입력 누락/형식 에러 시 과제 규격 {"error": "INVALID_INPUT"}으로 통일
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "INVALID_INPUT"},
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) POST /users
@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # email 중복 체크
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail={"error": "EMAIL_ALREADY_EXISTS"})
    
    new_user = models.User(email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2) POST /users/{user_id}/memos
@app.post("/users/{user_id}/memos", response_model=schemas.MemoOut)
def create_memo(user_id: int, memo: schemas.MemoCreate, db: Session = Depends(get_db)):
    # user_id 존재 여부 확인
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail={"error": "USER_NOT_FOUND"})
    
    new_memo = models.Memo(user_id=user_id, title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return new_memo

    

# 3) GET /memos (작성자 정보 대신 반응 개수 포함)
@app.get("/memos", response_model=List[schemas.MemoOutV2])
def read_all_memos(db: Session = Depends(get_db)):
    # 1단계의 joinedload 대신, LEFT OUTER JOIN과 GROUP BY를 사용합니다.
    # 반응이 없는 메모도 나와야 하므로 outerjoin이 필수입니다.
    results = db.query(
        models.Memo,
        func.count(models.MemoReaction.id).filter(models.MemoReaction.reaction == "like").label("like_count"),
        func.count(models.MemoReaction.id).filter(models.MemoReaction.reaction == "dislike").label("dislike_count")
    ).outerjoin(models.MemoReaction).group_by(models.Memo.id).all()

    # 쿼리 결과를 스키마 형식에 맞춰 리스트로 변환
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "title": m.title,
            "content": m.content,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
            "like_count": lc,
            "dislike_count": dc
        } for m, lc, dc in results
    ]    
    


# 4) GET /users/{user_id}/memos
@app.get("/users/{user_id}/memos", response_model=List[schemas.MemoOut])
def read_user_memos(user_id: int, db: Session = Depends(get_db)):
    # user_id 존재 여부 확인
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail={"error": "USER_NOT_FOUND"})
    
    return db.query(models.Memo).filter(models.Memo.user_id == user_id).all()


    # 5) POST /memos/{memo_id}/reactions
@app.post("/memos/{memo_id}/reactions")
def create_reaction(memo_id: int, req: schemas.ReactionRequest, db: Session = Depends(get_db)):
    # 1. 유저와 메모가 존재하는지 확인 (400 INVALID_ID)
    db_user = db.get(models.User, req.user_id)
    db_memo = db.get(models.Memo, memo_id)
    if not db_user or not db_memo:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ID"})

    # 2. cancel 요청 처리
    if req.reaction == "cancel":
        db.query(models.MemoReaction).filter(
            models.MemoReaction.memo_id == memo_id,
            models.MemoReaction.user_id == req.user_id
        ).delete()
        db.commit()
        return {"memo_id": memo_id, "user_id": req.user_id, "reaction": "none"}

    # 3. like / dislike 처리 (UPSERT 로직)
    # 기존 반응이 있는지 확인
    existing_reaction = db.query(models.MemoReaction).filter(
        models.MemoReaction.memo_id == memo_id,
        models.MemoReaction.user_id == req.user_id
    ).first()

    if existing_reaction:
        # 이미 있다면 상태 변경 (like -> dislike 등)
        existing_reaction.reaction = req.reaction
        existing_reaction.created_at = func.now() # 시간 갱신
    else:
        # 없다면 새로 생성
        new_reaction = models.MemoReaction(
            memo_id=memo_id, 
            user_id=req.user_id, 
            reaction=req.reaction
        )
        db.add(new_reaction)

    db.commit()
    return {"memo_id": memo_id, "user_id": req.user_id, "reaction": req.reaction}