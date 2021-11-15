package main;

import java.awt.FlowLayout;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;


public class GUI extends JFrame {
	
	Server server;
	static ArrayList<Sensor> sensors = new ArrayList<Sensor>();
	
	public GUI(){  

		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setLayout(new BoxLayout(getContentPane(), BoxLayout.PAGE_AXIS));
		loadPage();
		setTitle("Sensor Controller");
		setSize(500, 700);
		setVisible(true);		

		server = new Server(6000, this);
		Thread t = new Thread(server);
		t.setDaemon(true);
		t.start();
	}  
	
	public void loadPage() {
		
		try {
			BufferedReader reader = new BufferedReader(new FileReader("sensors.txt"));
			String line = reader.readLine();
			
			while(line != null) {
				createSensor(line);
				line = reader.readLine();
			}
		}
		catch(IOException e) {
			e.printStackTrace();
		}
		
	}
	
	public void createSensor(String line) {
		JPanel p = new JPanel();
		p.setLayout(new FlowLayout(FlowLayout.LEFT, 50, 20));
		String[] info = line.split(",");
		int id = Integer.parseInt(info[0]);
		String name = info[1];
		JLabel l = new JLabel(name);
		JLabel iplabel = new JLabel("Unknown");
		JLabel statusLabel = new JLabel("Not connected");
		JButton b = new JButton("Start");
		b.setEnabled(false);
		p.add(l);
		p.add(iplabel);
		p.add(statusLabel);
		p.add(b);
		getContentPane().add(p);
		
		Sensor s = new Sensor(id, name, b, iplabel, statusLabel);
		sensors.add(s);
	}
	
	public void addClientToSensor(Client c, String state) {
		for(Sensor s:sensors) {
			if(c.id == s.id && c.name.equals(s.name)) {
				s.updateClient(c, state);
				break;
			}
		}
	}
	
	public static void disconnectClient(Client c) {
		for(Sensor s:sensors) {
			if(c.id == s.id && c.name.equals(s.name)) {
				s.disconnection();
				break;
			}
		}	
	}
	
	public static void updateClientState(Client c, String state) {
		for(Sensor s:sensors) {
			if(c.id == s.id && c.name.equals(s.name)) {
				s.updateState(state);
				break;
			}
		}
	
	}
	
	

}
