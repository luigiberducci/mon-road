import pandas as pd
import yaml

from stl_rules.rss_lat_safety import RSSLateralSafetyRule
from stl_rules.utils import monitor_trace

# load data
with open("../data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)
trace = pd.read_csv("../data/toy_examples/example2.csv")

# create rss rule
rss2 = RSSLateralSafetyRule(rss_params=rss_params)
stl_spec = rss2.spec

words = stl_spec.split(" ")
line = ""
for i, word in enumerate(words):
    if i % 5 == 0:
        line += "\n"
    line += f" {word}"
print(line)


# process data to produce monitorable signals
signals = rss2.generate_signals(trace)

# compute robustness
robustness = [r for t, r in monitor_trace(rss2.spec, rss2.variables, rss2.types, signals)]

# plot
import matplotlib.pyplot as plt

plt.title("Monitoring RSS Lateral Safety")
plt.xlabel("time steps")
plt.ylabel("value")
plt.plot(signals['a_lat_l'], label="a_lat_l")
plt.plot(signals['a_lat_r'], label="a_lat_r")
plt.plot(signals['d_lat_lr'], label="d_lat_lr")
plt.plot(signals['d_lat_min'], label="d_lat_min")
plt.plot(robustness, label="robustness")
plt.legend()
plt.show()
