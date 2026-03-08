from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class VoltageMeasurement(BaseMeasurement):
    measurement_id = 'voltage'
    display_name = 'Voltage'
    requires_mass_file = False
    supported_extensions = ['.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.voltage_time import VoltageTimeAnalysis
        from .analyses.voltage_current import VoltageCurrentAnalysis
        from .analyses.voltage_stats import VoltageStatsAnalysis
        from .analyses.dv_dt import DvDtAnalysis
        return [VoltageTimeAnalysis, VoltageCurrentAnalysis, VoltageStatsAnalysis, DvDtAnalysis]
