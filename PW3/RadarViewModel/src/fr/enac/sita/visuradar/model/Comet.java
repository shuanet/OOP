/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.model;
import java.util.*;

/**
 *
 * @author Shuan
 */
public class Comet {
    //private LinkedList<Point> points;
    private Point p1;
    private Point p2;
    private Point p3;
    private Point p4;
    private Point p5;
    
    public Comet(Point firstPoint) {
        this.p1 = this.p2 = this.p3 = this.p4 = this.p5 = firstPoint;
    }
    public void addCoordinates(Point nextPoint){
        this.p1.set(nextPoint);
        this.p2.set(this.p1);
        this.p3.set(this.p2);
        this.p4.set(this.p3);
        this.p5.set(this.p4);
    }

    public Point getP1() {
        return p1;
    }

    public Point getP2() {
        return p2;
    }

    public Point getP3() {
        return p3;
    }

    public Point getP4() {
        return p4;
    }

    public Point getP5() {
        return p5;
    }
    
}
