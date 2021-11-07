import argparse
import glob
import pathlib
import time

import pandas as pd
import yaml
import matplotlib.pyplot as plt

from stl_rules.rss_lat_safety import RSSLateralSafetyRule
from stl_rules.rss_lon_safety import RSSLongitudinalSafetyRule
from stl_rules.tr_left_turn import TrafficRuleLeftTurn
from stl_rules.comfort_jerk import ComfortLateralJerk, ComfortLongitudinalJerk
from stl_rules.utils import monitor_trace

# map from stl-rule name to implementation class
stl_rules = {
    "safe1": RSSLongitudinalSafetyRule,
    "safe2": RSSLateralSafetyRule,
    "legal_turn": TrafficRuleLeftTurn,
    "comfort_lon": ComfortLongitudinalJerk,
    "comfort_lat": ComfortLateralJerk
}
rules_titles = {
    "safe1": "RSS Longitudinal Safety",
    "safe2": "RSS Lateral Safety",
    "legal_turn": "Traffic Law, Left-Turn",
    "comfort_lon": "Comfort Metric, Longitudinal Jerk",
    "comfort_lat": "Comfort Metric, Lateral Jerk"
}

parser = argparse.ArgumentParser()
parser.add_argument("--rules", type=str, nargs="+", help="rules to monitor", choices=stl_rules.keys())
parser.add_argument("--datadir", type=pathlib.Path, help="where csv logs are stored", required=True)
parser.add_argument("--begin", type=int, help="index of trace begin", default=10)
parser.add_argument("--end", type=int, help="index of trace end", default=1000)
args = parser.parse_args()

rules = args.rules
datadir = args.datadir
begin, end = args.begin, args.end
assert datadir.exists(), f"datadir {datadir} not exists"
assert begin <= end, f"not valid trace delimiters ({begin} > {end}"

# load params
with open("data/rss_params.yaml", 'r') as stream:
    rss_params = yaml.safe_load(stream)

# monitor rules
for rule_name in rules:
    # create stl-rule
    rule = stl_rules[rule_name](rss_params=rss_params)
    stl_spec = rule.spec
    #
    xs, ys, labels = [], [], []
    print(f"[Info] Monitoring rule {rule_name} from files in {datadir}")
    for filepath_str in glob.glob(str(datadir / f"{rule_name}*csv")):
        t0 = time.time()
        # read data
        filepath = pathlib.Path(filepath_str)
        trace = pd.read_csv(filepath)
        print(f"\tfile: {filepath}")
        print(f"\tload data: {len(trace)} rows in {time.time() - t0:.3f} sec")
        # monitoring
        signals = rule.generate_signals_for_demo(trace, begin=begin, end=end)
        robustness = [r for t, r in monitor_trace(rule.demo_spec, rule.variables, rule.types, signals)]
        print(f"\tmonitoring rule in {time.time() - t0:.3f} sec")
        # write results
        outpath = str(datadir / f"robustness_{filepath.stem}_{int(time.time())}.csv")
        out = pd.DataFrame({"elapsed_time": signals["elapsed_time"], "robustness": robustness})
        out.to_csv(outpath, index=False)
        print(f"\tresults written in {outpath}")
        # collect curves for aggregated plot
        xs.append(signals['elapsed_time'])
        ys.append(robustness)
        labels.append(str(filepath.stem))
    # plot
    plt.title(rules_titles[rule_name])
    plt.xlabel("time (sec)")
    plt.ylabel("robustness")
    for xx, yy, label in zip(xs, ys, labels):
        plt.plot(xx, yy, label=label)
    plt.legend()
    plt.savefig(datadir / f"plot_robustness_{rule_name}_{time.time()}.png")
    print()

