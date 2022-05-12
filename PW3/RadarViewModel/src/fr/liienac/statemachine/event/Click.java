/*
 * Copyright (c) 2016 Stéphane Conversy - ENAC - All rights Reserved
 */
package fr.liienac.statemachine.event;

import fr.liienac.statemachine.geometry.Point;

public class Click<Item> extends PositionalEvent<Item> {

    public int num;

    /**
     * Constructor for mouse
     */
    public Click(Point p_, Item s_) {
        super(p_, s_);
        num = 0;
    }

    /**
     * Constructor for multitouch without orientation
     */
    public Click(int cursorid_, Point p_, Item s_, int num_) {
        super(cursorid_, p_, s_);
        num = num_;
    }

    /**
     * Constructor for multitouch with orientation
     */
    public Click(int cursorid_, Point p_, Item s_, float angRad, int num_) {
        super(cursorid_, p_, s_, angRad);
        num = num_;
    }
}
