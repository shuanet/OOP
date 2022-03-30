/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.model;

import javafx.beans.property.DoubleProperty;
import javafx.beans.property.SimpleDoubleProperty;
/**
 *
 * @author Shuan
 */
public class Point implements IPoint{
    private DoubleProperty x = new SimpleDoubleProperty();
    private DoubleProperty y = new SimpleDoubleProperty();

    public Point(DoubleProperty x, DoubleProperty y) {
        this.x = x;
        this.y = y;
    }
    public Point(Point otherP){
        this.setX(otherP.getX());
        this.setY(otherP.getY());
    }
    
    @Override
    public DoubleProperty xProperty(){
        return this.x;
    }
    @Override
    public DoubleProperty yProperty(){
        return this.y;
    }
    @Override
    public Double getX(){
        return this.x.get();
    }
    @Override
    public Double getY(){
        return this.y.get();
    }
    @Override
    public void setX(double x){
        this.x.set(x);
    }
    @Override
    public void setY(double y){
        this.y.set(y);
    }
    @Override
    public void set(IPoint p){
        this.setX(p.getX());
        this.setY(p.getY());
    }
}
