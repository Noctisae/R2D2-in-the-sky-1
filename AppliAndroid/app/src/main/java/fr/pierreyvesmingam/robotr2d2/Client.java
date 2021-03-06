package fr.pierreyvesmingam.robotr2d2;

/**
 * Created by Pierre-yves on 18/04/2016.
 */
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.Socket;
import java.sql.Connection;
import java.util.Calendar;
import java.util.Vector;
import java.util.concurrent.atomic.AtomicBoolean;

import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

public class Client extends Thread {

    private String dstAddress;
    private int dstPort;
    private String response = "";
    private TextView textResponse;
    private AtomicBoolean stop;
    private Boolean connected;
    private Socket socket;
    private InputStream is;
    private OutputStream os;
    private DataOutputStream dos;
    private DataInputStream dis;
    private Vector<String> outputData;
    private ClientListener clientListener;
    private String envoieMessage;
    private String donneOut;
    private JSONObject JSONNul;
    private String stringNulQuandPasEnvoi = new String();
    private String millisToString;
    private int enculeDeConnexion;
    private InputStreamReader isr;
    private BufferedReader br;
    private Reception r;
    private Emission e;


    Client() {
        this.stop = new AtomicBoolean(false);
        this.connected = false;
        this.envoieMessage = new String();
        this.JSONNul = new JSONObject();
        enculeDeConnexion = 0;
        e = new Emission();
        r = new Reception();

    }
        /*Methode startClient */
    //
    // Permet le lancement du thread Client qui lui lance la connexion et le thread emission et reception
    //
    //



    public void startClient() throws IOException {
        //initialise ton socket
        if (this.getState() == Thread.State.NEW)
        {
            this.start();
        }


    }

    public void run()
    {

        System.out.println("ici");
        try {
            socket = new Socket("172.16.0.2", 12800);
            enculeDeConnexion = 1;
            System.out.println("La connexion a été faite");
            e.setSocket(socket);
            r.setSocket(socket);
            r.start();
            e.start();
            System.out.println("Les threads on été correctement lancés");
            //clientListener.onMessageReceived("Connexion faite!");
        } catch (IOException e1) {
            e1.printStackTrace();
        }


    }


    public String getStringFromReception()
    {
        return r.line;
    }

    public void stopClient() {
        try {
            r.closeSocketR();
            e.closeSocketE();
            socket.close();
            this.stop.set(false);
            clientListener.onMessageReceived("Déconnexion faite...");
        } catch (IOException e1) {
            e1.printStackTrace();

        }
    }

    public void addClientListener(ClientListener clientListener) {
        this.clientListener = clientListener;
    }

    /*Methode sendMessage */
    //
    // Permet de recuperer le message envoyé de l'activity et de l'envoyer dans le thread emission
    //
    //
    public void sendMessage(String message) {

        this.envoieMessage = message;
        System.out.println("initialisation message envoie");
        System.out.println(this.envoieMessage);
    }

    public Integer getConnxion()
    {
        return enculeDeConnexion;
    }

    public interface ClientListener {
        public void onMessageReceived(String message);
    }

    /******************************************/
    /*           Class de Reception          */
    /****************************************/
    private class Reception extends Thread
    {
        public String line;
        private Socket socket;

        public void setSocket(Socket socket) {
            this.socket = socket;

        }
        public void closeSocketR() {
            try {
                this.socket.close();
                System.out.println("socket reception close");
            } catch (IOException e1) {
                e1.printStackTrace();
            }

        }
        public void run()
        {
            //lecture
           try {
            BufferedReader in ;
            in = new BufferedReader(new InputStreamReader(this.socket.getInputStream()));
            line = null;
            clientListener.onMessageReceived("Dans le run du thread reception");
            System.out.println("dans le thread reception");
            while ((line = in.readLine()) != null) {
                if(clientListener == null)
                {
                    System.out.println("null clientListener");
                    clientListener.onMessageReceived("le message reçu est null");
                }
                else
                {
                    clientListener.onMessageReceived(line);
                    System.out.println(line);
                    System.out.println("doit recevoir");
                }

            }
            System.out.println("Je suis sorti de ma boucle MGL");
            }catch (IOException e1) {
            e1.printStackTrace();
            System.out.println("La reception à été coupé");
            }
        }

    }

    /******************************************/
    /*           Class de Emission           */
    /****************************************/
    private class Emission extends Thread {
        private Socket socket;

        public void setSocket(Socket socket) throws IOException {
            this.socket = socket;
            os = socket.getOutputStream();
            dos = new DataOutputStream(os);
        }

        public void closeSocketE() {
            try {
                this.socket.close();
                System.out.println("socket emission close");
            } catch (IOException e1) {
                e1.printStackTrace();
            }

        }

        public void run() {

            try {
                while (!stop.get()) {
                    // ecriture
                    System.out.println(envoieMessage);
                    if (!envoieMessage.isEmpty()) {
                        System.out.println("Je suis dans une magnifique boucle");
                        dos.writeUTF(envoieMessage);
                        envoieMessage = "";

                    } else if (envoieMessage.isEmpty()) {
                        Calendar cal = Calendar.getInstance();
                        millisToString = new String(String.valueOf(cal.getTimeInMillis()));
                        System.out.println("Inactivité !");

                        JSONNul.put("mode", "8"); //mode 0 pour landscape

                        JSONNul.put("vitesseG", "0000"); //vitesse moteur de gauche
                        JSONNul.put("vitesseD", "0000"); //vitesse moteur de gauche
                        JSONNul.put("temps", millisToString); //vitesse moteur de gauche
                        System.out.println(JSONNul.toString());
                        stringNulQuandPasEnvoi = JSONNul.toString();
                        dos.writeUTF(stringNulQuandPasEnvoi);
                        stringNulQuandPasEnvoi = "";

                    }
                    this.sleep(80);
                }
            } catch (ConnectException ex) {
                enculeDeConnexion = 0;
            } catch (Exception e) {

                System.out.println("L'emission à été coupé");
                e.printStackTrace();
            }

        }
    }
}
