/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package pw4_ivyrejeu.communication;

import fr.dgac.ivy.Ivy;
import fr.dgac.ivy.IvyClient;
import fr.dgac.ivy.IvyException;
import fr.dgac.ivy.IvyMessageListener;

/**
 *
 * @author joan
 */
public class Ex3Question3_CommunicationManager {

    private Ivy bus;

    public Ex3Question3_CommunicationManager() throws IvyException{
        // initialize (set up the bus, name and ready message)
        bus = new Ivy("Ex3_Question3CommunicationManager", "Ex3_Question3CommunicationManager Ready", null);
        bus.bindMsg("(.*)", new IvyMessageListener() {
            @Override
            public void receive(IvyClient client, String[] strings) {
                System.out.println(strings[0]);
            }
        });
        // start the bus on the default domain
        bus.start(null);
        //bus.start("10.0.0.255:1234");
    }
}