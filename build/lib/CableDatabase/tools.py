#
# tools.py (c) Stuart B. Wilkins 2013
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Part of the "CableDatabase" package
#

"""
Python module to provide tools to use the CableDatabase
to auto configuring of EPICS substitution files and channel archiver
"""

import pystache
import os

# Dictionary mapping from MKS chanel connection (on controller) to channel number.

mksChan   = {'A' : 1, 'A1' : 1, 'A2' : 2,
			 'B' : 3, 'B1' : 3, 'B2' : 4,
			 'C' : 4, 'C1' : 4, 'C2' : 5}

# Dictionary mapping from MKS channel connection to relay number.
			   
mksRelays = {'A'  : [1,2,3,4],    'A1' : [1,2],  'A2' : [3,4],
			 'B'  : [5,6,7,8],    'B1' : [5,6],  'B2' : [7,8],
			 'C'  : [9,10,11,12], 'C1' : [9,10], 'C2' : [11,12]}

# Dictionary mapping Gamma Vacuum IPC connection to channel.

gammaChan  = { '1' : 1 , '2' : 1, '3' : 2, '4' : 2}

# Dictionary mapping Gamma Vacuum IPC channel to relay number.

gammaRelays = {'1' : [1,2,3,4], '2' : [1,2,3,4],
	           '3' : [5,6,7,8], '4' : [5,6,7,8]}

chanDict =  {'mksvgc'    : mksChan,
			 'gammaipc'  : gammaChan}
			
relayDict = {'mksvgc'    : mksRelays,
	         'gammaipc'  : gammaRelays}

def render(template, ofile, dictionary):
	"""Render the dictionary from a template file and write output.
	
	
	
	"""
	renderer = pystache.Renderer()
	templateFile = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates/{0}'.format(template))
	data = renderer.render_path(templateFile, dictionary)
	f = open(ofile, 'w')
	f.write(data)
	f.close()
	
def makeArchiverDict(sys, rows, name, signals):
	"""Make dictionary to add to archiver"""
	pvs = list()
	for row in rows:
		if row[2]:
			for signal in signals:
				pv = dict(pv=sys + '{' + row[2] + '}' + signal)
				pvs.append(pv)
			
	return [dict(name = name, channels = pvs)]

def makeSimpleDictionary(sys,rows, ports, source = False, unique = False):
	"""Make Dictionary from all devices in list"""

	devices = list()	
	deviceList = list()
	for row in rows:
		if source:
			d = row[1].split('-')[0]
		else:
			d = row[2]
			
		if d:
			d = '{' + d + '}'
			if not (unique and (d in deviceList)):
				dev = dict()
				dev['sys']  = sys
				dev['dev']  = d
				dev['port'] = ports['{' + row[1].split('-')[0] + '}']
				devices.append(dev)
				deviceList.append(d)
	return devices

def makeVacuumDictionary(vtype, sys,rows,ports):
	"""Make Dictionary for substitution file"""
	gauges = list()
	relays = list()
	for row in rows:
		# Each row is a CC Gauge
		# First do the actual Gauge
		
		if (row[1] is not '') and (row[2] is not ''):
			gauge = dict()
			gauge['sys'] = sys
			gauge['dev'] = '{' + row[2] + '}'
			gauge['chan'] = chanDict[vtype][row[1].split('-')[1]]
			gauge['cntl'] = '{' + row[1].split('-')[0] + '}'
			gauge['port'] = ports[gauge['cntl']]
			gauges.append(gauge)
			
			# Now set the relay
			for spnum in relayDict[vtype][row[1].split('-')[1]]:
				relay = gauge.copy()
				relay['spnum'] = spnum
				relays.append(relay)
			
	return gauges, relays
	
