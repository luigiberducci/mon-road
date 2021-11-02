import pandas as pd
import yaml

from stl_rules.tr_left_turn import TrafficRuleLeftTurn
from stl_rules.utils import monitor_trace

# load data
with open("data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
trace = pd.read_csv("data/example4.csv")

# create traffic-rule spec
tr = TrafficRuleLeftTurn(rss_params=rss_params)

# process data to produce monitorable signals
signals = tr.generate_signals(trace)

# compute robustness
robustness = [r for t, r in monitor_trace(tr.spec, tr.variables, tr.types, signals)]

# plot
import matplotlib.pyplot as plt

plt.title("Monitoring Traffic Rule Safe Left-Turn")
plt.xlabel("time steps")
plt.ylabel("value")
plt.plot(signals['d_lon_ej'], label="d_lon_ej")
plt.plot(signals['d_lon_cj'], label="d_lon_cj")
plt.plot(signals['a_lon_e'], label="a_lon_e")
plt.plot(robustness, label="robustness")
print(robustness)
plt.legend()
plt.show()
