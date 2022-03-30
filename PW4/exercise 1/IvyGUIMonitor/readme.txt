-----------------------
- Using IvyGUIMonitor -
-----------------------

IvyGUIMonitor is a Java Graphical User Interface to monitor the messages sent on Ivy bus.

Installation:
If Java 8 is installed on your computer there is nothing more to do.

Launch from the desktop:
Double clic on IvyGUIMonitor icon

Launch from a command prompt or a .bat file:
- command line: java -jar IvyGUIMonitor.jar
- All the other clients must be connected to the bus on the same domain.
  The default domain is the computer's loopback IP on port 2010 (127.255.255.255:2010).
  
  Loopback IP is managed entirely by and within the operating system, without the use of a network.
  It enables the Server and Client processes on a single system to communicate with each other.
  Another domain can be chosen by adding -b option, for ex: -b 10.1.4.2:1234
  Choose this option when clients run on different computers on the same network.
  
  Note for Mac owners:
  The Ivy's default domain doesn't work on Mac.
  It is therefore necessary to connect to a wired network and use the broadcast address of this network. This address depends on the network but a shortcut allows to obtain it in a generic way: the option -b 224.255.255.255:2010 allows you to connect directly to the right domain without having to identify it first.
  You must therefore connect all Ivy clients with this option.
