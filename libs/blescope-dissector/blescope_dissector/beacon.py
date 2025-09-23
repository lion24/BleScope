"""Beacon-specific decoders (iBeacon, Eddystone, AltBeacon)"""
import logging
import struct
import uuid
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from blescope_dissector.base import DecodedAvertisement, AdvertisementDecoder

class BeaconType(Enum):
    IBEACON = "iBeacon"
    EDDYSTONE = "Eddystone"
    ALTBEACON = "AltBeacon"

@dataclass(kw_only=True)
class BeaconAdvertisement(DecodedAvertisement):
    """Base class for beacon advertisements."""
    beacon_type: BeaconType
    tx_power: Optional[int] = None

    def estimate_distance(self, rssi: int, path_loss_exponent: float = 2.0) -> Optional[float]:
        """Estimate distance based on RSSI and Tx Power using the path loss model.

        Args:
            rssi (int): Received Signal Strength Indicator.
            path_loss_exponent (float): Environmental factor, typically between 2 and 4.
        Returns:
            Optional[float]: Estimated distance in meters, or None if tx_power is not set.
        """
        if self.tx_power is None or self.tx_power == 0:
            return None

        # Path loss model: d = 10 ^ ((TxPower - RSSI) / (10 * path_loss_exponent))
        return 10 ** ((self.tx_power - rssi) / (10 * path_loss_exponent))

@dataclass
class IBeaconAdvertisement(BeaconAdvertisement):
    """iBeacon advertisement data."""
    uuid: uuid.UUID
    major: int
    minor: int

    def __post_init__(self):
        self.beacon_type = BeaconType.IBEACON
        self.description = (
            f"iBeacon - UUID: {self.uuid}, "
            f"Major: {self.major}, Minor: {self.minor}, "
            f"Tx Power: {self.tx_power}"
        )

class IBeaconDecoder(AdvertisementDecoder):
    """Decoder for iBeacon advertisements."""

    IBEACON_COMPANY_ID = 0x004C  # Apple Inc.
    IBEACON_TYPE = 0x02
    IBEACON_LENGTH = 0x15

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def can_decode(self, company_id: int, data: bytes) -> bool:
        return (
            company_id == self.IBEACON_COMPANY_ID and
            len(data) >= 23 and
            data[0] == self.IBEACON_TYPE and
            data[1] == self.IBEACON_LENGTH
        )

    def decode(self, data: bytes) -> Optional[IBeaconAdvertisement]:
        if not self.can_decode(self.IBEACON_COMPANY_ID, data):
            return None

        try:
            self.logger.debug(f"Decoding iBeacon data: {data.hex()}")
            uuid_bytes = data[2:18]
            major, minor, tx_power = struct.unpack(">HHb", data[18:23])
            beacon_uuid = uuid.UUID(bytes=uuid_bytes)

            return IBeaconAdvertisement(
                raw_data=data,
                uuid=beacon_uuid,
                major=major,
                minor=minor,
                tx_power=tx_power,
                beacon_type=BeaconType.IBEACON
            )
        except Exception as e:
            self.logger.error(f"Failed to decode iBeacon data: {e}", exc_info=True)
            return None
