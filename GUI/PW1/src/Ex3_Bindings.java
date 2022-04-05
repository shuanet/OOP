import javafx.application.Application;
import static javafx.application.Application.launch;
import javafx.scene.Scene;
import javafx.scene.control.Slider;
import javafx.scene.control.TextField;
import javafx.scene.layout.HBox;
import javafx.stage.Stage;
import javafx.util.StringConverter;
import javafx.util.converter.DoubleStringConverter;

/**
 *
 * @author Shuan
 */
public class Ex3_Bindings extends Application{
    @Override
    public void start(Stage primaryStage) {
        HBox hBox = new HBox();
        
        Slider s1 = new Slider();
        Slider s2 = new Slider();
        TextField txtBox = new TextField();
        
        // Adding objects to scene
        hBox.getChildren().add(s1);
        hBox.getChildren().add(txtBox);
        hBox.getChildren().add(s2);
        
        // 3.2
        s2.valueProperty().bindBidirectional(s1.valueProperty());
        
        // 3.3
        StringConverter sc = new DoubleStringConverter();
        txtBox.textProperty().bindBidirectional(s1.valueProperty(), sc);
        
        // Set up hbox container, scene and stage
        Scene scene = new Scene(hBox, 400, 100);
        primaryStage.setTitle("Binding Values");
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
