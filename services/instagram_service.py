"""
Instagram Basic Display API 서비스
Instagram의 트렌드 게시물, 해시태그, 검색 등을 조회하는 서비스
참고: Instagram API는 제한적이므로 일부 기능은 샘플 데이터로 대체합니다.
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.base_service import BaseSocialMediaService
from models.response_models import TrendResponse, SearchResponse, HashtagResponse

class InstagramService(BaseSocialMediaService):
    """Instagram Basic Display API 서비스"""
    
    def __init__(self):
        super().__init__("instagram")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.app_id = os.getenv("INSTAGRAM_APP_ID")
        self.app_secret = os.getenv("INSTAGRAM_APP_SECRET")
        self.base_url = "https://graph.instagram.com/v12.0"
        
        if not self.access_token:
            self.logger.warning("Instagram 액세스 토큰이 설정되지 않았습니다. 일부 기능이 제한될 수 있습니다.")
    
    async def get_trending_videos(self, max_results: int = 20) -> List[TrendResponse]:
        """Instagram 인기 게시물 조회 (제한적) - 기본 클래스 호환성을 위해 videos로 명명"""
        try:
            self.log_request("trending_posts", {"max_results": max_results})
            
            # Instagram은 공식 API로 트렌드 게시물을 제공하지 않으므로 샘플 데이터 반환
            # 실제 구현에서는 웹 스크래핑이나 비공식 API를 사용해야 함
            sample_posts = self._get_sample_trending_posts(max_results)
            
            self.log_response("trending_posts", len(sample_posts))
            return sample_posts
            
        except Exception as e:
            self.log_error("trending_posts", e)
            raise Exception(f"Instagram 트렌드 조회 실패: {str(e)}")
    
    async def get_trending_posts(self, max_results: int = 20) -> List[TrendResponse]:
        """Instagram 인기 게시물 조회 (제한적)"""
        return await self.get_trending_videos(max_results)
    
    async def search_videos(self, query: str, max_results: int = 20) -> List[SearchResponse]:
        """Instagram 게시물 검색 (제한적) - 기본 클래스 호환성을 위해 videos로 명명"""
        try:
            self.log_request("search_posts", {
                "query": query,
                "max_results": max_results
            })
            
            # Instagram은 공식 API로 검색을 제공하지 않으므로 샘플 데이터 반환
            # 실제 구현에서는 웹 스크래핑이나 비공식 API를 사용해야 함
            sample_results = self._get_sample_search_results(query, max_results)
            
            self.log_response("search_posts", len(sample_results))
            return sample_results
            
        except Exception as e:
            self.log_error("search_posts", e)
            raise Exception(f"Instagram 검색 실패: {str(e)}")
    
    async def search_posts(self, query: str, max_results: int = 20) -> List[SearchResponse]:
        """Instagram 게시물 검색 (제한적)"""
        return await self.search_videos(query, max_results)
    
    async def get_trending_hashtags(self, max_results: int = 20) -> List[HashtagResponse]:
        """Instagram 인기 해시태그 조회 (제한적)"""
        try:
            self.log_request("trending_hashtags", {"max_results": max_results})
            
            # Instagram은 공식 API로 해시태그 트렌드를 제공하지 않으므로 샘플 데이터 반환
            # 실제 구현에서는 웹 스크래핑이나 비공식 API를 사용해야 함
            sample_hashtags = self._get_sample_trending_hashtags(max_results)
            
            self.log_response("trending_hashtags", len(sample_hashtags))
            return sample_hashtags
            
        except Exception as e:
            self.log_error("trending_hashtags", e)
            raise Exception(f"Instagram 해시태그 조회 실패: {str(e)}")
    
    async def get_user_media(self, user_id: str = "me", max_results: int = 20) -> List[TrendResponse]:
        """사용자 미디어 조회 (Instagram Basic Display API 사용)"""
        if not self.access_token:
            raise Exception("Instagram 액세스 토큰이 필요합니다.")
        
        try:
            self.log_request("user_media", {"user_id": user_id, "max_results": max_results})
            
            url = f"{self.base_url}/{user_id}/media"
            params = {
                "access_token": self.access_token,
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                "limit": min(max_results, 25)  # API 제한
            }
            
            response_data = await self.make_request(url, params=params)
            media_items = response_data.get('data', [])
            
            # 결과 변환
            posts = []
            for item in media_items:
                try:
                    post = self._convert_media_to_trend(item)
                    posts.append(post)
                except Exception as e:
                    self.logger.warning(f"미디어 변환 실패: {str(e)}")
                    continue
            
            self.log_response("user_media", len(posts))
            return posts
            
        except Exception as e:
            self.log_error("user_media", e)
            raise
    
    def _get_sample_trending_posts(self, max_results: int) -> List[TrendResponse]:
        """샘플 트렌딩 게시물 데이터 생성"""
        sample_posts = [
            {
                "id": "instagram_trend_001",
                "title": "인기 Instagram 게시물 #1",
                "description": "샘플 트렌딩 게시물입니다. 실제 구현에서는 Instagram API나 웹 스크래핑을 사용해야 합니다.",
                "author": "instagram_user_1",
                "view_count": 850000,
                "like_count": 45000,
                "comment_count": 1800,
                "share_count": 1200,
                "hashtags": ["#trending", "#viral", "#instagram"]
            },
            {
                "id": "instagram_trend_002",
                "title": "인기 Instagram 게시물 #2",
                "description": "또 다른 샘플 트렌딩 게시물입니다.",
                "author": "instagram_user_2",
                "view_count": 720000,
                "like_count": 38000,
                "comment_count": 1500,
                "share_count": 980,
                "hashtags": ["#fashion", "#style", "#trending"]
            },
            {
                "id": "instagram_trend_003",
                "title": "인기 Instagram 게시물 #3",
                "description": "세 번째 샘플 트렌딩 게시물입니다.",
                "author": "instagram_user_3",
                "view_count": 650000,
                "like_count": 32000,
                "comment_count": 1200,
                "share_count": 850,
                "hashtags": ["#food", "#delicious", "#viral"]
            }
        ]
        
        posts = []
        for i, post in enumerate(sample_posts[:max_results]):
            posts.append(TrendResponse(
                id=post["id"],
                title=post["title"],
                description=post["description"],
                url=f"https://www.instagram.com/p/{post['id']}/",
                thumbnail_url=None,  # 실제 구현에서는 썸네일 URL을 가져와야 함
                platform="instagram",
                author=post["author"],
                author_url=f"https://www.instagram.com/{post['author']}/",
                view_count=post["view_count"],
                like_count=post["like_count"],
                comment_count=post["comment_count"],
                share_count=post["share_count"],
                published_at=datetime.now(),  # 실제 구현에서는 실제 게시 시간을 가져와야 함
                duration=None,  # Instagram은 동영상 길이를 API로 제공하지 않음
                tags=None,
                hashtags=post["hashtags"],
                category=None,
                language="ko",
                region="KR"
            ))
        
        return posts
    
    def _get_sample_search_results(self, query: str, max_results: int) -> List[SearchResponse]:
        """샘플 검색 결과 데이터 생성"""
        sample_results = [
            {
                "id": f"instagram_search_{query}_001",
                "title": f"'{query}' 관련 Instagram 게시물 #1",
                "description": f"'{query}' 키워드로 검색된 샘플 게시물입니다.",
                "author": "instagram_search_user_1",
                "view_count": 450000,
                "like_count": 25000,
                "comment_count": 800,
                "hashtags": [f"#{query}", "#search", "#instagram"]
            },
            {
                "id": f"instagram_search_{query}_002",
                "title": f"'{query}' 관련 Instagram 게시물 #2",
                "description": f"'{query}' 키워드로 검색된 또 다른 샘플 게시물입니다.",
                "author": "instagram_search_user_2",
                "view_count": 380000,
                "like_count": 22000,
                "comment_count": 650,
                "hashtags": [f"#{query}", "#trending", "#viral"]
            }
        ]
        
        results = []
        for i, result in enumerate(sample_results[:max_results]):
            results.append(SearchResponse(
                id=result["id"],
                title=result["title"],
                description=result["description"],
                url=f"https://www.instagram.com/p/{result['id']}/",
                thumbnail_url=None,
                platform="instagram",
                author=result["author"],
                author_url=f"https://www.instagram.com/{result['author']}/",
                view_count=result["view_count"],
                like_count=result["like_count"],
                comment_count=result["comment_count"],
                published_at=datetime.now(),
                relevance_score=0.9 - (i * 0.1),  # 샘플 관련도 점수
                tags=None,
                hashtags=result["hashtags"]
            ))
        
        return results
    
    def _get_sample_trending_hashtags(self, max_results: int) -> List[HashtagResponse]:
        """샘플 트렌딩 해시태그 데이터 생성"""
        sample_hashtags = [
            {"hashtag": "#instagram", "post_count": 2500000, "view_count": 80000000},
            {"hashtag": "#trending", "post_count": 1800000, "view_count": 60000000},
            {"hashtag": "#viral", "post_count": 1500000, "view_count": 50000000},
            {"hashtag": "#fashion", "post_count": 1200000, "view_count": 40000000},
            {"hashtag": "#food", "post_count": 980000, "view_count": 35000000},
            {"hashtag": "#travel", "post_count": 850000, "view_count": 30000000},
            {"hashtag": "#beauty", "post_count": 720000, "view_count": 25000000},
            {"hashtag": "#lifestyle", "post_count": 650000, "view_count": 22000000}
        ]
        
        hashtags = []
        for i, hashtag_data in enumerate(sample_hashtags[:max_results]):
            hashtags.append(HashtagResponse(
                hashtag=hashtag_data["hashtag"],
                post_count=hashtag_data["post_count"],
                view_count=hashtag_data["view_count"],
                platform="instagram",
                trending_score=1.0 - (i * 0.1),  # 샘플 트렌딩 점수
                related_hashtags=[f"#{sample_hashtags[j]['hashtag'][1:]}" for j in range(i+1, min(i+4, len(sample_hashtags)))]
            ))
        
        return hashtags
    
    def _convert_media_to_trend(self, media_item: Dict[str, Any]) -> TrendResponse:
        """Instagram API 응답을 TrendResponse로 변환"""
        caption = media_item.get('caption', '')
        hashtags = self.extract_hashtags(caption)
        
        return TrendResponse(
            id=media_item.get('id', ''),
            title=caption[:100] if caption else "Instagram 게시물",
            description=self.truncate_text(caption),
            url=media_item.get('permalink', ''),
            thumbnail_url=media_item.get('thumbnail_url') or media_item.get('media_url'),
            platform="instagram",
            author="me",  # Instagram Basic Display API는 자신의 게시물만 조회 가능
            author_url="https://www.instagram.com/me/",
            view_count=None,  # Instagram API는 조회수를 제공하지 않음
            like_count=self.safe_int(media_item.get('like_count')),
            comment_count=self.safe_int(media_item.get('comments_count')),
            share_count=None,  # Instagram API는 공유 수를 제공하지 않음
            published_at=datetime.fromisoformat(media_item.get('timestamp', '').replace('Z', '+00:00')) if media_item.get('timestamp') else None,
            duration=None,  # Instagram은 동영상 길이를 API로 제공하지 않음
            tags=None,
            hashtags=hashtags,
            category=media_item.get('media_type', ''),
            language="ko",
            region="KR"
        ) 