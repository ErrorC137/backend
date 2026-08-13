"""Test rate limiting and cost monitoring functionality."""

from app.ai_services.rate_limiter import RateLimiter, CostMonitor, RateLimitConfig

# Test rate limiter
print("=== Testing Rate Limiter ===")
config = RateLimitConfig(
    requests_per_minute=10,
    requests_per_hour=100,
    tokens_per_minute=100000,
    cost_per_hour_usd=10.0
)

rate_limiter = RateLimiter(config)

# Test rate limit check
allowed, message = rate_limiter.check_rate_limit(tokens=5000, cost_usd=0.50)
print(f"Rate limit check (5000 tokens, $0.50): {allowed}")
if message:
    print(f"Message: {message}")

# Record some requests
rate_limiter.record_request(
    provider="anthropic",
    tokens=5000,
    cost_usd=0.50,
    success=True
)

rate_limiter.record_request(
    provider="openai",
    tokens=3000,
    cost_usd=0.30,
    success=True
)

# Get usage stats
stats = rate_limiter.get_usage_stats()
print(f"\nUsage Statistics:")
print(f"Total Requests: {stats['total_requests']}")
print(f"Successful Requests: {stats['successful_requests']}")
print(f"Failed Requests: {stats['failed_requests']}")
print(f"Success Rate: {stats['success_rate']:.2%}")
print(f"Total Tokens: {stats['total_tokens']}")
print(f"Total Cost: ${stats['total_cost_usd']:.2f}")
print(f"Average Tokens per Request: {stats['average_tokens_per_request']:.0f}")
print(f"Average Cost per Request: ${stats['average_cost_per_request']:.2f}")
print(f"Requests by Provider: {stats['requests_by_provider']}")
print(f"Tokens by Provider: {stats['tokens_by_provider']}")
print(f"Cost by Provider: {stats['cost_by_provider']}")

# Test cost monitor
print("\n=== Testing Cost Monitor ===")
cost_monitor = CostMonitor(
    daily_budget_usd=100.0,
    hourly_budget_usd=10.0,
    alert_threshold_percent=0.8
)

# Record some costs
cost_monitor.record_cost(2.50)
cost_monitor.record_cost(3.75)
cost_monitor.record_cost(1.25)

# Get cost stats
cost_stats = cost_monitor.get_cost_stats()
print(f"\nCost Statistics:")
print(f"Hourly Cost: ${cost_stats['hourly_cost_usd']:.2f}")
print(f"Daily Cost: ${cost_stats['daily_cost_usd']:.2f}")
print(f"Hourly Budget: ${cost_stats['hourly_budget_usd']:.2f}")
print(f"Daily Budget: ${cost_stats['daily_budget_usd']:.2f}")
print(f"Hourly Budget Remaining: ${cost_stats['hourly_budget_remaining']:.2f}")
print(f"Daily Budget Remaining: ${cost_stats['daily_budget_remaining']:.2f}")
print(f"Hourly Budget Used: {cost_stats['hourly_budget_percent']:.1%}")
print(f"Daily Budget Used: {cost_stats['daily_budget_percent']:.1%}")
print(f"Alerts Triggered: {cost_stats['alerts_triggered']}")

# Test rate limit threshold
print("\n=== Testing Rate Limit Threshold ===")
for i in range(12):  # Try to exceed the 10 request limit
    allowed, message = rate_limiter.check_rate_limit()
    if not allowed:
        print(f"Request {i+1}: BLOCKED - {message}")
        break
    else:
        print(f"Request {i+1}: ALLOWED")
        rate_limiter.record_request("anthropic", 1000, 0.10, True)

print("\n=== All rate limiting and cost monitoring tests completed successfully ===")
