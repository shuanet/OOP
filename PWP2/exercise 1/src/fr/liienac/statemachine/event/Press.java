/*
 * Copyright (c) 2016 Stéphane Conversy - ENAC - All rights Reserved
 */
package fr.liienac.statemachine.event;

import fr.liienac.statemachine.geometry.Point;

public class Press<Item> extends PositionalEvent {

    /**
     * Constructor for mouse
     */
    public Press(Point p_, Item s_) {
        super(p_, s_);
    }

    /**
     * Constructor for multitouch without orientation
     */
    public Press(int cursorid_, Point p_, Item s_) {
        super(cursorid_, p_, s_);
    }

    /**
     * Constructor for multitouch with orientation
     */
    public Press(int cursorid_, Point p_, Item s_, float angRad) {
        super(cursorid_, p_, s_, angRad);
    }
}
