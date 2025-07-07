"""
연령대별 키워드 분석 서비스
특정 연령대가 많이 검색하는 키워드를 분석하는 서비스
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import asyncio
from services.youtube_service import YouTubeService
from services.tiktok_service import TikTokService
from services.instagram_service import InstagramService
from models.response_models import (
    AgeGroupKeywordResponse, 
    KeywordAnalysisResponse, 
    AgeGroupTrendResponse
)

class AgeAnalysisService:
    """연령대별 키워드 분석 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.youtube_service = YouTubeService()
        self.tiktok_service = TikTokService()
        self.instagram_service = InstagramService()
        
        # 연령대별 키워드 패턴 정의
        self.age_group_patterns = {
            "10대": {
                "keywords": [
                    "게임", "애니메이션", "만화", "아이돌", "K-pop", "댄스", "틱톡", 
                    "유튜브", "스트리밍", "코스프레", "팬아트", "팬픽", "캐릭터",
                    "스킨케어", "메이크업", "패션", "스니커즈", "백팩", "학원",
                    "수능", "입시", "대학", "고등학교", "중학교", "친구", "연애"
                ],
                "platforms": ["tiktok", "youtube", "instagram"],
                "weight": 1.0
            },
            "20대": {
                "keywords": [
                    "취업", "이력서", "면접", "스타트업", "창업", "투자", "주식",
                    "부동산", "집", "월세", "전세", "대출", "카드", "적금",
                    "연봉", "급여", "세금", "연말정산", "복지", "휴가",
                    "여행", "맛집", "카페", "술집", "클럽", "데이트", "연애",
                    "결혼", "웨딩", "신혼", "육아", "육아맘", "육아맘블로그"
                ],
                "platforms": ["instagram", "youtube", "tiktok"],
                "weight": 1.2
            },
            "30대": {
                "keywords": [
                    "결혼", "육아", "아이", "유치원", "초등학교", "학원", "과외",
                    "집", "아파트", "분양", "인테리어", "가전제품", "가구",
                    "차", "자동차", "보험", "투자", "펀드", "연금", "은퇴",
                    "건강", "운동", "다이어트", "요리", "베이킹", "가드닝",
                    "취미", "독서", "영화", "드라마", "넷플릭스", "OTT"
                ],
                "platforms": ["youtube", "instagram", "tiktok"],
                "weight": 1.1
            },
            "40대": {
                "keywords": [
                    "건강", "운동", "다이어트", "요리", "베이킹", "가드닝",
                    "취미", "독서", "영화", "드라마", "넷플릭스", "OTT",
                    "집", "아파트", "분양", "인테리어", "가전제품", "가구",
                    "차", "자동차", "보험", "투자", "펀드", "연금", "은퇴",
                    "부모님", "효도", "가족여행", "가족사진", "가족모임"
                ],
                "platforms": ["youtube", "instagram"],
                "weight": 0.9
            },
            "50대+": {
                "keywords": [
                    "건강", "운동", "다이어트", "요리", "베이킹", "가드닝",
                    "취미", "독서", "영화", "드라마", "넷플릭스", "OTT",
                    "집", "아파트", "분양", "인테리어", "가전제품", "가구",
                    "차", "자동차", "보험", "투자", "펀드", "연금", "은퇴",
                    "부모님", "효도", "가족여행", "가족사진", "가족모임",
                    "노후", "은퇴", "연금", "보험", "건강검진", "병원"
                ],
                "platforms": ["youtube"],
                "weight": 0.8
            }
        }
        
        # 키워드 가중치 점수 계산을 위한 가중치
        self.platform_weights = {
            "youtube": 1.0,
            "tiktok": 1.2,  # 젊은 층이 많이 사용
            "instagram": 1.1
        }

    async def analyze_keywords_by_age_group(
        self, 
        max_results: int = 20,
        platforms: List[str] = None
    ) -> List[AgeGroupKeywordResponse]:
        """
        연령대별 키워드 분석
        
        Args:
            max_results: 최대 결과 수
            platforms: 분석할 플랫폼 목록
            
        Returns:
            연령대별 키워드 분석 결과
        """
        if platforms is None:
            platforms = ["youtube", "tiktok", "instagram"]
            
        try:
            # 각 플랫폼에서 트렌드 데이터 수집
            all_trends = await self._collect_trends_from_platforms(platforms, max_results)
            
            # 연령대별 키워드 분석
            age_group_results = []
            
            for age_group, patterns in self.age_group_patterns.items():
                # 해당 연령대에 맞는 키워드 추출 및 분석
                age_keywords = await self._analyze_age_group_keywords(
                    all_trends, age_group, patterns, max_results
                )
                
                # 플랫폼별 분포 계산
                platform_distribution = self._calculate_platform_distribution(
                    age_keywords, platforms
                )
                
                # 트렌딩 점수 계산
                trending_score = self._calculate_trending_score(age_keywords)
                
                result = AgeGroupKeywordResponse(
                    age_group=age_group,
                    keywords=age_keywords,
                    total_searches=sum(kw.get("search_count", 0) for kw in age_keywords),
                    platform_distribution=platform_distribution,
                    trending_score=trending_score,
                    timestamp=datetime.now()
                )
                
                age_group_results.append(result)
            
            return age_group_results
            
        except Exception as e:
            raise Exception(f"연령대별 키워드 분석 실패: {str(e)}")

    async def analyze_specific_keyword(
        self, 
        keyword: str,
        platforms: List[str] = None
    ) -> KeywordAnalysisResponse:
        """
        특정 키워드의 연령대별 분석
        
        Args:
            keyword: 분석할 키워드
            platforms: 분석할 플랫폼 목록
            
        Returns:
            키워드별 연령대 분석 결과
        """
        if platforms is None:
            platforms = ["youtube", "tiktok", "instagram"]
            
        try:
            # 각 플랫폼에서 키워드 검색
            search_results = await self._search_keyword_across_platforms(
                keyword, platforms
            )
            
            # 연령대별 분석
            age_groups_analysis = {}
            total_mentions = 0
            platform_breakdown = defaultdict(int)
            
            for age_group, patterns in self.age_group_patterns.items():
                # 해당 연령대에서의 키워드 분석
                age_analysis = await self._analyze_keyword_for_age_group(
                    search_results, keyword, age_group, patterns
                )
                
                age_groups_analysis[age_group] = age_analysis
                total_mentions += age_analysis.get("mentions", 0)
                
                # 플랫폼별 분포 누적
                for platform, count in age_analysis.get("platform_mentions", {}).items():
                    platform_breakdown[platform] += count
            
            # 트렌드 방향 분석
            trending_trend = self._analyze_trending_direction(search_results)
            
            # 관련 키워드 추출
            related_keywords = self._extract_related_keywords(search_results)
            
            # 감정 점수 계산 (간단한 키워드 기반 분석)
            sentiment_score = self._calculate_sentiment_score(keyword, search_results)
            
            return KeywordAnalysisResponse(
                keyword=keyword,
                age_groups=age_groups_analysis,
                total_mentions=total_mentions,
                platform_breakdown=dict(platform_breakdown),
                trending_trend=trending_trend,
                related_keywords=related_keywords,
                sentiment_score=sentiment_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"키워드 분석 실패: {str(e)}")

    async def get_age_group_trends(
        self, 
        age_group: str,
        max_results: int = 15
    ) -> AgeGroupTrendResponse:
        """
        특정 연령대의 트렌드 분석
        
        Args:
            age_group: 분석할 연령대
            max_results: 최대 결과 수
            
        Returns:
            연령대별 트렌드 분석 결과
        """
        try:
            if age_group not in self.age_group_patterns:
                raise ValueError(f"지원하지 않는 연령대: {age_group}")
            
            patterns = self.age_group_patterns[age_group]
            platforms = patterns["platforms"]
            
            # 해당 연령대에 맞는 트렌드 수집
            trends = await self._collect_age_specific_trends(
                age_group, patterns, platforms, max_results
            )
            
            # 상위 키워드 추출
            top_keywords = self._extract_top_keywords(trends, max_results)
            
            # 트렌딩 토픽 분석
            trending_topics = self._analyze_trending_topics(trends)
            
            # 플랫폼 선호도 계산
            platform_preferences = self._calculate_platform_preferences(trends, platforms)
            
            # 콘텐츠 카테고리 분포
            content_categories = self._analyze_content_categories(trends)
            
            return AgeGroupTrendResponse(
                age_group=age_group,
                top_keywords=top_keywords,
                trending_topics=trending_topics,
                platform_preferences=platform_preferences,
                content_categories=content_categories,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"연령대 트렌드 분석 실패: {str(e)}")

    async def _collect_trends_from_platforms(
        self, 
        platforms: List[str], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """플랫폼별 트렌드 데이터 수집"""
        all_trends = []
        
        for platform in platforms:
            try:
                if platform == "youtube":
                    trends = await self.youtube_service.get_trending_videos(max_results=max_results)
                elif platform == "tiktok":
                    trends = await self.tiktok_service.get_trending_videos(max_results=max_results)
                elif platform == "instagram":
                    trends = await self.instagram_service.get_trending_posts(max_results=max_results)
                else:
                    continue
                
                # 플랫폼 정보 추가
                for trend in trends:
                    trend_dict = trend.dict() if hasattr(trend, 'dict') else trend
                    trend_dict['platform'] = platform
                    all_trends.append(trend_dict)
                    
            except Exception as e:
                print(f"{platform} 트렌드 수집 실패: {str(e)}")
                continue
        
        return all_trends

    async def _analyze_age_group_keywords(
        self, 
        trends: List[Dict[str, Any]], 
        age_group: str, 
        patterns: Dict[str, Any], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """연령대별 키워드 분석"""
        age_keywords = []
        keyword_scores = defaultdict(float)
        
        # 연령대별 키워드 패턴 매칭
        for trend in trends:
            title = trend.get('title', '').lower()
            description = trend.get('description', '').lower()
            tags = trend.get('tags', [])
            hashtags = trend.get('hashtags', [])
            
            # 텍스트에서 키워드 추출
            text_content = f"{title} {description} {' '.join(tags)} {' '.join(hashtags)}"
            
            # 연령대별 키워드 매칭
            for keyword in patterns["keywords"]:
                if keyword.lower() in text_content:
                    platform = trend.get('platform', 'unknown')
                    platform_weight = self.platform_weights.get(platform, 1.0)
                    age_weight = patterns["weight"]
                    
                    # 점수 계산 (조회수, 좋아요 수 등 고려)
                    engagement_score = self._calculate_engagement_score(trend)
                    keyword_scores[keyword] += engagement_score * platform_weight * age_weight
        
        # 상위 키워드 선택
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        
        for keyword, score in sorted_keywords[:max_results]:
            age_keywords.append({
                "keyword": keyword,
                "score": round(score, 2),
                "search_count": int(score * 100),  # 가상의 검색 수
                "trending_level": self._get_trending_level(score)
            })
        
        return age_keywords

    def _calculate_engagement_score(self, trend: Dict[str, Any]) -> float:
        """참여도 점수 계산"""
        view_count = trend.get('view_count', 0) or 0
        like_count = trend.get('like_count', 0) or 0
        comment_count = trend.get('comment_count', 0) or 0
        share_count = trend.get('share_count', 0) or 0
        
        # 가중치 적용
        score = (view_count * 0.1 + like_count * 0.3 + comment_count * 0.4 + share_count * 0.2)
        return min(score, 1000)  # 최대값 제한

    def _get_trending_level(self, score: float) -> str:
        """트렌딩 레벨 판정"""
        if score > 500:
            return "🔥 매우 인기"
        elif score > 200:
            return "📈 인기 상승"
        elif score > 50:
            return "📊 관심 증가"
        else:
            return "📋 일반"

    def _calculate_platform_distribution(
        self, 
        keywords: List[Dict[str, Any]], 
        platforms: List[str]
    ) -> Dict[str, int]:
        """플랫폼별 분포 계산"""
        distribution = {platform: 0 for platform in platforms}
        
        # 키워드 점수를 기반으로 플랫폼별 분포 추정
        total_score = sum(kw.get("score", 0) for kw in keywords)
        if total_score > 0:
            for platform in platforms:
                platform_weight = self.platform_weights.get(platform, 1.0)
                distribution[platform] = int(total_score * platform_weight / len(platforms))
        
        return distribution

    def _calculate_trending_score(self, keywords: List[Dict[str, Any]]) -> float:
        """트렌딩 점수 계산"""
        if not keywords:
            return 0.0
        
        total_score = sum(kw.get("score", 0) for kw in keywords)
        avg_score = total_score / len(keywords)
        
        # 정규화 (0-100 범위)
        return min(round(avg_score / 10, 2), 100.0)

    async def _search_keyword_across_platforms(
        self, 
        keyword: str, 
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """플랫폼별 키워드 검색"""
        search_results = []
        
        for platform in platforms:
            try:
                if platform == "youtube":
                    results = await self.youtube_service.search_videos(query=keyword, max_results=20)
                elif platform == "tiktok":
                    results = await self.tiktok_service.search_videos(query=keyword, max_results=20)
                elif platform == "instagram":
                    results = await self.instagram_service.search_posts(query=keyword, max_results=20)
                else:
                    continue
                
                # 플랫폼 정보 추가
                for result in results:
                    result_dict = result.dict() if hasattr(result, 'dict') else result
                    result_dict['platform'] = platform
                    search_results.append(result_dict)
                    
            except Exception as e:
                print(f"{platform} 키워드 검색 실패: {str(e)}")
                continue
        
        return search_results

    async def _analyze_keyword_for_age_group(
        self, 
        search_results: List[Dict[str, Any]], 
        keyword: str, 
        age_group: str, 
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """특정 연령대에서의 키워드 분석"""
        mentions = 0
        platform_mentions = defaultdict(int)
        engagement_score = 0
        
        for result in search_results:
            title = result.get('title', '').lower()
            description = result.get('description', '').lower()
            platform = result.get('platform', '')
            
            # 키워드 언급 확인
            if keyword.lower() in title or keyword.lower() in description:
                mentions += 1
                platform_mentions[platform] += 1
                
                # 참여도 점수 계산
                engagement_score += self._calculate_engagement_score(result)
        
        # 연령대별 관련성 점수 계산
        relevance_score = self._calculate_age_relevance(keyword, age_group, patterns)
        
        return {
            "mentions": mentions,
            "platform_mentions": dict(platform_mentions),
            "engagement_score": round(engagement_score, 2),
            "relevance_score": round(relevance_score, 2),
            "trending_level": self._get_trending_level(engagement_score)
        }

    def _calculate_age_relevance(
        self, 
        keyword: str, 
        age_group: str, 
        patterns: Dict[str, Any]
    ) -> float:
        """연령대별 관련성 점수 계산"""
        if keyword.lower() in [kw.lower() for kw in patterns["keywords"]]:
            return patterns["weight"] * 100
        else:
            # 부분 매칭 확인
            for pattern_keyword in patterns["keywords"]:
                if keyword.lower() in pattern_keyword.lower() or pattern_keyword.lower() in keyword.lower():
                    return patterns["weight"] * 50
            return 10.0  # 기본 점수

    def _analyze_trending_direction(self, search_results: List[Dict[str, Any]]) -> str:
        """트렌드 방향 분석"""
        if not search_results:
            return "유지"
        
        # 최근 콘텐츠 비율로 트렌드 방향 추정
        recent_count = 0
        total_count = len(search_results)
        
        for result in search_results:
            published_at = result.get('published_at')
            if published_at:
                # 최근 7일 내 콘텐츠 확인
                if isinstance(published_at, str):
                    try:
                        published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        if datetime.now(published_date.tzinfo) - published_date < timedelta(days=7):
                            recent_count += 1
                    except:
                        pass
        
        recent_ratio = recent_count / total_count if total_count > 0 else 0
        
        if recent_ratio > 0.6:
            return "상승"
        elif recent_ratio > 0.3:
            return "유지"
        else:
            return "하락"

    def _extract_related_keywords(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """관련 키워드 추출"""
        all_text = ""
        for result in search_results:
            title = result.get('title', '')
            description = result.get('description', '')
            tags = ' '.join(result.get('tags', []))
            hashtags = ' '.join(result.get('hashtags', []))
            all_text += f"{title} {description} {tags} {hashtags} "
        
        # 한국어 키워드 추출 (간단한 정규식)
        korean_words = re.findall(r'[가-힣]{2,}', all_text)
        word_counts = Counter(korean_words)
        
        # 상위 10개 키워드 반환
        return [word for word, count in word_counts.most_common(10)]

    def _calculate_sentiment_score(
        self, 
        keyword: str, 
        search_results: List[Dict[str, Any]]
    ) -> float:
        """감정 점수 계산 (간단한 키워드 기반)"""
        positive_words = ['좋다', '최고', '대박', '완벽', '사랑', '추천', '인기', '성공']
        negative_words = ['나쁘다', '최악', '실패', '별로', '싫다', '문제', '실망', '실패']
        
        all_text = ""
        for result in search_results:
            title = result.get('title', '')
            description = result.get('description', '')
            all_text += f"{title} {description} "
        
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return round((positive_count - negative_count) / total, 2)

    async def _collect_age_specific_trends(
        self, 
        age_group: str, 
        patterns: Dict[str, Any], 
        platforms: List[str], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """연령대별 특화 트렌드 수집"""
        trends = await self._collect_trends_from_platforms(platforms, max_results * 2)
        
        # 연령대에 맞는 트렌드 필터링
        filtered_trends = []
        for trend in trends:
            title = trend.get('title', '').lower()
            description = trend.get('description', '').lower()
            text_content = f"{title} {description}"
            
            # 연령대 키워드와 매칭되는 트렌드만 선택
            for keyword in patterns["keywords"]:
                if keyword.lower() in text_content:
                    filtered_trends.append(trend)
                    break
        
        return filtered_trends[:max_results]

    def _extract_top_keywords(
        self, 
        trends: List[Dict[str, Any]], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """상위 키워드 추출"""
        keyword_scores = defaultdict(float)
        
        for trend in trends:
            title = trend.get('title', '')
            description = trend.get('description', '')
            tags = trend.get('tags', [])
            hashtags = trend.get('hashtags', [])
            
            # 한국어 키워드 추출
            text_content = f"{title} {description} {' '.join(tags)} {' '.join(hashtags)}"
            korean_words = re.findall(r'[가-힣]{2,}', text_content)
            
            engagement_score = self._calculate_engagement_score(trend)
            
            for word in korean_words:
                if len(word) >= 2:  # 2글자 이상만
                    keyword_scores[word] += engagement_score
        
        # 상위 키워드 반환
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                "keyword": keyword,
                "score": round(score, 2),
                "trending_level": self._get_trending_level(score)
            }
            for keyword, score in sorted_keywords[:max_results]
        ]

    def _analyze_trending_topics(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """트렌딩 토픽 분석"""
        topics = defaultdict(lambda: {"count": 0, "engagement": 0})
        
        for trend in trends:
            category = trend.get('category', '기타')
            engagement = self._calculate_engagement_score(trend)
            
            topics[category]["count"] += 1
            topics[category]["engagement"] += engagement
        
        return [
            {
                "topic": topic,
                "count": data["count"],
                "engagement": round(data["engagement"], 2),
                "avg_engagement": round(data["engagement"] / data["count"], 2) if data["count"] > 0 else 0
            }
            for topic, data in sorted(topics.items(), key=lambda x: x[1]["engagement"], reverse=True)
        ]

    def _calculate_platform_preferences(
        self, 
        trends: List[Dict[str, Any]], 
        platforms: List[str]
    ) -> Dict[str, float]:
        """플랫폼 선호도 계산"""
        platform_counts = defaultdict(int)
        total_count = len(trends)
        
        for trend in trends:
            platform = trend.get('platform', 'unknown')
            platform_counts[platform] += 1
        
        preferences = {}
        for platform in platforms:
            count = platform_counts[platform]
            preferences[platform] = round(count / total_count * 100, 2) if total_count > 0 else 0
        
        return preferences

    def _analyze_content_categories(self, trends: List[Dict[str, Any]]) -> Dict[str, int]:
        """콘텐츠 카테고리 분포 분석"""
        categories = defaultdict(int)
        
        for trend in trends:
            category = trend.get('category', '기타')
            categories[category] += 1
        
        return dict(categories) 