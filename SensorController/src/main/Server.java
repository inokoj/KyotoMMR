package main;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

public class Server implements Runnable {
	
	int port;
	GUI parent;
	
	public Server(int p, GUI par) {
		port = p;
		parent = par;
	}
	
	public void run() {
		
		
        try  {
        	ServerSocket serverSocket = new ServerSocket(port);
        	 
            System.out.println("Sensor server is listening on port " + port);
 
            while (true) {
                Socket clientSocket = serverSocket.accept();
        		BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        		String info = in.readLine();
        		String[] data = info.split(",");
        		int sensorID = Integer.parseInt(data[0]);
        		String sensorType = data[1];
        		String sensorName = data[2];
        		String sensorState = data[3];
        		       		
        		Client c = new Client(clientSocket, in, sensorID, sensorName, sensorType);
        		
        		if(parent.addClientToSensor(c, sensorState) == null) {
        			System.out.println("Not a valid client, disconnecting...");
        			clientSocket.close();
        			continue;
        		}
                
        		Thread t = new Thread(c);
        		t.setDaemon(true);
        		t.start();

            }
 
        } catch (IOException ex) {
            System.out.println("Server exception: " + ex.getMessage());
            ex.printStackTrace();
        }
   
	}
}
