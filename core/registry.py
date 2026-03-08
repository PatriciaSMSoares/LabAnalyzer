from __future__ import annotations
from typing import Dict, Type
from .base_measurement import BaseMeasurement


class MeasurementRegistry:
    _instance: MeasurementRegistry | None = None
    _registry: Dict[str, Type[BaseMeasurement]] = {}

    @classmethod
    def instance(cls) -> MeasurementRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def register(cls, measurement_cls: Type[BaseMeasurement]) -> Type[BaseMeasurement]:
        cls._registry[measurement_cls.measurement_id] = measurement_cls
        return measurement_cls

    @classmethod
    def get(cls, measurement_id: str) -> Type[BaseMeasurement]:
        return cls._registry[measurement_id]

    @classmethod
    def all_ids(cls) -> list:
        return list(cls._registry.keys())

    @classmethod
    def all_measurements(cls) -> list:
        return list(cls._registry.values())
