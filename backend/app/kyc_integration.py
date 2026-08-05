"""KYC/KYB Integration Service for Enterprise Identity Verification.
Integrates with identity providers like Sumsub, Onfido for regulatory compliance."""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """KYC/KYB verification status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"


class EntityType(Enum):
    """Type of entity for KYB verification."""
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    TRUST = "trust"
    NON_PROFIT = "non_profit"


@dataclass
class KYCResult:
    """Result of KYC verification."""
    applicant_id: str
    status: VerificationStatus
    review_result: Optional[str]
    risk_score: float
    verification_date: str
    expiry_date: Optional[str]
    documents_verified: List[str]


@dataclass
class KYBResult:
    """Result of KYB verification."""
    entity_id: str
    entity_type: EntityType
    status: VerificationStatus
    company_name: str
    registration_number: str
    jurisdiction: str
    beneficial_owners: List[Dict[str, Any]]
    risk_score: float
    verification_date: str


class IdentityProvider:
    """Base class for identity provider integrations."""
    
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize identity provider.
        
        Args:
            api_key: Provider API key
            api_url: Provider API endpoint
        """
        self.api_key = api_key
        self.api_url = api_url
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def submit_kyc_application(
        self,
        applicant_data: Dict[str, Any]
    ) -> str:
        """Submit KYC application."""
        raise NotImplementedError
    
    async def get_kyc_result(self, applicant_id: str) -> KYCResult:
        """Get KYC verification result."""
        raise NotImplementedError
    
    async def submit_kyb_application(
        self,
        entity_data: Dict[str, Any]
    ) -> str:
        """Submit KYB application."""
        raise NotImplementedError
    
    async def get_kyb_result(self, entity_id: str) -> KYBResult:
        """Get KYB verification result."""
        raise NotImplementedError
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()


class SumsubProvider(IdentityProvider):
    """Sumsub identity provider integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sumsub provider.
        
        Args:
            api_key: Sumsub API key (defaults to SUMSUB_API_KEY env var)
        """
        api_key = api_key or os.getenv("SUMSUB_API_KEY")
        api_url = os.getenv("SUMSUB_API_URL", "https://api.sumsub.com")
        super().__init__(api_key, api_url)
    
    async def submit_kyc_application(
        self,
        applicant_data: Dict[str, Any]
    ) -> str:
        """
        Submit KYC application to Sumsub.
        
        Args:
            applicant_data: Applicant information
            
        Returns:
            Applicant ID
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self._client.post(
                f"{self.api_url}/resources/applicants",
                json=applicant_data,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            applicant_id = data.get("id", "")
            
            logger.info(f"Submitted KYC application: {applicant_id}")
            return applicant_id
            
        except Exception as e:
            logger.error(f"Failed to submit KYC application: {e}")
            raise
    
    async def get_kyc_result(self, applicant_id: str) -> KYCResult:
        """
        Get KYC verification result from Sumsub.
        
        Args:
            applicant_id: Applicant ID
            
        Returns:
            KYC verification result
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = await self._client.get(
                f"{self.api_url}/resources/applicants/{applicant_id}/status",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Map Sumsub status to our enum
            review_status = data.get("reviewStatus", "INIT")
            if review_status == "APPROVED":
                status = VerificationStatus.APPROVED
            elif review_status == "REJECTED":
                status = VerificationStatus.REJECTED
            elif review_status == "RETRY":
                status = VerificationStatus.REVIEW_REQUIRED
            else:
                status = VerificationStatus.PENDING
            
            result = KYCResult(
                applicant_id=applicant_id,
                status=status,
                review_result=data.get("reviewResult", ""),
                risk_score=data.get("riskScore", 0.0),
                verification_date=data.get("verificationDate", ""),
                expiry_date=data.get("expiryDate"),
                documents_verified=data.get("documentsVerified", [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get KYC result: {e}")
            raise
    
    async def submit_kyb_application(
        self,
        entity_data: Dict[str, Any]
    ) -> str:
        """
        Submit KYB application to Sumsub.
        
        Args:
            entity_data: Entity information
            
        Returns:
            Entity ID
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self._client.post(
                f"{self.api_url}/resources/applicants",
                json=entity_data,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            entity_id = data.get("id", "")
            
            logger.info(f"Submitted KYB application: {entity_id}")
            return entity_id
            
        except Exception as e:
            logger.error(f"Failed to submit KYB application: {e}")
            raise
    
    async def get_kyb_result(self, entity_id: str) -> KYBResult:
        """
        Get KYB verification result from Sumsub.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            KYB verification result
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = await self._client.get(
                f"{self.api_url}/resources/applicants/{entity_id}/status",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Map Sumsub status to our enum
            review_status = data.get("reviewStatus", "INIT")
            if review_status == "APPROVED":
                status = VerificationStatus.APPROVED
            elif review_status == "REJECTED":
                status = VerificationStatus.REJECTED
            elif review_status == "RETRY":
                status = VerificationStatus.REVIEW_REQUIRED
            else:
                status = VerificationStatus.PENDING
            
            # Extract entity type
            entity_type_str = data.get("entityType", "INDIVIDUAL")
            entity_type = EntityType.INDIVIDUAL
            if entity_type_str == "CORPORATION":
                entity_type = EntityType.CORPORATION
            elif entity_type_str == "PARTNERSHIP":
                entity_type = EntityType.PARTNERSHIP
            
            result = KYBResult(
                entity_id=entity_id,
                entity_type=entity_type,
                status=status,
                company_name=data.get("companyName", ""),
                registration_number=data.get("registrationNumber", ""),
                jurisdiction=data.get("jurisdiction", ""),
                beneficial_owners=data.get("beneficialOwners", []),
                risk_score=data.get("riskScore", 0.0),
                verification_date=data.get("verificationDate", "")
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get KYB result: {e}")
            raise


class OnfidoProvider(IdentityProvider):
    """Onfido identity provider integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Onfido provider.
        
        Args:
            api_key: Onfido API key (defaults to ONFIDO_API_KEY env var)
        """
        api_key = api_key or os.getenv("ONFIDO_API_KEY")
        api_url = os.getenv("ONFIDO_API_URL", "https://api.onfido.com")
        super().__init__(api_key, api_url)
    
    async def submit_kyc_application(
        self,
        applicant_data: Dict[str, Any]
    ) -> str:
        """Submit KYC application to Onfido."""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self._client.post(
                f"{self.api_url}/v3/applicants",
                json=applicant_data,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            applicant_id = data.get("id", "")
            
            logger.info(f"Submitted KYC application: {applicant_id}")
            return applicant_id
            
        except Exception as e:
            logger.error(f"Failed to submit KYC application: {e}")
            raise
    
    async def get_kyc_result(self, applicant_id: str) -> KYCResult:
        """Get KYC verification result from Onfido."""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}"
            }
            
            response = await self._client.get(
                f"{self.api_url}/v3/applicants/{applicant_id}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Map Onfido status to our enum
            onfido_status = data.get("status", "in_progress")
            if onfido_status == "completed":
                status = VerificationStatus.APPROVED
            elif onfido_status == "withdrawn":
                status = VerificationStatus.REJECTED
            else:
                status = VerificationStatus.PENDING
            
            result = KYCResult(
                applicant_id=applicant_id,
                status=status,
                review_result=data.get("result", ""),
                risk_score=data.get("riskScore", 0.0),
                verification_date=data.get("createdAt", ""),
                expiry_date=None,
                documents_verified=data.get("documents", [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get KYC result: {e}")
            raise
    
    async def submit_kyb_application(
        self,
        entity_data: Dict[str, Any]
    ) -> str:
        """Submit KYB application to Onfido."""
        # Onfido primarily focuses on KYC, KYB would require custom implementation
        logger.warning("Onfido KYB not fully implemented, using KYC as fallback")
        return await self.submit_kyc_application(entity_data)
    
    async def get_kyb_result(self, entity_id: str) -> KYBResult:
        """Get KYB verification result from Onfido."""
        # Fallback to KYC result
        kyc_result = await self.get_kyc_result(entity_id)
        
        return KYBResult(
            entity_id=entity_id,
            entity_type=EntityType.CORPORATION,
            status=kyc_result.status,
            company_name="",
            registration_number="",
            jurisdiction="",
            beneficial_owners=[],
            risk_score=kyc_result.risk_score,
            verification_date=kyc_result.verification_date
        )


class KYCService:
    """Service for managing KYC/KYB verifications."""
    
    def __init__(self, provider: str = "sumsub"):
        """
        Initialize KYC service.
        
        Args:
            provider: Identity provider ("sumsub" or "onfido")
        """
        self.provider = provider.lower()
        self._provider_client: Optional[IdentityProvider] = None
    
    def _get_provider(self) -> IdentityProvider:
        """Get or create provider client."""
        if self._provider_client is None:
            if self.provider == "sumsub":
                self._provider_client = SumsubProvider()
            elif self.provider == "onfido":
                self._provider_client = OnfidoProvider()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        return self._provider_client
    
    async def verify_individual(
        self,
        wallet_address: str,
        personal_data: Dict[str, Any],
        document_data: Optional[Dict[str, Any]] = None
    ) -> KYCResult:
        """
        Verify individual (KYC).
        
        Args:
            wallet_address: User's wallet address
            personal_data: Personal information
            document_data: Document information (optional)
            
        Returns:
            KYC verification result
        """
        provider = self._get_provider()
        
        applicant_data = {
            "externalUserId": wallet_address,
            "email": personal_data.get("email", ""),
            "phone": personal_data.get("phone", ""),
            "firstName": personal_data.get("firstName", ""),
            "lastName": personal_data.get("lastName", ""),
            "country": personal_data.get("country", ""),
            "dateOfBirth": personal_data.get("dateOfBirth", "")
        }
        
        if document_data:
            applicant_data["documents"] = [document_data]
        
        applicant_id = await provider.submit_kyc_application(applicant_data)
        result = await provider.get_kyc_result(applicant_id)
        
        return result
    
    async def verify_entity(
        self,
        wallet_address: str,
        entity_data: Dict[str, Any],
        beneficial_owners: Optional[List[Dict[str, Any]]] = None
    ) -> KYBResult:
        """
        Verify entity (KYB).
        
        Args:
            wallet_address: Entity's wallet address
            entity_data: Entity information
            beneficial_owners: List of beneficial owners
            
        Returns:
            KYB verification result
        """
        provider = self._get_provider()
        
        entity_submission = {
            "externalUserId": wallet_address,
            "entityType": entity_data.get("entityType", "CORPORATION"),
            "companyName": entity_data.get("companyName", ""),
            "registrationNumber": entity_data.get("registrationNumber", ""),
            "jurisdiction": entity_data.get("jurisdiction", ""),
            "address": entity_data.get("address", {})
        }
        
        if beneficial_owners:
            entity_submission["beneficialOwners"] = beneficial_owners
        
        entity_id = await provider.submit_kyb_application(entity_submission)
        result = await provider.get_kyb_result(entity_id)
        
        return result
    
    async def check_verification_status(
        self,
        verification_id: str,
        verification_type: str = "kyc"
    ) -> Optional[Dict[str, Any]]:
        """
        Check verification status.
        
        Args:
            verification_id: Verification ID
            verification_type: Type of verification ("kyc" or "kyb")
            
        Returns:
            Verification status
        """
        provider = self._get_provider()
        
        try:
            if verification_type == "kyc":
                result = await provider.get_kyc_result(verification_id)
                return {
                    "status": result.status.value,
                    "risk_score": result.risk_score,
                    "verification_date": result.verification_date
                }
            else:
                result = await provider.get_kyb_result(verification_id)
                return {
                    "status": result.status.value,
                    "risk_score": result.risk_score,
                    "verification_date": result.verification_date
                }
        except Exception as e:
            logger.error(f"Failed to check verification status: {e}")
            return None
    
    async def close(self):
        """Close provider client."""
        if self._provider_client:
            await self._provider_client.close()


# Global service instance
_kyc_service: Optional[KYCService] = None


def get_kyc_service(provider: str = "sumsub") -> KYCService:
    """
    Get or create global KYC service instance.
    
    Args:
        provider: Identity provider
        
    Returns:
        KYC service instance
    """
    global _kyc_service
    if _kyc_service is None:
        _kyc_service = KYCService(provider=provider)
    return _kyc_service
