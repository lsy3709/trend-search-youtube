# 작업 현황 체크리스트

- [x] 의존성 설치 및 venv 복구
- [x] pytrends 추가 및 서버 기동 확인
- [x] 루트(`/`) → `/web` 리다이렉트
- [x] 대시보드 하드코딩 문구 제거 및 "준비중입니다." 처리
- [x] YouTube 트렌드 분석 UI 추가(폼/버튼/결과)
- [x] 인라인 뷰어(영상/썸네일)와 페이징 기능
- [x] 구독자수/비율/길이 표시 안정화
- [x] 테스트 추가(pytest): 기본 엔드포인트/유틸/분석/Google Trends 모킹
- [ ] 쿼터 초과 시 사용자 메시지 고도화(429 변환)
- [ ] 표 정렬/필터 기능 확장

## 운영 명령 요약(Windows)

```bat
venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
venv\Scripts\python.exe -m pytest -q
```


