public class NamedPoint extends Point {
    private String name;

    public NamedPoint(String name, double x,double y){
        super(x, y);
        this.name = name;
    }
    public String getName(){
        return this.name;
    }
    // 1.3)
    public boolean isEqual(NamedPoint np){
        return super.isEqual(np) && np.getName().equals(this.name);
    }
    @Override
    public boolean isEqual(Point p){
        return (p instanceof NamedPoint) && (this.isEqual((NamedPoint)p));
    }
}
