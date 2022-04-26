/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package test;

import fr.enac.sita.visuradar.model.Airspace;
import fr.enac.sita.visuradar.data.cartoxanthane.CartographyManagerXanthane;

/**
 *
 * @author Shuan
 */
public class Main {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        CartographyManagerXanthane cartography = new CartographyManagerXanthane();
        Airspace myAirspace = new Airspace(cartography);
        //System.out.println(myAirspace.getBeacons());
        
        System.out.println(myAirspace.containsBeacon("ADATU"));
    }
    
}
