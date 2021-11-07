# Mon-Road
Library for monitoring of traffic metrics using STL, developed in the context of the FFG Project ADEX.

### ADEX Demonstration Session on 10-11.11.2021, TODO List
- [x] RSS Longitudinal Safety
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [x] Test integration with simulated data
  - [ ] Prepare fancy plot for a few episodes
- [ ] RSS Lateral Safety
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [ ] Test integration with simulated data
  - [ ] Prepare fancy plot for a few episodes
- [ ] Traffic Rule Left-Turn Right
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [ ] Test integration with simulated data
  - [ ] Prepare fancy plot for a few episodes
- [ ] Comfort Longitudinal Jerk
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [ ] Test integration with simulated data
  - [ ] Prepare fancy plot for a few episodes
- [ ] Comfort Lateral Jerk
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [ ] Test integration with simulated data
  - [ ] Prepare fancy plot for a few episodes

# Installation
Run the following command to install the dependencies 
```
pip install -r requirements.txt
```
It has been tested on Ubuntu 20.04, with Python3.8.

# How to run
I will try to keep a minimal set of examples to show how to use this library.

See the examples:
- `examples/example_longitudinal_safety.py` implements a simple offline monitor for RSS1 (*Longitudinal Safety*)
- `examples/example_lateral_safety.py` implements a simple offline monitor for RSS2 (*Lateral Safety*)
- `examples/example_traffic_rule_left_turn.py` implements a simple offline monitor for the custom Traffic Rule (*Safe Left-Turn*)

