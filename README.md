# Mon-Road
Library for monitoring of traffic metrics using STL, developed in the context of the FFG Project ADEX.

### ADEX Demonstration Session on 10-11.11.2021, TODO List
- [x] RSS Longitudinal Safety
  - [x] Implementation of STL monitoring
  - [x] Implementation of a minimal example
  - [ ] Test integration with simulated data
- [ ] RSS Lateral Safety
  - [x] Implementation of STL monitoring
  - [ ] Implementation of a minimal example
  - [ ] Test integration with simulated data
- [ ] Traffic Rule Left-Turn Right
  - [ ] Implementation of STL monitoring
  - [ ] Implementation of a minimal example
  - [ ] Test integration with simulated data
- [ ] Comfort Longitudinal Jerk
  - [ ] Implementation of STL monitoring
  - [ ] Implementation of a minimal example
  - [ ] Test integration with simulated data
- [ ] Comfort Lateral Jerk
  - [ ] Implementation of STL monitoring
  - [ ] Implementation of a minimal example
  - [ ] Test integration with simulated data

# Installation
Run the following command to install the dependencies 
```
pip install -r requirements.txt
```
It has been tested on Ubuntu 20.04, with Python3.8.

# How to run
I will try to keep a minimal set of examples to show how to use this library.

See the examples:
- `examples/example_lon_safety.py` implements a simple offline monitor for RSS1 (*Longitudinal Safety*)

