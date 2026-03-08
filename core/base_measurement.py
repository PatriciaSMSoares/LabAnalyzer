from abc import ABC, abstractmethod
from typing import ClassVar


class BaseMeasurement(ABC):
    measurement_id: ClassVar[str]
    display_name: ClassVar[str]
    requires_mass_file: ClassVar[bool] = False
    supported_extensions: ClassVar[list] = ['.csv', '.xlsx', '.txt']

    @classmethod
    @abstractmethod
    def get_analyses(cls) -> list: ...

    @classmethod
    def get_layout_options(cls) -> list:
        return ['All in One', 'Grid by Folder', 'Grid by File', 'Side by Side']
