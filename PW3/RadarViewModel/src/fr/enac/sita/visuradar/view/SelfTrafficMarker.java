/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.SelfTraffic;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;

/**
 *
 * @author Shuan
 */
public class SelfTrafficMarker {
    private Circle marker;

    public SelfTrafficMarker(SelfTraffic ST) {
        this.marker = new Circle(ST.getX(), ST.getY(), 5);
        ST.xProperty().addListener(new ChangeListener(){
            @Override
            public void changed(ObservableValue observable, Object oldValue, Object newValue) {
                marker.setCenterX(ST.getX());
                marker.setCenterY(ST.getY());
            }
            
        });
        this.marker.setFill(Color.YELLOW);
    }

    public Circle getMarker() {
        return marker;
    }
}
