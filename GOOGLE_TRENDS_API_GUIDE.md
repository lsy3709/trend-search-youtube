# 📊 Google Trends API 활용 가이드

## 🎯 개요

Google Trends API를 활용한 실시간 인기 검색어 및 트렌드 분석 기능 구현 가이드입니다.

## 📋 목차

1. [Google Trends API 소개](#google-trends-api-소개)
2. [설치 및 설정](#설치-및-설정)
3. [API 엔드포인트](#api-엔드포인트)
4. [기능별 사용법](#기능별-사용법)
5. [연령대별 데이터 현황](#연령대별-데이터-현황)
6. [제한사항 및 대안](#제한사항-및-대안)
7. [실제 활용 예시](#실제-활용-예시)
8. [트러블슈팅](#트러블슈팅)

---

## 🔍 Google Trends API 소개

### ✅ **가능한 기능들**

1. **실시간 인기 검색어**

   - 지역별 실시간 인기 검색어 순위
   - 카테고리별 인기 검색어
   - 글로벌 트렌드

2. **키워드 분석**

   - 시간별 관심도 추이
   - 관련 검색어 (상위/급상승)
   - 지역별 관심도

3. **트렌드 분석**
   - 키워드 비교 분석
   - 시계열 데이터
   - 관심도 점수 (0-100)

### ❌ **제한사항**

1. **연령대별 인기 검색어 순위**: 직접 제공하지 않음
2. **연령대별 실시간 순위**: API로 접근 불가
3. **개인정보 보호**: 연령대별 개별 검색 데이터는 비공개
4. **API 호출 제한**: 과도한 요청 시 일시적 차단 가능

---

## 🛠️ 설치 및 설정

### 1. 패키지 설치

```bash
pip install pytrends
```

### 2. 서비스 초기화

```python
from services.google_trends_service import GoogleTrendsService

# 한국어 설정으로 초기화
google_trends_service = GoogleTrendsService()
```

### 3. 환경 설정

```python
# 한국 시간대 (UTC+9) 설정
self.pytrends = TrendReq(hl='ko-KR', tz=540)
```

---

## 🔗 API 엔드포인트

### 1. 실시간 인기 검색어

```http
GET /api/google-trends/realtime?region=KR
```

**응답 예시:**

```json
{
  "region": "KR",
  "trending_searches": [
    {
      "keyword": "뉴진스",
      "rank": 1,
      "region": "KR",
      "timestamp": "2024-01-01T12:00:00",
      "source": "google_trends"
    }
  ],
  "total_count": 20,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. 카테고리별 인기 검색어

```http
GET /api/google-trends/category/entertainment?region=KR
```

**지원 카테고리:**

- `all`: 전체
- `entertainment`: 엔터테인먼트
- `business`: 비즈니스
- `sports`: 스포츠
- `health`: 건강
- `science_tech`: 과학기술
- `top_stories`: 주요 뉴스

### 3. 키워드 관심도 분석

```http
GET /api/google-trends/keyword/뉴진스/interest?region=KR&timeframe=today 12-m
```

**시간 범위 옵션:**

- `now 1-H`: 최근 1시간
- `now 4-H`: 최근 4시간
- `now 1-d`: 최근 1일
- `today 12-m`: 최근 12개월
- `today 5-y`: 최근 5년

### 4. 관련 검색어

```http
GET /api/google-trends/keyword/뉴진스/related?region=KR
```

### 5. 지역별 관심도

```http
GET /api/google-trends/keyword/뉴진스/regions?region=KR
```

### 6. 연령대별 관심도 (추정)

```http
GET /api/google-trends/keyword/뉴진스/age-groups?region=KR
```

---

## 📊 기능별 사용법

### 1. 실시간 인기 검색어 조회

```python
# 한국 실시간 인기 검색어
trending_searches = await google_trends_service.get_realtime_trending_searches("KR")

# 미국 실시간 인기 검색어
us_trends = await google_trends_service.get_realtime_trending_searches("US")
```

### 2. 카테고리별 분석

```python
# 엔터테인먼트 카테고리
entertainment_trends = await google_trends_service.get_trending_searches_by_category(
    category="entertainment",
    region="KR"
)

# 비즈니스 카테고리
business_trends = await google_trends_service.get_trending_searches_by_category(
    category="business",
    region="KR"
)
```

### 3. 키워드 관심도 분석

```python
# 키워드 관심도 추이
interest_data = await google_trends_service.get_keyword_interest_over_time(
    keyword="뉴진스",
    region="KR",
    timeframe="today 12-m"
)

print(f"평균 관심도: {interest_data['average_interest']}/100")
print(f"최대 관심도: {interest_data['max_interest']}/100")
```

### 4. 관련 검색어 분석

```python
# 관련 검색어 조회
related_data = await google_trends_service.get_related_queries(
    keyword="뉴진스",
    region="KR"
)

print("상위 관련 검색어:")
for query in related_data["top_queries"]:
    print(f"- {query['query']}: {query['value']}")

print("급상승 관련 검색어:")
for query in related_data["rising_queries"]:
    print(f"- {query['query']}: {query['value']}")
```

---

## 👥 연령대별 데이터 현황

### 🔴 **Google Trends API 한계**

Google Trends API는 **연령대별 인기 검색어 순위를 직접 제공하지 않습니다**.

### 🟡 **현재 구현 방식**

1. **키워드 특성 기반 추정**

   ```python
   age_patterns = {
       "뉴진스": {"10대": 95, "20대": 85, "30대": 60, "40대": 30, "50대+": 15},
       "게임": {"10대": 90, "20대": 80, "30대": 70, "40대": 50, "50대+": 30},
       "취업": {"10대": 40, "20대": 95, "30대": 80, "40대": 60, "50대+": 40}
   }
   ```

2. **키워드 매칭 알고리즘**
   - 키워드가 특정 연령대 패턴과 일치하는지 확인
   - 기본 패턴에 랜덤성 추가하여 자연스러운 데이터 생성

### 🟢 **대안 방법들**

1. **Google Analytics (유료)**

   - 실제 연령대별 데이터 제공
   - 웹사이트 분석 기반

2. **Facebook Audience Insights**

   - 소셜 미디어 기반 연령대별 데이터
   - 광고 플랫폼 활용

3. **네이버 데이터랩**
   - 한국 특화 연령대별 데이터
   - 검색어 트렌드 API

---

## ⚠️ 제한사항 및 대안

### 1. **API 호출 제한**

**문제:** 과도한 요청 시 일시적 차단
**해결책:**

```python
import time

# 요청 간격 조절
time.sleep(1)  # 1초 대기

# 에러 처리
try:
    data = await google_trends_service.get_realtime_trending_searches()
except Exception as e:
    # 더미 데이터 반환
    data = get_dummy_data()
```

### 2. **데이터 정확성**

**문제:** 실시간 데이터와 약간의 차이
**해결책:**

- 여러 소스 데이터 비교
- 평균값 계산
- 신뢰도 점수 추가

### 3. **연령대별 데이터 부재**

**문제:** Google Trends에서 연령대별 데이터 미제공
**해결책:**

- 키워드 특성 기반 추정
- 외부 데이터 소스 활용
- 머신러닝 모델 적용

---

## 🎯 실제 활용 예시

### 1. **마케팅 트렌드 분석**

```python
# 특정 제품의 관심도 분석
product_interest = await google_trends_service.get_keyword_interest_over_time(
    keyword="스마트폰",
    timeframe="today 12-m"
)

# 경쟁사 키워드 비교
competitors = ["삼성", "애플", "LG"]
for competitor in competitors:
    data = await google_trends_service.get_keyword_interest_over_time(
        keyword=competitor,
        timeframe="today 12-m"
    )
    print(f"{competitor}: {data['average_interest']}")
```

### 2. **콘텐츠 제작 가이드**

```python
# 인기 키워드 기반 콘텐츠 아이디어
trending_keywords = await google_trends_service.get_realtime_trending_searches("KR")

for keyword in trending_keywords[:5]:
    related = await google_trends_service.get_related_queries(keyword["keyword"])
    print(f"주제: {keyword['keyword']}")
    print(f"관련 키워드: {[q['query'] for q in related['top_queries'][:3]]}")
```

### 3. **지역별 마케팅 전략**

```python
# 지역별 관심도 분석
regions = ["KR", "US", "JP", "CN"]
for region in regions:
    trends = await google_trends_service.get_realtime_trending_searches(region)
    print(f"{region} 지역 인기 키워드: {[t['keyword'] for t in trends[:3]]}")
```

---

## 🔧 트러블슈팅

### 1. **API 연결 실패**

**증상:** `ConnectionError` 또는 `TimeoutError`
**해결책:**

```python
# 재시도 로직 구현
import asyncio

async def retry_api_call(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # 지수 백오프
```

### 2. **데이터 없음**

**증상:** 빈 결과 반환
**해결책:**

```python
# 더미 데이터 폴백
if not data or len(data) == 0:
    return get_dummy_trending_searches(region)
```

### 3. **한글 키워드 인코딩 문제**

**증상:** 한글 키워드가 깨짐
**해결책:**

```python
import urllib.parse

# URL 인코딩
encoded_keyword = urllib.parse.quote(keyword)
url = f"/api/google-trends/keyword/{encoded_keyword}/interest"
```

### 4. **요청 제한**

**증상:** `429 Too Many Requests`
**해결책:**

```python
# 요청 간격 조절
import time

class RateLimitedService:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.last_request = 0

    async def make_request(self, func):
        now = time.time()
        time_since_last = now - self.last_request
        min_interval = 60 / self.requests_per_minute

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self.last_request = time.time()
        return await func()
```

---

## 📈 성능 최적화

### 1. **캐싱 구현**

```python
import asyncio
from datetime import datetime, timedelta

class CachedGoogleTrendsService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)

    async def get_realtime_trending_searches(self, region="KR"):
        cache_key = f"trending_{region}"

        # 캐시 확인
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data

        # API 호출
        data = await google_trends_service.get_realtime_trending_searches(region)

        # 캐시 저장
        self.cache[cache_key] = (data, datetime.now())
        return data
```

### 2. **배치 처리**

```python
async def batch_get_keywords_interest(keywords, region="KR"):
    """여러 키워드의 관심도를 배치로 조회"""
    tasks = []
    for keyword in keywords:
        task = google_trends_service.get_keyword_interest_over_time(
            keyword=keyword, region=region
        )
        tasks.append(task)

    return await asyncio.gather(*tasks)
```

---

## 🚀 향후 개선 방향

### 1. **실시간 데이터 연동**

- Google Trends API와 네이버 데이터랩 연동
- 다중 소스 데이터 통합

### 2. **머신러닝 모델**

- 키워드-연령대 매칭 모델 학습
- 트렌드 예측 알고리즘 구현

### 3. **데이터베이스 저장**

- 수집된 데이터를 DB에 저장
- 히스토리 관리 및 분석

### 4. **API 키 관리**

- 환경변수를 통한 API 키 관리
- 보안 강화

---

## 📞 지원 및 문의

### 기술 지원

- **GitHub Issues**: 프로젝트 이슈 등록
- **문서 업데이트**: 이 가이드의 지속적 개선

### 참고 자료

- [Google Trends 공식 문서](https://trends.google.com/)
- [pytrends 라이브러리 문서](https://github.com/GeneralMills/pytrends)
- [Google Analytics API](https://developers.google.com/analytics)

---

**마지막 업데이트:** 2024년 1월
**버전:** 1.0.0
