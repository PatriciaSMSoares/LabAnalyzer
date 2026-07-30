from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class RamanMeasurement(BaseMeasurement):
    measurement_id = 'raman'
    display_name = 'Raman Spectroscopy'
    requires_mass_file = False
    supported_extensions = ['.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.count import CountRamanAnalysis
        from .analyses.sum_all_together_id_ig import SumAllTogetherIdIgAnalysis
        from .analyses.sum_all_together_norm import SumAllTogetherNormAnalysis
        from .analyses.sum_all_together_id_ig_norm import SumAllTogetherNormIdIgAnalysis
        from .analyses.identify_id_ig_peaks import IdentifyIDIGPeaksAnalysis
        return [CountRamanAnalysis, SumAllTogetherNormAnalysis, SumAllTogetherIdIgAnalysis, SumAllTogetherNormIdIgAnalysis, IdentifyIDIGPeaksAnalysis]
