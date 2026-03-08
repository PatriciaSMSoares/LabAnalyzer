from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class TGAMeasurement(BaseMeasurement):
    measurement_id = 'tga'
    display_name = 'TGA'
    requires_mass_file = False
    supported_extensions = ['.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.tga_curve import TGACurveAnalysis
        from .analyses.dtg import DTGAnalysis
        from .analyses.dsc import DSCAnalysis
        from .analyses.tga_dsc import TGADSCAnalysis
        return [TGACurveAnalysis, DTGAnalysis, DSCAnalysis, TGADSCAnalysis]
