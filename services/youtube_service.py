"""
YouTube Data API v3 서비스
YouTube의 트렌드 동영상, 검색, 채널 정보 등을 조회하는 서비스
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.base_service import BaseSocialMediaService
from models.response_models import TrendResponse, SearchResponse, HashtagResponse, ChannelResponse

class YouTubeService(BaseSocialMediaService):
    """YouTube Data API v3 서비스"""
    
    def __init__(self):
        super().__init__("youtube")
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            self.logger.warning("YouTube API 키가 설정되지 않았습니다. 일부 기능이 제한될 수 있습니다.")
        
        # YouTube API 클라이언트 초기화
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        except Exception as e:
            self.logger.error(f"YouTube API 클라이언트 초기화 실패: {str(e)}")
            self.youtube = None
    
    async def get_trending_videos(self, region_code: str = "KR", 
                                category_id: Optional[str] = None,
                                max_results: int = 25) -> List[TrendResponse]:
        """YouTube 인기 동영상 조회"""
        if not self.youtube:
            raise Exception("YouTube API 클라이언트가 초기화되지 않았습니다.")
        
        try:
            self.log_request("trending_videos", {
                "region_code": region_code,
                "category_id": category_id,
                "max_results": max_results
            })
            
            # 트렌딩 동영상 조회
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=min(max_results, 50),  # API 제한
                videoCategoryId=category_id if category_id else None
            )
            
            response = request.execute()
            videos = response.get('items', [])
            
            # 결과 변환
            trends = []
            for video in videos:
                try:
                    trend = self._convert_video_to_trend(video)
                    trends.append(trend)
                except Exception as e:
                    self.logger.warning(f"동영상 변환 실패: {str(e)}")
                    continue
            
            self.log_response("trending_videos", len(trends))
            return trends
            
        except HttpError as e:
            error_msg = f"YouTube API 오류: {e.resp.status} - {e.content.decode()}"
            self.log_error("trending_videos", Exception(error_msg))
            raise Exception(error_msg)
        except Exception as e:
            self.log_error("trending_videos", e)
            raise
    
    async def search_videos(self, query: str, max_results: int = 25, 
                          order: str = "relevance") -> List[SearchResponse]:
        """YouTube 동영상 검색"""
        if not self.youtube:
            raise Exception("YouTube API 클라이언트가 초기화되지 않았습니다.")
        
        try:
            self.log_request("search_videos", {
                "query": query,
                "max_results": max_results,
                "order": order
            })
            
            # 동영상 검색
            search_request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                order=order,
                maxResults=min(max_results, 50)
            )
            
            search_response = search_request.execute()
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # 상세 정보 조회
            videos_request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=','.join(video_ids)
            )
            
            videos_response = videos_request.execute()
            videos = videos_response.get('items', [])
            
            # 결과 변환
            results = []
            for video in videos:
                try:
                    result = self._convert_video_to_search(video)
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"검색 결과 변환 실패: {str(e)}")
                    continue
            
            self.log_response("search_videos", len(results))
            return results
            
        except HttpError as e:
            error_msg = f"YouTube API 오류: {e.resp.status} - {e.content.decode()}"
            self.log_error("search_videos", Exception(error_msg))
            raise Exception(error_msg)
        except Exception as e:
            self.log_error("search_videos", e)
            raise
    
    async def get_channel_info(self, channel_id: str) -> ChannelResponse:
        """YouTube 채널 정보 조회"""
        if not self.youtube:
            raise Exception("YouTube API 클라이언트가 초기화되지 않았습니다.")
        
        try:
            self.log_request("channel_info", {"channel_id": channel_id})
            
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            
            response = request.execute()
            channels = response.get('items', [])
            
            if not channels:
                raise Exception(f"채널을 찾을 수 없습니다: {channel_id}")
            
            channel = channels[0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})
            
            channel_info = ChannelResponse(
                id=channel_id,
                name=snippet.get('title', ''),
                description=snippet.get('description', ''),
                url=f"https://www.youtube.com/channel/{channel_id}",
                avatar_url=snippet.get('thumbnails', {}).get('default', {}).get('url'),
                platform="youtube",
                follower_count=self.safe_int(statistics.get('subscriberCount')),
                following_count=None,  # YouTube는 following_count를 제공하지 않음
                post_count=self.safe_int(statistics.get('videoCount')),
                verified=snippet.get('verified', False),
                created_at=datetime.fromisoformat(snippet.get('publishedAt', '').replace('Z', '+00:00')) if snippet.get('publishedAt') else None
            )
            
            self.log_response("channel_info", 1)
            return channel_info
            
        except HttpError as e:
            error_msg = f"YouTube API 오류: {e.resp.status} - {e.content.decode()}"
            self.log_error("channel_info", Exception(error_msg))
            raise Exception(error_msg)
        except Exception as e:
            self.log_error("channel_info", e)
            raise
    
    async def get_trending_hashtags(self, max_results: int = 20) -> List[HashtagResponse]:
        """YouTube 인기 해시태그 조회 (제한적)"""
        # YouTube는 공식적으로 해시태그 트렌드를 제공하지 않으므로
        # 인기 동영상에서 해시태그를 추출하는 방식으로 구현
        try:
            trending_videos = await self.get_trending_videos(max_results=50)
            
            # 해시태그 수집
            hashtag_count = {}
            for video in trending_videos:
                if video.hashtags:
                    for hashtag in video.hashtags:
                        hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
            
            # 인기 순으로 정렬
            sorted_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)
            
            # 결과 변환
            hashtags = []
            for hashtag, count in sorted_hashtags[:max_results]:
                hashtags.append(HashtagResponse(
                    hashtag=hashtag,
                    post_count=count,
                    view_count=None,  # YouTube 해시태그는 개별 조회수를 제공하지 않음
                    platform="youtube",
                    trending_score=count / len(trending_videos) if trending_videos else 0,
                    related_hashtags=None  # 관련 해시태그 정보는 별도 분석 필요
                ))
            
            return hashtags
            
        except Exception as e:
            self.log_error("trending_hashtags", e)
            raise
    
    def _convert_video_to_trend(self, video: Dict[str, Any]) -> TrendResponse:
        """YouTube API 응답을 TrendResponse로 변환"""
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})
        
        # 해시태그 추출
        description = snippet.get('description', '')
        title = snippet.get('title', '')
        hashtags = self.extract_hashtags(description + ' ' + title)
        
        return TrendResponse(
            id=video.get('id', ''),
            title=snippet.get('title', ''),
            description=self.truncate_text(snippet.get('description', '')),
            url=f"https://www.youtube.com/watch?v={video.get('id', '')}",
            thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
            platform="youtube",
            author=snippet.get('channelTitle', ''),
            author_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
            view_count=self.safe_int(statistics.get('viewCount')),
            like_count=self.safe_int(statistics.get('likeCount')),
            comment_count=self.safe_int(statistics.get('commentCount')),
            share_count=None,  # YouTube API는 공유 수를 직접 제공하지 않음
            published_at=datetime.fromisoformat(snippet.get('publishedAt', '').replace('Z', '+00:00')) if snippet.get('publishedAt') else None,
            duration=self.parse_duration(content_details.get('duration', '')),
            tags=None,  # YouTube는 태그를 API로 제공하지 않음
            hashtags=hashtags,
            category=snippet.get('categoryId', ''),
            language=snippet.get('defaultLanguage', ''),
            region=snippet.get('defaultAudioLanguage', '')
        )
    
    def _convert_video_to_search(self, video: Dict[str, Any]) -> SearchResponse:
        """YouTube API 응답을 SearchResponse로 변환"""
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        
        # 해시태그 추출
        description = snippet.get('description', '')
        title = snippet.get('title', '')
        hashtags = self.extract_hashtags(description + ' ' + title)
        
        return SearchResponse(
            id=video.get('id', ''),
            title=snippet.get('title', ''),
            description=self.truncate_text(snippet.get('description', '')),
            url=f"https://www.youtube.com/watch?v={video.get('id', '')}",
            thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
            platform="youtube",
            author=snippet.get('channelTitle', ''),
            author_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
            view_count=self.safe_int(statistics.get('viewCount')),
            like_count=self.safe_int(statistics.get('likeCount')),
            comment_count=self.safe_int(statistics.get('commentCount')),
            published_at=datetime.fromisoformat(snippet.get('publishedAt', '').replace('Z', '+00:00')) if snippet.get('publishedAt') else None,
            relevance_score=None,  # YouTube API는 관련도 점수를 제공하지 않음
            tags=None,  # YouTube는 태그를 API로 제공하지 않음
            hashtags=hashtags
        ) 