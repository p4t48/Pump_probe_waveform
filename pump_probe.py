gammaL = 3500 # Gyromagnetic ratio of Cs 

fieldStrength = 1 # B-field strength in uT
pumpTime = 30 # Duration of the pumping
totalTime = 100 # Duration of the total pump-probe cycle
pumpAmp = 0.5 # Amplitude of the pump in fractions of set Vpp
probeAmp = 0.03 # Amplitude of the probe in fractions of set Vpp

nuL = fieldStrength * gammaL
periodL = 1/nuL

print(periodL)
