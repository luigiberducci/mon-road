from typing import Dict, List

import numpy as np

from stl_rules.stl_rule import STLRule


class RSSLongitudinalSafetyRule(STLRule):
    """
    This rule implement the Longitudinal Safety Specification.

    It is based on formalization reported in Lemma 3.1 of [1: Hekmatnejad et al., MEMOCODE 2019]
    and the RSS model defined in [2: Shalev-Shwartz et al., 2018].
    Naming conventions: the variables will follow the same naming of [1], as close as possible.

    *Rewriting*: some operators have been rewritten to match the rtamt spec language (e.g. non-strict release)
        - Def. Release: phi_1 R_I phi_2 = not(not(phi_1) Until_i not(phi_2))
        - Def. Non-Strict Release: phi_1 R^ns_I phi_2 = phi_1 R_I (phi_1 or phi_2)
    """

    @property
    def variables(self):
        return ["time", "a_lon_b", "a_lon_f", "d_lon_bf", "d_lon_min"]

    @property
    def types(self):
        return ["int", "float", "float", "float", "float"]

    def __init__(self, rss_params):
        """
        :param rss_params: static parameters for rss monitoring
            `a_lon_minbr`, `a_lon_maxbr` : min, max longitudinal acceleration when breaking
            `a_lon_minacc`, `a_lon_maxacc` : min, max longitudinal acceleration
            `rho`: reaction time in seconds
            `rho_dt`: reaction time in number of steps (note: we use `next` operator, we need discrete-time stl)
            `max_steps`: overestimation of the episode length, used to monitor open intervals
        """
        required_parameters = ["a_lon_minbr", "a_lon_maxbr", "a_lon_maxacc", "rho", "rho_dt", "sim_dt", "max_steps"]
        assert all([p in rss_params for p in required_parameters])
        self._p = {p: rss_params[p] for p in required_parameters}

    @property
    def spec(self):
        # predicates
        S_lon_bf = "(d_lon_bf >= d_lon_min)"
        A_lon_b_maxacc = f"(a_lon_b <= {self._p['a_lon_maxacc']})"
        A_lon_b_minbr = f"(a_lon_b <= -{self._p['a_lon_minbr']})"
        A_lon_f_maxbr = f"(a_lon_f >= -{self._p['a_lon_maxbr']})"
        # specification
        # note: non-strict release operator is written using not and until
        psi1 = f"({A_lon_b_maxacc} and {A_lon_f_maxbr})"
        psi2 = f"({A_lon_b_minbr} and {A_lon_f_maxbr})"
        P_lon_1 = f"(not(not({S_lon_bf}) until[0:{self._p['rho_dt']}] (not({S_lon_bf} or {psi1}))))"
        P_lon_2 = f"(not(not({S_lon_bf}) until[{self._p['rho_dt']}:{self._p['max_steps']}] (not({S_lon_bf} or {psi2}))))"
        P_lon = f"({P_lon_1} and {P_lon_2})"
        # resulting specification
        phi_lon_resp = f"always (({S_lon_bf} and (next (not {S_lon_bf}))) -> (next {P_lon}))"
        return phi_lon_resp

    @property
    def demo_spec(self):
        # predicates
        S_lon_bf = "(d_lon_bf >= d_lon_min)"
        A_lon_b_maxacc = f"(a_lon_b <= {self._p['a_lon_maxacc']})"
        A_lon_b_minbr = f"(a_lon_b <= -{self._p['a_lon_minbr']})"
        A_lon_f_maxbr = f"(a_lon_f >= -{self._p['a_lon_maxbr']})"
        # specification
        # note: non-strict release operator is written using not and until
        psi1 = f"({A_lon_b_maxacc} and {A_lon_f_maxbr})"
        psi2 = f"({A_lon_b_minbr} and {A_lon_f_maxbr})"
        P_lon_1 = f"(not(not({S_lon_bf}) until[0:{self._p['rho_dt']}] (not({S_lon_bf} or {psi1}))))"
        P_lon_2 = f"(not(not({S_lon_bf}) until[{self._p['rho_dt']}:{self._p['max_steps']}] (not({S_lon_bf} or {psi2}))))"
        P_lon = f"({P_lon_1} and {P_lon_2})"
        # resulting specification
        phi_lon_resp = f"(next(not {S_lon_bf})) -> (next {P_lon})"
        return phi_lon_resp

    def _compute_dynamic_safe_long_dist(self, data: Dict[str, np.ndarray], v_b_field: str = "v_lon_b",
                                        v_f_field: str = "v_lon_f") -> np.ndarray:
        assert [f in data for f in [v_b_field, v_f_field]]
        d_b_prebr = data[v_b_field] * self._p['rho'] + 1 / 2 * self._p['a_lon_maxacc'] * self._p['rho'] ** 2
        d_b_brake_num = ((data[v_b_field] + self._p['rho'] * self._p['a_lon_maxacc']) ** 2)
        d_b_brake_den = 2 * self._p['a_lon_minbr']
        d_b_brake = d_b_brake_num / d_b_brake_den
        d_f_brake = (data[v_f_field] ** 2) / (2 * self._p['a_lon_maxbr'])
        d_diff = d_b_prebr + d_b_brake - d_f_brake
        d_lon_min = np.maximum(d_diff, np.zeros_like(d_diff))
        return d_lon_min

    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, List]:
        # check input
        obs_signals = ["time", "a_lon_b", "a_lon_f", "d_lon_bf", "v_lon_b", "v_lon_f"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {}
        out_signals["time"] = data["time"]
        out_signals["a_lon_b"] = data["a_lon_b"]
        out_signals["a_lon_f"] = data["a_lon_f"]
        out_signals["d_lon_bf"] = data["d_lon_bf"]
        out_signals["d_lon_min"] = self._compute_dynamic_safe_long_dist(data)
        out_signals = {k: list(v) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals

    def generate_signals_for_demo(self, data: Dict[str, np.ndarray], begin: int = 5, end: int = 1000) -> Dict[
        str, List]:
        # check input
        obs_signals = ["elapsed_time", "a_lon_ego", "a_lon_car", "d_lon_egocar", "v_lon_ego", "v_lon_car"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {}
        out_signals["elapsed_time"] = data["elapsed_time"] - data["elapsed_time"][0]
        out_signals["time"] = np.floor((data["elapsed_time"] - data["elapsed_time"][0]) / self._p["sim_dt"]).astype(int)
        out_signals["a_lon_b"] = data["a_lon_ego"]
        out_signals["a_lon_f"] = data["a_lon_car"]
        out_signals["d_lon_bf"] = data["d_lon_egocar"]
        out_signals["d_lon_min"] = self._compute_dynamic_safe_long_dist(data, v_b_field="v_lon_ego", v_f_field="v_lon_car")
        out_signals = {k: list(v[begin:end]) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals
