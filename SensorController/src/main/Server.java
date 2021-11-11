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
                System.out.println("New client connected");
        		BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        		String sensorName = in.readLine();
                Client c = new Client(clientSocket, in, sensorName);  
                parent.addClientToSensor(c);
            }
 
        } catch (IOException ex) {
            System.out.println("Server exception: " + ex.getMessage());
            ex.printStackTrace();
        }	
	}
}
