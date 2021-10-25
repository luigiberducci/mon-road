from abc import ABC, abstractmethod
from typing import Dict
import numpy as np


class STLRule(ABC):
    @property
    @abstractmethod
    def spec(self):
        pass

    @property
    @abstractmethod
    def variables(self):
        pass

    @property
    @abstractmethod
    def types(self):
        pass

    @abstractmethod
    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        pass
