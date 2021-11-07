from typing import Dict, List

import numpy as np

from stl_rules.stl_rule import STLRule


class ComfortLongitudinalJerk(STLRule):
    """
    This rule implement a Comfort requirement on Longitudinal Jerk.

    It is based on formalization reported in 5.2.22 of [3: Westhofen et al., 2021].
    """

    @property
    def variables(self):
        return ["time", "j_lon"]

    @property
    def types(self):
        return ["int", "float"]

    def __init__(self, rss_params):
        """
        :param rss_params: static parameters for rss monitoring
            `j_lon_max`: max comfortable longitudinal jerk
            `sim_dt`: integration time in simulation, used to compute acceleration derivative
        """
        required_parameters = ["j_lon_max", "sim_dt"]
        assert all([p in rss_params for p in required_parameters])
        self._p = {p: rss_params[p] for p in required_parameters}

    @property
    def spec(self):
        # specification
        J_bounded = f"(abs(j_lon) <= {self._p['j_lon_max']})"
        return J_bounded

    @property
    def demo_spec(self):
        return self.spec

    def generate_signals_for_demo(self, data: Dict[str, np.ndarray], begin: int = 5, end: int = 1000) -> Dict[str, list]:
        # check input
        obs_signals = ["elapsed_time", "j_lon"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {
            "elapsed_time": data["elapsed_time"],
            "time": np.floor((data["elapsed_time"] - data["elapsed_time"][0]) / self._p["sim_dt"]).astype(int),
            "j_lon": data["j_lon"]
        }
        out_signals = {k: list(v[begin:end]) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals

    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, List]:
        # check input
        obs_signals = ["a_lon"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {
            "time": data["time"],
            "j_lon": np.gradient(data['a_lon'], self._p['sim_dt'])
        }
        out_signals = {k: list(v) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals


class ComfortLateralJerk(STLRule):
    """
    This rule implement a Comfort requirement on Lateral Jerk.

    It is based on formalization reported in 5.2.22 of [3: Westhofen et al., 2021].
    """

    @property
    def variables(self):
        return ["time", "j_lat"]

    @property
    def types(self):
        return ["int", "float"]

    def __init__(self, rss_params):
        """
        :param rss_params: static parameters for rss monitoring
            `j_lat_max`: max comfortable lateral jerk
            `sim_dt`: integration time in simulation, used to compute acceleration derivative
        """
        required_parameters = ["j_lat_max", "sim_dt"]
        assert all([p in rss_params for p in required_parameters])
        self._p = {p: rss_params[p] for p in required_parameters}

    @property
    def spec(self):
        # specification
        J_bounded = f"(abs(j_lat) <= {self._p['j_lat_max']})"
        return J_bounded

    @property
    def demo_spec(self):
        return self.spec

    def generate_signals_for_demo(self, data: Dict[str, np.ndarray], begin: int = 5, end: int = 1000) -> Dict[
        str, List]:
        # check input
        obs_signals = ["elapsed_time", "j_lat"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {
            "elapsed_time": data["elapsed_time"] - data["elapsed_time"][0],
            "time": np.floor((data["elapsed_time"] - data["elapsed_time"][0]) / self._p["sim_dt"]).astype(int),
            "j_lat": data["j_lat"]
        }
        out_signals = {k: list(v[begin:end]) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals

    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, List]:
        # check input
        obs_signals = ["a_lat"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {
            "time": data["time"],
            "j_lat": np.gradient(data['a_lat'], self._p['sim_dt'])
        }
        out_signals = {k: list(v) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals
