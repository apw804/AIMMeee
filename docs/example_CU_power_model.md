# Power Consumption Estimation for Centralized Unit in OpenRAN System

This document presents a toy estimation of power consumption for the Centralized Unit in an OpenRAN system based on the parameters provided in the reference [@article{Lannelongue_GreenAlgorithms_2021}].

## Default Values

The default values used for the estimation are as follows:

- **Runtime:** 24 hours
- **Type of Cores:** CPU
- **Number of Cores (n_cpu):** 36
- **Model:** Other
- **TDP (Thermal Design Power) per Core (P_cpu):** 250 Watts / 36 cores = 6.94 Watts/core (Intel® Xeon® Platinum 8360Y)
- **Memory (ram):** 384 GB
- **Platform:** Local (assuming MNO data centre)
- **Location:** EU - UK
- **Real Usage:** Unknown
- **PUE (Power Usage Effectiveness):** No information provided
- **Pragmatic Scaling:** No information provided
- **Result:** 15.75 kWh per day, which is equivalent to 656.25 Watts.

## Power Consumption Calculation

The power consumption for the Centralized Unit can be estimated based on the provided result of 656.25 Watts (joules/second):

```python
# Default values for Centralized Unit
P_centralized_unit = 656.25  # Watts (W)

# If the power consumption is required for a different duration, it can be scaled accordingly.
# For example, for a different runtime (in hours), power consumption can be estimated as follows:
# P_centralized_unit = (656.25 / 24) * runtime_hours

# If the power consumption is required for different locations with varying PUE, adjustments can be made.
# For example, for a data center with PUE of 1.5, power consumption can be estimated as follows:
# P_centralized_unit_with_pue = P_centralized_unit * 1.5
