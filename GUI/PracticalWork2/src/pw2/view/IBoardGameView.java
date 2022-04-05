package pw2.view;

import pw2.model.Player;

/**
 * Interface for views of a board game linked to a {@link IBoardGameModel}
 *
 * @author garciafa, saporito
 */
public interface IBoardGameView {

    /**
     * Display the whole game.
     */
    public void displayGame();
    
    /**
     * Display the last move played.
     * @param line Line of the move on the set
     * @param column Column of the move on the set
     */
    public void displayLastMove(int line, int column);

    /**
     * Display an error in the view.
     * @param err The error text
     */
    public void displayError(String err);

    /**
     * Display the winner of the game and restart the game.
     * @param winner The player who has won
     */
    void displayWinnerAndRestart(Player winner);

    /**
     * Display the end of a game where there is no winner and restart the game.  
     */
    void displayEndWithNoWinnerAndRestart();

    /**
     * Free the resources associated with the view.
     */
    public void exit();
}
