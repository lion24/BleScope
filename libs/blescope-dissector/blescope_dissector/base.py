"""Base classes and interfaces for advertisement dissectors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum

@dataclass
class ManufacturerInfo:
    """Information about a manufacturer."""
    company_id: int
    company_name: str
    description: Optional[str] = None

@dataclass(kw_only=True)
class DecodedAvertisement:
    """Base class for decoded advertisement data."""
    raw_data: bytes
    description: Optional[str] = ""

class AdvertisementDecoder(ABC):
    """Base interface for advertisement decoders."""

    @abstractmethod
    def can_decode(self, company_id: int, data: bytes) -> bool:
        """Check if this decoder can handle the data"""
        pass

    @abstractmethod
    def decode(self, data: bytes) -> Optional[DecodedAvertisement]:
        """Decode raw advertisement data.

        Args:
            data (bytes): The raw advertisement data.

        Returns:
            Optional[DecodedAvertisement]: The decoded advertisement or None if decoding fails.
        """
        pass
