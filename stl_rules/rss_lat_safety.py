from typing import Dict, List

import numpy as np

from stl_rules.stl_rule import STLRule


class RSSLateralSafetyRule(STLRule):
    """
    This rule implement the Lateral Safety Specification.

    It is based on formalization reported in Lemma 3.2 of [1: Hekmatnejad et al., MEMOCODE 2019].
    Naming conventions: the variables will follow the same naming of [1], as close as possible.

    *Rewriting*: some operators have been rewritten to match the rtamt spec language (e.g. non-strict release)
        - Def. Release: phi_1 R_I phi_2 = not(not(phi_1) Until_i not(phi_2))
        - Def. Non-Strict Release: phi_1 R^ns_I phi_2 = phi_1 R_I (phi_1 or phi_2)
    """

    @property
    def variables(self):
        pass

    @property
    def types(self):
        pass

    def __init__(self, rss_params):
        """
        :param rss_params: static parameters for rss monitoring
            `a_lon_minbr`, `a_lon_maxbr` : min, max longitudinal acceleration when breaking
            `a_lon_minacc`, `a_lon_maxacc` : min, max longitudinal acceleration
            `rho`: reaction time in seconds
            `rho_dt`: reaction time in number of steps (note: we use `next` operator, we need discrete-time stl)
        """
        required_parameters = ["a_lat_maxacc", "rho_dt", "max_steps"]
        assert all([p in rss_params for p in required_parameters])
        self._p = {p: rss_params[p] for p in required_parameters}

    @property
    def spec(self):
        # predicates
        S_lat_lr = "(d_lat_lr > d_lat_min)"
        A_lat_l_maxacc = f"(abs(a_lat_l) <= {self._p['a_lat_maxacc']})"
        A_lat_l_minbr = f"(a_lat_l <= -{self._p['a_lat_minbr']})"
        A_lat_r_maxacc = f"(abs(a_lat_r) <= {self._p['a_lat_maxacc']})"
        A_lat_r_minbr = f"(a_lat_r >= -{self._p['a_lat_minbr']})"
        V_lat_l_stop = "(v_mulat_l == 0)"
        V_lat_l_neg = "(v_mulat_l <= 0)"
        V_lat_r_stop = "(v_mulat_r == 0)"
        V_lat_r_pos = "(v_mulat_r >= 0)"
        # specification
        # note: non-strict release operator is written using not and until
        psi_1 = f"({A_lat_l_maxacc} and {A_lat_r_maxacc})"
        P_lat_0_r = f"(not( not({S_lat_lr}) until[0:{self._p['rho_dt']}] not({S_lat_lr} or {psi_1})))"
        psi_2 = f"not( not({S_lat_lr} or {V_lat_l_stop}) until[{self._p['rho_dt']}:{self._p['max_steps']}] " \
                f"not(({S_lat_lr} or {V_lat_l_stop}) or {A_lat_l_minbr}))"
        psi_3 = f"not( not({S_lat_lr} or {V_lat_r_stop}) until[{self._p['rho_dt']}:{self._p['max_steps']}] " \
                f"not(({S_lat_lr} or {V_lat_r_stop}) or {A_lat_r_minbr}))"
        P_lat1_r_inf = f"({psi_2} and {psi_3})"
        psi_4_1 = f"({V_lat_l_stop} -> (next (always {V_lat_l_neg})))"
        psi_4 = f"(not( (not {S_lat_lr}) until[{self._p['rho_dt']}:{self._p['max_steps']}] (not ({S_lat_lr} or {psi_4_1}))))"
        psi_5_1 = f"({V_lat_r_stop} -> (next (always {V_lat_r_pos})))"
        psi_5 = f"(not ((not {S_lat_lr}) until[] (not ({S_lat_lr} or {psi_5_1}))))"
        P_lat2_r_inf = f"{psi_4} and {psi_5}"
        P_lat = f"({P_lat_0_r} and {P_lat1_r_inf} and {P_lat2_r_inf})"
        # resulting specification
        phi_lat_resp = f"always (({S_lat_lr} and (next (not {S_lat_lr}))) -> (next {P_lat}))"
        return phi_lat_resp

    def _compute_dynamic_safe_dist(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        # TODO
        pass

    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, List]:
        # check input
        obs_signals = ["a_lon_b", "a_lon_f", "d_lon_bf", "v_lon_b", "v_lon_f"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {}
        out_signals["time"] = data["time"]
        out_signals["a_lon_b"] = data["a_lon_b"]
        out_signals["a_lon_f"] = data["a_lon_f"]
        out_signals["d_lon_bf"] = data["d_lon_bf"]
        out_signals["d_lon_min"] = self._compute_dynamic_safe_dist(data)
        out_signals = {k: list(v) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals
