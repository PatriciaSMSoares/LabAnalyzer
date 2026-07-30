from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class ZetaMeasurement(BaseMeasurement):
    measurement_id = 'zeta'
    display_name = 'Zeta Potential'
    requires_mass_file = False
    supported_extensions = ['.csv', '.xlsx', '.txt']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.count_voltage import CountZetaAnalysis
        from .analyses.sum_all_together import SumAllTogetherAnalysis
        from .analyses.sum_all_together_norm import SumAllTogetherNormAnalysis
        return [CountZetaAnalysis, SumAllTogetherAnalysis, SumAllTogetherNormAnalysis]
