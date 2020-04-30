import json
import sys

def giveAgentData(filename):
	file1 = open(filename)

	agent_data = {'id':[], 'capacities':[]}

	lines = file1.readlines()

	for line in lines:
		ID, cap = line.split(' ')
		agent_data['id'].append(ID)
		agent_data['capacities'].append(int(cap))
	return agent_data

def main():
	file1 = open(sys.argv[1])
	export_name = sys.argv[2].split('.')[0]

	agent_data = {'id':[], 'capacities':[]}

	lines = file1.readlines()

	for line in lines:
		ID, cap = line.split(' ')
		agent_data['id'].append(ID)
		agent_data['capacities'].append(int(cap))

	with open('{}.json'.format(export_name), 'w') as fp:
		json.dump(agent_data, fp)

if __name__ == '__main__':
	main()

