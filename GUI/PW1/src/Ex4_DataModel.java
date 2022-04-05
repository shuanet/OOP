import javafx.application.Application;
import static javafx.application.Application.launch;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.StringProperty;
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
public class Ex4_DataModel extends Application{
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
        
        // 4
        DoubleProperty s1Prop = s1.valueProperty();
        DoubleProperty s2Prop = s2.valueProperty();
        StringProperty txtBoxProp = txtBox.textProperty();
        
        StringConverter sc = new DoubleStringConverter();
        
        s2Prop.bindBidirectional(s1Prop);
        txtBoxProp.bindBidirectional(s1Prop, sc);
        
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
