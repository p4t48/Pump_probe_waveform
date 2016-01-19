import matplotlib.pyplot as plt
import math as m
import usbtmc

# Values valid for all pump-probe waveforms
gammaL = 3500 # Gyromagnetic ratio of Cs (3500 Hz/uT)
totalTime = 100 # Duration of the total pump-probe cycle
totalPoints = 100000 # Total number of points in the waveform


fieldStrength = 1 # B-field strength in uT
pumpTime = 25 # Duration of the pumping
pumpAmp = 1 # Amplitude of the pump in fractions of set Vpp
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

#while (len(pumpProbeCycle) < totalPoints):
#    pumpProbeCycle.extend([probeAmp])


# Plot the generated pump-probe cycle
xVals = list(range(len(singlePumpCycle)))
plt.plot(xVals,singlePumpCycle,'o')
#plt.show()


# Connect to Keysight signal generator (idVendor, idProduct) in decimal
inst = usbtmc.Instrument(2391,11271)

print('Connected to device: ')
print(inst.ask('*IDN?'))


dataStrList = ['{:.3f}'.format(x) for x in singlePumpCycle]
dataStr = ','.join(dataStrList)
commandPump = 'DATA:ARB pump,' + dataStr

print(commandPump)

commandProbe = 'data:arb probe, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1'

inst.write('FUNC:ARB:SRATE 1E6')
inst.write('FUNC:ARB:FILTER OFF')
inst.write('FUNC:ARB:PTPEAK 6')

inst.write(commandPump)
inst.write(commandProbe)

inst.write('data:sequence #267"Cs_cycle","pump",5,repeat,maintain,10,"probe",0,once,highAtStart,5')

inst.write('FUNC:ARB Cs_cycle')
inst.write('MMEM:STORE:DATA "INT:\Cs_cycle.seq"')
inst.write('DATA:VOL:CLEAR')


inst.write('MMEM:LOAD:DATA "INT:\Cs_cycle.seq"')
inst.write('FUNC ARB')
inst.write('FUNC:ARB "INT:\Cs_cycle.seq"')

inst.write('OUTPUT ON')

inst.close()

