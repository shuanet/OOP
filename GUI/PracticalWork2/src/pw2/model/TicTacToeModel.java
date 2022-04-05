package pw2.model;

import pw2.view.IBoardGameView;

/**
 * Model of a tic-tac-toe game. 
 * This class must not be instantiated manually: the singleton design pattern 
 * ensures a single instance for the entire application.
 *
 * @author garciafa, saporito, jestin, leriche
 */
public final class TicTacToeModel implements IBoardGameModel {

    /**
     * Board size
     */
    public final int BOARD_SIZE;

    /**
     * Number of lined up squares to be occupied to win a game
     */
    public final int MOVES_TO_WIN;

    // Occupancy of the squares by the players
    private final Player[][] squares;

    // Current player
    private Player currentPlayer;

    // Number of moves played in a game
    private int playedMoves = 0;

    // view that subscribed to this model
    private IBoardGameView view;

    // Singleton instance:
    // Only one instance of this class is created once. It is easily accessed 
    // from anywhere in the application using the class method getInstance().
    private final static TicTacToeModel instance = new TicTacToeModel(3, 3);

    /**
     * Constructor of the singleton (reserved for internal use -> private)
     *
     * @param boardSize Board size
     * @param movesToWin Number of lined up squares to occupy in order to win a game
     */
    private TicTacToeModel(int boardSize, int movesToWin) {
        BOARD_SIZE = boardSize;
        MOVES_TO_WIN = Math.min(boardSize, movesToWin); // minimalistic precaution
        squares = new Player[BOARD_SIZE][BOARD_SIZE];
    }

    /**
     * Accessor on the singleton instance
     *
     * @return the singleton instance
     */
    public static TicTacToeModel getInstance() {
        return instance;
    }

    @Override
    public void subscribe(IBoardGameView view) {
        this.view = view;
        newGame();
    }

    @Override
    public void newGame() {
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                squares[i][j] = Player.VOID;
            }
        }
        currentPlayer = Player.CROSS;
        playedMoves = 0;
        view.displayGame();
    }

    @Override
    public void playMove(int line, int column) {
        try {
            if (getPlayerOnSquare(line, column) == Player.VOID) {
                squares[line][column] = currentPlayer;
                playedMoves++;
                if (isAWinningMove(line, column)) {
                    // if the game is over it is better to display the last move 
                    // before displaying the winner
                    view.displayLastMove(line, column);
                    view.displayWinnerAndRestart(currentPlayer);
                } else if (isGameOverWithoutWinner()) {
                    view.displayLastMove(line, column);
                    view.displayEndWithNoWinnerAndRestart();
                } else {
                    // if the game is not finished you have to change the player 
                    // in the model before displaying the last move 
                    // (because it also displays the player who has the hand)
                    changePlayer();
                    view.displayLastMove(line, column);
                }
            } else {
                view.displayError("The square " + line + ":" + column + " has already been played.");
            }
        } catch (InvalidSquareException e) {
            view.displayError("The square doesn't exist (board size: " + BOARD_SIZE + ").");
        }
    }

    @Override
    public Player getCurrentPlayer() {
        return currentPlayer;
    }

    @Override
    public Player getPlayerOnSquare(int line, int column) throws InvalidSquareException {
        // Test the validity of the square entered:
        /*
        if (line < BOARD_SIZE && line >= 0 && column >= 0 && column < BOARD_SIZE) {
            return squares[line][column];
        } else {
            throw new InvalidSquareException("Invalid square:" + line + ":" + column);
        }
        */
        // Or handle the exception that may occur in the absence of a test:
        try {
            return squares[line][column];
        } catch (IndexOutOfBoundsException e) {
            // If the chosen square is invalid, a more explicit exception, 
            // created for this application, is propagated 
            // and will be handled afterwards so as not to cause a problem.
            throw new InvalidSquareException("Invalid square:" + line + ":" + column);
        }
    }

    @Override
    public boolean isGameOverWithoutWinner() {
        return playedMoves == BOARD_SIZE * BOARD_SIZE;
    }

    @Override
    public boolean isAWinningMove(int line, int column) {
        // Counts the adjoining squares occupied by the player of the square (line, column) 
        // and returns true if the count reaches MOVES_TO_WIN in one of the 4 directions 
        // (counts twice the occupation of the square (line, column) for each direction, 
        // so strict inequality must be used in the tests).
        return (countOccupancyByDirection(line, column, 0, 1) + countOccupancyByDirection(line, column, 0, -1) > MOVES_TO_WIN)
                || (countOccupancyByDirection(line, column, 1, 1) + countOccupancyByDirection(line, column, -1, -1) > MOVES_TO_WIN)
                || (countOccupancyByDirection(line, column, 1, 0) + countOccupancyByDirection(line, column, -1, 0) > MOVES_TO_WIN)
                || (countOccupancyByDirection(line, column, 1, -1) + countOccupancyByDirection(line, column, -1, 1) > MOVES_TO_WIN);
    }

    private int countOccupancyByDirection(int i, int j, int di, int dj) throws InvalidSquareException {
        // Count the adjoining squares occupied by the player of the square (i,j) 
        // in the direction symbolized by the vector (di, dj).
        int result = 0;
        Player player = getPlayerOnSquare(i, j);
        while (result <= MOVES_TO_WIN
                && i >= 0 && j >= 0 && i < BOARD_SIZE && j < BOARD_SIZE
                && getPlayerOnSquare(i, j) == player) {
            result++;
            i += di;
            j += dj;
        }
        return result;
    }

    /**
     * Change player
     */
    private void changePlayer() {
        Player nextPlayer;
        switch (currentPlayer) {
            case CROSS:
                nextPlayer = Player.CIRCLE;
                break;
            case CIRCLE:
                nextPlayer = Player.CROSS;
                break;
            default:
                nextPlayer = Player.VOID;
        }
        currentPlayer = nextPlayer;
    }

}
