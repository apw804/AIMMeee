# Power Consumption Estimation for OpenRAN System

This document presents an estimation of power consumption for an OpenRAN system based on the default values provided by various sources. The power consumption is estimated for different components, including CPU, RAM, GPU, accelerator cards, ASICs, and NICs.

## Default Values

The default values used for the estimation are obtained from the following sources:

1. **Power Supply (P_supply):** The power supply capacity in Watts (W) is taken from the reference [@misc{intel_OpenRAN_2022}]. 

2. **Physical Cores (n_cpu) and Single Core Power (P_cpu):** The number of physical cores and the power consumption of a single core (TDP - Thermal Design Power) in Watts (W) are considered.

3. **RAM (ram) and RAM Power (P_ram):** The RAM capacity in Gigabytes (GB) is considered, and the power consumption estimation for RAM is based on an average of 3 watts per 8GB of RAM [@misc{micron_memory_power_2019}].

4. **Graphics Processing Units (n_gpu) and GPU Power (P_gpu):** The number of GPUs and the power consumption of a single GPU in Watts (W) are taken into account.

5. **Accelerator Cards (n_accel) and Accelerator Card Power (P_accel):** The number of accelerator cards and the power consumption of a single accelerator card in Watts (W) are obtained from the reference [@{silicom_accel_acc100_2022}].

6. **Application-Specific Integrated Circuits (ASICs) (n_asic) and ASIC Power (P_asic):** The number of ASICs and the power consumption per ASIC are considered based on the reference [@misc{intel_asic_8970_2022}].

7. **Network Interface Cards (NICs) (n_nic) and NIC Power (P_nic):** The number of Network Interface Cards and the power consumption per NIC are taken into account using the reference [@misc{intel_nic_e810_2023}].

## Power Consumption Calculation

The total power consumption of the OpenRAN system can be estimated by summing up the power consumption of each component:

```python
# Default values
P_supply = 1000  # Watts (W)
n_cpu = 16       # Number of physical cores
P_cpu = 50       # Watts (W) - Power consumption per single core
ram = 64         # Gigabytes (GB) - RAM capacity
P_ram = 24       # Watts (W) - Power consumption per 8GB of RAM
n_gpu = 2        # Number of GPUs
P_gpu = 200      # Watts (W) - Power consumption per single GPU
n_accel = 4      # Number of accelerator cards
P_accel = 150    # Watts (W) - Power consumption per single accelerator card
n_asic = 1       # Number of ASICs
P_asic = 100     # Watts (W) - Power consumption per single ASIC
n_nic = 2        # Number of NICs
P_nic = 30       # Watts (W) - Power consumption per single NIC

# Power consumption calculation
total_power_consumption = P_supply + (n_cpu * P_cpu) + (P_ram * (ram // 8)) + (n_gpu * P_gpu) + (n_accel * P_accel) + (n_asic * P_asic) + (n_nic * P_nic)
```

Please note that the above calculation is a simple example, and actual power consumption in a real OpenRAN system might vary depending on various factors such as workload, optimization, and hardware specifications.

This estimation serves as a starting point for understanding the power requirements of the OpenRAN system and can be adjusted based on specific hardware configurations and usage scenarios.