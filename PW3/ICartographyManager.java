package fr.enac.sita.visuradar.model;

import java.util.List;

public interface ICartographyManager {
	
	/**
	 * Load beacons. 
	 * @return list of published beacons, with coordinates in Cautra format
	 */
	public List<IBeacon> loadBeacons();
	
	/**
	 * Load sectors. 
	 * @return list of sectors, filtered for the right flight level, with coordinates in Cautra format
	 */
	public List<ISector> loadSectors();
	
	/**
	 * Load the base map. 
	 * @return An instance of an object implementing IBaseMap, describing the base map in Cautra format
	 */
	public IBaseMap loadBaseMap();

}