/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import CommunicationManager.IvyManager;
import fr.enac.sita.visuradar.data.cartoxanthane.CartographyManagerXanthane;
import fr.enac.sita.visuradar.manager.dragManager;
import fr.enac.sita.visuradar.manager.panManager;
import fr.enac.sita.visuradar.manager.zoomManager;
import fr.enac.sita.visuradar.model.Airspace;
import fr.enac.sita.visuradar.model.IBaseMap;
import fr.enac.sita.visuradar.model.IBeacon;
import fr.enac.sita.visuradar.model.SelfTraffic;
import java.util.Map;
import javafx.scene.layout.Pane;

/**
 *
 * @author Shuan
 */
public class RadarView extends Pane{
    private IvyManager IM;
    
    public RadarView(){
        CartographyManagerXanthane cartography = new CartographyManagerXanthane();
        Airspace myAirspace = new Airspace(cartography);

        Map<String, IBeacon> beacons = myAirspace.getBeaconsByNameMap();
        IBaseMap baseMap = cartography.loadBaseMap();
        BaseMapView BMV = new BaseMapView(baseMap);
        BeaconView BV = null;
        this.getChildren().add(BMV);
        
        // Ivy Bus
        SelfTraffic ST = new SelfTraffic(0, 0);
        try{
            IM = new IvyManager(ST);
        }
        catch(Exception e){
            throw new RuntimeException("Ivy bus had a failure...");
        }

        for(IBeacon beacon: beacons.values()){
            BV = new BeaconView(beacon);
            BMV.getChildren().add(BV);
        }
        SelfTrafficMarker aircraft = new SelfTrafficMarker(ST);
        BMV.getChildren().add(aircraft.getMarker()); //discuss layers
        
        panManager pM = new panManager(BMV);
        dragManager dM = new dragManager(BMV);
        zoomManager zM = new zoomManager(BMV);
    }
}
