// EXERCISE //

import java.util.Calendar;

public class User {
    private String id;
    private String password;
    private Calendar expDate;

    public User(String id, String password, Calendar expDate){
        this.id = id;
        this.password = password;
        this.expDate = expDate;
    }
    public boolean Equals(User otherUser){
        if (otherUser == null){return false;}
        if (otherUser == this){return true;}
        else{
            //return this == otherUser; NOT CORRECT because we cannot check semantic equality between objects
        
            // First Option
            return (this.id.equals(otherUser.id) && this.expDate.equals(otherUser.expDate));
            
            // Second Option
            //if(this.id == otherUser.id && this.password.equals(otherUser.password)){
            //    return true;
            //}
            //else{
            //    return false;
            //}
        }
    }
    public User close(){
        return new User(this.id, new String(this.password), new Calendar(this.expDate));
    }
}