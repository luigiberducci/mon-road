import pandas as pd
import yaml

from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.utils import monitor_trace

# load data
with open("data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
trace = pd.read_csv("data/example1.csv")

# create rss rule
rss_lon_safety = RSSLongitudinalSafetyRule(rss_params=rss_params)
vars = rss_lon_safety.variables
types = rss_lon_safety.types
stl_spec = rss_lon_safety.spec

# process data to produce monitorable signals
signals = rss_lon_safety.generate_signals(trace)

# compute robustness
robustness = [r for t, r in monitor_trace(stl_spec, vars, types, signals)]

# plot
import matplotlib.pyplot as plt
plt.title("Monitoring RSS Longitudinal Safety")
plt.xlabel("time steps")
plt.ylabel("value")
plt.plot(signals['a_lon_b'], label="a_lon_b")
plt.plot(signals['a_lon_f'], label="a_lon_f")
plt.plot(signals['d_lon_bf'], label="d_lon_bf")
plt.plot(signals['d_lon_min'], label="d_lon_min")
plt.plot(robustness, label="robustness")
plt.legend()
plt.show()