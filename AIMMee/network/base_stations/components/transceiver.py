class Transceiver:
    def __init__(self):
        self.power_consumption = 0.0  # Total power consumption in Watts

    def power_amplifier(self, signal_power, efficiency):
        # Power in Watts
        power_consumption = signal_power / efficiency
        self.power_consumption += power_consumption
        return power_consumption

    def adc(self, sampling_rate, resolution):
        # Power consumption in microWatts converted to Watts
        power_consumption = sampling_rate * resolution * 1e-6
        self.power_consumption += power_consumption
        return power_consumption

    def dac(self, sampling_rate, resolution):
        # Power consumption in microWatts converted to Watts
        power_consumption = sampling_rate * resolution * 1e-6
        self.power_consumption += power_consumption
        return power_consumption

    def iq_mixer(self, local_oscillator_power):
        # Power in Watts
        power_consumption = local_oscillator_power
        self.power_consumption += power_consumption
        return power_consumption

    def filter(self, signal_power, insertion_loss):
        # Power in Watts
        power_consumption = signal_power * insertion_loss
        self.power_consumption += power_consumption
        return power_consumption

    def ofdm_modulator(self, subcarrier_count):
        # Power consumption in microWatts converted to Watts
        power_consumption = subcarrier_count * 1e-6
        self.power_consumption += power_consumption
        return power_consumption

    def ofdm_demodulator(self, subcarrier_count):
        # Power consumption in microWatts converted to Watts
        power_consumption = subcarrier_count * 1e-6
        self.power_consumption += power_consumption
        return power_consumption
    
    def local_oscillator(self, frequency):
        # Simplified model: power consumption increases linearly with frequency
        # Let's assume power is in microWatts per MHz, converted to Watts
        power_consumption = frequency * 0.001 * 1e-6  # Assuming 0.001 μW/MHz
        self.power_consumption += power_consumption
        return power_consumption

    def total_power(self):
        return self.power_consumption  # Total power in Watts




if __name__ == "__main__":
  transceiver = Transceiver()
  transceiver.power_amplifier(10, 0.5)
  transceiver.adc(1e6, 16)
  transceiver.dac(1e6, 16)
  transceiver.iq_mixer(1)
  transceiver.filter(10, 0.1)
  transceiver.ofdm_modulator(1024)
  transceiver.ofdm_demodulator(1024)
  transceiver.local_oscillator(3.5e9)
  print(transceiver.total_power(), 'watts')
