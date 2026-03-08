from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Any
import matplotlib.figure


@dataclass
class OptionSpec:
    key: str
    label: str
    widget_type: str  # 'combobox' | 'spinbox' | 'checkbox' | 'lineedit'
    options: list = field(default_factory=list)
    default: Any = None
    min_val: float = 0.0
    max_val: float = 1000.0


class BaseAnalysis(ABC):
    analysis_id: ClassVar[str]
    display_name: ClassVar[str]

    @abstractmethod
    def render(self, datasets: list, config: dict, figure: matplotlib.figure.Figure, ax=None) -> None: ...

    @classmethod
    def get_extra_options(cls) -> list:
        return []
