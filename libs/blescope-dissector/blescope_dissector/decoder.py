import logging
import yaml

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from blescope_dissector.base import ManufacturerInfo, AdvertisementDecoder, DecodedAvertisement
from blescope_dissector.beacon import IBeaconDecoder

@dataclass
class DecodedManufacturerData:
    """Complete decoded manufacturer data."""
    company: ManufacturerInfo
    advertisement: Optional[DecodedAvertisement] = None
    raw_data: Optional[bytes] = None

class ManufacturerDataDecoder:
    """Main decoder that use specific decoders for different advertisement types."""

    def __init__(self, yaml_file: Optional[str] = None):
        if yaml_file is None:
            yaml_file = Path(__file__).parent / "company_identifiers.yaml"

        self.MANUFACTURERS = self._load_manufacturers(yaml_file)

        # Register all available decoders
        self._decoders: List[AdvertisementDecoder] = [
            IBeaconDecoder(),
            # Add other decoders here (EddystoneDecoder, AltBeaconDecoder, etc.)
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _load_manufacturers(self, yaml_path: Path) -> Dict[int, ManufacturerInfo]:
        """Load manufacturer info from a YAML file."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        manufacturers = {}
        for entry in data.get("company_identifiers", []):
            company_id = entry.get("value")
            name = entry.get("name")
            if company_id is not None and name:
                manufacturers[company_id] = ManufacturerInfo(company_id, name)
        
        return manufacturers

    def get_manufacturer_name(self, company_id: int) -> str:
        """Get manufacturer name by company ID."""
        return self.MANUFACTURERS.get(company_id, ManufacturerInfo(company_id, f"Unknown (0x{company_id:04X})", None)).company_name

    def decode(self, manufacturer_data: Dict[int, bytes]) -> List[DecodedManufacturerData]:
        """
        Decode manufacturer data from BLE advertisement
        
        Args:
            manufacturer_data: Dictionary mapping company ID to raw data bytes
            
        Returns:
            List of decoded manufacturer data
        """
        results = []

        for company_id, data in manufacturer_data.items():
            # Get company info
            company_info = self.MANUFACTURERS.get(company_id, ManufacturerInfo(company_id, f"Unknown (0x{company_id:04X})", None))

            # Try to decode with specific decoders
            decoded_adv = None
            for decoder in self._decoders:
                if decoder.can_decode(company_id, data):
                    try:
                        decoded_adv = decoder.decode(company_id, data)
                    except Exception as e:
                        # Log error and continue
                        self.logger.error(f"Error decoding with {decoder.__class__.__name__}: {e}")
                    break  # Stop after first successful decoder
            
            result = DecodedManufacturerData(
                company=company_info,
                advertisement=decoded_adv,
                raw_data=data
            )

            if not decoded_adv:
                generic_adv = DecodedAvertisement(
                    raw_data=data,
                    description=f"{company_info.company_name} - Raw: {data.hex()}"
                )
                result.advertisement = generic_adv
            
            results.append(result)

        return results

    def register_decoder(self, decoder: AdvertisementDecoder):
        """Register a new advertisement decoder."""
        self._decoders.append(decoder)
