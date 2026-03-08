from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class PorosimetryMeasurement(BaseMeasurement):
    measurement_id = 'porosimetry'
    display_name = 'Porosimetry'
    requires_mass_file = True
    supported_extensions = ['.csv', '.xlsx', '.dat']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.isotherm import IsothermAnalysis
        from .analyses.bet_analysis import BETAnalysis
        from .analyses.pore_size_dist import PoreSizeDistAnalysis
        from .analyses.isotherm_sbet import IsothermSBETAnalysis
        return [IsothermAnalysis, BETAnalysis, PoreSizeDistAnalysis, IsothermSBETAnalysis]
