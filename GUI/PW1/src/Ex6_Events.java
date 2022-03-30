import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

/**
 *
 * @author shuanet
 */
public class Ex6_Events extends Application {

    /**
     *
     * @param primaryStage
     */
    @Override
    public void start(Stage primaryStage) {
        // Create a button
        Button btn = new Button("Click me!");
        
        // Listen to ActionEvents on button (convenience method)
        btn.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent event) {
                System.out.println("Convenience method ActionEvent on button");
                System.out.println("    target: " + event.getTarget() + " - source:" + event.getSource() + "\n");
            }
        });

        // Create the root container and add the button as its child
        StackPane root = new StackPane();
        root.getChildren().add(btn);

        // Set up root container, scene and stage
        Scene scene = new Scene(root, 300, 250);
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
