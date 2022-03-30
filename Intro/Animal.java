import java.lang.Math;

public class Animal {
    private String name;
    private int age = 0;
    private int lifeSpan = (int)(Math.random()*6) + 9;
    private int maxEnergy = (int)(Math.random()*5) + 5;
    private int energy = (int)(Math.random()*(this.maxEnergy - 2)) + 3;
    private boolean alive = true;

    public Animal(String name){
        this.name = name;
    }

    // getters
    public void printAnimal(){
        System.out.println(this.name + "\n" +
        "Age: " + this.age + "\n" +
        "Lifespan: " + this.lifeSpan + "\n" +
        "Energy: " + this.energy + "\n" +
        "Max energy: " + this.maxEnergy);
    }
    public boolean getAlive(){
        return this.alive;
    }

    // methods
    public void talk(){
        if(this.energy >= 5){
            System.out.println("\n" + this.name + ": Just chillin bro");
        }
        else{
            System.out.println("\n" + this.name + ": Man, I gotta eat somethin\n");
        }

    }
    public void eat(){
        if(energy == maxEnergy){
            System.out.println("\n" + this.name + ": You ain't gonna make me eat that shit motherf**!");
        }
        else{
            this.energy += (int)(Math.random()*3) + 1;
            if(this.energy > maxEnergy){
                this.energy = maxEnergy;
            }
        }
    }
    public void isAlive(){
        if(this.age == this.lifeSpan){
            this.alive = false;
            System.out.println("\n" + "Ain't you gonna clean that mess? You gotta corpse in there...");
        }
        else{
            this.alive = true;
        }
    }
    public void grow(){
        if(this.energy > 0){
            this.age++;
            this.energy--;
            isAlive();
            if(this.alive == true){
                System.out.println("\n" + this.name + ": go get some chicks bro, its my birthday! I'm turnin " + this.age);
            }
        }
        else{
            System.out.println("\n" + this.name + ": yo, a man can't grow up with an empty stomach");
        }
    }
}
