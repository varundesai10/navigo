from convert_agent_data import giveAgentData
from distMatrix import giveData
from optimize import pleaseOptimize
from plotroutes import pleasePlotRoutes

def solveItAll(agent_data_filename, client_data_filename):
	agent_data = giveAgentData(agent_data_filename)
	client_data = giveData(client_data_filename)
	route_data = pleaseOptimize(client_data, agent_data)
	final_routes = pleasePlotRoutes(route_data, client_data, agent_data)
	return final_routes
