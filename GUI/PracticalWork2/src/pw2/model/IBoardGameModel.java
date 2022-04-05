package pw2.model;

import pw2.view.IBoardGameView;

/**
 * Interface for board game models 
 * (where moves consist of placing pieces on a square board 
 * such as tic-tac-toe, power4 or reversi).
 * 
 * MVC Design Pattern (Model-View-Controller) : 
 * The model is responsible for maintaining the data and performing the 
 * calculations required to run the application. It constitutes with the utility 
 * classes (calculations, communications...) what is called the functional core.
 * The views that subscribed to the model manage the display.
 * They are notified by the model when it undergoes changes.
 * Controllers modify the model.
 * 
 * In reality it is difficult/useless to strictly implement the MVC design pattern 
 * because the view and control aspects are intrinsically linked in many technologies. 
 * The solution proposed here is a simplification that mixes view and controller 
 * (under the name of view) while keeping the essential point: 
 * the separation with the model, which allows to change technology (e.g. textual, 
 * swing and JavaFX) without having to modify the functional core.
 *
 * @author garciafa, leriche, saporito
 */
public interface IBoardGameModel {

    /**
     * Subscribe to this model.
     * @param view the view to subscribe
     */
    public void subscribe(IBoardGameView view);

    /**
     * Initialize the game.
     */
    public void newGame();

    /**
     * Play the current player's move and pass the hand to the next player 
     * if the game is not over.
     * @param line Line
     * @param column Column
     */
    public void playMove(int line, int column);

    /**
     * Get the current player (the one who has to play).
     * @return the current player
     */
    public Player getCurrentPlayer();

    /**
     * Determine which player occupies a square.
     * @param line Line
     * @param column Column
     * @return The player who occupies this square or Player.VOID if it is empty
     */
    public Player getPlayerOnSquare(int line, int column);

    /**
     * Determine whether the move played in (line,column) is winning.
     * @param line Line
     * @param column Column
     * @return true if it's a winning move
     */
    boolean isAWinningMove(int line, int column);

    /**
     * Determine whether the game is over without a winner.
     * @return true there is no winner
     */
    boolean isGameOverWithoutWinner();

}
