from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class SuperCapsMeasurement(BaseMeasurement):
    measurement_id = 'super_caps'
    display_name = 'Supercapacitors'
    requires_mass_file = True
    supported_extensions = ['.mpt', '.sta', '.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.cv import CVAnalysis
        from .analyses.gcd import GCDAnalysis
        from .analyses.capacitance import CapacitanceAnalysis
        from .analyses.ragone import RagoneAnalysis
        from .analyses.eis_sc import EISSCAnalysis
        from .analyses.rate_capability import RateCapabilityAnalysis
        return [CVAnalysis, GCDAnalysis, CapacitanceAnalysis, RagoneAnalysis, EISSCAnalysis, RateCapabilityAnalysis]
