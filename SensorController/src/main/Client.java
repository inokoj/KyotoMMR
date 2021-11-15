package main;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.SocketException;

public class Client implements Runnable{
	
	Socket socket;
	BufferedReader in;
	boolean isConnected;
	public String name;
	PrintWriter writer;
	InetAddress ip;
	int id;
	
	
	public Client(Socket s, BufferedReader br, int i, String n) {
		socket = s;
		in = br;
		name = n;
		id = i;
		isConnected = true;
		ip = (InetAddress)s.getInetAddress();
		
		try {
			writer = new PrintWriter(s.getOutputStream(), true);
		}
		catch(IOException e) {
			e.printStackTrace();
		}
		
	}
	
	public void sendMessage(String message) {
		writer.println(message);
	}
	
	@Override
	public void run() {
		
		while(true) {
			try {
				String message = in.readLine();
				String[] info = message.split(",");
				String state = info[2];
				GUI.updateClientState(this, state);
			}
			catch(SocketException e) {
				GUI.disconnectClient(this);
				break;
			}
			catch(IOException e) {
				e.printStackTrace();
				break;
			}
		
		}
		
	}
	
}
