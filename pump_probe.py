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
dutyCycle = float(sys.argv[5])
offset = float(sys.argv[6])

# Values valid for all pump-probe waveforms
gammaL = 3498.621 # Gyromagnetic ratio of Cs (3500 Hz/uT)
totalTime = 0.1 # Duration of the total pump-probe cycle in s
totalPoints = 1000000 # Total number of points in the waveform

#
# Generating the points for the pump-probe waveform 
#

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
# Generating points for the trigger signal which is synchronized to pump-probe.
# The trigger signal is high during pumping and low during probing.
#

triggerSinglePumpCycle = []

cyclePoints = 0
while (cyclePoints < periodPoints):
    triggerSinglePumpCycle.append(1)
    cyclePoints += 1

triggerTransitionPulse = []

for i in range(m.floor(dutyPoints)):
    triggerTransitionPulse.append(1)


# Connect to Keysight signal generator (idVendor, idProduct) in decimal

inst = usbtmc.Instrument(2391,11271)

print('Connected to device: ')
print(inst.ask('*IDN?')) # Is it there?

#
# Generate SCPI command to send pump-probe waveform to channel 1 of the signal generator.
#

# Generates SCPI command to send a single pump pulse to the signal genearator
pumpStrList = ['{:.3f}'.format(x) for x in singlePumpCycle]
pumpStr = ','.join(pumpStrList)
commandPump = 'sour1:data:arb pump,' + pumpStr

# Idem for probe segment of 10 data points
probePoints = 10
probeList = [probeAmp+offset for x in range(probePoints)]
probeStrList = ['{:.3f}'.format(x) for x in probeList]
probeStr = ','.join(probeStrList)
commandProbe = 'sour1:data:arb probe,' + probeStr

# Idem for transition pulse between pump and probe
transitionStrList = ['{:.3f}'.format(x) for x in transitionPulse]
transitionStr = ','.join(transitionStrList)
commandTransition = 'sour1:data:arb transition,' + transitionStr

# Generates SCPI command which builds the pump-probe waveform on the signal generator
pumpPoints = m.floor(pumpTime/periodL)*periodPoints
pumpPulses = m.floor(pumpPoints/periodPoints)
probeLength = m.floor((totalPoints - pumpPoints)/probePoints)
pumpProbe = '"Cs_cycle","pump",%i,repeat,maintain,5,"transition",0,once,highAtStart,5,"probe",%i,repeat,maintain,5' % (pumpPulses,probeLength)
charLen = str(len(pumpProbe))
bytesLen = str(len(charLen))
commandPumpProbe = 'sour1:data:seq #%s%s%s' % (bytesLen,charLen,pumpProbe)

#
# Generate SCPI command to send trigger signal to channel 2 of the signal generator.
#

# Generates SCPI command to send a single pump pulse length trigger signal to the signal genearator
triggerPumpStrList = ['{:.3f}'.format(x) for x in triggerSinglePumpCycle]
triggerPumpStr = ','.join(triggerPumpStrList)
commandTriggerPump = 'sour2:data:arb trPump,' + triggerPumpStr

# Idem for probe trigger segment of 10 data points
triggerProbePoints = 10
triggerProbeList = [0 for x in range(triggerProbePoints)]
triggerProbeStrList = ['{:.3f}'.format(x) for x in triggerProbeList]
triggerProbeStr = ','.join(triggerProbeStrList)
commandTriggerProbe = 'sour2:data:arb trProbe,' + triggerProbeStr

# Idem for transition pulse between pump and probe
triggerTransitionStrList = ['{:.3f}'.format(x) for x in triggerTransitionPulse]
triggerTransitionStr = ','.join(triggerTransitionStrList)
commandTriggerTransition = 'sour2:data:arb trTransition,' + triggerTransitionStr

# Generates SCPI command which builds the entire trigger waveform on the signal generator
trigger = '"Cs_trigger","trPump",%i,repeat,maintain,5,"trTransition",0,once,highAtStart,5,"trProbe",%i,repeat,maintain,5' % (pumpPulses,probeLength)
triggerCharLen = str(len(trigger))
triggerBytesLen = str(len(triggerCharLen))
commandTrigger = 'sour2:data:seq #%s%s%s' % (triggerBytesLen,triggerCharLen,trigger)

#
# Start setting up the signal generator
#

# Sampling parameters for channel 1
inst.write('sour1:func:arb:srate 1e7')
inst.write('sour1:func:arb:filter off')
inst.write('sour1:func:arb:ptpeak 6')

# Sampling parameters for channel 2
inst.write('sour2:func:arb:srate 1e7')
inst.write('sour2:func:arb:filter off')
inst.write('sour2:func:arb:ptpeak 3')

# Send commands which build pump-probe waveform on the signal generator.
inst.write(commandPump)
inst.write(commandTransition)
inst.write(commandProbe)
inst.write(commandPumpProbe)

# Send commands wich will build the trigger waveform on the signal generator.
inst.write(commandTriggerPump)
inst.write(commandTriggerTransition)
inst.write(commandTriggerProbe)
inst.write(commandTrigger)

# Save pump-probe waveform and trigger waveform
inst.write('sour1:func:arb Cs_cycle')
inst.write('mmem:store:data1 "INT:\Cs_cycle.seq"')

inst.write('sour2:func:arb Cs_trigger')
inst.write('mmem:store:data2 "INT:\Cs_trigger.seq"')

inst.write('sour1:data:vol:clear')
inst.write('sour2:data:vol:clear')

# Load waveform to flash memory to generate
inst.write('mmem:load:data1 "INT:\Cs_cycle.seq"')
inst.write('sour1:func arb')
inst.write('sour1:func:arb "INT:\Cs_cycle.seq"')

inst.write('mmem:load:data2 "INT:\Cs_trigger.seq"')
inst.write('sour2:func arb')
inst.write('sour2:func:arb "INT:\Cs_trigger.seq"')

# Synchronize the start points of both waveforms for proper triggering.
inst.write('func:arb:sync')

# Turn both outputs on
inst.write('output1 on')
inst.write('output2 on')

inst.close()

