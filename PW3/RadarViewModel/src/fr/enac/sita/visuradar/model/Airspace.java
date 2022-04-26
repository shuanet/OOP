
/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.model;

import java.util.*;
import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/**
 *
 * @author Shuan
 */
public class Airspace{
    private Map<String, IBeacon> Beacons;   // K=Beacon param name, V=Interface objects value
    private Map<String, ISector> Sectors;   // K=Beacon param name, V=Interface objects value
    
    public Airspace(){
        this.Beacons = Collections.emptyMap();
        this.Sectors = Collections.emptyMap();
    }
    public Airspace(ICartographyManager cartographyManager){  
        this.Beacons = new HashMap();
        this.Sectors = new HashMap();
        
        List<IBeacon> listBeacons = cartographyManager.loadBeacons();
        List<ISector> listSectors = cartographyManager.loadSectors();
        
        for(int i = 0; i < listBeacons.size(); i++){
            this.Beacons.put(listBeacons.get(i).getCode(), listBeacons.get(i));
        }
        for(int i = 0; i < listSectors.size(); i++){
            this.Sectors.put(listSectors.get(i).getName(), listSectors.get(i));
        }
    }
    
    // Airspace Class Methods
    public Boolean containsSector(String s){
        return Sectors.containsKey(s);
    }
    public Boolean containsBeacon(String b){
        return Beacons.containsKey(b);
    }
    public List<IBeacon> getPublishedBeacons(){
        List<IBeacon> publishedList = null;
        for(String beacon: this.Beacons.keySet()){
            if("published".equals(this.Beacons.get(beacon).getType())){
                publishedList.add(this.Beacons.get(beacon));
            }
        }
        return publishedList;
    }
    public Map<String,ISector> getSectorsByNameMap(){
        return this.Sectors;
    }
    public Map<String,IBeacon> getBeaconsByNameMap(){
        return this.Beacons;
    }

    public Map<String, IBeacon> getBeacons() {
        return Beacons;
    }

    public Map<String, ISector> getSectors() {
        return Sectors;
    }
    
}
