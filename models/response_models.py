"""
API 응답 모델 정의
소셜 미디어 플랫폼의 트렌드 및 검색 결과를 위한 데이터 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TrendResponse(BaseModel):
    """트렌드 응답 모델"""
    id: str = Field(..., description="콘텐츠 고유 ID")
    title: str = Field(..., description="콘텐츠 제목")
    description: Optional[str] = Field(None, description="콘텐츠 설명")
    url: str = Field(..., description="콘텐츠 URL")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 이미지 URL")
    platform: str = Field(..., description="플랫폼명 (youtube, tiktok, instagram)")
    author: Optional[str] = Field(None, description="작성자/채널명")
    author_url: Optional[str] = Field(None, description="작성자 프로필 URL")
    view_count: Optional[int] = Field(None, description="조회수")
    like_count: Optional[int] = Field(None, description="좋아요 수")
    comment_count: Optional[int] = Field(None, description="댓글 수")
    share_count: Optional[int] = Field(None, description="공유 수")
    published_at: Optional[datetime] = Field(None, description="게시일시")
    duration: Optional[str] = Field(None, description="동영상 길이")
    tags: Optional[List[str]] = Field(None, description="태그 목록")
    hashtags: Optional[List[str]] = Field(None, description="해시태그 목록")
    category: Optional[str] = Field(None, description="카테고리")
    language: Optional[str] = Field(None, description="언어")
    region: Optional[str] = Field(None, description="지역")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SearchResponse(BaseModel):
    """검색 결과 응답 모델"""
    id: str = Field(..., description="콘텐츠 고유 ID")
    title: str = Field(..., description="콘텐츠 제목")
    description: Optional[str] = Field(None, description="콘텐츠 설명")
    url: str = Field(..., description="콘텐츠 URL")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 이미지 URL")
    platform: str = Field(..., description="플랫폼명")
    author: Optional[str] = Field(None, description="작성자/채널명")
    author_url: Optional[str] = Field(None, description="작성자 프로필 URL")
    view_count: Optional[int] = Field(None, description="조회수")
    like_count: Optional[int] = Field(None, description="좋아요 수")
    comment_count: Optional[int] = Field(None, description="댓글 수")
    published_at: Optional[datetime] = Field(None, description="게시일시")
    relevance_score: Optional[float] = Field(None, description="관련도 점수")
    tags: Optional[List[str]] = Field(None, description="태그 목록")
    hashtags: Optional[List[str]] = Field(None, description="해시태그 목록")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HashtagResponse(BaseModel):
    """해시태그 응답 모델"""
    hashtag: str = Field(..., description="해시태그명")
    post_count: Optional[int] = Field(None, description="게시물 수")
    view_count: Optional[int] = Field(None, description="조회수")
    platform: str = Field(..., description="플랫폼명")
    trending_score: Optional[float] = Field(None, description="트렌딩 점수")
    related_hashtags: Optional[List[str]] = Field(None, description="관련 해시태그")

class ChannelResponse(BaseModel):
    """채널/계정 정보 응답 모델"""
    id: str = Field(..., description="채널/계정 ID")
    name: str = Field(..., description="채널/계정명")
    description: Optional[str] = Field(None, description="설명")
    url: str = Field(..., description="프로필 URL")
    avatar_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    platform: str = Field(..., description="플랫폼명")
    follower_count: Optional[int] = Field(None, description="팔로워 수")
    following_count: Optional[int] = Field(None, description="팔로잉 수")
    post_count: Optional[int] = Field(None, description="게시물 수")
    verified: Optional[bool] = Field(None, description="인증 여부")
    created_at: Optional[datetime] = Field(None, description="계정 생성일")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    code: Optional[str] = Field(None, description="에러 코드")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GlobalTrendsResponse(BaseModel):
    """전역 트렌드 응답 모델"""
    youtube: Optional[List[TrendResponse]] = Field(None, description="YouTube 트렌드")
    tiktok: Optional[List[TrendResponse]] = Field(None, description="TikTok 트렌드")
    instagram: Optional[List[TrendResponse]] = Field(None, description="Instagram 트렌드")
    timestamp: datetime = Field(default_factory=datetime.now, description="조회 시간")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GlobalSearchResponse(BaseModel):
    """전역 검색 응답 모델"""
    youtube: Optional[List[SearchResponse]] = Field(None, description="YouTube 검색 결과")
    tiktok: Optional[List[SearchResponse]] = Field(None, description="TikTok 검색 결과")
    instagram: Optional[List[SearchResponse]] = Field(None, description="Instagram 검색 결과")
    query: str = Field(..., description="검색 쿼리")
    total_results: int = Field(..., description="전체 결과 수")
    timestamp: datetime = Field(default_factory=datetime.now, description="검색 시간")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 