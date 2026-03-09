from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class FuelCellMeasurement(BaseMeasurement):
    measurement_id = 'fuel_cell'
    display_name = 'Fuel Cell'
    requires_mass_file = False
    supported_extensions = ['.fcd', '.mpt', '.csv', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.polarization import PolarizationAnalysis
        from .analyses.power_density import PowerDensityAnalysis
        from .analyses.polarization_power import PolarizationPowerAnalysis
        from .analyses.eis import EISAnalysis
        from .analyses.eis_bode import EISBodeAnalysis
        from .analyses.voltage_time_fc import VoltageTimeFCAnalysis
        from .analyses.humidity_time import HumidityTimeAnalysis
        from .analyses.anode_vs_cathode_rh import AnodeVsCathodeRHAnalysis
        from .analyses.temperature_time import TemperatureTimeAnalysis
        from .analyses.power_time_fc import PowerTimeFCAnalysis
        from .analyses.hfr_time import HFRTimeAnalysis
        from .analyses.current_time_fc import CurrentTimeFCAnalysis
        from .analyses.flow_time import FlowTimeAnalysis
        return [
            PolarizationAnalysis, PowerDensityAnalysis, PolarizationPowerAnalysis,
            EISAnalysis, EISBodeAnalysis,
            VoltageTimeFCAnalysis, HumidityTimeAnalysis, AnodeVsCathodeRHAnalysis,
            TemperatureTimeAnalysis, PowerTimeFCAnalysis, HFRTimeAnalysis,
            CurrentTimeFCAnalysis, FlowTimeAnalysis,
        ]
