/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.IBeacon;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Polygon;
import javafx.scene.text.Text;

/**
 *
 * @author Shuan
 */
public class BeaconView extends Pane{

    public BeaconView(IBeacon beacon){
        double vertex1X = -7;
        double vertex1Y = 0;
        double vertex2X = 7;
        double vertex2Y = vertex1Y;
        double vertex3X = 0;
        double vertex3Y = -10;
        
        Polygon triangle = new Polygon();

        triangle.setLayoutX(beacon.getX());
        triangle.setLayoutY(beacon.getY());
        triangle.getPoints().addAll(new Double[]{vertex1X, vertex1Y, vertex2X, vertex2Y, vertex3X, vertex3Y});
        triangle.setFill(Color.WHITE);

        Text name = new Text(beacon.getX() - 20, beacon.getY() + 15, beacon.getCode());
        name.setFill(Color.BLUE);
        this.getChildren().addAll(name, triangle);
    }
}
