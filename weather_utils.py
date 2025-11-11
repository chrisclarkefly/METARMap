from dataclasses import dataclass, field
from typing import List, Dict, Any
import datetime

@dataclass
class Condition:
	flightCategory: str = ""
	windDir: str = ""
	windSpeed: int = 0
	windGustSpeed: int = 0
	windGust: bool = False
	lightning: bool = False
	tempC: int = 0
	dewpointC: int = 0
	vis: int = 0
	altimHg: float = 0.0
	obs: str = ""
	skyConditions: List[Dict[str, Any]] = field(default_factory=list)
	obsTime: datetime.datetime = field(default_factory=datetime.datetime.now)

	# allow dict-like access (so existing code using conditions["flightCategory"] keeps working)
	def __getitem__(self, key):
		return getattr(self, key)

	def to_dict(self) -> Dict[str, Any]:
		return {
			"flightCategory": self.flightCategory,
			"windDir": self.windDir,
			"windSpeed": self.windSpeed,
			"windGustSpeed": self.windGustSpeed,
			"windGust": self.windGust,
			"lightning": self.lightning,
			"tempC": self.tempC,
			"dewpointC": self.dewpointC,
			"vis": self.vis,
			"altimHg": self.altimHg,
			"obs": self.obs,
			"skyConditions": self.skyConditions,
			"obsTime": self.obsTime,
		}