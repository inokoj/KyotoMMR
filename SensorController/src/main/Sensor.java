package main;

import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JLabel;

public class Sensor {
	
	JButton button;
	String name;
	Client client;
	JLabel iplabel;
	JLabel statusLabel;
	int id;
	String state;
	
	public Sensor(int i, String n, JButton b, JLabel l, JLabel m) {
		id = i;
		name = n;
		button = b;
		this.createButtonListener();
		iplabel = l;
		statusLabel = m;
		state = "Disconnected";
	}
	
	public void updateClient(Client c, String state) {
		client = c;
		iplabel.setText(c.ip.toString());
		button.setEnabled(true);
		this.state = state;
		updateStatusGUI();
	}
	
	private void createButtonListener() {
		button.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				if(client != null) {
					if(state.equals("Ready")) {
						client.sendMessage("RECSTART");
					}
					else if(state.equals("Recording")) {
						client.sendMessage("RECSTOP");
					}
				}			
			}
		});
	}
	

	public void updateState(String state) {
		this.state = state;
		this.updateStatusGUI();
	}
	
	private void updateStatusGUI() {
		if(state.toUpperCase().equals("READY")) {
			statusLabel.setText("Ready");
			statusLabel.setForeground(new Color(0, 100, 0));
			button.setText("Start");
		}
		else if(state.toUpperCase().equals("RECORDING")) {
			statusLabel.setText("Recording");
			statusLabel.setForeground(Color.RED);
			button.setText("Stop");
		}
	}
	
	public void disconnection() {
		state = "Disconnected";
		statusLabel.setText("Disconnected");
		statusLabel.setForeground(Color.BLACK);
		iplabel.setText("Unknown");
		client = null;
		button.setEnabled(false);
	}

	
	public String toString() {
		return id + ":" + name;
	}

}
