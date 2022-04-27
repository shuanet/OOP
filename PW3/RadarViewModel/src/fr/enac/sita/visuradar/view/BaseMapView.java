/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.controls.IHomothetic;
import fr.enac.sita.visuradar.controls.ITranslatable;
import fr.enac.sita.visuradar.model.IBaseMap;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.SimpleDoubleProperty;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Polygon;
import javafx.scene.transform.Affine;
/**
 *
 * @author Shuan
 */
public class BaseMapView extends Pane implements ITranslatable, IHomothetic{
    // Model for the zoom factor (in order to manage the differentiated zoom)
    // (to update when there is a scale change)
    private final DoubleProperty scale = new SimpleDoubleProperty(1.0);
    
    // All the transformations are to be accumulated in a single matrix
    private final Affine transforms;
    
    public BaseMapView(IBaseMap baseMap) {        
        // Initialize the transformation matrix
        transforms = new Affine();
        getTransforms().add(transforms);
        
        for(int i = 0; i < baseMap.getZones().size(); i++){
            Polygon myPolygon = new Polygon();
            
            myPolygon.getPoints().addAll(baseMap.getZones().get(i).getVertexesXYArray());
            
            myPolygon.setFill(Color.GREY);
            this.getChildren().add(myPolygon);
        }
    }
    
    @Override
    public final double getScale() {
        return scale.get();
    }
    
    @Override
    public void setScale(double newScale) {
        throw new UnsupportedOperationException("Not supported yet.");
    }
    
    @Override
    public void setScale(double newScale, double pivotX, double pivotY) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public void appendScale(double deltaScale) {
        try{
            transforms.appendScale(this.getScale()*scale.get(), this.getScale()*scale.get());
        }
        catch(Exception e){
            throw new UnsupportedOperationException("Not supported yet.");
        }
    }

    @Override
    public void appendScale(double deltaScale, double pivotX, double pivotY) {
        try{
            //transforms.appendScale(this.getScale()*scale.get(), this.getScale()*scale.get());
        }
        catch(Exception e){
            throw new UnsupportedOperationException("Not supported yet.");

        }
    }

    @Override
    public void translate(double dx, double dy) {
        try{
            transforms.appendTranslation(dx, dy);
        }
        catch(Exception e){
            throw new UnsupportedOperationException("Not supported yet.");
        }
    }
}