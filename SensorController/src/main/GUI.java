package main;

import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
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
	public JButton batchStart;
	public JButton batchStop;
	
	public GUI(){  

		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setLayout(new BoxLayout(getContentPane(), BoxLayout.PAGE_AXIS));
		loadPage();
		setTitle("Sensor Controller");
		setSize(1000, 700);
		setVisible(true);		

		server = new Server(6000, this);
		Thread t = new Thread(server);
		t.setDaemon(true);
		t.start();
	}  
	
	public void loadPage() {
		
		createHeader();
				
		try {
			BufferedReader reader = new BufferedReader(new FileReader("sensors.txt"));
			String line = reader.readLine();
			
			while(line != null) {
				createSensorGUI(line);
				line = reader.readLine();
			}
		}
		catch(IOException e) {
			e.printStackTrace();
		}
		
		createBatchButtons();
		
	}
	
	private void createHeader() {
		
		JPanel p = new JPanel();
		p.setLayout(new FlowLayout(FlowLayout.LEFT, 50, 10));
		
		int fontSize = 24;
		int prefWidth = 170;
		int prefHeight = 20;
		
		JLabel l = new JLabel("Sensor");
		l.setFont(new Font("Sans-Serif", Font.BOLD, fontSize));
		l.setPreferredSize(new Dimension(prefWidth, prefHeight));
		
		JLabel iplabel = new JLabel("IP");
		iplabel.setPreferredSize(new Dimension(prefWidth, prefHeight));
		iplabel.setFont(new Font("Sans-Serif", Font.BOLD, fontSize));
		
		JLabel statusLabel = new JLabel("Status");
		statusLabel.setPreferredSize(new Dimension(prefWidth, prefHeight));
		statusLabel.setFont(new Font("Sans-Serif", Font.BOLD, fontSize));
		
		p.add(l);
		p.add(iplabel);
		p.add(statusLabel);
		getContentPane().add(p);
	
	}

	
	public void createSensorGUI(String line) {
		
		int fontSize = 24;
		int prefWidth = 170;
		int prefHeight = 50;
		
		JPanel p = new JPanel();
		p.setLayout(new FlowLayout(FlowLayout.LEFT, 50, 20));
		String[] info = line.split(",");
		int id = Integer.parseInt(info[0]);
		String name = info[1];
		
		JLabel l = new JLabel(name);
		l.setFont(new Font("Sans-Serif", Font.PLAIN, fontSize));
		l.setPreferredSize(new Dimension(prefWidth, prefHeight));
		
		JLabel iplabel = new JLabel("Unknown");
		iplabel.setPreferredSize(new Dimension(prefWidth, prefHeight));
		iplabel.setFont(new Font("Sans-Serif", Font.PLAIN, fontSize));
		
		JLabel statusLabel = new JLabel("Disconnected");
		statusLabel.setPreferredSize(new Dimension(prefWidth, prefHeight));
		statusLabel.setFont(new Font("Sans-Serif", Font.PLAIN, fontSize));
		
		JButton b = new JButton("Start");
		b.setPreferredSize(new Dimension(100, 40));
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
	
	
	private void createBatchButtons() {
		
		JPanel p = new JPanel();
		p.setLayout(new FlowLayout(FlowLayout.CENTER, 50, 20));
		batchStart = new JButton("Start All");
		batchStart.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				for(Sensor s:sensors) {
					if(s.state.equals("Ready")) {
						s.client.sendMessage("RECSTART");
					}
				}
			}
		});
		batchStart.setPreferredSize(new Dimension(100, 40));
		p.add(batchStart);
		
		batchStop = new JButton("Stop All");
		batchStop.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				for(Sensor s:sensors) {
					if(s.state.equals("Recording")) {
						s.client.sendMessage("RECSTOP");
					}
				}
			}
		});
		batchStop.setPreferredSize(new Dimension(100, 40));
		p.add(batchStop);
		
		getContentPane().add(p);
		
	}
	
	

}
