# ⚾ TossBaseball-Practice (FastAPI-Study)

> **안내**: 이 프로젝트는 FastAPI와 PostgreSQL의 기초를 익히기 위한 연습용 저장소입니다. 실전 프로젝트는 https://github.com/returnfree200/TossBaseball-Backend (새 주소)에서 진행 중입니다.

**TossBaseball-Practice**는 KBO 리그 경기 결과 예측 데이터를 체계적으로 관리하고 집계하기 위한 고성능 백엔드 시스템입니다. 본 프로젝트는 **'앱인토스(App-in-Toss)'** 플랫폼 정식 등재를 목표로 본격적인 개발을 진행하기 전, 기술 검증 및 아키텍처 구상을 위한 **연습 및 테스트(Practice) 단계**의 프로젝트입니다. 대규모 승부예측 데이터를 안정적으로 처리할 수 있는 기반을 마련하는 것을 지향합니다.

## 🎯 프로젝트 핵심 목표
* **정밀한 승부예측 데이터 모델링**: 유저별 예측 데이터를 구조화하여 향후 정산 및 스코어링 알고리즘 적용이 용이하도록 설계
* **데이터 무결성 확보**: PostgreSQL의 제약 조건을 활용하여 승부예측 데이터의 중복 및 논리적 오류를 원천 차단
* **대용량 집계 최적화**: 다수의 유저가 참여하는 승부예측 데이터를 효율적으로 카운팅하고 통계를 산출

---

## 🛠️ 기술 스택
* **Core**: Python 3.13, FastAPI
* **Database**: PostgreSQL (Relational DB)
* **ORM**: SQLAlchemy
* **Environment**: antigravity (Virtual Env: `./env/bin/python`)

---

## 🏗️ Step 2 주요 구현 사항

### 1. 효율적인 데이터 업데이트 (UPSERT 로직)
* 사용자가 자신의 예측 정보를 수정할 때, 새로운 행을 생성하지 않고 기존 데이터를 갱신하는 UPSERT 방식을 도입했습니다.
* `db.get()`과 `UniqueConstraint`를 조합하여 데이터 중복을 방지합니다.

### 2. 고성능 통계 쿼리 최적화
* `func.count`와 `group_by`를 활용하여 방대한 예측 데이터를 API 호출 한 번으로 즉시 집계하여 반환합니다.
* `outerjoin`을 사용하여 참여자가 없는 초기 항목도 목록 조회 시 누락되지 않도록 처리했습니다.

---

## 🚀 실행 가이드
1. **의존성 설치**
   ```bash
   ./env/bin/python -m pip install -r requirements.txt
