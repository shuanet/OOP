/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package fr.enac.sita.visuradar.manager;

import fr.enac.sita.visuradar.view.BaseMapView;
import javafx.event.EventHandler;
import javafx.scene.input.MouseEvent;

/**
 *
 * @author shuanet
 */
public class dragManager {
    private BaseMapView paneToDrag;
    private double x;
    private double y;

    public dragManager(BaseMapView pane) {
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
