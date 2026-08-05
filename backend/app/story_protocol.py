"""Story Protocol Integration for Programmable IP Licensing.
Implements IP Asset (IPA) creation, Programmable IP Licenses (PIL), and royalty management."""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Types of programmable IP licenses."""
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    RESEARCH_ONLY = "research_only"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"


class RoyaltyType(Enum):
    """Types of royalty structures."""
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"


@dataclass
class IPAsset:
    """Represents an IP Asset on Story Protocol."""
    ip_id: str
    owner: str
    metadata_uri: str
    license_terms: Dict[str, Any]
    royalty_config: Dict[str, Any]
    created_at: str
    is_registered: bool


@dataclass
class ProgrammableLicense:
    """Represents a Programmable IP License (PIL)."""
    license_id: str
    ip_id: str
    licensor: str
    licensee: str
    license_type: LicenseType
    terms: Dict[str, Any]
    royalty_config: Dict[str, Any]
    start_date: str
    end_date: Optional[str]
    is_active: bool


@dataclass
class RoyaltyDistribution:
    """Represents a royalty distribution event."""
    distribution_id: str
    ip_id: str
    license_id: str
    total_amount: float
    currency: str
    recipients: List[Dict[str, Any]]
    timestamp: str
    transaction_hash: str


class StoryProtocolClient:
    """Client for interacting with Story Protocol Layer-1."""
    
    def __init__(self, rpc_url: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize Story Protocol client.
        
        Args:
            rpc_url: Story Protocol RPC endpoint
            private_key: Private key for signing transactions
        """
        self.rpc_url = rpc_url or os.getenv("STORY_PROTOCOL_RPC", "https://story-rpc.com")
        self.private_key = private_key or os.getenv("STORY_PROTOCOL_PRIVATE_KEY")
        self._web3 = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize Web3 connection and Story Protocol contracts."""
        if self._initialized:
            return
        
        try:
            from web3 import Web3
            self._web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self._web3.is_connected():
                raise ConnectionError("Failed to connect to Story Protocol RPC")
            
            logger.info("Connected to Story Protocol RPC")
            self._initialized = True
            
        except ImportError:
            logger.error("web3 not installed. Install with: pip install web3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Story Protocol client: {e}")
            raise
    
    async def register_ip_asset(
        self,
        owner: str,
        metadata_uri: str,
        license_terms: Dict[str, Any],
        royalty_config: Optional[Dict[str, Any]] = None
    ) -> IPAsset:
        """
        Register a new IP Asset on Story Protocol.
        
        Args:
            owner: Owner wallet address
            metadata_uri: IPFS URI containing IP metadata
            license_terms: License terms and conditions
            royalty_config: Royalty distribution configuration
            
        Returns:
            Registered IP Asset
        """
        self._initialize()
        
        try:
            # Generate IP ID (in production, this would come from the contract)
            ip_id = f"ip_{hash(metadata_uri) % (10**12)}"
            
            # Default royalty config
            if royalty_config is None:
                royalty_config = {
                    "royalty_type": RoyaltyType.PERCENTAGE.value,
                    "royalty_rate": 0.05,  # 5%
                    "recipients": [
                        {"address": owner, "share": 1.0}
                    ]
                }
            
            ip_asset = IPAsset(
                ip_id=ip_id,
                owner=owner,
                metadata_uri=metadata_uri,
                license_terms=license_terms,
                royalty_config=royalty_config,
                created_at=self._get_current_timestamp(),
                is_registered=True
            )
            
            logger.info(f"Registered IP Asset: {ip_id}")
            return ip_asset
            
        except Exception as e:
            logger.error(f"Failed to register IP Asset: {e}")
            raise
    
    async def create_programmable_license(
        self,
        ip_id: str,
        licensor: str,
        licensee: str,
        license_type: LicenseType,
        terms: Dict[str, Any],
        royalty_config: Optional[Dict[str, Any]] = None,
        duration_days: Optional[int] = None
    ) -> ProgrammableLicense:
        """
        Create a Programmable IP License (PIL).
        
        Args:
            ip_id: IP Asset ID
            licensor: Licensor wallet address
            licensee: Licensee wallet address
            license_type: Type of license
            terms: License terms and conditions
            royalty_config: Royalty configuration for this license
            duration_days: License duration in days (None = perpetual)
            
        Returns:
            Created Programmable License
        """
        self._initialize()
        
        try:
            from datetime import datetime, timedelta
            
            license_id = f"pil_{hash(ip_id + licensor + licensee) % (10**12)}"
            start_date = self._get_current_timestamp()
            end_date = None
            
            if duration_days:
                end_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
            
            programmable_license = ProgrammableLicense(
                license_id=license_id,
                ip_id=ip_id,
                licensor=licensor,
                licensee=licensee,
                license_type=license_type,
                terms=terms,
                royalty_config=royalty_config or {},
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            
            logger.info(f"Created Programmable License: {license_id}")
            return programmable_license
            
        except Exception as e:
            logger.error(f"Failed to create Programmable License: {e}")
            raise
    
    async def distribute_royalties(
        self,
        ip_id: str,
        license_id: str,
        amount: float,
        currency: str = "USD"
    ) -> RoyaltyDistribution:
        """
        Distribute royalties according to IP Asset configuration.
        
        Args:
            ip_id: IP Asset ID
            license_id: License ID generating royalties
            amount: Total royalty amount
            currency: Currency of the amount
            
        Returns:
            Royalty distribution record
        """
        self._initialize()
        
        try:
            # In production, this would query the IP Asset's royalty config
            # For now, we'll use a simple distribution
            distribution_id = f"royalty_{hash(ip_id + license_id) % (10**12)}"
            
            # Simple equal distribution (in production, use actual config)
            recipients = [
                {"address": "0xOwner", "share": 0.7, "amount": amount * 0.7},
                {"address": "0xPlatform", "share": 0.3, "amount": amount * 0.3}
            ]
            
            distribution = RoyaltyDistribution(
                distribution_id=distribution_id,
                ip_id=ip_id,
                license_id=license_id,
                total_amount=amount,
                currency=currency,
                recipients=recipients,
                timestamp=self._get_current_timestamp(),
                transaction_hash="0x" + "0" * 64  # Placeholder
            )
            
            logger.info(f"Distributed royalties: {distribution_id}")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to distribute royalties: {e}")
            raise
    
    async def group_ip_assets(
        self,
        ip_ids: List[str],
        group_name: str,
        shared_royalty_config: Dict[str, Any]
    ) -> str:
        """
        Group multiple IP Assets under shared terms.
        
        Args:
            ip_ids: List of IP Asset IDs to group
            group_name: Name for the IP group
            shared_royalty_config: Shared royalty configuration
            
        Returns:
            Group ID
        """
        self._initialize()
        
        try:
            group_id = f"group_{hash(group_name) % (10**12)}"
            
            logger.info(f"Created IP Group: {group_id} with {len(ip_ids)} assets")
            return group_id
            
        except Exception as e:
            logger.error(f"Failed to group IP Assets: {e}")
            raise
    
    async def file_dispute(
        self,
        ip_id: str,
        dispute_reason: str,
        evidence_uri: str,
        challenger: str
    ) -> str:
        """
        File a dispute against an IP Asset.
        
        Args:
            ip_id: IP Asset ID to dispute
            dispute_reason: Reason for the dispute
            evidence_uri: IPFS URI containing evidence
            challenger: Challenger wallet address
            
        Returns:
            Dispute ID
        """
        self._initialize()
        
        try:
            dispute_id = f"dispute_{hash(ip_id + dispute_reason) % (10**12)}"
            
            logger.info(f"Filed dispute: {dispute_id} against IP {ip_id}")
            return dispute_id
            
        except Exception as e:
            logger.error(f"Failed to file dispute: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


class StoryProtocolService:
    """Service for Story Protocol operations in MatDAO."""
    
    def __init__(self):
        self._client: Optional[StoryProtocolClient] = None
    
    def get_client(self) -> StoryProtocolClient:
        """Get or create Story Protocol client."""
        if self._client is None:
            self._client = StoryProtocolClient()
        return self._client
    
    async def create_research_ip_asset(
        self,
        researcher_address: str,
        metadata: Dict[str, Any],
        license_type: LicenseType = LicenseType.NON_COMMERCIAL
    ) -> IPAsset:
        """
        Create an IP Asset for research output.
        
        Args:
            researcher_address: Researcher's wallet address
            metadata: Research metadata (title, abstract, etc.)
            license_type: Type of license to apply
            
        Returns:
            Created IP Asset
        """
        client = self.get_client()
        
        # Prepare license terms
        license_terms = {
            "license_type": license_type.value,
            "attribution_required": True,
            "commercial_use": license_type == LicenseType.COMMERCIAL,
            "modification_allowed": True,
            "share_alike": license_type != LicenseType.EXCLUSIVE
        }
        
        # Prepare royalty config
        royalty_config = {
            "royalty_type": RoyaltyType.PERCENTAGE.value,
            "royalty_rate": 0.05,
            "recipients": [
                {"address": researcher_address, "share": 0.8},
                {"address": "0xMatDAO", "share": 0.2}
            ]
        }
        
        # In production, upload metadata to IPFS
        metadata_uri = f"ipfs://metadata_{hash(str(metadata)) % (10**12)}"
        
        return await client.register_ip_asset(
            owner=researcher_address,
            metadata_uri=metadata_uri,
            license_terms=license_terms,
            royalty_config=royalty_config
        )
    
    async def create_commercial_license(
        self,
        ip_id: str,
        company_address: str,
        terms: Dict[str, Any]
    ) -> ProgrammableLicense:
        """
        Create a commercial license for an IP Asset.
        
        Args:
            ip_id: IP Asset ID
            company_address: Company wallet address
            terms: Commercial license terms
            
        Returns:
            Created commercial license
        """
        client = self.get_client()
        
        # Get IP owner (in production, query contract)
        ip_owner = "0xResearcher"
        
        # Commercial royalty config
        royalty_config = {
            "royalty_type": RoyaltyType.TIERED.value,
            "tiers": [
                {"threshold": 0, "rate": 0.05},
                {"threshold": 1000000, "rate": 0.03},
                {"threshold": 10000000, "rate": 0.01}
            ],
            "recipients": [
                {"address": ip_owner, "share": 0.7},
                {"address": "0xMatDAO", "share": 0.3}
            ]
        }
        
        return await client.create_programmable_license(
            ip_id=ip_id,
            licensor=ip_owner,
            licensee=company_address,
            license_type=LicenseType.COMMERCIAL,
            terms=terms,
            royalty_config=royalty_config,
            duration_days=365 * 5  # 5 years
        )


# Global service instance
_story_protocol_service: Optional[StoryProtocolService] = None


def get_story_protocol_service() -> StoryProtocolService:
    """Get or create global Story Protocol service instance."""
    global _story_protocol_service
    if _story_protocol_service is None:
        _story_protocol_service = StoryProtocolService()
    return _story_protocol_service
