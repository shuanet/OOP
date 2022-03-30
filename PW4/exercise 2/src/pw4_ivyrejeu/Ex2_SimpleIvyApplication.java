package pw4_ivyrejeu;

import fr.dgac.ivy.Ivy;
import fr.dgac.ivy.IvyClient;
import fr.dgac.ivy.IvyException;
import fr.dgac.ivy.IvyMessageListener;

class Ex2_SimpleIvyApplication {

    private Ivy bus;

    public Ex2_SimpleIvyApplication() throws IvyException {
        // initialize (set up the bus, name and ready message)
        bus = new Ivy("Ex2_SimpleIvyApplication", "Ex2_SimpleIvyApplication Ready", null);

        // subscribe to "Bye" messages
        bus.bindMsg("^Bye$", new IvyMessageListener() {
            // callback
            @Override
            public void receive(IvyClient client, String[] strings) {
                System.out.println("IvyTest is disconnecting...");
                // leave the bus, and as it is the only thread, quit the app
                bus.stop();
            }
        });
        
        // start the bus on the default domain
        bus.start(null);
        //bus.start("10.0.0.255:1234");
    }

    public static void main(String args[]) {
        try {
            new Ex2_SimpleIvyApplication();
        } catch (IvyException ex) {
            // Print an explicit message in case of IvyException
            throw new RuntimeException("Ivy bus had a failure. Quitting Ex2_SimpleIvyApplication...");
        }
    }
}
