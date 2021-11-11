package main;

import javax.swing.JButton;

public class Sensor {
	
	JButton button;
	String name;
	boolean started;
	Client client;
	
	public Sensor(String n, JButton b) {
		name = n;
		button = b;
		
		
	}
	
	public void updateClient(Client c) {
		client = c;
		button.setEnabled(true);
	}
	

}
