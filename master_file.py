import os
import sys
'''
final file which merges all files!
input format:
1 -> input file which takes in data of all consumers
2 -> input file which takes in data of all agents
3 -> output file name in html
'''
agent_data_file = sys.argv[2]
consumer_data_file = sys.argv[1]
output_file_name = sys.argv[3]

#first, converting agent txt file into json file
print("running agent file converter")
os.system('python3 convert_agent_data.py {} agentdata.json'.format(agent_data_file))

#now calling distMatrix.py
print("running distance matrix")
os.system('python3 distMatrix.py {} distances.json y'.format(consumer_data_file))

#now calling optimize.py
print("running optimize.py")
os.system('python3 optimize.py distances.json agentdata.json finalroutes.json 1000')

#now calling plotroutes.py
print("running plotroutes.py")
os.system('python3 plotroutes.py finalroutes.json distances.json agentdata.json {}.hmtl'.format(output_file_name))