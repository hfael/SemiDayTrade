import os
import subprocess
import time
import tracemalloc
import asyncio
from messageEvent import sendMessage

tracemalloc.start()

# Répertoire contenant les fichiers .py à exécuter
directory = "enter directory here"

# Liste de tous les fichiers .py dans le répertoire (en excluant "RUNNING.py" et "modifier.py")
python_files = [f for f in os.listdir(directory) if f.endswith(".py") and f not in ["modifier.py", "RUNNING.py", "messageEvent.py", "OrderUtils.py", "SemiDayTrade.py"]]

# Boucle à travers la liste des fichiers .py et les exécute dans des sessions screen

asyncio.run(sendMessage(f"----------------------------------"))
for file in python_files:
    file_path = os.path.join(directory, file)
    screen_session_name = file.split(".py")[0]
    command = f"screen -dmS {screen_session_name} python {file_path}"
    print(f"{file_path} ouvert")
    subprocess.Popen(command, shell=True)
    time.sleep(0.5)

time.sleep(1)

command = "screen -dmS SemiDayTrade python /home/ubuntu/SemiDayTrade/SemiDayTrade.py"
print(f"/home/ubuntu/SemiDayTrade/SemiDayTrade.py ouvert END")
subprocess.Popen(command, shell=True)
time.sleep(1)

# Optionnel : Affiche la liste des sessions screen créées
subprocess.Popen("screen -list", shell=True)

time.sleep(1)

command = "screen -r SemiDayTrade"
subprocess.Popen(command, shell=True)
