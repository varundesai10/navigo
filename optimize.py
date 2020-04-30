import pandas as pd
import json
from docplex.mp.model import Model
import numpy as np
import sys

#sys.argv[1] -> input_file_name_clients, sys.argv[2] -> input file name for agents sys.argv[3] -> export file name sys.argv[4] -> solving time limit (default 100s)



#data = pd.read_json(sys.argv[1]).to_dict()
#agent_data = pd.read_json(sys.argv[2].to_dict())



def giveOptimizedRoutes(data, agent_data, time_limit):
	distanceMatrix = data['distances']
	print('inside function giveOptimizedRoutes now... printing distmatr:')
	print(distanceMatrix)
	#importing the set of customers with their demands
	n = len(distanceMatrix)-1 #total_number_of_clients
	N = [i for i in range(1, len(distanceMatrix))] #set of all customers
	V = [0]+N  #set of all customers+depot
	q = {i:data['demands'][i-1] for i in N} #set of demand of all customers.
	c = {(i,j):distanceMatrix[i][j] for i in V for j in V if i!=j}
	total_demand = sum(q[i] for i in N)

	#inporting the set of all deliviry agents
	m = len(agent_data['id'])
	K = [i for i in range(1, m+1)]
	C = {i:agent_data['capacities'][i-1] for i in K}
	total_capacity = sum(C[i] for i in K)

	if(total_capacity < total_demand): #no solutoin exists
		print('Capacity is greater than demand. Cannot solve.')
		return None, None, total_capacity, total_demand

	#now, solution must exist!

	E = [(i,j,k) for i in V for j in V for k in K if i!=j]

	#building optimization model
	mdl = Model('CVRP')
	mdl.clear()
	x = mdl.binary_var_dict(E, name='x')
	Q = mdl.continuous_var_dict([(i,k) for i in N for k in K], name='Q')
	y = mdl.binary_var_dict([(i,k) for i in N for k in K], name='y')

	mdl.minimize(mdl.sum(c[i,j]*x[i,j,k] for i,j,k in E))
	#for indicator contraints
	mdl.add_constraints(mdl.sum(x[i,j,k] for j in V if j != i) == y[i,k] for i in N for k in K)
	#flow_constraints
	mdl.add_constraints(mdl.sum(x[i,j,k] for j in V for k in K if i!=j) == 1 for i in N)
	mdl.add_constraints(mdl.sum(x[i,j,k] for i in V for k in K if i!=j) == 1 for j in N)
	mdl.add_constraints((mdl.sum(x[i, h, k] for i in V if i!=h) - mdl.sum(x[h, j, k] for j in V if j!=h)) == 0 for h in N for k in K)
	mdl.add_constraints(mdl.sum(x[0,j,k] for j in N)==1 for k in K)
	mdl.add_constraints(mdl.sum(x[i,0,k] for i in N)==1 for k in K)
	#capacity_contraints
	'''
	mdl.add_indicator_constraints(mdl.indicator_constraint(x[i,j,k], u[i,k]+q[i] == u[j,k]) for i,j,k in E if i!=0 and j!=0)
	mdl.add_constraints(u[i,k]>=q[i] for i in N for k in K)
	mdl.add_constraints(u[i,k]<=Q[k] for i in N for k in K)
	'''
	mdl.add_indicator_constraints(mdl.indicator_constraint(y[i,k],Q[i,k]>=q[i]) for i in N for k in K)
	mdl.add_indicator_constraints(mdl.indicator_constraint(y[i,k], Q[i,k]-q[i] <= C[k]) for i in N for k in K)

	#definitional constraints
	mdl.add_indicator_constraints(mdl.indicator_constraint(x[i,j,k], Q[j,k] == Q[i,k]-q[i]) for i in N for j in N for k in K if i!=j)
	mdl.add_indicator_constraints(mdl.indicator_constraint(x[0,j,k], Q[j,k] == C[k]) for j in N for k in K)

	mdl.parameters.timelimit = time_limit

	solution = mdl.solve(log_output = True)
	if solution == None:
		return None, None, total_capacity, total_demand

	#now making different graphs out of the solution set.
	active_arcs = [(i,j,k) for (i,j,k) in E if x[i,j,k].solution_value > 0.9]
	routes = {k:[0] for k in K}
	for k in K:
		i = 0
		while(True):
			for j in V:
				if (i,j,k) in active_arcs:
					routes[k].append(j)
					i = j
					break
			if (i==0):
				break
	#should clean here only.
	print('here are the initial routes: ')
	print(routes)
	#now replacing the indexed locations by the actual locations!
	final_routes = {}
	final_routes['routes'] = [[data['coords'][i] for i in routes[k]] for k in K]
	final_routes['id'] = agent_data['id']
	return final_routes, solution, total_capacity, total_demand

def pleaseOptimize(data, agent_data, output_file_name = 'finalRoutes.json'):

	while(True):
		print(data)
		totally_final_routes, final_solution, C, D = giveOptimizedRoutes(data, agent_data, 100)
		if(C < D):
			print('Capacity less than demand. Cannot solve model.')
			exit()
			break;
		if(final_solution != None):
			print(final_solution)
			print(final_solution.solve_status)
			break;
		else:
			#modifying data, agent_data
			print('12345678  Trying to Split and Solve.... 12345678')
			demands = data['demands']
			distMatr = data['distances']
			coords = data['coords']
			for i in range(1, len(data['coords'])):
				coords.append(coords[i])
				if (demands[i-1]%2 == 0):
					demands.append(demands[i-1]/2)
					demands[i-1] = demands[i-1]/2
				else:
					demands.append(int(demands[i-1]/2) + 1)
					demands[i-1] = int(demands[i-1]/2)
				appended = []
			n = len(distMatr)
			X = [[0 for i in range(2*n - 1)] for j in range(2*n - 1)]
			old_x = lambda x: x if x <= n -1 else x - (n-1)
			for i in range(2*n-1):
				for j in range(2*n - 1):
					X[i][j] = distMatr[old_x(i)][old_x(j)]
			data['demands'] = demands
			data['distances'] = X
			data['coords'] = coords

	#model now solved. Removing duplicate stuff from totally_final_routes
	print(totally_final_routes)
	for j in range(len(totally_final_routes['routes'])):
		
		temp = totally_final_routes['routes'][j][0]
		length = len(totally_final_routes['routes'][j])
		i = 1
		while(i < len(totally_final_routes['routes'][j])):
			if(totally_final_routes['routes'][j][i][0] == temp[0] and totally_final_routes['routes'][j][i][1] == temp[1]):
				print('Popping!')
				totally_final_routes['routes'][j].pop(i)
			else:
				temp = totally_final_routes['routes'][j][i]
				i += 1

	print("Optimized:")
	print(totally_final_routes)
	with open('{}.json'.format(output_file_name.split('.')[0]), 'w') as fp:
		json.dump(totally_final_routes, fp)
		print('file saved')
	return totally_final_routes

def main():
	with open(sys.argv[1]) as fp:
		data  = json.load(fp)

	with open(sys.argv[2]) as fp:
		agent_data = json.load(fp)
		totally_final_routes = pleaseOptimize(data, agent_data)

if __name__ == "__main__":
	main()
'''
toBeSaved = pd.DataFrame.from_dict(final_routes)
toBeSaved.to_json(r'{}.{}'.format(sys.argv[3].split('.')[0], 'json'))
toBeSaved.to_csv(r'{}.{}'.format(sys.argv[3].split('.')[0], 'csv'))
'''
