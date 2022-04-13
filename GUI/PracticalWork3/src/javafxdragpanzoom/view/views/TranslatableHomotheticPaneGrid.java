package javafxdragpanzoom.view.views;

import javafx.scene.Group;
import javafx.scene.shape.Line;

/**
 * Grid which is translatable and whose scaling is homothetic.
 * @author Nicolas Saporito - ENAC
 */
public class TranslatableHomotheticPaneGrid extends TranslatableHomotheticPane {
    
    // Style and size
    private final static String STYLE = "-fx-background-color: lightgrey; -fx-border-color: blue;";
    private final static int WIDTH = 700;
    private final static int HEIGHT = 600;
    private final static int GRID_OFFSET = 50;
    
    /** Group to hold the grid drawings */
    protected final Group grid = new Group();
    
    public TranslatableHomotheticPaneGrid() {
        super();
        
        // Add the group to this component's scene graph
        getChildren().add(grid);
        
        // Make this group transparent to mouse events
        grid.setMouseTransparent(true);
        
        // Create the grid
        setStyle(STYLE);
        setPrefSize(WIDTH, HEIGHT);
        
        
        // Vertical Lines
        for(int x = 0; x < WIDTH; x += GRID_OFFSET){
            Line vLine = new Line(x, 0, x, HEIGHT);
            grid.getChildren().add(vLine);
        }
        
        // Horizontal Lines
        for(int y = 0; y < HEIGHT; y += GRID_OFFSET){
            Line hLine = new Line(0, y, WIDTH, y);
            grid.getChildren().add(hLine);
        }
    }
}
