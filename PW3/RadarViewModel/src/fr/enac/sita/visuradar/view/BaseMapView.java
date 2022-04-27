/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.IBaseMap;
import java.util.*;
import javafx.scene.layout.Pane;
import javafx.scene.shape.Polygon;
import javafx.scene.transform.Affine;

/**
 *
 * @author Shuan
 */
public class BaseMapView extends Pane{
    // All the transformations are to be accumulated in a single matrix
    private final Affine transforms;
    
    public BaseMapView(IBaseMap baseMap) {        
        // Initialize the transformation matrix
        transforms = new Affine();
        
        for(int i = 0; i < baseMap.getZones().size(); i++){
            Polygon myPolygon = new Polygon();
            
            myPolygon.getPoints().addAll(baseMap.getZones().get(i).getVertexesXYArray());
            this.translate(USE_PREF_SIZE/2, USE_PREF_SIZE/2);
            this.getChildren().add(myPolygon);
        }
    }
   
    public void translate(double dx, double dy) {
        try{
            transforms.appendTranslation(dx, dy);
        }
        catch(Exception e){
            throw new UnsupportedOperationException("Not supported yet.");
        }
    }
}
