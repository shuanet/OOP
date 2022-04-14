/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javafxdragpanzoom.managers;

import javafx.event.EventHandler;
import javafx.scene.input.ScrollEvent;
import javafxdragpanzoom.view.views.TranslatableHomotheticPane;

/**
 *
 * @author shuanet
 */
public class zoomManager {
    private TranslatableHomotheticPane paneToZoom;
    private double x;
    private double y;
    private double scale;

    public zoomManager(TranslatableHomotheticPane paneToZoom) {
        this.paneToZoom = paneToZoom;
    
        this.paneToZoom.addEventFilter(ScrollEvent.SCROLL_STARTED, new EventHandler<ScrollEvent>(){
            @Override
            public void handle(ScrollEvent e){
                x = e.getX();
                y = e.getY();
                scale = e.getDeltaY();
                e.consume();
            }
        });
        this.paneToZoom.addEventFilter(ScrollEvent.SCROLL_FINISHED, new EventHandler<ScrollEvent>(){
            @Override
            public void handle(ScrollEvent e){
                paneToZoom.appendScale(scale, x, y);
                e.consume();
            }
        });
    }
}
