/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMain.java to edit this template
 */
package test;

import fr.enac.sita.visuradar.view.RadarView;
import javafx.application.Application;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.paint.Color;
import javafx.stage.Stage;

/**
 *
 * @author Shuan
 */
public class buildMap extends Application {
    
    @Override
    public void start(Stage primaryStage) {
        Group root = new Group();
        root.setStyle("-fx-background-color: black;");
               
        RadarView RV = new RadarView();
        root.getChildren().add(RV);
        
        Scene scene = new Scene(root, 1500, 920, Color.BLACK);
        primaryStage.setTitle("Interactive Map");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }
}