/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.IBeacon;
import java.util.Map;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;

/**
 *
 * @author Shuan
 */
public class BeaconView extends Pane{

    public BeaconView(Map<String, IBeacon> beacons){
        //Polygon myBeacon = new Polygon();
        
        for(String key: beacons.keySet()){
            //myBeacon.getPoints().addAll(center.getX(), center.getY());
            //this.getChildren().add(myBeacon);
            
            Text name = new Text(beacons.get(key).getX(), beacons.get(key).getY(), key);
            name.setFill(Color.BLUE);
            this.getChildren().add(name);
        }
    }
}
