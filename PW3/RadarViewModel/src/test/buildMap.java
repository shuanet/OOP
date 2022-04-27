/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMain.java to edit this template
 */
package test;

import fr.enac.sita.visuradar.data.cartoxanthane.CartographyManagerXanthane;
import fr.enac.sita.visuradar.manager.dragManager;
import fr.enac.sita.visuradar.manager.panManager;
import fr.enac.sita.visuradar.manager.zoomManager;
import fr.enac.sita.visuradar.model.Airspace;
import fr.enac.sita.visuradar.model.IBaseMap;
import fr.enac.sita.visuradar.view.BaseMapView;
import fr.enac.sita.visuradar.view.BeaconView;
import javafx.application.Application;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
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
               
        CartographyManagerXanthane cartography = new CartographyManagerXanthane();
        Airspace myAirspace = new Airspace(cartography);
        
        IBaseMap baseMap = cartography.loadBaseMap();
        BaseMapView BMV = new BaseMapView(baseMap);
        BeaconView BV = new BeaconView(myAirspace.getBeaconsByNameMap());
        
        panManager pM = new panManager(BMV);
        dragManager dM = new dragManager(BMV);
        zoomManager zM = new zoomManager(BMV);
        
        // SELF TRAFFIC
        Circle me = new Circle();
        me.setFill(Color.YELLOW);
        
        root.getChildren().add(BMV);
        BMV.getChildren().add(BV);
        
        BMV.setLayoutX(root.getLayoutX()/2); BMV.setLayoutY(root.getLayoutY()/2);
        BV.setLayoutX(root.getLayoutX()/2); BV.setLayoutY(root.getLayoutY()/2);
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