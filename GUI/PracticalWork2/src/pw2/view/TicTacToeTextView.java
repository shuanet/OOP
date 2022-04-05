package pw2.view;

import pw2.model.Player;
import pw2.model.TicTacToeModel;
import java.util.Scanner;

/**
 * View of a tic-tac-toe game in textual form in the terminal.
 *
 * @author garciafa, saporito, leriche
 */
public class TicTacToeTextView implements IBoardGameView {
    
    private final TicTacToeModel model;
    private final int BOARD_SIZE;
    
    private boolean isEndAsked;

    /**
     * Constructor. 
     * By subscribing this view to the model (at the end of the constructor), 
     * the latter will call the view for updates through the methods 
     * specified in the {@link IBoardGameView} interface.
     */
    public TicTacToeTextView() {
        // Set up this instance
        this.model = TicTacToeModel.getInstance();
        BOARD_SIZE = model.BOARD_SIZE;
        // Subscribe to the model so that it updates the view 
        // (by calling the methods specified by the IBoardGameView interface).
        // It is not a good practice to pass to another object a reference 
        // to this instance under construction. The other object could then 
        // try to act on our instance before the end of its initialization 
        // (especially in multi-thread), which could cause problems. 
        // To avoid this it would be necessary to set up a mechanism 
        // similar to the launch of a JavaFX application (see ViewMorpionJavaFX).
        model.subscribe(this);
        // Create the view
        createView();
    }
    
    /**
     * Create the view.
     */
    private void createView() {
        // As there is no event-driven programming in the console
        // this view keeps running in a loop while the end of the game is not asked.
        while (!isEndAsked) {            
            askMove();
        }
    }

    /**
     * Ask the user to play a move.
     */
    private void askMove() {
        boolean aLine = false;
        boolean aColumn = false;
        System.out.println("Next player: " + model.getCurrentPlayer());
        System.out.println("Make your move <line> <column> or 'n' to start a new game or 'q' to quit: ");
        int line = -1;
        int column = -1;
        while (!(aLine && aColumn)) {
            aLine = false;
            aColumn = false;
            Scanner scan = new Scanner(System.in);
            if (scan.hasNextInt()) {
                line = scan.nextInt();
                aLine = true;
                if (scan.hasNextInt()) {
                    column = scan.nextInt();
                    aColumn = true;
                }
            } else {
                String commande = scan.next();
                switch (commande) {
                    case "n":
                        model.newGame();
                        return;
                    case "q":
                        exit();
                        return;
                }
            }
        }
        model.playMove(line, column);
    }

    @Override
    public void displayGame() {
        for (int j = 0; j < BOARD_SIZE; j++) {
            System.out.print("  " + j);
        }
        System.out.println();
        for (int i = 0; i < BOARD_SIZE; i++) {
            System.out.print(i);
            for (int j = 0; j < BOARD_SIZE; j++) {
                switch (model.getPlayerOnSquare(i, j)) {
                    case CROSS:
                        System.out.print(" X ");
                        break;
                    case VOID:
                        System.out.print("   ");
                        break;
                    case CIRCLE:
                        System.out.print(" O ");
                        break;
                }
            }
            System.out.println();
        }
    }

    @Override
    public void displayLastMove(int lig, int col) {
        displayGame();
        // Impossible with this view, the whole game board must must be displayed at once.
    }

    @Override
    public void displayError(String err) {
        System.out.println();
        System.out.println("Error : " + err);
        System.out.println();
        displayGame();
    }

    @Override
    public void displayWinnerAndRestart(Player gagnant) {
        displayEndAndRestart(gagnant + " won!");
    }

    @Override
    public void displayEndWithNoWinnerAndRestart() {
        displayEndAndRestart("No one has won!");
    }
    
    private void displayEndAndRestart(String message) {
        System.out.println();
        System.out.println(message);
        System.out.println();
        model.newGame();
    }

    @Override
    public void exit() {
        isEndAsked = true;
    }

}
