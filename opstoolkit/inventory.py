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




def overloaded(servers, threshold: int = 90) : 
	overloaded = []
	for s in servers:
		if s["cpu"] > threshold:
			overloaded.append(s["name"])
	return overloaded


def aligned (servers) : 
	sorted_servers = sorted(servers, key = lambda s: s["cpu"], reverse = True)
	for s in sorted_servers:
		print (s)


def print_table(servers: list[dict], threshold: int = 90):
    print(f"{'NOM':<10}{'IP':<12}{'ROLE':<8}{'CPU':>5}  ETAT")
    print("-" * 42)
    for s in sorted(servers, key=lambda s: s["cpu"], reverse=True):
        if not s["up"]:
            etat = "DOWN"
        elif s["cpu"] > threshold:
            etat = "SURCHARGE"
        else:
            etat = "OK"
        print(f"{s['name']:<10}{s['ip']:<12}{s['role']:<8}{s['cpu']:>4}%  {etat}")


print_table(servers)
print("Par rôle :", count_by_role(servers))
print("Éteints :", down_servers(servers))
print("Surchargés :", overloaded(servers))






print (f"{'NOM':<10}{'IP':<12}{'ROLE':<8}{'CPU':>5} ETAT")
print (aligned(servers))
print (*sorted(servers, key = lambda s: s["cpu"], reverse = True), sep= '\n', )
print (count_by_role(servers))
print (down_servers(servers))
print (overloaded(servers))
