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
public class panManager {
    private TranslatableHomotheticPane paneToPan;
    private double x;
    private double y;

    public panManager(TranslatableHomotheticPane pane) {
        this.paneToPan = pane;
        this.paneToPan.addEventHandler(MouseEvent.MOUSE_PRESSED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                x = e.getX();
                y = e.getY();
            }
        });
        this.paneToPan.addEventHandler(MouseEvent.MOUSE_DRAGGED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                paneToPan.translate(e.getX() - x, e.getY() - y);
            }
        });
    }
}
