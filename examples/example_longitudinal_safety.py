import pathlib

import pandas as pd
import yaml

from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.utils import monitor_trace

# load data
with open("data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
# trace = pd.read_csv("data/example1.csv")
datadir = pathlib.Path("data")
filename = "safe1_3159_3162"
trace = pd.read_csv(datadir / f"{filename}.csv")

# create rss rule
rss1 = RSSLongitudinalSafetyRule(rss_params=rss_params)

# process data to produce monitorable signals
signals = rss1.generate_signals_for_demo(trace)

# compute robustness
original_robustness = [r for t, r in monitor_trace(rss1.spec, rss1.variables, rss1.types, signals)]
demo_robustness = [r for t, r in monitor_trace(rss1.demo_spec, rss1.variables, rss1.types, signals)]
rhodf = pd.DataFrame({"rho_safe_imply_plan": demo_robustness,
                      "rho_safeandnextunsafe_imply_plan": original_robustness})
rhodf.to_csv(datadir / f"robustness_{filename}.csv")

# plot
import matplotlib.pyplot as plt

plt.title(f"Monitoring RSS Long. Safety - File: {filename}")
plt.xlabel("time steps")
plt.ylabel("value")
plt.plot(signals['d_lon_bf'], label="d_lon_bf", color="blue")
plt.plot(signals['d_lon_min'], label="d_lon}_min", color="green")
plt.plot(demo_robustness, label="rho_our", color="red")
plt.plot(original_robustness, label="rho_fainekos", color="orange")
plt.legend()
plt.savefig(datadir / f"robustness_{filename}.png")
