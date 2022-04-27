/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMain.java to edit this template
 */
package test;

import fr.enac.sita.visuradar.data.cartoxanthane.CartographyManagerXanthane;
import fr.enac.sita.visuradar.model.Airspace;
import fr.enac.sita.visuradar.model.IBaseMap;
import fr.enac.sita.visuradar.view.BaseMapView;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;

/**
 *
 * @author Shuan
 */
public class buildMap extends Application {
    
    @Override
    public void start(Stage primaryStage) {
        Group root = new Group();
        Pane mapPane = new Pane();
        root.getChildren().add(mapPane);
                
        CartographyManagerXanthane cartography = new CartographyManagerXanthane();
        Airspace myAirspace = new Airspace(cartography);
        IBaseMap baseMap = cartography.loadBaseMap();
        
        mapPane.getChildren().add(new BaseMapView(baseMap));
        for ..
        BeaconView beaconsView = new BeaconView(myAirspace.getBeaconsByNameMap().get(i));
                
        Scene scene = new Scene(root, 600, 800);
        
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