"""Beacon-specific decoders (ibeacon, Eddystone, AltBeacon)"""
import logging
import struct
import uuid
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from blescope_dissector.base import DecodedAvertisement, AdvertisementDecoder

class BeaconType(Enum):
    IBEACON = "ibeacon"
    EDDYSTONE = "Eddystone"
    ALTBEACON = "AltBeacon"

@dataclass(kw_only=True)
class BeaconAdvertisement(DecodedAvertisement):
    """Base class for beacon advertisements.

    Notes
    -----
    - measured_power_dbm is the calibrated RSSI at 1 meter (a signed value, typically around -59 dBm).
    - tx_power is kept as a backward-compatible alias for measured_power_dbm because older code
      sometimes misused the name. If only one is provided, values are mirrored during __post_init__.
    - This "measured power" is NOT the BLE AD Type 0x0A Tx Power Level (which can be positive and
      represents transmitter output power in dBm). Do not use AD 0x0A value for distance estimates.
    """
    beacon_type: BeaconType
    # New, explicit field name for the iBeacon/Eddystone calibrated RSSI at 1m
    measured_power_dbm: Optional[int] = None
    # Deprecated alias retained for compatibility with existing call sites
    tx_power: Optional[int] = None

    def __post_init__(self):
        # Backward-compatibility and value unification between measured_power_dbm and tx_power
        if self.measured_power_dbm is None and self.tx_power is not None:
            self.measured_power_dbm = self.tx_power
        elif self.measured_power_dbm is not None and self.tx_power is None:
            self.tx_power = self.measured_power_dbm
        elif self.measured_power_dbm is not None and self.tx_power is not None:
            # If both are set but disagree, prefer the explicit measured_power_dbm
            if self.measured_power_dbm != self.tx_power:
                try:
                    logging.getLogger(__name__).warning(
                        "Both measured_power_dbm (%s) and tx_power (%s) provided; "
                        "preferring measured_power_dbm.",
                        self.measured_power_dbm, self.tx_power,
                    )
                except Exception:
                    pass
                # Keep tx_power mirrored to avoid confusion downstream
                self.tx_power = self.measured_power_dbm

    def estimate_distance(self, rssi_dbm: float, path_loss_exponent: float = 2.0) -> Optional[float]:
        """Estimate distance from RSSI using the log-distance path loss model.

        Args:
            rssi_dbm (float): RSSI in dBm (typically negative).
            path_loss_exponent (float): Environmental factor n, usually 1.6–3.5 indoors.

        Returns:
            Optional[float]: Estimated distance in meters, or None if inputs are invalid.
        """
        # measured_power_dbm is expected to be the calibrated RSSI at 1m (negative dBm value)
        A = self.measured_power_dbm
        if A is None or path_loss_exponent <= 0:
            return None
        # Sanity: measured power should be in a plausible range for RSSI at 1m
        if not (-100 <= A <= -10):
            return None
        if rssi_dbm is None or rssi_dbm >= 0:
            return None  # 0 or positive dBm RSSI is likely invalid here

        # d = 10 ^ ((A - RSSI) / (10 * n))
        return float(pow(10.0, (A - rssi_dbm) / (10.0 * path_loss_exponent)))

@dataclass
class IBeaconAdvertisement(BeaconAdvertisement):
    """ibeacon advertisement data."""
    uuid: uuid.UUID
    major: int
    minor: int

    def __post_init__(self):
        # Ensure base unification of measured_power_dbm/tx_power
        super().__post_init__()
        self.beacon_type = BeaconType.IBEACON
        self.description = (
            f"ibeacon - UUID: {self.uuid}, "
            f"Major: {self.major}, Minor: {self.minor}, "
            f"Measured Power: {self.measured_power_dbm} dBm"
        )

class IBeaconDecoder(AdvertisementDecoder):
    """Decoder for ibeacon advertisements."""

    IBEACON_COMPANY_ID = 0x004C  # Apple Inc.
    IBEACON_TYPE = 0x02 # ibeacon type (proximity beacon)
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

    def decode(self, company_id: int, data: bytes) -> Optional[IBeaconAdvertisement]:
        if not self.can_decode(company_id, data):
            return None

        try:
            self.logger.debug(f"Decoding ibeacon data: {data.hex()}")
            uuid_bytes = data[2:18]
            major, minor, tx_power = struct.unpack(">HHb", data[18:23])
            beacon_uuid = uuid.UUID(bytes=uuid_bytes)

            # The last byte is the calibrated RSSI at 1m (Measured Power, signed)
            return IBeaconAdvertisement(
                raw_data=data,
                uuid=beacon_uuid,
                major=major,
                minor=minor,
                measured_power_dbm=tx_power,
                tx_power=tx_power,  # keep alias populated for backward-compat
                beacon_type=BeaconType.IBEACON,
            )
        except Exception as e:
            self.logger.error(f"Failed to decode ibeacon data: {e}", exc_info=True)
            return None
