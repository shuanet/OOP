public class Point {
    private double x;
    private double y;

    public Point(double x, double y){
        this.x = x;
        this.y = y;
    }
    public double getX(){
        return this.x;
    }
    public double getY(){
        return this.y;
    }
    // 1.1)
    public boolean isEqual(Point p){
        return p != null && p.getX() == this.x && p.getY() == this.y;
    }
}
