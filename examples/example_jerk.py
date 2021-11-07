import pandas as pd
import yaml

from stl_rules.comfort_jerk import ComfortLongitudinalJerk, ComfortLateralJerk
from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.utils import monitor_trace

# load data
with open("../data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
trace = pd.read_csv("../data/toy_examples/example3.csv")

# create rss rule
long_jerk = ComfortLongitudinalJerk(rss_params=rss_params)
lat_jerk = ComfortLateralJerk(rss_params=rss_params)

# process data to produce monitorable signals
import matplotlib.pyplot as plt
for name, rule in zip(["long", "lat"], [long_jerk, lat_jerk]):
    signals = rule.generate_signals(trace)
    # compute robustness
    robustness = [r for t, r in monitor_trace(rule.spec, rule.variables, rule.types, signals)]
    # plot
    plt.title("Monitoring RSS Longitudinal Safety")
    plt.xlabel("time steps")
    plt.ylabel("value")
    plt.plot(robustness, label=f"robustness ({name} jerk)")
plt.legend()
plt.show()
