package main;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.net.Socket;

public class Client{
	
	Socket socket;
	BufferedReader in;
	boolean isConnected;
	public String name;
	
	public Client(Socket s, BufferedReader br, String n) {
		socket = s;
		in = br;
		name = n;
		isConnected = true;
	}

}
