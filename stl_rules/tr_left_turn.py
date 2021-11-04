from typing import Dict, List

import numpy as np

from stl_rules.stl_rule import STLRule


class TrafficRuleLeftTurn(STLRule):
    """
    This rule implement the Traffic Rule for two cars approaching a junction in opposite directions:
    <<[...] They may only proceed if they can see that they will neither endanger nor substantially impede a road user who
    has the right of way.
    [...] Nor must a road user who is obliged to give way substantially impede a road user who has the right of way when
    the latter turns into the other road.>>

    Intuition behind formalization:
        premise = "ego is approaching but not occupying the junction j, other car has no time to brake"
        proper response = "ego brakes until reach zero-velocity or other car crossed the intersection"

    Formalization in STL:
        premise = (ego_can_brake AND NOT(next(ego_can_brake))) AND (car_can_brake) AND (is_in_junction(ego, j)<=0)
        ego_can_brake = dist(ego,j) > d_lon_safe(ego,j)
        car_can_brake = dist(car,j) > d_lon_safe(car,j)

        plan = plan_react AND plan_brake
        plan_react = (release_condition) R^ns_{0:rho} (a_lon(ego) <= a_lon_maxacc)
        plan_brake = (release_condition) R^ns_{rho:inf} (a_lon(ego) <= -a_lon_minbr)
        release_condition = (v_lon(ego) <= 0) OR (dist(car, j) <= 0) OR (car_can_brake)
    Note: this condition takes into account 2 possible implementation of the distance metric (only-positive or pos-neg)
    If pos-neg, when car crosses junction, d(car,j)<0 and then release_condition is true (the ego can cross)
    If only-pos, when car crosses junction, d(car,j)=inf, then car_can_brake and release_condition is true

    *Rewriting*: some operators have been rewritten to match the rtamt spec language (e.g. non-strict release)
        - Def. Release: phi_1 R_I phi_2 = not(not(phi_1) Until_i not(phi_2))
        - Def. Non-Strict Release: phi_1 R^ns_I phi_2 = phi_1 R_I (phi_1 or phi_2)
    """

    @property
    def variables(self):
        return ["time", "d_lon_ej", "d_lon_cj", "d_lon_min_ej", "d_lon_min_cj",
                "is_e_in_junc", "v_lon_e", "a_lon_e"]

    @property
    def types(self):
        return ["int", "float", "float", "float", "float", "float", "float", "float"]

    def __init__(self, rss_params):
        """
        :param rss_params: static parameters for rss monitoring
            `a_lon_minbr`, `a_lon_maxbr` : min, max longitudinal acceleration when breaking
            `a_lon_minacc`, `a_lon_maxacc` : min, max longitudinal acceleration
            `rho`: reaction time in seconds
            `rho_dt`: reaction time in number of steps (note: we use `next` operator, we need discrete-time stl)
            `max_steps`: overestimation of the episode length, used to monitor open intervals
        """
        required_parameters = ["a_lon_minbr", "a_lon_maxacc", "rho", "rho_dt", "max_steps"]
        assert all([p in rss_params for p in required_parameters])
        self._p = {p: rss_params[p] for p in required_parameters}

    @property
    def spec(self):
        # predicates
        E_canbrake = "(d_lon_ej > d_lon_min_ej)"
        C_canbrake = "(d_lon_cj > d_lon_min_cj)"
        E_not_injunc = "(is_e_in_junc <= 0)"
        V_lon_e_stop = "(v_lon_e <= 0)"
        C_react_or_crossed = f"({C_canbrake} or (d_lon_cj<0))"  # the check on d_lon_cj in case d has pos-neg interpret.
        A_lon_e_maxacc = f"(a_lon_e <= {self._p['a_lon_maxacc']})"
        A_lon_e_minbr = f"(a_lon_e <= -{self._p['a_lon_minbr']})"
        release_cond = f"({V_lon_e_stop} or {C_react_or_crossed})"
        # specification
        # note: non-strict release operator is written using not and until
        S = f"(({E_canbrake} and not(next({E_canbrake}))) and (not({C_canbrake})) and ({E_not_injunc}))"
        P_react = f"(not(not({release_cond}) until[0:{self._p['rho_dt']}] not({release_cond} or {A_lon_e_maxacc})))"
        P_brake = f"(not(not({release_cond}) until[0:{self._p['rho_dt']}] not({release_cond} or {A_lon_e_minbr})))"
        P_leftturn = f"({P_react} and {P_brake})"
        # resulting specification
        phi_lt_resp = f"always (({S} and (next (not {S}))) -> (next {P_leftturn}))"
        return phi_lt_resp

    def _compute_dynamic_safe_long_dist_to_junction(self, data: Dict[str, np.ndarray], v_field: str) -> np.ndarray:
        # note: the only change is the assumption that v_front = 0, because a junction is stationary
        # then, we just remove the `d_f_brake` term from the calculation
        d_b_prebr = data[v_field] * self._p['rho'] + 1 / 2 * self._p['a_lon_maxacc'] * self._p['rho'] ** 2
        d_b_brake_num = ((data[v_field] + self._p['rho'] * self._p['a_lon_maxacc']) ** 2)
        d_b_brake_den = 2 * self._p['a_lon_minbr']
        d_b_brake = d_b_brake_num / d_b_brake_den
        d_diff = d_b_prebr + d_b_brake
        d_lon_min = np.maximum(d_diff, np.zeros_like(d_diff))
        return d_lon_min

    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, List]:
        # check input
        obs_signals = ["time", "a_lon_e", "v_lon_e", "v_lon_c", "d_lon_ej", "d_lon_cj", "is_e_in_junc"]
        assert all([s in data for s in obs_signals]), f"missing in signals ({obs_signals} not in {data.keys()})"
        # generate output signals from input signals
        out_signals = {}
        out_signals["time"] = data["time"]
        out_signals["a_lon_e"] = data["a_lon_e"]
        out_signals["v_lon_e"] = data["v_lon_e"]
        out_signals["d_lon_ej"] = data["d_lon_ej"]
        out_signals["d_lon_cj"] = data["d_lon_cj"]
        out_signals["is_e_in_junc"] = data["is_e_in_junc"]
        out_signals["d_lon_min_ej"] = self._compute_dynamic_safe_long_dist_to_junction(data, v_field="v_lon_e")
        out_signals["d_lon_min_cj"] = self._compute_dynamic_safe_long_dist_to_junction(data, v_field="v_lon_c")
        out_signals = {k: list(v) for k, v in out_signals.items()}
        # check output
        assert all([s in out_signals for s in
                    self.variables]), f"missing out signals ({self.variables} not in {out_signals.keys()})"
        return out_signals
