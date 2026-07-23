"""Agent Coordinator for task distribution and result aggregation."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from app.ai_services.agents.ip_agent import IPAnalysisAgent, IPAnalysisResult
from app.ai_services.agents.market_agent import MarketAnalysisAgent, MarketAnalysisResult
from app.ai_services.agents.technical_agent import TechnicalAnalysisAgent, TechnicalAnalysisResult
from app.ai_services.agents.trl_agent import TRLAssessmentAgent, TRLAssessmentResult
from app.ai_services.base import AIService


@dataclass
class AgentTask:
    """Task to be executed by an agent."""
    task_type: str
    document_content: str
    abstract: str
    methodology: str
    claims_outcomes: str
    sector: str = ""
    working_field: str = ""
    patent_data: Optional[dict[str, Any]] = None
    market_data: Optional[dict[str, Any]] = None
    valuation_data: Optional[dict[str, Any]] = None
    trl_level: int = 3
    priority: int = 0


@dataclass
class AgentResult:
    """Result from an agent execution."""
    task_type: str
    success: bool
    result: Optional[Any]
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    provider_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0


@dataclass
class CoordinatorResult:
    """Combined result from all agents."""
    trl_assessment: Optional[TRLAssessmentResult] = None
    market_analysis: Optional[MarketAnalysisResult] = None
    ip_analysis: Optional[IPAnalysisResult] = None
    technical_analysis: Optional[TechnicalAnalysisResult] = None
    total_execution_time_ms: float = 0.0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    agent_results: list[AgentResult] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None


class AgentCoordinator:
    """Coordinator for managing multiple AI agents and aggregating results."""
    
    def __init__(self, ai_service: AIService, timeout_seconds: int = 300):
        self.ai_service = ai_service
        self.timeout_seconds = timeout_seconds
        self.trl_agent = TRLAssessmentAgent(ai_service)
        self.market_agent = MarketAnalysisAgent(ai_service)
        self.ip_agent = IPAnalysisAgent(ai_service)
        self.technical_agent = TechnicalAnalysisAgent(ai_service)
    
    async def coordinate_analysis(
        self,
        task: AgentTask,
        parallel: bool = True,
    ) -> CoordinatorResult:
        """Coordinate analysis across all agents."""
        start_time = time.time()
        result = CoordinatorResult()
        
        if parallel:
            # Execute all agents in parallel
            agent_results = await asyncio.gather(
                self._execute_trl_agent(task),
                self._execute_market_agent(task),
                self._execute_ip_agent(task),
                self._execute_technical_agent(task),
                return_exceptions=True,
            )
            
            # Process results
            for agent_result in agent_results:
                if isinstance(agent_result, Exception):
                    result.agent_results.append(
                        AgentResult(
                            task_type="unknown",
                            success=False,
                            error_message=str(agent_result),
                        )
                    )
                else:
                    result.agent_results.append(agent_result)
        else:
            # Execute agents sequentially
            trl_result = await self._execute_trl_agent(task)
            result.agent_results.append(trl_result)
            
            market_result = await self._execute_market_agent(task)
            result.agent_results.append(market_result)
            
            ip_result = await self._execute_ip_agent(task)
            result.agent_results.append(ip_result)
            
            technical_result = await self._execute_technical_agent(task)
            result.agent_results.append(technical_result)
        
        # Extract individual results
        for agent_result in result.agent_results:
            if agent_result.success:
                if agent_result.task_type == "trl":
                    result.trl_assessment = agent_result.result
                elif agent_result.task_type == "market":
                    result.market_analysis = agent_result.result
                elif agent_result.task_type == "ip":
                    result.ip_analysis = agent_result.result
                elif agent_result.task_type == "technical":
                    result.technical_analysis = agent_result.result
                
                result.total_tokens_used += agent_result.tokens_used
                result.total_cost_usd += agent_result.cost_usd
        
        # Check if all agents succeeded
        failed_agents = [r for r in result.agent_results if not r.success]
        if failed_agents:
            result.success = len(failed_agents) < len(result.agent_results)  # Partial success
            result.error_message = f"{len(failed_agents)} agent(s) failed: {', '.join([r.task_type for r in failed_agents])}"
        
        result.total_execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def _execute_trl_agent(self, task: AgentTask) -> AgentResult:
        """Execute TRL assessment agent."""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                self.trl_agent.assess_trl_enhanced(
                    document_content=task.document_content,
                    abstract=task.abstract,
                    methodology=task.methodology,
                    claims_outcomes=task.claims_outcomes,
                    patent_data=task.patent_data,
                    market_data=task.market_data,
                ),
                timeout=self.timeout_seconds,
            )
            
            return AgentResult(
                task_type="trl",
                success=True,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
                provider_used=result.provider_used,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
            )
        except asyncio.TimeoutError:
            return AgentResult(
                task_type="trl",
                success=False,
                error_message="TRL assessment timed out",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return AgentResult(
                task_type="trl",
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _execute_market_agent(self, task: AgentTask) -> AgentResult:
        """Execute market analysis agent."""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                self.market_agent.analyze_market_enhanced(
                    document_content=task.document_content,
                    abstract=task.abstract,
                    sector=task.sector,
                    working_field=task.working_field,
                    trl_level=task.trl_level,
                    valuation_data=task.valuation_data,
                ),
                timeout=self.timeout_seconds,
            )
            
            return AgentResult(
                task_type="market",
                success=True,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
                provider_used=result.provider_used,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
            )
        except asyncio.TimeoutError:
            return AgentResult(
                task_type="market",
                success=False,
                error_message="Market analysis timed out",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return AgentResult(
                task_type="market",
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _execute_ip_agent(self, task: AgentTask) -> AgentResult:
        """Execute IP analysis agent."""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                self.ip_agent.analyze_ip_enhanced(
                    document_content=task.document_content,
                    abstract=task.abstract,
                    methodology=task.methodology,
                    patent_data=task.patent_data,
                    trl_level=task.trl_level,
                ),
                timeout=self.timeout_seconds,
            )
            
            return AgentResult(
                task_type="ip",
                success=True,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
                provider_used=result.provider_used,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
            )
        except asyncio.TimeoutError:
            return AgentResult(
                task_type="ip",
                success=False,
                error_message="IP analysis timed out",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return AgentResult(
                task_type="ip",
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _execute_technical_agent(self, task: AgentTask) -> AgentResult:
        """Execute technical analysis agent."""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                self.technical_agent.analyze_technical_enhanced(
                    document_content=task.document_content,
                    abstract=task.abstract,
                    methodology=task.methodology,
                    claims_outcomes=task.claims_outcomes,
                    trl_level=task.trl_level,
                    patent_data=task.patent_data,
                ),
                timeout=self.timeout_seconds,
            )
            
            return AgentResult(
                task_type="technical",
                success=True,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
                provider_used=result.provider_used,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
            )
        except asyncio.TimeoutError:
            return AgentResult(
                task_type="technical",
                success=False,
                error_message="Technical analysis timed out",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return AgentResult(
                task_type="technical",
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def execute_single_agent(
        self,
        task: AgentTask,
        agent_type: str,
    ) -> AgentResult:
        """Execute a single agent by type."""
        if agent_type == "trl":
            return await self._execute_trl_agent(task)
        elif agent_type == "market":
            return await self._execute_market_agent(task)
        elif agent_type == "ip":
            return await self._execute_ip_agent(task)
        elif agent_type == "technical":
            return await self._execute_technical_agent(task)
        else:
            return AgentResult(
                task_type=agent_type,
                success=False,
                error_message=f"Unknown agent type: {agent_type}",
            )
    
    def get_coordinator_stats(self, result: CoordinatorResult) -> dict[str, Any]:
        """Get statistics from coordinator execution."""
        successful_agents = [r for r in result.agent_results if r.success]
        failed_agents = [r for r in result.agent_results if not r.success]
        
        return {
            "total_agents": len(result.agent_results),
            "successful_agents": len(successful_agents),
            "failed_agents": len(failed_agents),
            "success_rate": len(successful_agents) / len(result.agent_results) if result.agent_results else 0,
            "total_execution_time_ms": result.total_execution_time_ms,
            "total_tokens_used": result.total_tokens_used,
            "total_cost_usd": result.total_cost_usd,
            "average_execution_time_ms": (
                sum(r.execution_time_ms for r in result.agent_results) / len(result.agent_results)
                if result.agent_results
                else 0
            ),
            "agent_breakdown": [
                {
                    "task_type": r.task_type,
                    "success": r.success,
                    "execution_time_ms": r.execution_time_ms,
                    "provider_used": r.provider_used,
                    "tokens_used": r.tokens_used,
                    "cost_usd": r.cost_usd,
                }
                for r in result.agent_results
            ],
        }
