/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.view;

import fr.enac.sita.visuradar.model.IBeacon;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.shape.Polygon;
import javafx.scene.text.Font;
import javafx.scene.text.Text;

/**
 *
 * @author Shuan
 */
public class BeaconView extends Pane{

    public BeaconView(IBeacon beacon){
        double vertex1X = -4;
        double vertex1Y = 0;
        double vertex2X = 4;
        double vertex2Y = vertex1Y;
        double vertex3X = 0;
        double vertex3Y = -6;
        
        Polygon triangle = new Polygon();

        triangle.setLayoutX(beacon.getX());
        triangle.setLayoutY(beacon.getY());
        triangle.getPoints().addAll(new Double[]{vertex1X, vertex1Y, vertex2X, vertex2Y, vertex3X, vertex3Y});
        triangle.setFill(Color.WHITE);

        Text name = new Text(beacon.getX() - 10, beacon.getY() + 10, beacon.getCode());
        name.setFill(Color.LIGHTBLUE);
        name.setFont(new Font(10));
        this.getChildren().addAll(name, triangle);
    }
}
