import logging

from typing import Dict, List, Optional
from dataclasses import dataclass

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

    # Company ID to manufacturer info mapping
    MANUFACTURERS = {
        0x0006: ManufacturerInfo(0x0006, "Microsoft", "Microsoft Corporation"),
        0x004C: ManufacturerInfo(0x004C, "Apple", "Apple, Inc."),
        0x0075: ManufacturerInfo(0x0075, "Samsung", "Samsung Electronics Co. Ltd."),
        0x00E0: ManufacturerInfo(0x00E0, "Google", "Google LLC"),
        0x0087: ManufacturerInfo(0x0087, "Intel", "Intel Corporation"),
        0x005A: ManufacturerInfo(0x005A, "Nordic Semiconductor", "Nordic Semiconductor ASA"),
        0x0078: ManufacturerInfo(0x0078, "Nike", "Nike, Inc."),
        0x006B: ManufacturerInfo(0x006B, "Polar Electro", "Polar Electro Oy"),
        0x0157: ManufacturerInfo(0x0157, "Xiaomi", "Anhui Huami Information Technology Co., Ltd."),
        0x02D0: ManufacturerInfo(0x02D0, "Estimote", "Estimote, Inc."),
    }

    def __init__(self):
        # Register all available decoders
        self._decoders: List[AdvertisementDecoder] = [
            IBeaconDecoder(),
            # Add other decoders here (EddystoneDecoder, AltBeaconDecoder, etc.)
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

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
                        decoded_adv = decoder.decode(data)
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
