"""
速率限制中间件
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import time


class RateLimiter:
    """基于滑动窗口的速率限制器"""

    def __init__(self):
        # 存储每个 IP 的请求时间戳
        self.requests: Dict[str, List[float]] = defaultdict(list)
        # 默认限制：20次/分钟
        self.default_limit = 20
        self.window_seconds = 60

    def is_allowed(self, client_ip: str, limit: int = None) -> tuple[bool, int]:
        """
        检查是否允许请求

        Args:
            client_ip: 客户端 IP
            limit: 速率限制（None 使用默认值）

        Returns:
            (是否允许, 剩余次数)
        """
        if limit is None:
            limit = self.default_limit

        # 无限制
        if limit == 0:
            return True, -1

        now = time.time()
        window_start = now - self.window_seconds

        # 清理过期的请求记录
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]

        # 检查是否超过限制
        current_count = len(self.requests[client_ip])

        if current_count >= limit:
            return False, 0

        # 记录本次请求
        self.requests[client_ip].append(now)

        remaining = limit - current_count - 1
        return True, remaining

    def get_retry_after(self, client_ip: str) -> int:
        """
        获取需要等待的秒数

        Args:
            client_ip: 客户端 IP

        Returns:
            需要等待的秒数
        """
        if not self.requests[client_ip]:
            return 0

        oldest_request = min(self.requests[client_ip])
        retry_after = int(self.window_seconds - (time.time() - oldest_request))
        return max(0, retry_after)

    def cleanup(self):
        """清理过期的记录（定期调用）"""
        now = time.time()
        window_start = now - self.window_seconds

        # 清理所有过期记录
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if req_time > window_start
            ]
            # 删除空记录
            if not self.requests[ip]:
                del self.requests[ip]


# 全局速率限制器实例
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实 IP

    优先从 X-Forwarded-For 获取（支持反向代理）
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def check_rate_limit(
    request: Request,
    api_key: str = None,
    limit: int = None
) -> None:
    """
    检查速率限制

    Args:
        request: FastAPI 请求对象
        api_key: API Key（白名单用户）
        limit: 自定义限制（None 使用默认值）

    Raises:
        HTTPException: 超过速率限制时抛出 429 错误
    """
    # 如果有有效的 API Key，跳过限制检查
    if api_key:
        # 这里应该验证 API Key 并获取其速率限制
        # 暂时简化处理：有 API Key 就不限制
        return

    client_ip = get_client_ip(request)
    allowed, remaining = rate_limiter.is_allowed(client_ip, limit)

    if not allowed:
        retry_after = rate_limiter.get_retry_after(client_ip)
        raise HTTPException(
            status_code=429,
            detail={
                "code": 429,
                "message": f"请求过于频繁，请稍后再试（限制：{limit or rate_limiter.default_limit}次/分钟）",
                "data": [],
                "retry_after": retry_after
            },
            headers={
                "X-RateLimit-Limit": str(limit or rate_limiter.default_limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                "Retry-After": str(retry_after)
            }
        )
