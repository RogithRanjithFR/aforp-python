servers = [
{"name": "web01", "ip": "10.0.0.11", "role": "web", "cpu": 72, "up": True},
{"name": "web02", "ip": "10.0.0.12", "role": "web", "cpu": 95, "up": True},
{"name": "db01", "ip": "10.0.0.21", "role": "db", "cpu": 40, "up": False},
{"name": "cache01", "ip": "10.0.0.31", "role": "cache", "cpu": 15, "up": True}]


def count_by_role(servers) :
	counts = {}
	for s in servers: 
		counts[s["role"]] = counts.get(s["role"], 0) + 1
	return counts


def down_servers(servers) : 
	alldownservers = []
	for s in servers:
		if not s["up"]:
			alldownservers.append(s["name"])
	return alldownservers




def overloaded(servers, threshold) : 
	overloaded = []
	for s in servers:
		if s["cpu"] > threshold:
			overloaded.append(s["name"])
	return overloaded


def aligned (servers) : 
	sorted_servers = sorted(servers, key = lambda s: s["cpu"], reverse = True)
	for s in sorted_servers:
		print (s)



def print_table(servers: list[dict], threshold:int):
	print (f"{'NOM':<10}{'IP':<12}{'ROLE':<8}{'CPU':>5} ETAT")


print_table (servers, 90)
print (aligned(servers))
print (*sorted(servers, key = lambda s: s["cpu"], reverse = True), sep= '\n', )
print (count_by_role(servers))
print (down_servers(servers))
print (overloaded(servers, 90))
