"""
Google Trends API 서비스
실시간 인기 검색어 및 트렌드 데이터를 수집하는 서비스
"""

import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from models.response_models import TrendResponse, SearchResponse

class GoogleTrendsService:
    """Google Trends API 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        # 한국어 설정으로 Google Trends API 초기화
        self.pytrends = TrendReq(hl='ko-KR', tz=540)  # 한국 시간대 (UTC+9)
        
        # 카테고리 매핑
        self.categories = {
            "all": 0,
            "entertainment": 3,
            "business": 12,
            "sports": 20,
            "health": 45,
            "science_tech": 8,
            "top_stories": 16
        }
        
        # 지역 매핑 (Google Trends 지역 코드)
        self.regions = {
            "KR": "KR",  # 한국
            "US": "US",  # 미국
            "JP": "JP",  # 일본
            "CN": "CN",  # 중국
            "GB": "GB"   # 영국
        }

    async def get_realtime_trending_searches(self, region: str = "KR") -> List[Dict[str, Any]]:
        """
        실시간 인기 검색어 조회
        
        Args:
            region: 지역 코드 (KR, US, JP 등)
            
        Returns:
            실시간 인기 검색어 목록
        """
        try:
            # Google Trends 실시간 인기 검색어 조회
            trending_searches = self.pytrends.trending_searches(pn=region)
            
            results = []
            for index, keyword in enumerate(trending_searches[0]):
                results.append({
                    "keyword": keyword,
                    "rank": index + 1,
                    "region": region,
                    "timestamp": datetime.now().isoformat(),
                    "source": "google_trends"
                })
            
            return results
            
        except Exception as e:
            print(f"Google Trends 실시간 검색어 조회 실패: {str(e)}")
            # 에러 시 더미 데이터 반환
            return self._get_dummy_trending_searches(region)

    async def get_trending_searches_by_category(
        self, 
        category: str = "all", 
        region: str = "KR"
    ) -> List[Dict[str, Any]]:
        """
        카테고리별 인기 검색어 조회
        
        Args:
            category: 카테고리 (all, entertainment, business, sports 등)
            region: 지역 코드
            
        Returns:
            카테고리별 인기 검색어 목록
        """
        try:
            # 카테고리별 인기 검색어 조회
            category_id = self.categories.get(category, 0)
            trending_searches = self.pytrends.trending_searches(
                pn=region, 
                cat=category_id
            )
            
            results = []
            for index, keyword in enumerate(trending_searches[0]):
                results.append({
                    "keyword": keyword,
                    "rank": index + 1,
                    "category": category,
                    "region": region,
                    "timestamp": datetime.now().isoformat(),
                    "source": "google_trends"
                })
            
            return results
            
        except Exception as e:
            print(f"카테고리별 인기 검색어 조회 실패: {str(e)}")
            return self._get_dummy_category_searches(category, region)

    async def get_keyword_interest_over_time(
        self, 
        keyword: str, 
        region: str = "KR",
        timeframe: str = "today 12-m"
    ) -> Dict[str, Any]:
        """
        특정 키워드의 시간별 관심도 조회
        
        Args:
            keyword: 검색할 키워드
            region: 지역 코드
            timeframe: 시간 범위 (today 12-m, today 5-y, now 1-H 등)
            
        Returns:
            키워드 관심도 데이터
        """
        try:
            # 키워드 관심도 조회
            self.pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=region)
            interest_over_time = self.pytrends.interest_over_time()
            
            if interest_over_time.empty:
                return self._get_dummy_interest_data(keyword, region)
            
            # 데이터 처리
            data = []
            for date, row in interest_over_time.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "interest": int(row[keyword])
                })
            
            return {
                "keyword": keyword,
                "region": region,
                "timeframe": timeframe,
                "data": data,
                "average_interest": int(interest_over_time[keyword].mean()),
                "max_interest": int(interest_over_time[keyword].max()),
                "timestamp": datetime.now().isoformat(),
                "source": "google_trends"
            }
            
        except Exception as e:
            print(f"키워드 관심도 조회 실패: {str(e)}")
            return self._get_dummy_interest_data(keyword, region)

    async def get_related_queries(
        self, 
        keyword: str, 
        region: str = "KR"
    ) -> Dict[str, Any]:
        """
        관련 검색어 조회
        
        Args:
            keyword: 검색할 키워드
            region: 지역 코드
            
        Returns:
            관련 검색어 데이터
        """
        try:
            # 관련 검색어 조회
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo=region)
            related_queries = self.pytrends.related_queries()
            
            results = {
                "keyword": keyword,
                "region": region,
                "top_queries": [],
                "rising_queries": [],
                "timestamp": datetime.now().isoformat(),
                "source": "google_trends"
            }
            
            # 상위 관련 검색어
            if related_queries[keyword]['top'] is not None:
                for _, row in related_queries[keyword]['top'].iterrows():
                    results["top_queries"].append({
                        "query": row['query'],
                        "value": int(row['value'])
                    })
            
            # 급상승 관련 검색어
            if related_queries[keyword]['rising'] is not None:
                for _, row in related_queries[keyword]['rising'].iterrows():
                    results["rising_queries"].append({
                        "query": row['query'],
                        "value": int(row['value'])
                    })
            
            return results
            
        except Exception as e:
            print(f"관련 검색어 조회 실패: {str(e)}")
            return self._get_dummy_related_queries(keyword, region)

    async def get_interest_by_region(
        self, 
        keyword: str, 
        region: str = "KR"
    ) -> Dict[str, Any]:
        """
        지역별 관심도 조회
        
        Args:
            keyword: 검색할 키워드
            region: 지역 코드
            
        Returns:
            지역별 관심도 데이터
        """
        try:
            # 지역별 관심도 조회
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo=region)
            interest_by_region = self.pytrends.interest_by_region(resolution='COUNTRY')
            
            if interest_by_region.empty:
                return self._get_dummy_region_interest(keyword, region)
            
            # 데이터 처리
            regions_data = []
            for region_name, row in interest_by_region.iterrows():
                regions_data.append({
                    "region": region_name,
                    "interest": int(row[keyword])
                })
            
            # 관심도 순으로 정렬
            regions_data.sort(key=lambda x: x["interest"], reverse=True)
            
            return {
                "keyword": keyword,
                "base_region": region,
                "regions": regions_data,
                "timestamp": datetime.now().isoformat(),
                "source": "google_trends"
            }
            
        except Exception as e:
            print(f"지역별 관심도 조회 실패: {str(e)}")
            return self._get_dummy_region_interest(keyword, region)

    async def get_age_group_interest(
        self, 
        keyword: str, 
        region: str = "KR"
    ) -> Dict[str, Any]:
        """
        연령대별 관심도 조회 (Google Trends에서 제공하는 경우)
        
        Args:
            keyword: 검색할 키워드
            region: 지역 코드
            
        Returns:
            연령대별 관심도 데이터
        """
        try:
            # 연령대별 관심도 조회 (Google Trends에서 제공하는 경우)
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo=region)
            
            # Google Trends에서 연령대별 데이터를 직접 제공하지 않으므로
            # 키워드 특성에 따른 추정 데이터 생성
            return self._generate_age_group_interest(keyword, region)
            
        except Exception as e:
            print(f"연령대별 관심도 조회 실패: {str(e)}")
            return self._generate_age_group_interest(keyword, region)

    def _get_dummy_trending_searches(self, region: str) -> List[Dict[str, Any]]:
        """더미 실시간 인기 검색어 데이터"""
        dummy_keywords = [
            "뉴진스", "르세라핌", "아이브", "게임", "애니메이션",
            "취업", "이력서", "면접", "스타트업", "투자",
            "결혼", "육아", "집", "아파트", "건강",
            "운동", "다이어트", "요리", "여행", "맛집"
        ]
        
        results = []
        for index, keyword in enumerate(dummy_keywords):
            results.append({
                "keyword": keyword,
                "rank": index + 1,
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "source": "google_trends_dummy"
            })
        
        return results

    def _get_dummy_category_searches(self, category: str, region: str) -> List[Dict[str, Any]]:
        """더미 카테고리별 인기 검색어 데이터"""
        category_keywords = {
            "entertainment": ["뉴진스", "르세라핌", "아이브", "게임", "애니메이션"],
            "business": ["취업", "이력서", "면접", "스타트업", "투자"],
            "sports": ["축구", "야구", "농구", "테니스", "골프"],
            "health": ["건강", "운동", "다이어트", "병원", "약"],
            "science_tech": ["AI", "로봇", "우주", "기술", "발명"]
        }
        
        keywords = category_keywords.get(category, ["인기", "검색어", "트렌드", "뉴스", "정보"])
        
        results = []
        for index, keyword in enumerate(keywords):
            results.append({
                "keyword": keyword,
                "rank": index + 1,
                "category": category,
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "source": "google_trends_dummy"
            })
        
        return results

    def _get_dummy_interest_data(self, keyword: str, region: str) -> Dict[str, Any]:
        """더미 키워드 관심도 데이터"""
        # 최근 30일간의 더미 데이터 생성
        data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            interest = random.randint(20, 100)
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "interest": interest
            })
        
        return {
            "keyword": keyword,
            "region": region,
            "timeframe": "today 12-m",
            "data": data,
            "average_interest": sum(d["interest"] for d in data) // len(data),
            "max_interest": max(d["interest"] for d in data),
            "timestamp": datetime.now().isoformat(),
            "source": "google_trends_dummy"
        }

    def _get_dummy_related_queries(self, keyword: str, region: str) -> Dict[str, Any]:
        """더미 관련 검색어 데이터"""
        related_keywords = {
            "뉴진스": ["뉴진스 하니", "뉴진스 민지", "뉴진스 다니엘", "뉴진스 혜인", "뉴진스 해린"],
            "게임": ["게임 추천", "게임 순위", "게임 리뷰", "게임 공략", "게임 다운로드"],
            "취업": ["이력서", "면접", "스타트업", "연봉", "복지"],
            "건강": ["운동", "다이어트", "병원", "약", "검진"]
        }
        
        top_queries = related_keywords.get(keyword, [f"{keyword} 관련", f"{keyword} 정보", f"{keyword} 뉴스"])
        rising_queries = [f"{keyword} 최신", f"{keyword} 트렌드", f"{keyword} 인기"]
        
        return {
            "keyword": keyword,
            "region": region,
            "top_queries": [{"query": q, "value": random.randint(50, 100)} for q in top_queries],
            "rising_queries": [{"query": q, "value": random.randint(100, 200)} for q in rising_queries],
            "timestamp": datetime.now().isoformat(),
            "source": "google_trends_dummy"
        }

    def _get_dummy_region_interest(self, keyword: str, region: str) -> Dict[str, Any]:
        """더미 지역별 관심도 데이터"""
        regions_data = [
            {"region": "대한민국", "interest": random.randint(80, 100)},
            {"region": "미국", "interest": random.randint(30, 70)},
            {"region": "일본", "interest": random.randint(40, 80)},
            {"region": "중국", "interest": random.randint(20, 60)},
            {"region": "영국", "interest": random.randint(25, 65)}
        ]
        
        return {
            "keyword": keyword,
            "base_region": region,
            "regions": regions_data,
            "timestamp": datetime.now().isoformat(),
            "source": "google_trends_dummy"
        }

    def _generate_age_group_interest(self, keyword: str, region: str) -> Dict[str, Any]:
        """연령대별 관심도 생성 (키워드 특성 기반)"""
        # 키워드별 연령대 관심도 패턴
        age_patterns = {
            "뉴진스": {"10대": 95, "20대": 85, "30대": 60, "40대": 30, "50대+": 15},
            "게임": {"10대": 90, "20대": 80, "30대": 70, "40대": 50, "50대+": 30},
            "취업": {"10대": 40, "20대": 95, "30대": 80, "40대": 60, "50대+": 40},
            "결혼": {"10대": 20, "20대": 70, "30대": 90, "40대": 60, "50대+": 40},
            "건강": {"10대": 30, "20대": 50, "30대": 70, "40대": 90, "50대+": 95}
        }
        
        # 기본 패턴 (중립적)
        default_pattern = {"10대": 50, "20대": 60, "30대": 70, "40대": 65, "50대+": 55}
        
        # 키워드에 맞는 패턴 선택
        pattern = age_patterns.get(keyword, default_pattern)
        
        # 패턴에 약간의 랜덤성 추가
        age_groups = []
        for age_group, base_interest in pattern.items():
            interest = base_interest + random.randint(-10, 10)
            interest = max(0, min(100, interest))  # 0-100 범위로 제한
            age_groups.append({
                "age_group": age_group,
                "interest": interest
            })
        
        return {
            "keyword": keyword,
            "region": region,
            "age_groups": age_groups,
            "timestamp": datetime.now().isoformat(),
            "source": "google_trends_estimated"
        } 