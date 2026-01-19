# IU_Dashboard

Dieses Dashboard ermöglicht die eigenen Studienziele im Blick zu behalten. Es visualisiert den zeitlichen Studienverlauf und zeigt, ob die Wunsch-Abschlussnote eingehalten wird.

Dieses Programm ist im Rahmen des Studiums *Angewandte Künstliche Intelligenz* an der IU Internationalen Hochschule entstanden. 
Es wurde im *Projekt: Objektorientierte und funktionale Programmierung mit Python* von Florian Erik Janssens entworfen und programmiert. Das *Dashboard*-Programm dient ausschließlich Lernzwecken.

GitHub-Repository: https://github.com/printhellogithub/IU_Dashboard

## Installation:

### Voraussetzung
Es muss Python 3.11 oder höher installiert sein. 
Das Programm wurde mit Python ≥ 3.11 getestet und mit einer aktuellen Python-3.13-Vorabversion entwickelt.

Alle folgenden Befehle beziehen sich auf die Windows Eingabeaufforderung (CMD.exe).

Um auf Windows Python 3.13 zu installieren, geben Sie in der Windows Eingabeaufforderung den Befehl `winget install Python.Python.3.13` ein und drücken Enter. Eventuell müssen Sie mit `Y` die Bedingungen der Vereinbarungen bestätigen. Python wird installiert. Nach erfolgreicher Installation können Sie CMD schließen.

### Installation des Dashboards
1️ **GitHub-Repo klonen oder herunterladen**
Um das Programm herunterzuladen, laden Sie die ZIP-Datei des Repos vom [GitHub Repo](https://github.com/printhellogithub/IU_Dashboard), die bei dem grünen Code-Button bereitgestellt wird. Entpacken Sie die ZIP-Datei.
Falls git installiert sein sollte, können Sie das GitHub-Repo mit 
`git clone https://github.com/printhellogithub/IU_Dashboard` klonen. 

2️ **Projektordner in CMD öffnen**
Öffnen Sie den entpackten Projektordner `IU_Dashboard-main` im Explorer. Dort können Sie Verzeichnisse wie `assets` und `data` sehen.
Geben Sie `cmd` in die Adresszeile ein und drücken Enter.
Der Ordner wird in CMD geöffnet.
Sie sollten bei dem Befehl `dir` jetzt Verzeichnisse wie `assets` und `data` sehen können.

3️ **Virtuelle Umgebung einrichten und aktivieren**
Jetzt können Sie die Virtuelle Umgebung einrichten. 
Geben Sie den Befehl `py -m venv .venv` ein. 
Um die Umgebung zu aktivieren, geben Sie `.venv\Scripts\activate.bat` ein. Nach erfolgreicher Aktivierung steht `(.venv)` vor dem Pfad. 

4️ **Abhängigkeiten installieren**
Um erforderliche Pakete zu installieren, geben Sie 
`py -m pip install -r requirements.txt` ein.

### Das Dashboard starten
Nach Erfolgreicher Installation lässt sich das Dashboard mit dem Befehl `py -m src.app` starten.

**Startoptionen**
Das Dashboard lässt sich in verschiedenen Modi starten, diese lassen sich auch kombinieren (z.B. `py -m src.app --follow_system_mode --offline`):

*Offline-Modus*
Das Programm macht im Rahmen der Email-Validierung DNS-Abfragen. Hierfür wird eine Internetverbindung benötigt.
Um auch ohne Internetverbindung das Programm nutzen zu können, starten Sie das Programm mit dem Zusatzargument `--offline`.

*Light-/Dark-Mode*
Wenn dieser Modus aktiv ist, wird der aktuelle System-Modus übernommen. Starten Sie das Programm mit dem Zusatzargument `--follow_system_mode`. (Beta: Darkmode nicht 100% getestet.)

*Debug-Modus*
Aktiviert für das Logging das DEBUG-Level. Starten Sie das Programm mit dem Zusatzargument `--debug`.

*Log-to-Console-Modus*
Aktiviert Log-Anzeige in der Konsole. Starten Sie das Programm mit dem Zusatzargument `--log_to_console`.
