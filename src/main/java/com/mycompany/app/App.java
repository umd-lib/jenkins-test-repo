package com.mycompany.app;

/**
 * Hello world!
 */
public class App {
    /**
     * The message to display.
     */
    private final String message = "Hello World!";

    /**
     * Default constructor.
     */
    public App() {
    }

    /**
     * Main method.
     *
     * @param args the arguments from the command-line
     */
    public static void main(final String[] args) {
        System.out.println(new App().getMessage());
    }

    /**
     * Getter method.
     *
     * @return the message
     */
    private String getMessage() {
        return message;
    }
}
