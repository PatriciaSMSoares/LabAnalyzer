from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class CurrentMeasurement(BaseMeasurement):
    measurement_id = 'current'
    display_name = 'Current'
    requires_mass_file = False
    supported_extensions = ['.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.current_time import CurrentTimeAnalysis
        from .analyses.current_density import CurrentDensityAnalysis
        from .analyses.charge_discharge import ChargeDischargeAnalysis
        return [CurrentTimeAnalysis, CurrentDensityAnalysis, ChargeDischargeAnalysis]
