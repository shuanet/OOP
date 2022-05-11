/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.model;

import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;

/**
 *
 * @author Shuan
 */
public class SelfTrafficMarker {
    private Circle marker;

    public SelfTrafficMarker(double x, double y) {
        this.marker = new Circle(x, y, 5);
        this.marker.setFill(Color.YELLOW);
    }

    public Circle getMarker() {
        return marker;
    }
}
