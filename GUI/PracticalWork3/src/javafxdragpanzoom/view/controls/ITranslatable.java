package javafxdragpanzoom.view.controls;

/**
 * Generic interface for a widget that can be translated.
 *
 * @author Nicolas Saporito - ENAC
 */
public interface ITranslatable {

    /**
     * Translate
     *
     * @param dx component of the translation along the abscissa axis
     * @param dy component of the translation along the ordinate axis
     */
    public void translate(double dx, double dy);

}
