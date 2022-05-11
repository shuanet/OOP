--------------------------
- Using rejeu on Windows -
--------------------------


Installation:
Double clic the provided Rejeu.msi installer.
This will install Rejeu and its dependencies in "C:\Program Files (x86)\Rejeu"

Launch:
- launch the command prompt,
- from the command prompt go to the folder containing the traffic file: cd "path_to_traffic_folder"
- launch Rejeu: "C:\Program Files (x86)\Rejeu\Rejeu.exe" traffic_small.txt -s auto
- All the other clients must be connected to the bus on the same domain.
  The default domain is the computer's loopback IP on port 2010 (127.255.255.255:2010).
  Another domain can be chosen by adding -b option, for ex: -b 10.1.4.2:1234
  Choose this option when clients run on different computers on the same network.