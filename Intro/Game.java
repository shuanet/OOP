import java.util.Scanner;

public class Game {

    public static Animal[] tamagochiArray;

    public static void main(String[] args){

        int numT = Integer.parseInt(args[0]);
        tamagochiArray = new Animal[numT];
        Scanner s = new Scanner();

        for(int i=0; i < numT; i++){
            System.out.println("How are the Tamagochis called?");
            String name = s.next();
            tamagochiArray[i] = new Animal(name);
        }

        boolean 
    }
}
