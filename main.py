"""
소셜 미디어 트렌드 조사 API
YouTube, TikTok, Instagram 플랫폼의 트렌드와 키워드를 조사하는 API 서비스
"""

from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# API 모듈들 임포트
from services.youtube_service import YouTubeService
from services.tiktok_service import TikTokService
from services.instagram_service import InstagramService
from models.response_models import TrendResponse, SearchResponse, ErrorResponse

# FastAPI 앱 생성
app = FastAPI(
    title="소셜 미디어 트렌드 조사 API",
    description="YouTube, TikTok, Instagram의 트렌드와 키워드를 조사하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 인스턴스 생성
youtube_service = YouTubeService()
tiktok_service = TikTokService()
instagram_service = InstagramService()

# 정적 파일, 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_model=Dict[str, str])
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "소셜 미디어 트렌드 조사 API에 오신 것을 환영합니다!",
        "docs": "/docs",
        "version": "1.0.0",
        "web_dashboard": "/web"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# ==================== YouTube API 엔드포인트 ====================

@app.get("/api/youtube/trends", response_model=List[TrendResponse])
async def get_youtube_trends(
    region_code: str = Query("KR", description="국가 코드 (예: KR, US, JP)"),
    category_id: Optional[str] = Query(None, description="카테고리 ID"),
    max_results: int = Query(25, description="최대 결과 수", ge=1, le=50)
):
    """YouTube 인기 동영상 조회"""
    try:
        trends = await youtube_service.get_trending_videos(
            region_code=region_code,
            category_id=category_id,
            max_results=max_results
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 트렌드 조회 실패: {str(e)}")

@app.get("/api/youtube/search", response_model=List[SearchResponse])
async def search_youtube(
    query: str = Query(..., description="검색 키워드"),
    max_results: int = Query(25, description="최대 결과 수", ge=1, le=50),
    order: str = Query("relevance", description="정렬 기준 (relevance, date, rating, viewCount)")
):
    """YouTube 동영상 검색"""
    try:
        results = await youtube_service.search_videos(
            query=query,
            max_results=max_results,
            order=order
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 검색 실패: {str(e)}")

@app.get("/api/youtube/channels/{channel_id}")
async def get_youtube_channel_info(channel_id: str):
    """YouTube 채널 정보 조회"""
    try:
        channel_info = await youtube_service.get_channel_info(channel_id)
        return channel_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채널 정보 조회 실패: {str(e)}")

# ==================== TikTok API 엔드포인트 ====================

@app.get("/api/tiktok/trends", response_model=List[TrendResponse])
async def get_tiktok_trends(
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """TikTok 인기 동영상 조회"""
    try:
        trends = await tiktok_service.get_trending_videos(max_results=max_results)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok 트렌드 조회 실패: {str(e)}")

@app.get("/api/tiktok/hashtags")
async def get_tiktok_hashtags(
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """TikTok 인기 해시태그 조회"""
    try:
        hashtags = await tiktok_service.get_trending_hashtags(max_results=max_results)
        return hashtags
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok 해시태그 조회 실패: {str(e)}")

@app.get("/api/tiktok/search", response_model=List[SearchResponse])
async def search_tiktok(
    query: str = Query(..., description="검색 키워드"),
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """TikTok 콘텐츠 검색"""
    try:
        results = await tiktok_service.search_videos(
            query=query,
            max_results=max_results
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok 검색 실패: {str(e)}")

# ==================== Instagram API 엔드포인트 ====================

@app.get("/api/instagram/trends", response_model=List[TrendResponse])
async def get_instagram_trends(
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """Instagram 인기 게시물 조회"""
    try:
        trends = await instagram_service.get_trending_posts(max_results=max_results)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram 트렌드 조회 실패: {str(e)}")

@app.get("/api/instagram/hashtags")
async def get_instagram_hashtags(
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """Instagram 인기 해시태그 조회"""
    try:
        hashtags = await instagram_service.get_trending_hashtags(max_results=max_results)
        return hashtags
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram 해시태그 조회 실패: {str(e)}")

@app.get("/api/instagram/search", response_model=List[SearchResponse])
async def search_instagram(
    query: str = Query(..., description="검색 키워드"),
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """Instagram 게시물 검색"""
    try:
        results = await instagram_service.search_posts(
            query=query,
            max_results=max_results
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram 검색 실패: {str(e)}")

# ==================== 통합 API 엔드포인트 ====================

@app.get("/api/trends/global")
async def get_global_trends(
    platforms: List[str] = Query(["youtube", "tiktok", "instagram"], description="조회할 플랫폼 목록"),
    max_results: int = Query(10, description="플랫폼당 최대 결과 수", ge=1, le=20)
):
    """모든 플랫폼의 트렌드 통합 조회"""
    try:
        global_trends = {}
        
        if "youtube" in platforms:
            global_trends["youtube"] = await youtube_service.get_trending_videos(max_results=max_results)
        
        if "tiktok" in platforms:
            global_trends["tiktok"] = await tiktok_service.get_trending_videos(max_results=max_results)
        
        if "instagram" in platforms:
            global_trends["instagram"] = await instagram_service.get_trending_posts(max_results=max_results)
        
        return global_trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전역 트렌드 조회 실패: {str(e)}")

@app.get("/api/search/global")
async def search_global(
    query: str = Query(..., description="검색 키워드"),
    platforms: List[str] = Query(["youtube", "tiktok", "instagram"], description="검색할 플랫폼 목록"),
    max_results: int = Query(10, description="플랫폼당 최대 결과 수", ge=1, le=20)
):
    """모든 플랫폼에서 통합 검색"""
    try:
        global_search = {}
        
        if "youtube" in platforms:
            global_search["youtube"] = await youtube_service.search_videos(query=query, max_results=max_results)
        
        if "tiktok" in platforms:
            global_search["tiktok"] = await tiktok_service.search_videos(query=query, max_results=max_results)
        
        if "instagram" in platforms:
            global_search["instagram"] = await instagram_service.search_posts(query=query, max_results=max_results)
        
        return global_search
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전역 검색 실패: {str(e)}")

@app.get("/api/trends/realtime")
async def get_realtime_trends(
    region_code: str = Query("KR", description="국가 코드 (예: KR, US, JP)"),
    max_results: int = Query(50, description="최대 결과 수", ge=1, le=100)
):
    """실시간 인기 검색어 및 트렌딩 동영상 조회"""
    try:
        # YouTube 실시간 트렌딩 동영상 조회
        youtube_trends = await youtube_service.get_trending_videos(
            region_code=region_code,
            max_results=max_results
        )
        
        # TikTok 실시간 트렌딩 동영상 조회
        tiktok_trends = await tiktok_service.get_trending_videos(max_results=max_results)
        
        # Instagram 실시간 트렌딩 게시물 조회
        instagram_trends = await instagram_service.get_trending_posts(max_results=max_results)
        
        # 실시간 인기 검색어 추출 (해시태그 기반)
        trending_keywords = await extract_trending_keywords(youtube_trends, tiktok_trends, instagram_trends)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "region": region_code,
            "trending_keywords": trending_keywords,
            "youtube_trends": youtube_trends[:10],  # 상위 10개만
            "tiktok_trends": tiktok_trends[:10],
            "instagram_trends": instagram_trends[:10],
            "total_trends": len(youtube_trends) + len(tiktok_trends) + len(instagram_trends)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 트렌드 조회 실패: {str(e)}")

@app.get("/api/trends/keywords")
async def get_trending_keywords(
    max_results: int = Query(20, description="최대 키워드 수", ge=1, le=50)
):
    """실시간 인기 검색어만 조회"""
    try:
        # 각 플랫폼의 트렌딩 콘텐츠 조회
        youtube_trends = await youtube_service.get_trending_videos(max_results=50)
        tiktok_trends = await tiktok_service.get_trending_videos(max_results=50)
        instagram_trends = await instagram_service.get_trending_posts(max_results=50)
        
        # 인기 검색어 추출
        trending_keywords = await extract_trending_keywords(youtube_trends, tiktok_trends, instagram_trends)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "trending_keywords": trending_keywords[:max_results],
            "total_keywords": len(trending_keywords)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인기 검색어 조회 실패: {str(e)}")

async def extract_trending_keywords(youtube_trends, tiktok_trends, instagram_trends):
    """트렌딩 콘텐츠에서 인기 검색어 추출"""
    keyword_scores = {}
    
    # YouTube 트렌딩에서 키워드 추출
    for trend in youtube_trends:
        # 제목과 설명에서 키워드 추출
        text = f"{trend.title} {trend.description or ''}"
        keywords = extract_keywords_from_text(text)
        
        for keyword in keywords:
            if keyword not in keyword_scores:
                keyword_scores[keyword] = {"count": 0, "total_views": 0, "platforms": set()}
            
            keyword_scores[keyword]["count"] += 1
            keyword_scores[keyword]["total_views"] += trend.view_count or 0
            keyword_scores[keyword]["platforms"].add("youtube")
    
    # TikTok 트렌딩에서 키워드 추출
    for trend in tiktok_trends:
        text = f"{trend.title} {trend.description or ''}"
        keywords = extract_keywords_from_text(text)
        
        for keyword in keywords:
            if keyword not in keyword_scores:
                keyword_scores[keyword] = {"count": 0, "total_views": 0, "platforms": set()}
            
            keyword_scores[keyword]["count"] += 1
            keyword_scores[keyword]["total_views"] += trend.view_count or 0
            keyword_scores[keyword]["platforms"].add("tiktok")
    
    # Instagram 트렌딩에서 키워드 추출
    for trend in instagram_trends:
        text = f"{trend.title} {trend.description or ''}"
        keywords = extract_keywords_from_text(text)
        
        for keyword in keywords:
            if keyword not in keyword_scores:
                keyword_scores[keyword] = {"count": 0, "total_views": 0, "platforms": set()}
            
            keyword_scores[keyword]["count"] += 1
            keyword_scores[keyword]["total_views"] += trend.view_count or 0
            keyword_scores[keyword]["platforms"].add("instagram")
    
    # 점수 계산 및 정렬
    trending_keywords = []
    for keyword, data in keyword_scores.items():
        # 트렌딩 점수 계산 (등장 횟수 + 조회수 + 플랫폼 수)
        trending_score = (data["count"] * 10) + (data["total_views"] // 1000) + (len(data["platforms"]) * 5)
        
        trending_keywords.append({
            "keyword": keyword,
            "trending_score": trending_score,
            "count": data["count"],
            "total_views": data["total_views"],
            "platforms": list(data["platforms"]),
            "platform_count": len(data["platforms"])
        })
    
    # 트렌딩 점수 기준으로 정렬
    trending_keywords.sort(key=lambda x: x["trending_score"], reverse=True)
    
    return trending_keywords

def extract_keywords_from_text(text):
    """텍스트에서 키워드 추출"""
    if not text:
        return []
    
    import re
    
    # 한글, 영문, 숫자로 구성된 단어 추출 (2글자 이상)
    keywords = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text.lower())
    
    # 불용어 제거
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '에서', '으로', '에게', '를', '을'
    }
    
    # 해시태그 제거 (이미 별도로 처리됨)
    keywords = [kw for kw in keywords if not kw.startswith('#') and kw not in stop_words]
    
    return keywords

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={"error": "서버 내부 오류가 발생했습니다", "detail": str(exc)}
    )

@app.get("/web")
async def web_dashboard(request: Request, keyword: str = ""):
    """웹 대시보드: 키워드 입력 및 결과 시각화"""
    trends = []
    search_results = []
    error = None
    if keyword:
        try:
            # YouTube 트렌드 100개
            trends = await youtube_service.search_videos(query=keyword, max_results=100)
            # YouTube 검색량(조회수 합산)
            total_views = sum([t.view_count or 0 for t in trends])
            # 키워드 순위(조회수 기준 상위 10개)
            top_trends = sorted(trends, key=lambda x: x.view_count or 0, reverse=True)[:10]
        except Exception as e:
            error = str(e)
            trends = []
            total_views = 0
            top_trends = []
    else:
        total_views = 0
        top_trends = []
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "keyword": keyword,
        "trends": trends,
        "total_views": total_views,
        "top_trends": top_trends,
        "error": error
    })

if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 