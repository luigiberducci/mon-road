import pandas as pd
import yaml

from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.utils import monitor_trace

# load data
with open("../data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
trace = pd.read_csv("../data/toy_examples/example1.csv")

# create rss rule
rss1 = RSSLongitudinalSafetyRule(rss_params=rss_params)

# process data to produce monitorable signals
signals = rss1.generate_signals(trace)

# compute robustness
robustness = [r for t, r in monitor_trace(rss1.spec, rss1.variables, rss1.types, signals)]

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
