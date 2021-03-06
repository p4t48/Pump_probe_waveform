"""
Single frequency pump-probe signal for Keysight 33522B
======================================================

Generates an AM pump-probe signal for the Keysight 33522B generator
via SCPI commands.

Use the script as follows:

python pump_probe.py B Tpump Apump Aprobe Duty Offset

where: - B: field strength in uT (up to 35 uT)
       - Tpump: pumping time in s
       - Apump: Pump amplitude as a fraction of Vpp
       - Aprobe: Probe amplitdue as a fraction of Vpp
       - Aprobe2: 2nd Probe amplitdue as a fraction of Vpp
       - Duty: Duty cycle of the pump waveform
       - Offset: Offset added to waveform (fraction of Vpp) to adjust EOM

"""

import matplotlib.pyplot as plt
import math as m
import usbtmc
import sys

# Pump-probe cycle quantities
fieldStrength = float(sys.argv[1]) 
pumpTime = float(sys.argv[2]) 
pumpAmp = float(sys.argv[3]) 
probeAmp = float(sys.argv[4])
probeAmp2 = float(sys.argv[5])
dutyCycle = float(sys.argv[6])
offset = float(sys.argv[7])

# Values valid for all pump-probe waveforms
gammaL = 3498.621 # Gyromagnetic ratio of Cs (3500 Hz/uT)
totalTime = 0.1 # Duration of the total pump-probe cycle in s
totalPoints = 1000000 # Total number of points in the waveform

# Larmor frequency and period
nuL = fieldStrength * gammaL
periodL = 1/nuL

# Points required to generate a single pump pulse 
periodPoints = m.floor(periodL/totalTime * totalPoints)
dutyPoints = periodPoints * dutyCycle
singlePumpCycle = []

cyclePoints = 0
while (cyclePoints < periodPoints):
    if (cyclePoints < dutyPoints):
        singlePumpCycle.append(pumpAmp+offset)
    else:
        singlePumpCycle.append(offset)
    cyclePoints += 1

# Points required for the transition pulse between pump and probe
transitionPulse = []
for i in range(m.floor(dutyPoints)):
    transitionPulse.append(pumpAmp+offset)


#
# Connect to Keysight signal generator (idVendor, idProduct) in decimal
#

inst = usbtmc.Instrument(2391,11271)

print('Connected to device: ')
print(inst.ask('*IDN?')) # Is it there?

# Generates SCPI command to send a single pump pulse to the signal genearator
pumpStrList = ['{:.3f}'.format(x) for x in singlePumpCycle]
pumpStr = ','.join(pumpStrList)
commandPump = 'data:arb pump,' + pumpStr

# Idem for probe segment of 10 data points
probePoints = 10
probeList = [probeAmp+offset for x in range(probePoints)]
probeStrList = ['{:.3f}'.format(x) for x in probeList]
probeStr = ','.join(probeStrList)
commandProbe = 'data:arb probe,' + probeStr

# Idem for probe segment of 10 data points
probePoints = 10
probeList = [probeAmp2+offset for x in range(probePoints)]
probeStrList = ['{:.3f}'.format(x) for x in probeList]
probeStr = ','.join(probeStrList)
commandProbeTwo = 'data:arb probetwo,' + probeStr

# Idem for transition pulse between pump and probe
transitionStrList = ['{:.3f}'.format(x) for x in transitionPulse]
transitionStr = ','.join(transitionStrList)
commandTransition = 'data:arb transition,' + transitionStr

# Generates SCPI command which builds the pump-probe waveform on the signal generator
pumpPoints = m.floor(pumpTime/periodL)*periodPoints
pumpPulses = m.floor(pumpPoints/periodPoints)
probeLength = m.floor((totalPoints - pumpPoints)/probePoints)
pumpProbe = '"Cs_cycle","pump",%i,repeat,maintain,5,"transition",0,once,highAtStart,5,"probe",%i,repeat,maintain,5,"pump",%i,repeat,maintain,5,"transition",0,once,highAtStart,5,"probetwo",%i,repeat,maintain,5' % (pumpPulses,probeLength,pumpPulses,probeLength)
charLen = str(len(pumpProbe))
bytesLen = str(len(charLen))
commandPumpProbe = 'data:seq #%s%s%s' % (bytesLen,charLen,pumpProbe)

#
# Start setting up the signal generator
#


inst.write('func:arb:srate 1e7')
inst.write('func:arb:filter off')
inst.write('func:arb:ptpeak 6')


# Send command which build pump-probe waveform on signal generator
inst.write(commandPump)
inst.write(commandTransition)
inst.write(commandProbe)
inst.write(commandProbeTwo)
inst.write(commandPumpProbe)

# Save pump-probe waveform
inst.write('func:arb Cs_cycle')
inst.write('mmem:store:data "INT:\Cs_cycle.seq"')
inst.write('data:vol:clear')

# Load waveform to flash memory to generate
inst.write('mmem:load:data "INT:\Cs_cycle.seq"')
inst.write('func arb')
inst.write('func:arb "INT:\Cs_cycle.seq"')

"""
# Generate proper sync signal for external triggering
inst.write('apply:arb 1 MHz,6.0,0.0 V')
inst.write('burst:mode trig')
inst.write('burst:ncycles 1')
inst.write('burst:int:per 1.1e-2')
inst.write('burst:phase 0')
inst.write('trigger:source imm')
inst.write('burst:state on')


inst.write('frequency:mode cw')
inst.write('output:sync on')
inst.write('output:sync:mode mark')
inst.write('marker:point 30000')
inst.write('output:sync:polarity normal')
inst.write('output:sync:source CH1')
inst.write('output:trigger on')
"""

inst.write('output on')

inst.close()

