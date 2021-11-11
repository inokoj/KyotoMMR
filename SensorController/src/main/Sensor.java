package main;

import javax.swing.JButton;
import javax.swing.JLabel;

public class Sensor {
	
	JButton button;
	String name;
	boolean started;
	Client client;
	JLabel iplabel;
	
	public Sensor(String n, JButton b, JLabel l) {
		name = n;
		button = b;
		iplabel = l;
	}
	
	public void updateClient(Client c) {
		client = c;
		iplabel.setText(c.ip.toString());
		button.setEnabled(true);
	}

}
