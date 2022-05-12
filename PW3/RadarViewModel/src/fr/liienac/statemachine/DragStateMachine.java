/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package fr.liienac.statemachine;

import fr.liienac.statemachine.event.Move;
import fr.liienac.statemachine.event.Press;
import fr.liienac.statemachine.event.Release;

/**
 *
 * @author Shuan
 */
public class DragStateMachine extends StateMachine {
    private double x;
    private double y;
    
    public State start = new State() {
        Transition press = new Transition<Press>() {
            @Override
            public void action(){
                x = evt.p.x;
                y = evt.p.y;
            }
            @Override
            public State goTo() {
                return dragging;
            }
        };
    };
    
    public State dragging = new State() {
        Transition up = new Transition<Release>() {
            @Override
            public State goTo() {
                return start;
            }
        };
        Transition move = new Transition<Move>() {
            @Override
            public void action() {
                System.out.println("Drag " + evt.p.x + evt.p.y);
                
            }
        };
    };
}
