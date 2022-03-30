/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package pw4_ivyrejeu.communication;

import fr.dgac.ivy.Ivy;
import fr.dgac.ivy.IvyClient;
import fr.dgac.ivy.IvyException;
import fr.dgac.ivy.IvyMessageListener;
import javafx.scene.control.TextArea;
import javafx.application.Platform;

/**
 *
 * @author joan
 */
public class Ex3Question4_CommunicationManager {

    private Ivy bus;

    public Ex3Question4_CommunicationManager(TextArea textArea) throws IvyException {
        // initialize (set up the bus, name and ready message)
        bus = new Ivy("Ex3_Question4_CommunicationManager", "Ex3_Question4_CommunicationManager Ready", null);
        bus.bindMsg("(.*)", new IvyMessageListener() {
            @Override
            public void receive(IvyClient client, String[] strings) {
                Platform.runLater(new Runnable() {
                    @Override
                    public void run() {
                        textArea.appendText(strings[0] + "\n");
                    }
                });
            }
        });
    }

}