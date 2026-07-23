"""Rate limiting and cost monitoring for AI services."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    tokens_per_minute: int = 100000
    cost_per_hour_usd: float = 10.0


@dataclass
class UsageStats:
    """Usage statistics tracking."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    requests_by_provider: dict[str, int] = field(default_factory=dict)
    tokens_by_provider: dict[str, int] = field(default_factory=dict)
    cost_by_provider: dict[str, float] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)


class RateLimiter:
    """Rate limiter for AI API calls."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.request_timestamps: list[float] = []
        self.token_usage: list[tuple[float, int]] = []
        self.cost_tracking: list[tuple[float, float]] = []
        self.usage_stats = UsageStats()
    
    def check_rate_limit(self, tokens: int = 0, cost_usd: float = 0.0) -> tuple[bool, Optional[str]]:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Check requests per minute
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_timestamps if t > minute_ago]
        
        if len(recent_requests) >= self.config.requests_per_minute:
            return False, f"Rate limit exceeded: {len(recent_requests)} requests in the last minute (limit: {self.config.requests_per_minute})"
        
        # Check requests per hour
        hour_ago = current_time - 3600
        recent_hour_requests = [t for t in self.request_timestamps if t > hour_ago]
        
        if len(recent_hour_requests) >= self.config.requests_per_hour:
            return False, f"Rate limit exceeded: {len(recent_hour_requests)} requests in the last hour (limit: {self.config.requests_per_hour})"
        
        # Check tokens per minute
        recent_tokens = [t for t, tokens in self.token_usage if t > minute_ago]
        total_tokens = sum(tokens for _, tokens in recent_tokens)
        
        if total_tokens + tokens > self.config.tokens_per_minute:
            return False, f"Token rate limit exceeded: {total_tokens + tokens} tokens in the last minute (limit: {self.config.tokens_per_minute})"
        
        # Check cost per hour
        recent_costs = [t for t, cost in self.cost_tracking if t > hour_ago]
        total_cost = sum(cost for _, cost in recent_costs)
        
        if total_cost + cost_usd > self.config.cost_per_hour_usd:
            return False, f"Cost limit exceeded: ${total_cost + cost_usd:.2f} in the last hour (limit: ${self.config.cost_per_hour_usd:.2f})"
        
        return True, None
    
    def record_request(
        self,
        provider: str,
        tokens: int,
        cost_usd: float,
        success: bool,
    ):
        """Record a request for rate limiting and statistics."""
        current_time = time.time()
        
        # Record timestamp
        self.request_timestamps.append(current_time)
        
        # Record token usage
        self.token_usage.append((current_time, tokens))
        
        # Record cost
        self.cost_tracking.append((current_time, cost_usd))
        
        # Update statistics
        self.usage_stats.total_requests += 1
        if success:
            self.usage_stats.successful_requests += 1
        else:
            self.usage_stats.failed_requests += 1
        
        self.usage_stats.total_tokens += tokens
        self.usage_stats.total_cost_usd += cost_usd
        
        # Update provider-specific stats
        self.usage_stats.requests_by_provider[provider] = (
            self.usage_stats.requests_by_provider.get(provider, 0) + 1
        )
        self.usage_stats.tokens_by_provider[provider] = (
            self.usage_stats.tokens_by_provider.get(provider, 0) + tokens
        )
        self.usage_stats.cost_by_provider[provider] = (
            self.usage_stats.cost_by_provider.get(provider, 0.0) + cost_usd
        )
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
    
    def _cleanup_old_entries(self, current_time: float):
        """Clean up entries older than 1 hour."""
        hour_ago = current_time - 3600
        
        self.request_timestamps = [t for t in self.request_timestamps if t > hour_ago]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > hour_ago]
        self.cost_tracking = [(t, cost) for t, cost in self.cost_tracking if t > hour_ago]
    
    def get_wait_time(self) -> float:
        """Get estimated wait time until next request is allowed."""
        current_time = time.time()
        
        # Check requests per minute
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_timestamps if t > minute_ago]
        
        if len(recent_requests) >= self.config.requests_per_minute:
            oldest_recent = min(recent_requests)
            return max(0, oldest_recent + 60 - current_time)
        
        # Check tokens per minute
        recent_tokens = [(t, tokens) for t, tokens in self.token_usage if t > minute_ago]
        total_tokens = sum(tokens for _, tokens in recent_tokens)
        
        if total_tokens >= self.config.tokens_per_minute:
            oldest_recent = min(t for t, _ in recent_tokens)
            return max(0, oldest_recent + 60 - current_time)
        
        return 0.0
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics."""
        uptime = time.time() - self.usage_stats.start_time
        
        return {
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "success_rate": (
                self.usage_stats.successful_requests / self.usage_stats.total_requests
                if self.usage_stats.total_requests > 0
                else 0
            ),
            "total_tokens": self.usage_stats.total_tokens,
            "total_cost_usd": self.usage_stats.total_cost_usd,
            "average_tokens_per_request": (
                self.usage_stats.total_tokens / self.usage_stats.total_requests
                if self.usage_stats.total_requests > 0
                else 0
            ),
            "average_cost_per_request": (
                self.usage_stats.total_cost_usd / self.usage_stats.total_requests
                if self.usage_stats.total_requests > 0
                else 0
            ),
            "requests_per_minute": len([t for t in self.request_timestamps if t > time.time() - 60]),
            "uptime_seconds": uptime,
            "requests_by_provider": self.usage_stats.requests_by_provider,
            "tokens_by_provider": self.usage_stats.tokens_by_provider,
            "cost_by_provider": self.usage_stats.cost_by_provider,
        }
    
    def reset(self):
        """Reset rate limiter statistics."""
        self.request_timestamps = []
        self.token_usage = []
        self.cost_tracking = []
        self.usage_stats = UsageStats()


class CostMonitor:
    """Monitor and alert on AI service costs."""
    
    def __init__(
        self,
        daily_budget_usd: float = 100.0,
        hourly_budget_usd: float = 10.0,
        alert_threshold_percent: float = 0.8,
    ):
        self.daily_budget_usd = daily_budget_usd
        self.hourly_budget_usd = hourly_budget_usd
        self.alert_threshold_percent = alert_threshold_percent
        self.daily_costs: list[tuple[float, float]] = []
        self.hourly_costs: list[tuple[float, float]] = []
        self.alerts_triggered: list[str] = []
    
    def record_cost(self, cost_usd: float):
        """Record a cost for monitoring."""
        current_time = time.time()
        
        self.daily_costs.append((current_time, cost_usd))
        self.hourly_costs.append((current_time, cost_usd))
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check for alerts
        self._check_alerts()
    
    def _cleanup_old_entries(self, current_time: float):
        """Clean up entries older than 24 hours."""
        day_ago = current_time - 86400
        hour_ago = current_time - 3600
        
        self.daily_costs = [(t, cost) for t, cost in self.daily_costs if t > day_ago]
        self.hourly_costs = [(t, cost) for t, cost in self.hourly_costs if t > hour_ago]
    
    def _check_alerts(self):
        """Check if cost thresholds have been exceeded."""
        current_time = time.time()
        
        # Check hourly budget
        hour_ago = current_time - 3600
        recent_hourly_costs = [cost for t, cost in self.hourly_costs if t > hour_ago]
        total_hourly_cost = sum(recent_hourly_costs)
        
        if total_hourly_cost >= self.hourly_budget_usd * self.alert_threshold_percent:
            alert = f"Hourly cost threshold exceeded: ${total_hourly_cost:.2f} (threshold: ${self.hourly_budget_usd * self.alert_threshold_percent:.2f})"
            if alert not in self.alerts_triggered:
                self.alerts_triggered.append(alert)
                print(f"COST ALERT: {alert}")
        
        # Check daily budget
        day_ago = current_time - 86400
        recent_daily_costs = [cost for t, cost in self.daily_costs if t > day_ago]
        total_daily_cost = sum(recent_daily_costs)
        
        if total_daily_cost >= self.daily_budget_usd * self.alert_threshold_percent:
            alert = f"Daily cost threshold exceeded: ${total_daily_cost:.2f} (threshold: ${self.daily_budget_usd * self.alert_threshold_percent:.2f})"
            if alert not in self.alerts_triggered:
                self.alerts_triggered.append(alert)
                print(f"COST ALERT: {alert}")
    
    def get_cost_stats(self) -> dict:
        """Get current cost statistics."""
        current_time = time.time()
        
        hour_ago = current_time - 3600
        day_ago = current_time - 86400
        
        recent_hourly_costs = [cost for t, cost in self.hourly_costs if t > hour_ago]
        recent_daily_costs = [cost for t, cost in self.daily_costs if t > day_ago]
        
        return {
            "hourly_cost_usd": sum(recent_hourly_costs),
            "daily_cost_usd": sum(recent_daily_costs),
            "hourly_budget_usd": self.hourly_budget_usd,
            "daily_budget_usd": self.daily_budget_usd,
            "hourly_budget_remaining": max(0, self.hourly_budget_usd - sum(recent_hourly_costs)),
            "daily_budget_remaining": max(0, self.daily_budget_usd - sum(recent_daily_costs)),
            "hourly_budget_percent": sum(recent_hourly_costs) / self.hourly_budget_usd if self.hourly_budget_usd > 0 else 0,
            "daily_budget_percent": sum(recent_daily_costs) / self.daily_budget_usd if self.daily_budget_usd > 0 else 0,
            "alerts_triggered": self.alerts_triggered,
        }
    
    def reset(self):
        """Reset cost monitoring."""
        self.daily_costs = []
        self.hourly_costs = []
        self.alerts_triggered = []


# Global rate limiter and cost monitor instances
_global_rate_limiter: Optional[RateLimiter] = None
_global_cost_monitor: Optional[CostMonitor] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(config)
    return _global_rate_limiter


def get_cost_monitor(
    daily_budget_usd: float = 100.0,
    hourly_budget_usd: float = 10.0,
    alert_threshold_percent: float = 0.8,
) -> CostMonitor:
    """Get or create the global cost monitor instance."""
    global _global_cost_monitor
    if _global_cost_monitor is None:
        _global_cost_monitor = CostMonitor(
            daily_budget_usd, hourly_budget_usd, alert_threshold_percent
        )
    return _global_cost_monitor
