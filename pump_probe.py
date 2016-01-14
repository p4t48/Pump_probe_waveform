import matplotlib.pyplot as plt
import math as m
import usbtmc

# Values valid for all pump-probe waveforms
gammaL = 3500 # Gyromagnetic ratio of Cs 
totalTime = 100 # Duration of the total pump-probe cycle
totalPoints = 100000 # Total number of points in the waveform


fieldStrength = 1 # B-field strength in uT
pumpTime = 30 # Duration of the pumping
pumpAmp = 0.5 # Amplitude of the pump in fractions of set Vpp
probeAmp = 0.03 # Amplitude of the probe in fractions of set Vpp
dutyCycle = 0.1

nuL = fieldStrength * gammaL
periodL = 1/nuL
periodPoints = periodL * totalPoints
dutyPoints = periodPoints * dutyCycle
pumpPoints = m.floor((pumpTime/totalTime) * totalPoints)

singlePumpCycle = []
pumpProbeCycle = []

cyclePoints = 0
while (cyclePoints < periodPoints):
    if (cyclePoints < dutyPoints):
        singlePumpCycle.append(pumpAmp)
    else:
        singlePumpCycle.append(0.0)
    cyclePoints += 1

while (len(pumpProbeCycle) < pumpPoints):
    pumpProbeCycle.extend(singlePumpCycle)        

while (len(pumpProbeCycle) < totalPoints):
    pumpProbeCycle.extend([probeAmp])

print(singlePumpCycle)
#print(pumpProbeCycle)
xVals = list(range(len(pumpProbeCycle)))

plt.plot(xVals,pumpProbeCycle)
plt.show()
