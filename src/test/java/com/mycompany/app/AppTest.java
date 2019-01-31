package com.mycompany.app;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import org.junit.Before;
import org.junit.Test;
import org.junit.After;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

/**
 * Unit test for simple App.
 */
public class AppTest {
    /**
     * The output stream.
     */
    private final ByteArrayOutputStream outContent =
        new ByteArrayOutputStream();

    /**
     * Set up the streams.
     */
    @Before
    public void setUpStreams() {
        System.setOut(new PrintStream(outContent));
    }

    /**
     * Test the application constructor.
     */
    @Test
    public void testAppConstructor() {
        try {
            new App();
        } catch (Exception e) {
            fail("Construction failed.");
        }
    }

    /**
     * Test the main method.
     */
    @Test
    public void testAppMain() {
        App.main(null);
        try {
            assertEquals("Hello World!" + System.getProperty("line.separator"),
                         outContent.toString());
        } catch (AssertionError e) {
            fail("\"message\" is not \"Hello World!\"");
        }
    }

    /**
     * Clean up the streams.
     */
    @After
    public void cleanUpStreams() {
        System.setOut(null);
    }
}
