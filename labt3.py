# Lab 3



#cd ~/lab && docker compose up -d && bash scripts/check_lab.sh # attendu : 17 OK, 0 KO
#cd ~/aforp-python
#ls data/inventory.yaml # présent depuis le lab 2.3 ; sinon :
#cp ~/lab/data/inventory.yaml data/
# Copier lab3.py à la racine du projet, à côté du dossier data/.


# Vérifiez vos fonctions à tout moment, même sans le labo Docker, avec les exemples des docstrings :
# python -m doctest lab3.py
# aucun affichage = tous les exemples passent

# Lab 3.1 - TODO 1 a 3 


import shutil
import subprocess

OUTILS = {
"python3": ["python3", "--version"],
"git": ["git", "--version"],
"docker": ["docker", "--version"],
"kubectl": ["kubectl", "version", "--client"],
"terraform": ["terraform", "version"],
}


def exec(cmd: list[str], timeout: float=5) -> tuple[int, str]:
	try:
		result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
	except FileNotFoundError:
		return 127, "absent"
	except subprocess.TimeOutExpired:
		return 125, f"Pas de réponse en {timeout} s"
	output = (result.stdout or result.stderr).strip()
	return result.returncode, output.splitlines()[0] if output else ""

if __name__ == "__main__":
	for name, cmd in OUTILS.items():
		code, text = exec(cmd)
		print (f"{name:<10} code={code:<4} {text:<45} {shutil.which(cmd[0]) or '-'}")
