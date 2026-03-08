from labanalyzer.core.registry import MeasurementRegistry
from labanalyzer.core.base_measurement import BaseMeasurement


@MeasurementRegistry.register
class SEMMeasurement(BaseMeasurement):
    measurement_id = 'sem'
    display_name = 'SEM'
    requires_mass_file = False
    supported_extensions = ['.tif', '.tiff', '.png', '.jpg', '.jpeg', '.csv']

    @classmethod
    def get_analyses(cls) -> list:
        from .analyses.image_gallery import ImageGalleryAnalysis
        from .analyses.particle_size import ParticleSizeAnalysis
        from .analyses.roughness import RoughnessAnalysis
        return [ImageGalleryAnalysis, ParticleSizeAnalysis, RoughnessAnalysis]
