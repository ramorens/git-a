"""Redis缓存管理模块"""
import os
import json
import hashlib
import redis
from typing import Optional

# Redis配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# 缓存过期时间（秒）
CACHE_EXPIRE_TIME = 3600 * 24  # 24小时


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis连接失败，缓存功能已禁用: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_key(self, prefix: str, content: str) -> str:
        """生成缓存键"""
        hash_value = hashlib.md5(content.encode('utf-8')).hexdigest()
        return f"{prefix}:{hash_value}"
    
    def get_resume_cache(self, pdf_content: bytes) -> Optional[dict]:
        """获取简历解析缓存"""
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key('resume', pdf_content.decode('latin-1'))
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"获取缓存失败: {str(e)}")
        return None
    
    def set_resume_cache(self, pdf_content: bytes, resume_data: dict):
        """设置简历解析缓存"""
        if not self.enabled:
            return
        
        try:
            key = self._generate_key('resume', pdf_content.decode('latin-1'))
            self.redis_client.setex(
                key,
                CACHE_EXPIRE_TIME,
                json.dumps(resume_data, ensure_ascii=False)
            )
        except Exception as e:
            print(f"设置缓存失败: {str(e)}")
    
    def get_match_cache(self, resume_info: dict, job_requirements: str) -> Optional[dict]:
        """获取匹配评分缓存"""
        if not self.enabled:
            return None
        
        try:
            cache_key = json.dumps(resume_info, ensure_ascii=False, sort_keys=True) + job_requirements
            key = self._generate_key('match', cache_key)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"获取缓存失败: {str(e)}")
        return None
    
    def set_match_cache(self, resume_info: dict, job_requirements: str, match_data: dict):
        """设置匹配评分缓存"""
        if not self.enabled:
            return
        
        try:
            cache_key = json.dumps(resume_info, ensure_ascii=False, sort_keys=True) + job_requirements
            key = self._generate_key('match', cache_key)
            self.redis_client.setex(
                key,
                CACHE_EXPIRE_TIME,
                json.dumps(match_data, ensure_ascii=False)
            )
        except Exception as e:
            print(f"设置缓存失败: {str(e)}")


# 全局缓存管理器实例
cache_manager = CacheManager()
