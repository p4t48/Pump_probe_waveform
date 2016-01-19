import matplotlib.pyplot as plt
import math as m
import usbtmc

# Values valid for all pump-probe waveforms
gammaL = 3500 # Gyromagnetic ratio of Cs (3500 Hz/uT)
totalTime = 0.1 # Duration of the total pump-probe cycle in s
totalPoints = 100000 # Total number of points in the waveform


fieldStrength = 1 # B-field strength in uT
pumpTime = 0.025 # Duration of the pumping in s
pumpAmp = 1 # Amplitude of the pump in fractions of set Vpp
probeAmp = 0.03 # Amplitude of the probe in fractions of set Vpp
dutyCycle = 0.1

nuL = fieldStrength * gammaL
periodL = 1/nuL

# Points required to generate a single pump pulse
periodPoints = m.floor(periodL/totalTime * totalPoints)
dutyPoints = periodPoints * dutyCycle
singlePumpCycle = []

cyclePoints = 0
while (cyclePoints < periodPoints):
    if (cyclePoints < dutyPoints):
        singlePumpCycle.append(pumpAmp)
    else:
        singlePumpCycle.append(0.0)
    cyclePoints += 1


# Connect to Keysight signal generator (idVendor, idProduct) in decimal
inst = usbtmc.Instrument(2391,11271)

print('Connected to device: ')
print(inst.ask('*IDN?'))

# Generates SCPI command to send a single pump pulse to the signal genearator
pumpStrList = ['{:.3f}'.format(x) for x in singlePumpCycle]
pumpStr = ','.join(pumpStrList)
commandPump = 'data:arb pump,' + pumpStr

# Idem for probe segment
probePoints = 10
probeList = [probeAmp for x in range(probePoints)]
probeStrList = ['{:.3f}'.format(x) for x in probeList]
probeStr = ','.join(probeStrList)
commandProbe = 'data:arb probe,' + probeStr


# Generates SCPI command which builds the pump-probe waveform on the signal generator
pumpPoints = m.floor(pumpTime/periodL)*periodPoints
pumpPulses = m.floor(pumpPoints/periodPoints)
probeLength = m.floor((totalPoints - pumpPoints)/probePoints)

pumpProbe = '"Cs_cycle","pump",%i,repeat,maintain,5,"probe",%i,repeat,maintain,5' % (pumpPulses,probeLength)
charLen = str(len(pumpProbe))
bytesLen = str(len(charLen))
commandPumpProbe = 'data:seq #%s%s%s' % (bytesLen,charLen,pumpProbe)

print(commandProbe)
print(commandPumpProbe)


inst.write('FUNC:ARB:SRATE 1E6')
inst.write('FUNC:ARB:FILTER OFF')
inst.write('FUNC:ARB:PTPEAK 6')


inst.write(commandPump)
inst.write(commandProbe)
inst.write(commandPumpProbe)


inst.write('FUNC:ARB Cs_cycle')
inst.write('MMEM:STORE:DATA "INT:\Cs_cycle.seq"')
inst.write('DATA:VOL:CLEAR')

inst.write('MMEM:LOAD:DATA "INT:\Cs_cycle.seq"')
inst.write('FUNC ARB')
inst.write('FUNC:ARB "INT:\Cs_cycle.seq"')

inst.write('OUTPUT ON')

inst.close()

