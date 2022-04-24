package pw2;

import javafx.application.Application;
//import javax.swing.SwingUtilities;
import pw2.view.TicTacToeJavaFXView;
//import pw2.view.TicTacToeSwingView;
//import pw2.view.TicTacToeTextView;

/**
 * Factory (in the sense of "Design Pattern") of the different versions of the tic-tac-toe game. 
 * https://en.wikipedia.org/wiki/Factory_method_pattern
 *
 * @author leriche
 *
 */
public abstract class MainTicTacToeFactory {

    /**
     * Launch the game in its textual version.
     */
    //@SuppressWarnings("unused")
    //private static void launchTextView() {
    //    new TicTacToeTextView();
    //}

    /**
     * Launch the game in its Swing version.
     */
    //@SuppressWarnings("unused")
    //private static void launchSwingView() {
        // How to launch a Swing application:
        // https://docs.oracle.com/javase/tutorial/uiswing/concurrency/initial.html
    //    SwingUtilities.invokeLater(() -> {
    //        new TicTacToeSwingView();
    //    });
    //}

    /**
     * Launch the game in its JavaFX version.
     */
    @SuppressWarnings("unused")
    private static void launchJavaFXView() {
        // How to launch a JavaFX application
        // https://docs.oracle.com/javase/8/javafx/api/javafx/application/Application.html#launch-java.lang.Class-java.lang.String...-
        Application.launch(TicTacToeJavaFXView.class, (String) null);
    }

    public static void main(String[] args) {
        //launchTextView();
        //launchSwingView();
        launchJavaFXView();
    }

}
