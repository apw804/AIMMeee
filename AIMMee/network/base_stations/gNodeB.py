from components import antennas
import numpy as np

def degree_to_radian(degree):
    return degree*(np.pi/180)

# Define the sector azimuths
sector0_azimuth = degree_to_radian(0)
sector1_azimuth = degree_to_radian(120)
sector2_azimuth = degree_to_radian(240)

# Define the sector downtilt
sector0_downtilt = degree_to_radian(10)
sector1_downtilt = degree_to_radian(10)
sector2_downtilt = degree_to_radian(10)

# Define the sector antenna patterns
sector0_pattern = '38.901'
sector1_pattern = '38.901'
sector2_pattern = '38.901'

# Create the panel array antennas
sector0_ant = antennas.PanelArray(num_rows=2, 
                               num_cols=2, 
                               num_rows_per_panel=4, 
                               num_cols_per_panel=4,
                               polarization="dual", 
                               polarization_type="cross",
                               antenna_pattern="38.901",
                               carrier_frequency=3.5e9)

sector1_ant = antennas.PanelArray(num_rows=2,
                                num_cols=2,
                                num_rows_per_panel=4,
                                num_cols_per_panel=4,
                                polarization="dual",
                                polarization_type="cross",
                                antenna_pattern="38.901",
                                carrier_frequency=3.5e9)

sector2_ant = antennas.PanelArray(num_rows=2,
                                num_cols=2,
                                num_rows_per_panel=4,
                                num_cols_per_panel=4,
                                polarization="dual",
                                polarization_type="cross",
                                antenna_pattern="38.901",
                                carrier_frequency=3.5e9)


# Update the antenna azimuths
sector1_ant._ant_pol1.field(theta=0.0, phi=sector1_azimuth)
sector1_ant._ant_pol2.field(theta=0.0, phi=sector1_azimuth)
sector2_ant._ant_pol1.field(theta=0.0, phi=sector2_azimuth)
sector2_ant._ant_pol2.field(theta=0.0, phi=sector2_azimuth)

# View the antenna patterns
sector0_ant._ant_pol1.show()
sector0_ant._ant_pol2.show()
sector1_ant._ant_pol1.show()
sector1_ant._ant_pol2.show()
sector2_ant._ant_pol1.show()
sector2_ant._ant_pol2.show()








class gNB:
    """
    An initial attempt at defining a gNodeB (base station) within a Cell (an area of coverage).
    """
    def __init__(self) -> None:
        pass
