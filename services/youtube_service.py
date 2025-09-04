"""
YouTube Data API v3 서비스
YouTube의 트렌드 동영상, 검색, 채널 정보 등을 조회하는 서비스
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.base_service import BaseSocialMediaService
from models.response_models import (
    TrendResponse,
    SearchResponse,
    HashtagResponse,
    ChannelResponse,
    YouTubeAnalyzeRequest,
    YouTubeAnalyzeRow,
    YouTubeAnalyzeResponse,
)

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

    # ==================== 분석 기능 ====================
    async def analyze(self, req: YouTubeAnalyzeRequest) -> YouTubeAnalyzeResponse:
        """채널/키워드 기반 최근 N일 영상 수집 및 필터링"""
        if not self.youtube:
            raise Exception("YouTube API 클라이언트가 초기화되지 않았습니다.")

        collected: List[YouTubeAnalyzeRow] = []

        # 1) 수집 대상 결정
        do_channel = req.mode in ("channel", "both") and req.channel_handles
        do_keyword = req.mode in ("keyword", "both") and req.keywords

        # 2) 채널 단위 수집
        if do_channel:
            for handle in req.channel_handles or []:
                try:
                    channel_id = await self._resolve_channel_id_by_handle(handle)
                    videos = await self._fetch_recent_videos_by_channel(
                        channel_id=channel_id,
                        max_results=req.max_per_channel,
                        region_code=req.region,
                    )
                    rows = [self._to_analyze_row(v) for v in videos]
                    collected.extend(rows)
                except Exception as e:
                    self.log_error("analyze_channel", e)

        # 3) 키워드 단위 수집
        if do_keyword:
            for keyword in req.keywords or []:
                try:
                    results = await self.search_videos(keyword, max_results=req.max_per_keyword, order="date")
                    rows = [self._to_analyze_row_from_search(r) for r in results]
                    collected.extend(rows)
                except Exception as e:
                    self.log_error("analyze_keyword", e)

        # 4) 기간/폼 필터링
        collected = self._filter_by_time_and_form(
            rows=collected,
            timeframe_days=req.timeframe_days,
            form=req.form,
            shorts_threshold=req.shorts_threshold_seconds,
        )

        # 5) 통계 정보(구독자, 조회/구독 비율) 보강
        collected = await self._enrich_with_channel_stats(collected)

        # 6) 최소 조건 필터링
        filtered_rows = []
        for row in collected:
            if row.view_count is None:
                continue
            views_ok = row.view_count >= req.min_view_count
            vph_ok = (row.views_per_hour or 0) >= req.min_views_per_hour
            if views_ok and vph_ok:
                filtered_rows.append(row)

        settings_summary = {
            "mode": req.mode,
            "form": req.form,
            "timeframe_days": req.timeframe_days,
            "region": req.region,
            "language": req.language,
            "thresholds": {
                "min_view_count": req.min_view_count,
                "min_views_per_hour": req.min_views_per_hour,
                "shorts_threshold_seconds": req.shorts_threshold_seconds,
            },
        }

        return YouTubeAnalyzeResponse(
            rows=filtered_rows,
            total=len(collected),
            filtered=len(filtered_rows),
            settings=settings_summary,
        )

    # -------------------- 내부 유틸 --------------------
    async def _resolve_channel_id_by_handle(self, handle: str) -> str:
        """@handle -> channelId 해석"""
        handle = handle.strip().lstrip("@")
        try:
            req = self.youtube.search().list(part="snippet", q=f"@{handle}", type="channel", maxResults=1)
            res = req.execute()
            items = res.get("items", [])
            if not items:
                raise Exception(f"채널 핸들을 찾을 수 없음: {handle}")
            return items[0]["snippet"]["channelId"]
        except Exception as e:
            self.log_error("resolve_channel_id", e)
            raise

    async def _fetch_recent_videos_by_channel(self, channel_id: str, max_results: int, region_code: str) -> List[Dict[str, Any]]:
        """채널의 최신 영상 조회 후 상세정보 반환"""
        # 채널 업로드 플레이리스트 조회 -> 최신 영상 검색
        search_req = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            regionCode=region_code,
            maxResults=min(max_results, 50),
        )
        search_res = search_req.execute()
        video_ids = [i["id"]["videoId"] for i in search_res.get("items", [])]
        if not video_ids:
            return []
        videos_req = self.youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
        videos_res = videos_req.execute()
        return videos_res.get("items", [])

    def _to_analyze_row(self, video: Dict[str, Any]) -> YouTubeAnalyzeRow:
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        published_at = snippet.get("publishedAt")
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00')) if published_at else None
        view_count = self.safe_int(statistics.get("viewCount"))
        views_per_hour = None
        if dt and view_count is not None:
            hours = max((datetime.now(dt.tzinfo) - dt).total_seconds() / 3600, 1e-6)
            views_per_hour = round(view_count / hours, 2)
        duration = self.parse_duration(content_details.get("duration", ""))
        video_id = video.get("id", "") if isinstance(video.get("id"), str) else video.get("id", {}).get("videoId", "")
        return YouTubeAnalyzeRow(
            video_id=video_id,
            channel_id=snippet.get("channelId"),
            channel_name=snippet.get("channelTitle", ""),
            title=snippet.get("title", ""),
            published_at=dt,
            view_count=view_count,
            views_per_hour=views_per_hour,
            subscriber_count=None,
            view_to_subscriber_ratio=None,
            duration=duration,
            video_url=f"https://www.youtube.com/watch?v={video_id}",
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
        )

    def _to_analyze_row_from_search(self, search: Dict[str, Any] | SearchResponse) -> YouTubeAnalyzeRow:
        # SearchResponse 또는 dict 지원
        if hasattr(search, 'dict'):
            data = search.dict()
            video_id = data.get('id')
            view_count = data.get('view_count')
            published_at = data.get('published_at')
            dt = published_at
            if isinstance(published_at, str):
                try:
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except Exception:
                    dt = None
            views_per_hour = None
            if dt and view_count is not None:
                hours = max((datetime.now(dt.tzinfo) - dt).total_seconds() / 3600, 1e-6)
                views_per_hour = round(view_count / hours, 2)
            return YouTubeAnalyzeRow(
                video_id=video_id,
                channel_id=None,
                channel_name=data.get('author') or '',
                title=data.get('title') or '',
                published_at=dt,
                view_count=view_count,
                views_per_hour=views_per_hour,
                subscriber_count=None,
                view_to_subscriber_ratio=None,
                duration=None,
                video_url=f"https://www.youtube.com/watch?v={video_id}",
                thumbnail_url=data.get('thumbnail_url'),
            )
        else:
            # dict (search API 원본)
            vid = search.get('id', {}).get('videoId')
            snippet = search.get('snippet', {})
            dt = None
            if snippet.get('publishedAt'):
                try:
                    dt = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                except Exception:
                    dt = None
            return YouTubeAnalyzeRow(
                video_id=vid or '',
                channel_id=snippet.get('channelId'),
                channel_name=snippet.get('channelTitle', ''),
                title=snippet.get('title', ''),
                published_at=dt,
                view_count=None,
                views_per_hour=None,
                subscriber_count=None,
                view_to_subscriber_ratio=None,
                duration=None,
                video_url=f"https://www.youtube.com/watch?v={vid}",
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
            )

    def _filter_by_time_and_form(self, rows: List[YouTubeAnalyzeRow], timeframe_days: int, form: str, shorts_threshold: int) -> List[YouTubeAnalyzeRow]:
        threshold_dt = datetime.now().astimezone() - timedelta(days=timeframe_days)
        result: List[YouTubeAnalyzeRow] = []
        for r in rows:
            if r.published_at and r.published_at < threshold_dt:
                continue
            # 폼 필터
            if form != 'both' and r.duration is not None:
                # duration 형식 m:ss 또는 h:mm:ss => 초로 변환
                total_seconds = self._duration_to_seconds(r.duration)
                is_shorts = total_seconds <= shorts_threshold
                if form == 'shorts' and not is_shorts:
                    continue
                if form == 'long' and is_shorts:
                    continue
            result.append(r)
        return result

    async def _enrich_with_channel_stats(self, rows: List[YouTubeAnalyzeRow]) -> List[YouTubeAnalyzeRow]:
        # 채널별로 구독자 수를 조회하여 비율 계산
        channel_ids = list({r.channel_id for r in rows if r.channel_id})
        id_to_subs: Dict[str, Optional[int]] = {}
        for chunk_start in range(0, len(channel_ids), 50):
            chunk = channel_ids[chunk_start:chunk_start+50]
            if not chunk:
                continue
            try:
                req = self.youtube.channels().list(part="statistics", id=",".join(chunk))
                res = req.execute()
                for item in res.get('items', []):
                    cid = item.get('id')
                    subs = self.safe_int(item.get('statistics', {}).get('subscriberCount'))
                    id_to_subs[cid] = subs
            except Exception as e:
                self.log_error("enrich_channel_stats", e)
        # 반영
        for r in rows:
            if r.channel_id and r.channel_id in id_to_subs:
                r.subscriber_count = id_to_subs[r.channel_id]
                if r.subscriber_count and r.view_count:
                    r.view_to_subscriber_ratio = round(r.view_count / max(r.subscriber_count, 1), 2)
        return rows

    def _duration_to_seconds(self, duration_str: str) -> int:
        if not duration_str:
            return 0
        parts = duration_str.split(':')
        try:
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(s)
            if len(parts) == 2:
                m, s = parts
                return int(m) * 60 + int(s)
            return int(parts[0])
        except Exception:
            return 0
    
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