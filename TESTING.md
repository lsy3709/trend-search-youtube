# 테스트 가이드

## 실행

```bat
venv\Scripts\python.exe -m pytest -q
```

## 주요 테스트 항목
- tests/test_main_endpoints.py: /health 200, 루트 리다이렉트
- tests/test_services_youtube.py: 유틸리티(parse_duration) 및 키 존재 시 검색 스모크
- tests/test_base_utils.py: 텍스트/숫자 유틸 검사
- tests/test_analyze_endpoints.py: /api/youtube/analyze 와 export 성공/실패 모킹
- tests/test_google_trends_service.py: Google Trends 더미/성공 분기 모킹

## 주의
- 라이브 YouTube 호출은 .env 의 YOUTUBE_API_KEY 가 없으면 자동 skip
- 네트워크 의존 테스트는 CI에서 flakiness를 줄이기 위해 가급적 모킹 권장
