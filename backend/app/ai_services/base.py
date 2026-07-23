"""Base AI service layer with multi-provider support and fallback logic."""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import httpx


class Provider(Enum):
    """Available AI providers."""
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"


@dataclass
class AIModelConfig:
    """Configuration for an AI model."""
    provider: Provider
    model: str
    max_tokens: int = 4000
    temperature: float = 0.3
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    provider: Provider
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.client = httpx.Client(timeout=60.0)
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AIResponse:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate the cost of the API call."""
        pass
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AIResponse:
        """Generate a response from the AI model."""
        start_time = time.time()
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.config.model,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "messages": messages,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["content"][0]["text"]
            tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_cost(tokens_used)
            
            return AIResponse(
                content=content,
                model=self.config.model,
                provider=Provider.ANTHROPIC,
                tokens_used=tokens_used,
                cost_usd=cost,
                latency_ms=latency_ms,
                success=True,
            )
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.ANTHROPIC,
                latency_ms=latency_ms,
                success=False,
                error_message=f"HTTP error: {e.response.status_code}",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.ANTHROPIC,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost for Claude API."""
        # Claude 3.5 Sonnet pricing: $3/M input, $15/M output
        # Assuming 50/50 split for estimation
        input_tokens = tokens_used // 2
        output_tokens = tokens_used - input_tokens
        cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
        return cost


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter API provider for multi-model access."""
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AIResponse:
        """Generate a response using OpenRouter API."""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "messages": messages,
        }
        
        try:
            response = self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_cost(tokens_used)
            
            return AIResponse(
                content=content,
                model=self.config.model,
                provider=Provider.OPENROUTER,
                tokens_used=tokens_used,
                cost_usd=cost,
                latency_ms=latency_ms,
                success=True,
            )
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.OPENROUTER,
                latency_ms=latency_ms,
                success=False,
                error_message=f"HTTP error: {e.response.status_code}",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.OPENROUTER,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost for OpenRouter API."""
        # OpenRouter pricing varies by model, using Claude 3.5 Sonnet as baseline
        input_tokens = tokens_used // 2
        output_tokens = tokens_used - input_tokens
        cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
        return cost


class GoogleProvider(BaseAIProvider):
    """Google Gemini API provider."""
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AIResponse:
        """Generate a response using Google Gemini API."""
        start_time = time.time()
        
        # Combine system prompt with user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
            },
        }
        
        try:
            response = self.client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent?key={self.api_key}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_cost(tokens_used)
            
            return AIResponse(
                content=content,
                model=self.config.model,
                provider=Provider.GOOGLE,
                tokens_used=tokens_used,
                cost_usd=cost,
                latency_ms=latency_ms,
                success=True,
            )
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.GOOGLE,
                latency_ms=latency_ms,
                success=False,
                error_message=f"HTTP error: {e.response.status_code}",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model,
                provider=Provider.GOOGLE,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost for Google Gemini API."""
        # Gemini 1.5 Pro pricing: $3.5/M input, $10.5/M output
        input_tokens = tokens_used // 2
        output_tokens = tokens_used - input_tokens
        cost = (input_tokens * 3.5 / 1_000_000) + (output_tokens * 10.5 / 1_000_000)
        return cost


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek API provider."""
    
    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AIResponse:
        """Generate a response using DeepSeek API."""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model or "deepseek-chat",
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "messages": messages,
        }
        
        try:
            response = self.client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            cost = self._calculate_cost(tokens_used)
            
            return AIResponse(
                content=content,
                model=self.config.model or "deepseek-chat",
                provider=Provider.DEEPSEEK,
                tokens_used=tokens_used,
                cost_usd=cost,
                latency_ms=latency_ms,
                success=True,
            )
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model or "deepseek-chat",
                provider=Provider.DEEPSEEK,
                latency_ms=latency_ms,
                success=False,
                error_message=f"HTTP error: {e.response.status_code}",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AIResponse(
                content="",
                model=self.config.model or "deepseek-chat",
                provider=Provider.DEEPSEEK,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost for DeepSeek API."""
        # DeepSeek pricing: $1/M input, $2/M output
        input_tokens = tokens_used // 2
        output_tokens = tokens_used - input_tokens
        cost = (input_tokens * 1 / 1_000_000) + (output_tokens * 2 / 1_000_000)
        return cost


class AIService:
    """Main AI service with multi-provider support and fallback logic."""
    
    def __init__(self):
        self.providers: dict[Provider, BaseAIProvider] = {}
        self.provider_priority: list[Provider] = []
        self.cost_tracking_enabled = os.getenv("COST_MONITORING_ENABLED", "true").lower() == "true"
        self.total_cost_usd = 0.0
        self.total_tokens = 0
        self.total_requests = 0
        self.failed_requests = 0
    
    def add_provider(self, provider: BaseAIProvider, priority: int = 0):
        """Add a provider with priority (lower = higher priority)."""
        self.providers[provider.config.provider] = provider
        self.provider_priority.append(provider.config.provider)
        self.provider_priority.sort(key=lambda p: priority if p == provider.config.provider else 0)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        preferred_provider: Optional[Provider] = None,
    ) -> AIResponse:
        """Generate a response with automatic fallback."""
        self.total_requests += 1
        
        # Try preferred provider first if specified
        if preferred_provider and preferred_provider in self.providers:
            response = await self._try_provider(
                preferred_provider, prompt, system_prompt, max_tokens, temperature
            )
            if response.success:
                self._track_usage(response)
                return response
        
        # Try providers in priority order
        for provider in self.provider_priority:
            if preferred_provider and provider == preferred_provider:
                continue  # Already tried
            
            response = await self._try_provider(
                provider, prompt, system_prompt, max_tokens, temperature
            )
            if response.success:
                self._track_usage(response)
                return response
        
        # All providers failed
        self.failed_requests += 1
        return AIResponse(
            content="",
            model="unknown",
            provider=Provider.ANTHROPIC,
            success=False,
            error_message="All AI providers failed",
        )
    
    async def _try_provider(
        self,
        provider: Provider,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: Optional[int],
        temperature: Optional[float],
    ) -> AIResponse:
        """Try a specific provider."""
        if provider not in self.providers:
            return AIResponse(
                content="",
                model="unknown",
                provider=provider,
                success=False,
                error_message=f"Provider {provider.value} not configured",
            )
        
        try:
            return await self.providers[provider].generate(
                prompt, system_prompt, max_tokens, temperature
            )
        except Exception as e:
            return AIResponse(
                content="",
                model="unknown",
                provider=provider,
                success=False,
                error_message=str(e),
            )
    
    def _track_usage(self, response: AIResponse):
        """Track usage statistics."""
        if self.cost_tracking_enabled:
            self.total_cost_usd += response.cost_usd
            self.total_tokens += response.tokens_used
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                (self.total_requests - self.failed_requests) / self.total_requests
                if self.total_requests > 0
                else 0
            ),
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "average_cost_per_request": (
                self.total_cost_usd / self.total_requests
                if self.total_requests > 0
                else 0
            ),
        }
    
    def close(self):
        """Close all provider clients."""
        for provider in self.providers.values():
            provider.close()


def create_ai_service() -> AIService:
    """Create and configure the AI service with available providers."""
    service = AIService()
    
    # Add Anthropic (Claude) - highest priority
    if os.getenv("ANTHROPIC_API_KEY"):
        anthropic_config = AIModelConfig(
            provider=Provider.ANTHROPIC,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.3")),
        )
        service.add_provider(AnthropicProvider(anthropic_config), priority=1)
    
    # Add Google - second priority
    if os.getenv("GOOGLE_API_KEY"):
        google_config = AIModelConfig(
            provider=Provider.GOOGLE,
            model=os.getenv("GOOGLE_MODEL", "gemini-1.5-pro"),
            max_tokens=int(os.getenv("GOOGLE_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("GOOGLE_TEMPERATURE", "0.3")),
        )
        service.add_provider(GoogleProvider(google_config), priority=2)
    
    # Add OpenRouter - third priority
    if os.getenv("OPENROUTER_API_KEY"):
        openrouter_config = AIModelConfig(
            provider=Provider.OPENROUTER,
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.3")),
        )
        service.add_provider(OpenRouterProvider(openrouter_config), priority=3)
    
    # Add DeepSeek - lowest priority (fallback)
    if os.getenv("DEEPSEEK_API_KEY"):
        deepseek_config = AIModelConfig(
            provider=Provider.DEEPSEEK,
            model="deepseek-chat",
            max_tokens=4000,
            temperature=0.3,
        )
        service.add_provider(DeepSeekProvider(deepseek_config), priority=4)
    
    return service
