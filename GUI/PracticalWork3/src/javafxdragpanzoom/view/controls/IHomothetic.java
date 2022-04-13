package javafxdragpanzoom.view.controls;

/**
 * Generic interface for a widget whose scaling is always homothetic.
 * @author Nicolas Saporito - ENAC
 */
public interface IHomothetic {

    /**
     * Get the current scale factor
     * @return scale factor
     */
    public abstract double getScale();

    /**
     * Replace the current scale factor by a new value
     * (the zoom pivot is the origin of the local coordinates system).
     * @param scale the new scale factor
     */
    public abstract void setScale(double scale);

    /**
     * Replace the current scale factor by a new value.
     * @param scale the new scale factor
     * @param pivotX zoom pivot abscissa
     * @param pivotY zoom pivot abscissa
     */
    public abstract void setScale(double scale, double pivotX, double pivotY);

    /**
     * Apply additional scaling (multiply by the current zoom factor) 
     * (the zoom pivot is the origin of the local coordinates system).
     * @param deltaScale additional scale factor to apply
     */
    public void appendScale(double deltaScale);

    /**
     * Apply additional scaling (multiply by the current zoom factor).
     * @param deltaScale additional scale factor to apply
     * @param pivotX zoom pivot abscissa
     * @param pivotY zoom pivot abscissa
     */
    public void appendScale(double deltaScale, double pivotX, double pivotY);
}
