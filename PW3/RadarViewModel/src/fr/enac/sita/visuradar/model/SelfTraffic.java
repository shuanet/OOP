/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.enac.sita.visuradar.model;

import static java.lang.Double.parseDouble;
import static java.lang.Integer.parseInt;

/**
 *
 * @author Shuan
 */
public class SelfTraffic extends Point{
    private final String callSign;
    private final int flightNum;
    private int ssr;
    private String sector;
    private Double vX;
    private Double vY;
    private Double FL;
    private Double VR;
    private Double GS;
    private Double hdg;
    private Double tendency;
    private String time;

    public SelfTraffic(double x, double y){
        super(x, y);
        this.callSign = "AAF312Q";
        this.flightNum = 4996;
    }
    
    public void updateParams(String ssr, String vX, String vY, String FL, String VR, String GS, String hdg, String tendency, String time) {
        this.ssr = parseInt(ssr);
        this.vX = parseDouble(vX);
        this.vY = parseDouble(vY);
        this.FL = parseDouble(FL);
        this.VR = parseDouble(VR);
        this.GS = parseDouble(GS);
        this.hdg = parseDouble(hdg);
        this.tendency = parseDouble(tendency);
        this.time = time;
    }

    public String getCallSign() {
        return callSign;
    }

    public int getFlightNum() {
        return flightNum;
    }

    @Override
    public String toString() {
        return "callSign=" + callSign + "\t flightNum=" + flightNum + "\t nssr=" + ssr + "\t sector=" + sector + "\t vX=" + vX + "\t vY=" + vY + "\t FL=" + FL + "\t VR=" + VR + "\t GS=" + GS + "\t hdg=" + hdg + "\t tendency=" + tendency + "\t time=" + time;
    }
    
}
