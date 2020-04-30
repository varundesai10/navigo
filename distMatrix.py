import openrouteservice as nav
import requests
import sys
import pandas as pd
import json

def giveDistMatrix(coords, demands, key='5b3ce3597851110001cf62480bea960faed84e018b953afbd3510ae7', dry_run = False, verbose=True):
	client = nav.Client(key=key)
	distanceMatrix = nav.distance_matrix.distance_matrix(client, locations=coords, profile='driving-car', sources = None, destinations = None, metrics = ['distance', 'duration'], resolve_locations = True, units = 'm', optimized = True, validate = True, dry_run = dry_run)
	if(verbose):
		print(distanceMatrix)
	temp = {'distances':distanceMatrix['distances'], 'durations':distanceMatrix['durations'], 'coords':coords, 'demands':demands}
	return temp
#INPUT FORMAT: 1:input file name
#				2: output file name
#				3: whether to dry ryn or not
#				4(optional): key
def giveCoordsDemands(filename):
	file1 = open(filename)
	lines = file1.readlines()
	coords = []
	demands = []
	if(filename.split('.')[-1] == 'txt'):
		for line in lines:
			STRINGS = line.split(' ')
			strings = STRINGS[0].split(',')
			if(len(STRINGS) > 1):
				demand = STRINGS[1]
				if(demand != None):
					demands.append(int(demand.strip()))
			x, y = float(strings[0].strip()), float(strings[1].strip())
			coords.append((x, y))
	return coords, demands

def giveData(filename, key = '5b3ce3597851110001cf62480bea960faed84e018b953afbd3510ae7', dry_run=False, verbose = True):
 	coords, demands = giveCoordsDemands(filename)
 	return giveDistMatrix(coords, demands, key, dry_run, verbose)

def main():


	key = '5b3ce3597851110001cf62480bea960faed84e018b953afbd3510ae7'
	if(len(sys.argv) >= 5):
		key = sys.argv[4]
	dry_run = False
	export_name = sys.argv[2].split('.')[0]
	file_name = sys.argv[1]
	file1 = open(sys.argv[1])
	lines = file1.readlines()
	coords = []
	demands = []
	if(file_name.split('.')[-1] == 'txt'):
		for line in lines:
			STRINGS = line.split(' ')
			strings = STRINGS[0].split(',')
			if(len(STRINGS) > 1):
				demand = STRINGS[1]
				if(demand != None):
					demands.append(int(demand.strip()))
			x, y = float(strings[0].strip()), float(strings[1].strip())
			coords.append((x, y))
	elif(file_name.split('.')[-1] == 'csv'):
		data = pd.read_csv(file_name).to_dict()
		lats = data['lat']
		lngs = data['lng']
		demands = data['demands']
		for i in range(len(lats)):
			coords.append((int(lats[i]), int(lngs[i])))
	elif(file_name.split('.')[-1] == 'json'):
		data = pd.read_json(file_name).to_dict()
		lats = data['lat']
		lngs = data['lng']
		demands = data['demands']
		for i in range(len(lats)):
			coords.append((int(lats[i]), int(lngs[i])))

	if (sys.argv[3] == 'y'):
		dry_run = False
	else:
		dry_run = True

	client = nav.Client(key=key)
	distanceMatrix = nav.distance_matrix.distance_matrix(client, locations=coords, profile='driving-car', sources = None, destinations = None, metrics = ['distance', 'duration'], resolve_locations = True, units = 'm', optimized = True, validate = True, dry_run = dry_run)
	print(distanceMatrix)

	temp = {'distances':distanceMatrix['distances'], 'durations':distanceMatrix['durations'], 'coords':coords, 'demands':demands}
	with open('{}.json'.format(export_name), 'w') as fp:
		json.dump(temp, fp)

if __name__ == '__main__':
	main()

