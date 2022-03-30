package fr.enac.sita.visuradar.model;

import java.util.List;

/**
 * Interface specifying the information available on an
 * air traffic control sector.
 *
 * @author Pierre Rondin, Nicolas Saporito
 *
 */
public interface ISector {

    /**
     * Get the floor of the sector in FL.
     * @return 
     */
    public String getFloor();

    /**
     * Get the sector ceiling in FL.
     * @return 
     */
    public String getCeiling();

    /**
     * Get the name of the sector.
     * @return 
     */
    public String getName();

    /**
     * Get the name of the Area Control Centre.
     * @return 
     */
    public String getAcc();

    /**
     * Get a copy of the list of slices that constitute the sector.
     * @return 
     */
    public List<IZone> getSlices();

    /**
     * Fill in the list of slices in this sector.
     *
     * @param slices list of layers (the handles to the layers are kept but not the list, which is copied)
     */
    public void setSlices(List<IZone> slices);

}
