# 🔍 트렌드 검색 API & 웹 대시보드

YouTube, TikTok, Instagram 등 소셜 미디어 플랫폼에서 트렌드 조사 및 키워드 분석을 위한 FastAPI 기반 REST API 및 웹 대시보드입니다.

## 📋 목차

- [기능 소개](#-기능-소개)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [API 사용법](#-api-사용법)
- [웹 대시보드](#-웹-대시보드)
- [환경 설정](#-환경-설정)
- [문제 해결](#-문제-해결)

## ✨ 기능 소개

### 🔍 키워드 검색 및 트렌드 분석

- **다중 플랫폼 검색**: YouTube, TikTok, Instagram 동시 검색
- **실시간 데이터**: 최신 트렌드 정보 제공
- **상세 분석**: 조회수, 좋아요, 댓글 수 등 메트릭 분석
- **결과 시각화**: 차트와 테이블로 직관적 표시

### 📊 실시간 인기 검색어

- **자동 갱신**: 5분마다 자동으로 인기 검색어 업데이트
- **수동 새로고침**: 실시간 데이터 요청 가능
- **순위 시스템**: 키워드 등장 횟수, 조회수, 플랫폼 수 기반 순위

### 📈 데이터 시각화

- **상위 10개 키워드 차트**: 플랫폼별 분포 시각화
- **통계 대시보드**: 총 검색량, 평균 조회수 등
- **상세 결과 테이블**: 정렬 및 필터링 기능

## 🏗️ 프로젝트 구조

```
trend-search/
├── main.py                 # FastAPI 메인 애플리케이션
├── requirements.txt        # Python 패키지 의존성
├── env_example.txt        # 환경 변수 예시 파일
├── README.md              # 프로젝트 문서
├── SERVER_COMMANDS.md     # 서버 명령어 가이드
├── models/
│   ├── __init__.py
│   └── response_models.py # API 응답 모델 정의
├── services/
│   ├── __init__.py
│   ├── base_service.py    # 추상 기본 서비스 클래스
│   ├── youtube_service.py # YouTube API 서비스
│   ├── tiktok_service.py  # TikTok API 서비스
│   └── instagram_service.py # Instagram API 서비스
├── static/
│   └── style.css          # 웹 대시보드 스타일시트
├── templates/
│   └── dashboard.html     # 웹 대시보드 템플릿
└── venv/                  # Python 가상환경
```

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone [repository-url]
cd trend-search
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
copy env_example.txt .env

# .env 파일 편집하여 API 키 설정
# YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 5. 서버 실행

```bash
python -m uvicorn main:app --reload
```

### 6. 웹 대시보드 접속

- **API 루트**: http://127.0.0.1:8000/ (JSON 응답)
- **웹 대시보드**: http://127.0.0.1:8000/web (메인 웹 페이지)
- **API 문서**: http://127.0.0.1:8000/docs

## 🔌 API 사용법

### 기본 검색 API

```bash
# 키워드 검색 (모든 플랫폼)
GET /api/search/{keyword}

# 예시
curl http://127.0.0.1:8000/api/search/인공지능
```

### 플랫폼별 검색 API

```bash
# YouTube 전용 검색
GET /api/youtube/{keyword}

# TikTok 전용 검색
GET /api/tiktok/{keyword}

# Instagram 전용 검색
GET /api/instagram/{keyword}
```

### 실시간 트렌드 API

```bash
# 실시간 인기 검색어 조회
GET /api/trending
```

### API 응답 예시

```json
{
  "keyword": "인공지능",
  "total_results": 150,
  "platforms": {
    "youtube": 50,
    "tiktok": 60,
    "instagram": 40
  },
  "trends": [
    {
      "title": "AI 기술 동향",
      "platform": "youtube",
      "views": 1500000,
      "likes": 25000,
      "comments": 1200,
      "url": "https://youtube.com/watch?v=..."
    }
  ]
}
```

## 🌐 웹 대시보드

### 주요 기능

1. **키워드 검색**: 검색창에 키워드 입력 후 검색 버튼 클릭
2. **실시간 인기 검색어**: 5분마다 자동 갱신되는 인기 키워드
3. **데이터 시각화**: 차트와 테이블로 검색 결과 표시
4. **통계 정보**: 총 검색량, 평균 조회수 등 메트릭

### ⚠️ 중요: 올바른 접속 URL

- **웹 대시보드**: http://127.0.0.1:8000/web
- **API 루트**: http://127.0.0.1:8000/ (JSON 응답만 반환)

### 사용 방법

1. 웹 브라우저에서 http://127.0.0.1:8000/web 접속
2. 검색창에 원하는 키워드 입력
3. "검색" 버튼 클릭
4. 결과 확인 및 분석

## ⚙️ 환경 설정

### YouTube API 키 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성
5. `.env` 파일에 API 키 추가:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

### 환경 변수 목록

```bash
# .env 파일 예시
YOUTUBE_API_KEY=your_youtube_api_key_here
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 서버 실행 문제

```bash
# 가상환경이 활성화되어 있는지 확인
venv\Scripts\activate

# 패키지 재설치
pip install -r requirements.txt

# 서버 실행 (가상환경 활성화 후)
python -m uvicorn main:app --reload
```

#### 2. 웹 대시보드 접속 문제

- **올바른 URL**: http://127.0.0.1:8000/web
- **잘못된 URL**: http://127.0.0.1:8000/ (API 응답만 반환)

#### 3. 모듈을 찾을 수 없음

```bash
# 가상환경이 활성화되어 있는지 확인
venv\Scripts\activate

# 패키지 재설치
pip install -r requirements.txt
```

#### 4. 포트 충돌

```bash
# 다른 포트로 서버 실행
python -m uvicorn main:app --reload --port 8001
```

#### 5. YouTube API 오류

- API 키가 올바르게 설정되었는지 확인
- YouTube Data API v3가 활성화되었는지 확인
- API 할당량을 초과하지 않았는지 확인

#### 6. 서버 시작 실패

```bash
# 백그라운드 프로세스 종료
netstat -ano | findstr :8000
taskkill /PID [프로세스ID] /F

# 서버 재시작
python -m uvicorn main:app --reload
```

## 📊 데이터 제한사항

### YouTube

- **공식 API 사용**: 실제 데이터 제공
- **API 키 필요**: Google Cloud Console에서 발급
- **할당량 제한**: 일일 요청 수 제한

### TikTok & Instagram

- **제한적 API**: 샘플 데이터 제공
- **실제 데이터**: 공식 API 제한으로 인해 모의 데이터
- **향후 개선**: 공식 API 연동 예정

## 🛠️ 개발 정보

### 기술 스택

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: HTML, CSS, JavaScript
- **템플릿**: Jinja2
- **HTTP 클라이언트**: aiohttp, httpx
- **데이터 처리**: pandas, numpy

### 의존성 패키지

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
google-api-python-client==2.108.0
pandas==2.1.3
numpy==1.25.2
aiohttp==3.12.13
jinja2==3.1.6
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**트렌드 검색 API & 웹 대시보드** - 소셜 미디어 트렌드 분석을 위한 강력한 도구
"# trend-search-youtube"
