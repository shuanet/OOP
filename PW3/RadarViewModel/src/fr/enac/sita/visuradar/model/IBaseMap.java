package fr.enac.sita.visuradar.model;

import java.util.List;

/**
 * Interface specifying the information available on a base map: 
 * a list of areas (outlines)
 *
 * @author Pierre Rondin, Nicolas Saporito
 */
public interface IBaseMap {

    /**
     * Get a copy of the list of zones that constitute the base map
     */
    public List<IZone> getZones();
}
