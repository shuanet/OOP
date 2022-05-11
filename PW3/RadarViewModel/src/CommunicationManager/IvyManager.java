/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package CommunicationManager;

import fr.dgac.ivy.Ivy;
import fr.dgac.ivy.IvyClient;
import fr.dgac.ivy.IvyException;
import fr.dgac.ivy.IvyMessageListener;
import fr.enac.sita.visuradar.model.SelfTraffic;
import java.util.Arrays;
import javafx.application.Platform;

/**
 *
 * @author Shuan
 */
public class IvyManager {
    private final Ivy ivyBus;
    
    public IvyManager(SelfTraffic SF) throws IvyException{
        // initialize (set up the bus, name and ready message)
        ivyBus = new Ivy("Ivy Bus Manager", "Ivy Bus Manager - Ready", null);
        
        // BIND TO PARAMS
        ivyBus.bindMsg("TrackMovedEvent Flight=(.*) CallSign=(.*) Ssr=(.*) Sector=-- Layers=I X=(.*) Y=(.*) Vx=(.*) Vy=(.*) Afl=(.*) Rate=(.*) Heading=(.*) GroundSpeed=(.*) Tendency=(.*) Time=(.*)", new IvyMessageListener() {
            @Override
            public void receive(IvyClient client, String[] params) {
                if (params[0].equals(SF.getFlightNum()) || params[1].equals(SF.getCallSign())) {
                    
                    Platform.runLater(new Runnable() {
                        @Override
                        public void run() {
                            SF.setX(Double.parseDouble(params[3]));
                            SF.setY(Double.parseDouble(params[4]));
                            SF.updateParams(params[2], params[5], params[6], params[7], params[8], params[9], params[10], params[11], params[12]);
                        }
                    });
                    System.out.println(SF.toString());
                }
            }
        });
        
        // start the bus on the default domain
        ivyBus.start(null);
        //bus.start("10.0.0.255:1234");
    }
}
