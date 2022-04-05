import java.text.SimpleDateFormat;
import java.util.Date;
import javafx.application.Application;
import static javafx.application.Application.launch;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.StringProperty;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
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
public class Ex5_ChangeListener extends Application{
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
        
        DoubleProperty s1Prop = s1.valueProperty();
        DoubleProperty s2Prop = s2.valueProperty();
        StringProperty txtBoxProp = txtBox.textProperty();
        
        StringConverter sc = new DoubleStringConverter();
        
        s2Prop.bindBidirectional(s1Prop);
        txtBoxProp.bindBidirectional(s1Prop, sc);
        
        // 5.1
        Boolean fellBack = new Boolean();
        
        s1Prop.addListener(new ChangeListener<Number>(){
            @Override
            public void changed(ObservableValue<? extends Number> obs, Number oldVal, Number newVal){
                String date = new SimpleDateFormat("HH:mm:ss.SSS").format(new Date());
                if(s1Prop.get() > 75 && fellBack == true){
                    fellBack = false;
                    System.out.println(date + " - ALERT\nYou have exceeded 75");
                }
                if(s1Prop.get() < 75 && fellBack == false){
                    fellBack = true;
                    System.out.println(date + " - Safe values");
                }
            }
        });
        
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
