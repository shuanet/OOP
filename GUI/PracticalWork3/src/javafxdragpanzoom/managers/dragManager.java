/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javafxdragpanzoom.managers;

import javafx.event.EventHandler;
import javafx.scene.input.MouseEvent;
import javafxdragpanzoom.view.views.TranslatableHomotheticPane;

/**
 *
 * @author shuanet
 */
public class dragManager {
    private TranslatableHomotheticPane paneToDrag;
    private double x;
    private double y;

    public dragManager(TranslatableHomotheticPane pane) {
        this.paneToDrag = pane;
        this.paneToDrag.addEventFilter(MouseEvent.MOUSE_PRESSED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                x = e.getX();
                y = e.getY();
                e.consume();
            }
        });
        this.paneToDrag.addEventFilter(MouseEvent.MOUSE_DRAGGED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                paneToDrag.translate(e.getX() - x, e.getY() - y);
                e.consume();
            }
        });
    }
}
