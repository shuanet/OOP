package pw4_ivyrejeu;

import pw4_ivyrejeu.communication.Ex3Question3_CommunicationManager;
import fr.dgac.ivy.IvyException;

public class Ex3Question3_IvyRejeuApplication {

    public static void main(String[] args) {
        
        // Launch communications with Rejeu and do nothing else in the main
        Ex3Question3_CommunicationManager communicationManager;
        try {
            communicationManager = new Ex3Question3_CommunicationManager();
        } catch (IvyException e) {
            // Print an explicit message in case of IvyException
            throw new RuntimeException("Ivy bus had a failure. Quitting Ex3Question3_IvyRejeuApplication...");
        }
        
    }
    
}
