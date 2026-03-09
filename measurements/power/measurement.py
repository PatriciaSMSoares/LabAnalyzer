from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class PowerMeasurement(BaseMeasurement):
    measurement_id = 'power'
    display_name = 'Power'
    requires_mass_file = False
    supported_extensions = ['.fcd', '.mpt', '.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.power_time import PowerTimeAnalysis
        from .analyses.current_time import CurrentTimeAnalysis
        from .analyses.energy import EnergyAnalysis
        from .analyses.efficiency import EfficiencyAnalysis
        from .analyses.voltage_time_pw import VoltageTimePWAnalysis
        from .analyses.max_power_time import MaxPowerTimeAnalysis
        from .analyses.internal_resistance_time import InternalResistanceTimeAnalysis
        from .analyses.max_power_vs_resistance import MaxPowerVsResistanceAnalysis
        from .analyses.power_vs_resistance import PowerVsResistanceAnalysis
        return [
            PowerTimeAnalysis, CurrentTimeAnalysis, EnergyAnalysis, EfficiencyAnalysis,
            VoltageTimePWAnalysis, MaxPowerTimeAnalysis, InternalResistanceTimeAnalysis,
            MaxPowerVsResistanceAnalysis, PowerVsResistanceAnalysis,
        ]
