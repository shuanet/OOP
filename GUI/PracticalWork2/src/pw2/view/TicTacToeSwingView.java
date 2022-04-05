package pw2.view;

import pw2.model.Player;
import pw2.model.TicTacToeModel;
import java.awt.Container;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.net.URL;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.KeyStroke;

/**
 * Swing version of a tic-tac-toe game. 
 * This class is a JFrame, a basic Swing window 
 * that can be created directly from a standard java application.
 *
 * @author garciafa, saporito
 */
public class TicTacToeSwingView extends JFrame implements IBoardGameView, ActionListener {

    private final TicTacToeModel model;
    private final int BOARD_SIZE;

    private final JLabel[][] squareViews;
    private JLabel nextPlayer;
    private JButton buttonNew, buttonQuit;
    private JMenuItem menuItemNew, menuItemQuit;

    // Resource retrieval: solution 1
    // The path to load resources is specified relative to the project root.
    // These resources will not be included in the jar when it is built.
    // When deploying the jar, it is therefore necessary to keep a relative path 
    // from the folder containing the jar identical to the one declared below 
    // (except that here it is from the root of the project).
    private final static ImageIcon CROSS = new ImageIcon("resources/cross.jpg");
    private final static ImageIcon CIRCLE = new ImageIcon("resources/circle.jpg");
    private final static ImageIcon VOID = new ImageIcon("resources/void.jpg");
    // Resource retrieval: solution 2
    // Solution 1 leaves the resources accessible in the jar folder.
    // If there is a need to lock them, place them in a directory 
    // in the src folder and use getResource() to access them. 
    // The resources will then be included in the jar when it is built.
//    private final URL urlCross = this.getClass().getResource("/resources/cross.jpg");
//    private final URL urlCircle = this.getClass().getResource("/resources/circle.jpg");
//    private final URL urlVoid = this.getClass().getResource("/resources/void.jpg");
//    private final ImageIcon CROSS = new ImageIcon(urlCross);
//    private final ImageIcon CIRCLE = new ImageIcon(urlCircle);
//    private final ImageIcon VOID = new ImageIcon(urlVoid);

    /**
     * Constructor. 
     * By subscribing this view to the model (at the end of the constructor), 
     * the latter will call the view for updates through the methods 
     * specified in the {@link IBoardGameView} interface.
     */
    public TicTacToeSwingView() {
        super("Tic-tac-toe Swing version");
        // Set up this instance
        this.model = TicTacToeModel.getInstance();
        BOARD_SIZE = model.BOARD_SIZE;
        squareViews = new JLabel[BOARD_SIZE][BOARD_SIZE];
        // Create the view
        createView();
        // Subscribe to the model so that it updates the view 
        // (by calling the methods specified by the IBoardGameView interface).
        // It is not a good practice to pass to another object a reference 
        // to this instance under construction. The other object could then 
        // try to act on our instance before the end of its initialization 
        // (especially in multi-thread), which could cause problems. 
        // Here, the fact that it's the last instruction is not even a guarantees 
        // that it will be called last because the compiler can optimize 
        // and interchange some instructions.
        // To avoid this it would be necessary to set up a mechanism 
        // similar to the launch of a JavaFX application (see ViewMorpionJavaFX).
        model.subscribe(this);
    }

    /**
     * Create the view and give it the ability to modify the model (controller aspect).
     */
    private void createView() {
        // JFrame's contentPane
        Container panel = this.getContentPane();
        panel.setLayout(new BoxLayout(panel, BoxLayout.PAGE_AXIS));

        // Board game
        JPanel boardGame = new JPanel();
        boardGame.setLayout(new GridLayout(BOARD_SIZE, BOARD_SIZE));
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                squareViews[i][j] = new JLabel();
                squareViews[i][j].setIcon(VOID);
                squareViews[i][j].addMouseListener(myMouseAdapter); // subscription to clicks on the squares
                boardGame.add(squareViews[i][j]);
            }
        }
        panel.add(boardGame);

        // current player label and game control buttons
        nextPlayer = new JLabel();
        nextPlayer.setIcon(VOID);
        buttonNew = new JButton("N");
        buttonNew.setPreferredSize(nextPlayer.getSize());
        buttonNew.addActionListener(this); // subscription to actions on "New game" button
        buttonQuit = new JButton("Q");
        buttonQuit.setPreferredSize(nextPlayer.getSize());
        buttonQuit.addActionListener(this); // subscription to actions on "Quit" button

        // panel containing the label of the current player and the buttons
        JPanel controlBar = new JPanel();
        controlBar.setLayout(new GridLayout(1, 3));
        panel.add(controlBar);
        controlBar.add(buttonNew);
        controlBar.add(nextPlayer);
        controlBar.add(buttonQuit);

        // menus and keystrokes
        JMenuBar menuBar = new JMenuBar();
        setJMenuBar(menuBar);
        JMenu menu = new JMenu("Game");
        menuBar.add(menu);
        menuItemNew = new JMenuItem("New game");
        menu.add(menuItemNew);
        KeyStroke nks = KeyStroke.getKeyStroke('n');
        menuItemNew.setAccelerator(nks); // keystroke
        menuItemNew.addActionListener(this);  // subscription to actions on "New game" menu item
        menuItemQuit = new JMenuItem("Quit");
        menu.add(menuItemQuit);
        KeyStroke qks = KeyStroke.getKeyStroke('q');
        menuItemQuit.setAccelerator(qks); // keystroke
        menuItemQuit.addActionListener(this); // subscription to actions on "Quit" menu item 

        // Ensure that the application is exited when this window is closed...
        addWindowListener(new MyWindowAdapter());

        // Setup, position and display the window
        pack();
        setLocation(400, 400);
        setResizable(false);
        setVisible(true);
    }

    // Subscription to clicks on the squares.
    // - When there are few methods to redefine to describe a response to
    //   mouse events, it's better to inherit a MouseAdapter rather than 
    //   to implement the MouseListener interface, which would then force  
    //   to define all specified methods even if they are empty.
    // - Here we create a single instance of the adapter, which we'll share
    //   between all the Jlabel representing the squares.
    private final MouseAdapter myMouseAdapter = new MouseAdapter() {
        @Override
        public void mouseClicked(MouseEvent e) {
            int line = -1;
            int column = -1;
            for (int i = 0; i < BOARD_SIZE; i++) {
                for (int j = 0; j < BOARD_SIZE; j++) {
                    if (squareViews[i][j] == e.getSource()) {
                        line = i;
                        column = j;
                    }
                }
            }
            if (line != -1) {
                model.playMove(line, column);
            }
        }
    };

    // Subscription close window to exit the application.
    // - See note above about inheriting an adapter rather than implementing a listener.
    // - Here we declare an internal class that must be instantiated when subscribing: 
    //   addListener(new MyWindowAdapter())
    private class MyWindowAdapter extends WindowAdapter {
        @Override
        public void windowClosing(WindowEvent e) {
            exit();
            // Just to do the same thing as with the Exit button.
            // The same result would be obtained by simply placing  
            // the following line at JFrame initialization:
            // setDefaultCloseOperation(EXIT_ON_CLOSE);
        }
    }

    // Subscription to the "Exit" and "New Game" button and menu actions.
    // - The choice made here is to implement the ActionListener interface 
    //   directly in this class rather than to create an internal class. 
    // - In all cases and contrary to subscriptions to events mouse and window, 
    //   there is only one method to implement, so there's no need to use an adapter.
    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == buttonNew
                || e.getSource() == menuItemNew) {
            model.newGame();
        } else if (e.getSource() == buttonQuit
                || e.getSource() == menuItemQuit) {
            exit();
        }
    }

    /**
     * Change the icon of a JLabel displaying a player. 
     * @param label JLabel whose icon is to be changed
     * @param player Player whose icon is to be displayed
     */
    private void setIconFromJoueur(JLabel label, Player player) {
        switch (player) {
            case VOID:
                label.setIcon(VOID);
                break;
            case CROSS:
                label.setIcon(CROSS);
                break;
            case CIRCLE:
                label.setIcon(CIRCLE);
                break;
        }
    }

    @Override
    public void displayGame() {
        // Redraws the icons of all the squares of the board, which is required 
        // at the beginning of the game but which is not optimal during the game 
        // since only one square changes at each move.
        // -> prefer displayLastMove(int line, int column)
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                setIconFromJoueur(squareViews[i][j], model.getPlayerOnSquare(i, j));
            }
        }
        // change the next player icon
        setIconFromJoueur(nextPlayer, model.getCurrentPlayer());
    }

    @Override
    public void displayLastMove(int line, int column) {
        // change the icon of the square that has just been played
        setIconFromJoueur(squareViews[line][column], model.getPlayerOnSquare(line, column));
        // change the next player icon
        setIconFromJoueur(nextPlayer, model.getCurrentPlayer());
    }

    @Override
    public void displayError(String err) {
        JOptionPane.showMessageDialog(this, err, "Error", JOptionPane.ERROR_MESSAGE);
    }

    @Override
    public void displayWinnerAndRestart(Player winner) {
        displayEndAndRestart(winner + " won!");
    }

    @Override
    public void displayEndWithNoWinnerAndRestart() {
        displayEndAndRestart("No one has won!");
    }

    private void displayEndAndRestart(String message) {
        JOptionPane.showMessageDialog(this, message);
        model.newGame();
    }

    @Override
    public void exit() {
        System.exit(EXIT_ON_CLOSE);
    }
}
