package javafxdragpanzoom.view.views;

import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.shape.StrokeType;

/**
 * Rectangle which is translatable and whose scaling is homothetic.
 * @author Nicolas Saporito - ENAC
 */
public class TranslatableHomotheticPaneRect extends TranslatableHomotheticPane {

    /**
     * Constructor
     */
    public TranslatableHomotheticPaneRect() {
        super();
        
        // Create a rectangle of 100px by 100px, positioned at (0, 0).
        Rectangle rect = new Rectangle(100, 100);
        rect.setStroke(Color.BLUE);
        rect.setStrokeType(StrokeType.INSIDE);
        rect.setFill(Color.BLUE.deriveColor(1, 1, 1, 0.5));
        super.getChildren().add(rect);
    }
}
