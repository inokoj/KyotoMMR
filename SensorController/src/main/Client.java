package main;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

public class Client{
	
	Socket socket;
	BufferedReader in;
	boolean isConnected;
	public String name;
	PrintWriter writer;
	
	
	public Client(Socket s, BufferedReader br, String n) {
		socket = s;
		in = br;
		name = n;
		isConnected = true;
		
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

}
