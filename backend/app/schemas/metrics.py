"""Schemas for the human-only baseline metrics export.

Every metric carries its own definition string so a frozen baseline file stays
interpretable without the code that produced it.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MetricValue(BaseModel):
    key: str
    label: str
    value: Optional[float] = Field(
        None,
        description="None when sample_size is 0 — an empty window has no rate, which is not the same as a rate of zero.",
    )
    unit: str = Field(..., description="ratio | seconds | count")
    sample_size: int = Field(..., description="Denominator the value was computed over.")
    definition: str


class UnavailableMetric(BaseModel):
    """A metric the protocol asks for that system data cannot supply."""

    key: str
    label: str
    reason: str
    how_to_collect: str


class ModeratorWorkload(BaseModel):
    moderator_id: str
    name_or_alias: str
    decisions: int
    median_review_seconds: Optional[float]


class BaselineMetricsOut(BaseModel):
    generated_at: datetime
    window_start: Optional[datetime]
    window_end: Optional[datetime]

    # The baseline is only valid as a *human-only* comparator while these are false.
    phase: str
    ai_enabled: bool
    whatsapp_enabled: bool

    volumes: Dict[str, int]
    metrics: List[MetricValue]
    unavailable_metrics: List[UnavailableMetric]
    moderator_workload: List[ModeratorWorkload]
    interpretation_note: str
