"""
소셜 미디어 서비스 기본 클래스
모든 플랫폼별 서비스가 상속받는 공통 기능들을 정의
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import logging
from datetime import datetime

from models.response_models import TrendResponse, SearchResponse, HashtagResponse

class BaseSocialMediaService(ABC):
    """소셜 미디어 서비스 기본 클래스"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{platform_name}_service")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def get_trending_videos(self, max_results: int = 25, **kwargs) -> List[TrendResponse]:
        """인기 동영상 조회 (추상 메서드)"""
        pass
    
    @abstractmethod
    async def search_videos(self, query: str, max_results: int = 25, **kwargs) -> List[SearchResponse]:
        """동영상 검색 (추상 메서드)"""
        pass
    
    @abstractmethod
    async def get_trending_hashtags(self, max_results: int = 20) -> List[HashtagResponse]:
        """인기 해시태그 조회 (추상 메서드)"""
        pass
    
    async def make_request(self, url: str, headers: Optional[Dict[str, str]] = None, 
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """HTTP 요청 수행 (공통 메서드)"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"HTTP 요청 실패: {response.status} - {response.reason}")
                    raise Exception(f"HTTP {response.status}: {response.reason}")
        except Exception as e:
            self.logger.error(f"요청 중 오류 발생: {str(e)}")
            raise
    
    def parse_duration(self, duration_str: str) -> str:
        """ISO 8601 형식의 시간을 읽기 쉬운 형식으로 변환"""
        if not duration_str:
            return ""
            
        # PT1H2M3S 형식을 1:02:03 형식으로 변환
        duration = duration_str.replace("PT", "")
        hours = 0
        minutes = 0
        seconds = 0
        
        if "H" in duration:
            hours = int(duration.split("H")[0])
            duration = duration.split("H")[1]
        
        if "M" in duration:
            minutes = int(duration.split("M")[0])
            duration = duration.split("M")[1]
            
        if "S" in duration:
            seconds = int(duration.split("S")[0])
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def extract_hashtags(self, text: str) -> List[str]:
        """텍스트에서 해시태그 추출"""
        if not text:
            return []
        
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def safe_int(self, value: Any) -> Optional[int]:
        """안전한 정수 변환"""
        try:
            if value is None:
                return None
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def safe_float(self, value: Any) -> Optional[float]:
        """안전한 실수 변환"""
        try:
            if value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def truncate_text(self, text: str, max_length: int = 200) -> str:
        """텍스트 길이 제한"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    async def rate_limit_delay(self, delay_seconds: float = 1.0):
        """API 요청 제한을 위한 지연"""
        await asyncio.sleep(delay_seconds)
    
    def log_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        """요청 로깅"""
        self.logger.info(f"{self.platform_name} API 요청: {endpoint}")
        if params:
            self.logger.debug(f"파라미터: {params}")
    
    def log_response(self, endpoint: str, result_count: int):
        """응답 로깅"""
        self.logger.info(f"{self.platform_name} API 응답: {endpoint} - {result_count}개 결과")
    
    def log_error(self, endpoint: str, error: Exception):
        """에러 로깅"""
        self.logger.error(f"{self.platform_name} API 에러: {endpoint} - {str(error)}") 