from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.utils import monitor_trace
import numpy as np

reaction_time = 1.0
sim_step = 1.0

rss_params = {
    "a_lon_minbr": 4.0,                     # m/s2
    "a_lon_maxbr": 10.0,                    # m/s2
    "a_lon_maxacc": 5.5,                    # m/s2
    "rho": reaction_time,                   # s
    "rho_dt": int(reaction_time / sim_step),     # int
    "max_steps": 1000,                      # over-estimation of trace len
}

trace = {
    "time": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "a_lon_b": [1.0, 1.0, 1.0, 0.0, -4.0, -4.0, 0.0, 0.0, 0.0, 0.0],
    "a_lon_f": [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "d_lon_bf": [100.0, 50.0, 20.0, 10.0, 5.0, 10.0, 10.0, 15.0, 15.0, 20.0],
    "v_lon_b": [1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 0.0, 0.0],
    "v_lon_f": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
}
trace = {k: np.array(v) for k, v in trace.items()}

rss_lon_safety = RSSLongitudinalSafetyRule(rss_params=rss_params)
vars = rss_lon_safety.variables
types = rss_lon_safety.types
stl_spec = rss_lon_safety.spec

for i in range(0, len(stl_spec), 50):
    print(stl_spec[i:i+50])

signals = rss_lon_safety.generate_signals(trace)
robustness = [r for t, r in monitor_trace(stl_spec, vars, types, signals)]

import matplotlib.pyplot as plt

#plt.plot(signals['d_lon_bf_minus_d_safe'], label="d_lon_bf - d_lon_min")
print("d_lon_bf: " + str(signals["d_lon_bf"]))
print("d_lon_min: " + str(signals["d_lon_min"]))
print("rob: " + str(robustness))
plt.plot(signals['a_lon_b'], label="a_lon_b")
plt.plot(signals['a_lon_f'], label="a_lon_f")
plt.plot(signals['d_lon_bf'], label="d_lon_bf")
plt.plot(signals['d_lon_min'], label="d_lon_min")
plt.plot(robustness, label="robustness")
plt.legend()
plt.show()