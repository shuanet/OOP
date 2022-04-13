/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javafxdragpanzoom.managers;

import java.awt.event.MouseEvent;
import java.beans.EventHandler;
import javafxdragpanzoom.view.views.TranslatableHomotheticPane;

/**
 *
 * @author shuanet
 */
public class panManager {
    private TranslatableHomotheticPane panToPan;
    private double x;
    private double y;

    public panManager(TranslatableHomotheticPane panToPan) {
        this.panToPan = panToPan;
        panToPan.addEventFilter(MouseEvent.MOUSE_PRESSED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                x = e.getX();
                y = e.getY();
                System.out.println(x + ", " + y);
            }
        });
        panToPan.addEventFilter(MouseEvent.MOUSE_DRAGGED, new EventHandler<MouseEvent>(){
            @Override
            public void handle(MouseEvent e){
                panToPan.translate(e.getX() - x, e.getY() - y);
            }
        });
    }
}
