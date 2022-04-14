/*
 * Author: Saporito Nicolas - ENAC
 * Direct manipulation interactions in JavaFX : drag, pan, mouse centered differentiated zoom
 */
package javafxdragpanzoom;

import javafx.application.Application;
import static javafx.application.Application.launch;
import javafx.event.EventHandler;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.input.KeyEvent;
import javafx.stage.Stage;
import javafxdragpanzoom.managers.dragManager;
import javafxdragpanzoom.managers.panManager;
import javafxdragpanzoom.managers.zoomManager;
import javafxdragpanzoom.view.views.TranslatableHomotheticPane;
import javafxdragpanzoom.view.views.TranslatableHomotheticPaneGrid;
import javafxdragpanzoom.view.views.TranslatableHomotheticPaneRect;

public class DragPanZoomApplication extends Application {

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        // Scene graph root component
        Group root = new Group();

        // Grid with pan & zoom
        TranslatableHomotheticPane panAndZoomPane = new TranslatableHomotheticPaneGrid();
        panAndZoomPane.setLayoutX(100);
        panAndZoomPane.setLayoutY(100);
        root.getChildren().add(panAndZoomPane);
        panManager pM = new panManager(panAndZoomPane);
        zoomManager zM = new zoomManager(panAndZoomPane);
        
        // Rectangle with drag
        TranslatableHomotheticPane rect = new TranslatableHomotheticPaneRect();
        rect.setLayoutX(450);
        rect.setLayoutY(450);
        panAndZoomPane.getChildren().add(rect);
        dragManager dM = new dragManager(rect);

        // Scene creation
        Scene scene = new Scene(root, 1024, 768);
        stage.setScene(scene);
        stage.setTitle("Direct manipulation - provided code");
        stage.show();

        // Move the rectangle with keyboard
        scene.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent event) {
                int offset = 50;
                int dx = 0;
                int dy = 0;
                // Decide the translation to make
                switch (event.getCode()) {
                    case UP:
                        dx = 0;
                        dy = - offset;
                        break;
                    case DOWN:
                        dx = 0;
                        dy = offset;
                        break;
                    case LEFT:
                        dx = - offset;
                        dy = 0;
                        break;
                    case RIGHT:
                        dx = offset;
                        dy = 0;
                        break;
                    default:
                        break;
                }
                // Translate
                rect.setTranslateX(rect.getTranslateX() + dx);
                rect.setTranslateY(rect.getTranslateY() + dy);
                // Warning: this was just an example to show how to react to keyboard events.
                // For the rest of the work session you will have to implement the methods specified 
                // in the interfaces for graphical transformations on the grid and rectangle, so use:
                // rect.translate(dx, dy);
            }
        });
    }
}
