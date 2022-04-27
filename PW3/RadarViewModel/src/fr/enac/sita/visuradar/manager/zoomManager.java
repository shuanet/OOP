/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package fr.enac.sita.visuradar.manager;

import fr.enac.sita.visuradar.view.BaseMapView;
import javafx.event.EventHandler;
import javafx.scene.input.ScrollEvent;
/**
 *
 * @author shuanet
 */
public class zoomManager {
    private BaseMapView paneToZoom;
    private double x;
    private double y;
    private double scale;

    public zoomManager(BaseMapView paneToZoom) {
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
                paneToZoom.appendScale(scale);
                e.consume();
            }
        });
    }
}
