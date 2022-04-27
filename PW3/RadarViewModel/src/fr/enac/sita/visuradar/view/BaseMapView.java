/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.IBaseMap;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Polygon;
/**
 *
 * @author Shuan
 */
public final class BaseMapView extends Pane{
    
    public BaseMapView(IBaseMap baseMap) {        
        
        for(int i = 0; i < baseMap.getZones().size(); i++){
            Polygon myPolygon = new Polygon();
            
            myPolygon.getPoints().addAll(baseMap.getZones().get(i).getVertexesXYArray());
            
            myPolygon.setFill(Color.GREY);
            this.getChildren().add(myPolygon);
        }
    }
}
