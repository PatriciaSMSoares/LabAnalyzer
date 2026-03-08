from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class AppConfig:
    recent_dirs: list = field(default_factory=list)
    recent_mass_files: list = field(default_factory=list)
    default_layout: str = 'All in One'
    default_smoothing: str = 'None'
    theme: str = 'light'
    font_size: int = 11
    last_export_dir: str = ''
    window_geometry: dict = field(default_factory=dict)

    CONFIG_PATH = Path.home() / '.labanalyzer' / 'config.json'

    def save(self):
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'recent_dirs': self.recent_dirs,
            'recent_mass_files': self.recent_mass_files,
            'default_layout': self.default_layout,
            'default_smoothing': self.default_smoothing,
            'theme': self.theme,
            'font_size': self.font_size,
            'last_export_dir': self.last_export_dir,
            'window_geometry': self.window_geometry,
        }
        with open(self.CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls) -> 'AppConfig':
        try:
            with open(cls.CONFIG_PATH) as f:
                data = json.load(f)
            return cls(**data)
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return cls()
