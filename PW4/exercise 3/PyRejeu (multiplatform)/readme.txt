-----------------
- Using PyRejeu -
-----------------

PyRejeu is a multiplatform application written in python whose the aim is to replay Air Traffic.

Installation:
To run PyRejeu, you will need python3 (version >= 3.4.0), and will have to install the following python packages with pip (Python Packages Installer), thanks to the command "pip3 install package_name", with package_name=...
- numpy
- SQLAlchemy
- ivy-python 

Documentation:
The documentation is available in the folder *docs/html*

Launch:
- launch the command prompt (Windows) or a terminal (Linux or Mac),
- from the command prompt go to the folder containing PyRejeu: cd "path_to_PyRejeu"
- launch PyRejeu: python3 pyrejeu.py data/traffic_small.txt -s auto -b ivy://224.255.255.255:2010
- All the other clients must be connected to the bus on the same domain.
  The default domain is the computer's loopback IP on port 2010 (127.255.255.255:2010).
  Another domain can be chosen by adding -b option, for ex: -b 10.1.4.2:1234
  Choose this option when clients run on different computers on the same network.