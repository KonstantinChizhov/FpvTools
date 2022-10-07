import math
import xml.etree.cElementTree as ET
import sys
import os
import glob

def ReadLog(logPath):
	skip = 10
	firstLine = True
	header = {}
	telemetry = []
	with open(logPath, "r") as logfile:
		for line in logfile:
			if firstLine:
				for i, paramName in enumerate(line.split(",")):
					header[paramName] = i
				firstLine = False
			if not line[0].isdigit():
				continue
			value = [a for a in line.split(",")]
			telemetry.append(value)
	return telemetry, header
	
def ConvertTelemetryToTrackData(logPath):
	print('Converting file: ' + logPath)
	telemetry, header = ReadLog(logPath)

	root = ET.Element("gpx", attrib={'version': '1.0'})

	ET.SubElement(root, "name").text = os.path.basename(logPath)
	ET.SubElement(root, "desc").text = "from OpenTX telemetry log"

	track = ET.SubElement(root, "trk")
	ET.SubElement(track, "name").text  = "flight track"
	trkseg = ET.SubElement(track, "trkseg")
	if 'GPS' not in header:
		print ('No GPS data in ' + logPath)
		return
	gpsIndex = header['GPS']
	altIndex = header['Alt(m)']
	dateIndex = header['Date']
	timeIndex = header['Time']

	for pt in telemetry:
		strGps = pt[gpsIndex].split(" ")
		lat = strGps[0]
		lon = strGps[1]
		date = pt[dateIndex]
		time = pt[timeIndex]
		trkpt = ET.SubElement(trkseg, "trkpt", attrib={'lat':lat, 'lon':lon})
		ET.SubElement(trkpt, 'ele').text  = pt[altIndex]
		ET.SubElement(trkpt, 'time').text  = f"{date}T{time}Z"

	tree = ET.ElementTree(root)
	pre, ext = os.path.splitext(logPath)
	tree.write(pre + '.gpx')
	
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('Parameters expected: <opentx telemetry log file> [...]')
		exit
	
	for arg in sys.argv[1:]:
		if '*' in arg:
			files = glob.glob(arg)
			for file in files:
				ConvertTelemetryToTrackData(file)
		else:
			ConvertTelemetryToTrackData(arg)
	print('Done')


