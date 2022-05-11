/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.data.cartoxanthane.CartographyManagerXanthane;
import fr.enac.sita.visuradar.manager.dragManager;
import fr.enac.sita.visuradar.manager.panManager;
import fr.enac.sita.visuradar.manager.zoomManager;
import fr.enac.sita.visuradar.model.Airspace;
import fr.enac.sita.visuradar.model.IBaseMap;
import fr.enac.sita.visuradar.model.IBeacon;
import fr.enac.sita.visuradar.model.SelfTrafficMarker;
import java.util.Map;
import javafx.scene.layout.Pane;

/**
 *
 * @author Shuan
 */
public class RadarView extends Pane{
    public RadarView(){
        CartographyManagerXanthane cartography = new CartographyManagerXanthane();
        Airspace myAirspace = new Airspace(cartography);

        Map<String, IBeacon> beacons = myAirspace.getBeaconsByNameMap();
        IBaseMap baseMap = cartography.loadBaseMap();
        BaseMapView BMV = new BaseMapView(baseMap);
        BeaconView BV = null;
        this.getChildren().add(BMV);

        for(IBeacon beacon: beacons.values()){
            BV = new BeaconView(beacon);
            BMV.getChildren().add(BV);
        }
        SelfTrafficMarker aircraft = new SelfTrafficMarker(0, 0);
        BMV.getChildren().add(aircraft.getMarker()); //discuss layers
        
        panManager pM = new panManager(BMV);
        dragManager dM = new dragManager(BMV);
        zoomManager zM = new zoomManager(BMV);

        BMV.setLayoutX(this.getLayoutX()/2); BMV.setLayoutY(this.getLayoutY()/2);
        BV.setLayoutX(this.getLayoutX()/2); BV.setLayoutY(this.getLayoutY()/2);
    }
}
