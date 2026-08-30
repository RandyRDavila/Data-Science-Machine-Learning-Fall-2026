"""A deterministic battery-risk model with an explicit feature contract."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

RiskBand = Literal["low", "medium", "high"]


class BatteryInput(BaseModel):
    """Validated feature vector accepted by the prediction API.

    Parameters
    ----------
    ambient_temperature_c : float
        Ambient temperature in degrees Celsius.
    charge_rate_c : float
        Charge rate expressed as a multiple of nominal capacity.
    state_of_charge_pct : float
        State of charge on the closed interval from 0 to 100 percent.
    cycle_count : int
        Number of completed charge-discharge cycles.
    internal_resistance_mohm : float
        Estimated internal resistance in milliohms.
    """

    model_config = ConfigDict(extra="forbid")

    ambient_temperature_c: Annotated[float, Field(ge=-40.0, le=85.0)]
    charge_rate_c: Annotated[float, Field(ge=0.1, le=5.0)]
    state_of_charge_pct: Annotated[float, Field(ge=0.0, le=100.0)]
    cycle_count: Annotated[int, Field(ge=0, le=5_000)]
    internal_resistance_mohm: Annotated[float, Field(ge=0.0, le=500.0)]


@dataclass(frozen=True, slots=True)
class Prediction:
    """Framework-independent output from the model."""

    failure_probability: float
    risk_band: RiskBand


class BatteryRiskModel:
    """Small deterministic model used to teach operational behavior.

    The coefficients are pedagogical and do not represent a validated physical
    battery model. Their purpose is to create realistic system behavior without
    requiring a serialized third-party estimator in the introductory lab.
    """

    def __init__(self, version: str) -> None:
        self.version = version

    def predict(
        self, features: BatteryInput, *, temperature_c: float | None = None
    ) -> Prediction:
        """Return a bounded probability and policy-owned risk band.

        Parameters
        ----------
        features : BatteryInput
            Validated request features.
        temperature_c : float, optional
            Explicit transformed temperature. Supplying it makes a simulated
            training-serving transformation defect observable in tests.

        Returns
        -------
        Prediction
            Probability of failure in the teaching horizon and a risk band.
        """

        temperature = (
            features.ambient_temperature_c
            if temperature_c is None
            else temperature_c
        )
        log_odds = (
            -5.2
            + 0.055 * (temperature - 25.0)
            + 0.0012 * features.cycle_count
            + 0.020 * (features.internal_resistance_mohm - 45.0)
            + 0.70 * (features.charge_rate_c - 1.0)
            + 0.012 * max(features.state_of_charge_pct - 85.0, 0.0)
        )
        probability = 1.0 / (1.0 + math.exp(-log_odds))
        if probability >= 0.65:
            band: RiskBand = "high"
        elif probability >= 0.25:
            band = "medium"
        else:
            band = "low"
        return Prediction(failure_probability=probability, risk_band=band)
