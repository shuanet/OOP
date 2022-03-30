
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
public class Airspace implements ISector, IBeacon{
    private Map<String, IBeacon> Beacons;   // K=Beacon param name, V=Interface objects value
    private Map<String, ISector> Sectors;   // K=Beacon param name, V=Interface objects value
    
    public Airspace(){
        this.Beacons = Collections.emptyMap();
        this.Sectors = Collections.emptyMap();
    }
    
    // Airspace Class Methods
    public Boolean containsSector(String s){
        
    }
    public Boolean containsBeacon(String b){
        
    }
    public List<IBeacon> getPublishedBeacons(){
        
    }
    public Map<String,ISector> getSectorsByNameMap(){
        
    }
    public Map<String,ISector> getBeaconsByNameMap(){
        
    }
}
