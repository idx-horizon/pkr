from math import sin, cos, sqrt, atan2, radians

def measure(from_loc, to_loc):
	earth_radius = 6373

	lat1 = radians(from_loc[0]) 
	lon1 = radians(from_loc[1])   
	lat2 = radians(to_loc[0]) 
	lon2 = radians(to_loc[1]) 
	
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	
	a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	
	distance = round((earth_radius * c) * 5 / 8, 2)
	
	return distance
