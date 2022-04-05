package pw2.model;

/**
 * Exception indicating that the coordinates of a square are not valid. 
 * This exception inherits from RuntimeException because it can only be caused 
 * by the user in the text version of the game, where the coordinates of the 
 * square to be played must be entered. In the other versions the user clicks on 
 * the existing squares and therefore cannot cause the error. 
 * Only the developer can do this by making mistakes in the indices of the tables 
 * to be searched, which does not require any processing other than displaying an 
 * error log, and this is very well done with a RuntimeException.
 * Setting an exception under compiler control (inheriting from Exception) 
 * is then not only unnecessary but it would make the processing in non-text 
 * versions more cumbersome.
 *
 * @author garciafa, saporito
 */
public class InvalidSquareException extends RuntimeException {

    public InvalidSquareException() {
        super();
    }

    public InvalidSquareException(String message) {
        super(message);
    }

    public InvalidSquareException(Throwable cause) {
        super(cause);
    }

    public InvalidSquareException(String message, Throwable cause) {
        super(message, cause);
    }

}
