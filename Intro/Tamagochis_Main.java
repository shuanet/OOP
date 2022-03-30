import java.util.Scanner;

public class Tamagochis_Main {

    public static void main(String[] args){
        Scanner scan = new Scanner(System.in);

        System.out.println("\n>> Welcome to Tamagochi Gang!\n");        
        System.out.println("\n>> ¿How many animals do you want to play with?");
        while(!scan.hasNextInt()){
            scan.next();
        }
        int n = scan.nextInt();
        
        System.out.println("\n>> You will play with " + n + " animals. Name them!");
        Animal[] tamagochis = new Animal[n];
        for(int i = 1; i <= n; i++){
            System.out.println(">> " + i + ")");
            String name = scan.next();
            Animal a = new Animal(name);
            a.printAnimal();
            tamagochis[i-1] = a;
        }
        for(Animal t : tamagochis){
            while(t.getAlive() == true){
                t.talk();
                System.out.println("\n>> 1-Eat/2-Grow/3-Nothing");
                int order = scan.nextInt();
                if(order == 1){
                    t.eat();
                }
                if(order == 2){
                    t.grow();
                }
                if(order == 3){
                    break;
                }
                if(order != 1 && order != 2 && order != 3){
                    System.out.println("\n>> Write 1, 2 or 3.");
                }
            }
        }
        scan.close();
    }
}
