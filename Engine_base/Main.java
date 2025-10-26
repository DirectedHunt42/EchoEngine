//Jack Murray | Nova Foundry
//Echo Engine
//v 2.1.0

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
// import java.nio.file.Files;
// import java.nio.file.Paths;
// import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Random;
import java.util.Scanner;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.UnsupportedAudioFileException;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class Main {
    private static JTextArea outputArea;
    private static JFrame frame;
    private static StringBuilder outputBuffer = new StringBuilder();
    private static volatile String userInput = null;
    private static final Object inputLock = new Object();
    private static int promptPosition = 0;

    // Always scroll to the end of the output area
    private static void scrollToEnd() {
        SwingUtilities.invokeLater(() -> {
            outputArea.setCaretPosition(outputArea.getDocument().getLength());
        });
    }

    public static void main(String[] args) {
        // Read the title from the text file
        String windowTitle = "";
        try {
            File titleFile = new File("Text/Misc/Title.txt");
            if (titleFile.exists()) {
                Scanner titleScanner = new Scanner(titleFile);
                if (titleScanner.hasNextLine()) {
                    windowTitle = titleScanner.nextLine();
                } else {
                    windowTitle = "Echo Engine";
                    System.err.println("Warning: Title.txt is empty. Using default title.");
                }
                titleScanner.close();
            } else {
                windowTitle = "Echo Engine";
                System.err.println("Warning: Title.txt not found. Using default title.");
            }
        } catch (Exception e) {
            windowTitle = "Echo Engine";
            System.err.println("Warning: Error reading Title.txt. Using default title.");
        }

        // Start playing sound in the background
        Thread soundThread = new Thread(() -> {
            try {
                File soundFile = new File("Sounds/Background.wav");
                AudioInputStream audioIn = AudioSystem.getAudioInputStream(soundFile);
                Clip clip = AudioSystem.getClip();
                clip.open(audioIn);
                clip.loop(Clip.LOOP_CONTINUOUSLY);
                clip.start();
            } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e) {
                e.printStackTrace();
            }
        });
        soundThread.start();

        // Setup GUI
        final String finalWindowTitle = windowTitle;
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception e) {}

            frame = new JFrame(finalWindowTitle);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setUndecorated(true);
            frame.getRootPane().setWindowDecorationStyle(JRootPane.FRAME);

            // Maximize window (no true fullscreen, keeps window responsive)
            frame.setExtendedState(JFrame.MAXIMIZED_BOTH);

            // Set app icon (taskbar)
            try {
                Image iconImage = null;
                // Try Icon.png first
                File iconFile = new File("Icons/Icon.png");
                if (iconFile.exists()) {
                    iconImage = Toolkit.getDefaultToolkit().getImage(iconFile.getAbsolutePath());
                } else {
                    // Fallback to Default_icon.png
                    File defaultIconFile = new File("Icons/Default_icon.png");
                    if (defaultIconFile.exists()) {
                        iconImage = Toolkit.getDefaultToolkit().getImage(defaultIconFile.getAbsolutePath());
                    }
                }
                if (iconImage != null) {
                    frame.setIconImage(iconImage);
                }
            } catch (Exception e) {
                // ignore icon errors
            }
            // Load custom fonts if available, else fallback
            Font mainFont = null;
            Font titleFont = null;
            try {
                File fontFile = new File("Fonts/Font.ttf");
                if (fontFile.exists()) {
                    mainFont = Font.createFont(Font.TRUETYPE_FONT, fontFile).deriveFont(Font.PLAIN, 16f);
                }
            } catch (Exception e) {
                mainFont = null;
            }
            try {
                File titleFontFile = new File("Fonts/Title_font.ttf");
                if (titleFontFile.exists()) {
                    titleFont = Font.createFont(Font.TRUETYPE_FONT, titleFontFile).deriveFont(Font.BOLD, 16f);
                }
            } catch (Exception e) {
                titleFont = null;
            }
            // Fallback to Default.ttf if needed
            if (mainFont == null) {
                try {
                    File defaultFontFile = new File("Fonts/Default.ttf");
                    if (defaultFontFile.exists()) {
                        mainFont = Font.createFont(Font.TRUETYPE_FONT, defaultFontFile).deriveFont(Font.PLAIN, 16f);
                    }
                } catch (Exception e) {
                    mainFont = null;
                }
            }
            if (titleFont == null) {
                try {
                    File defaultFontFile = new File("Fonts/Default.ttf");
                    if (defaultFontFile.exists()) {
                        titleFont = Font.createFont(Font.TRUETYPE_FONT, defaultFontFile).deriveFont(Font.PLAIN, 16f);
                    }
                } catch (Exception e) {
                    titleFont = null;
                }
            }
            // Final fallback to Consolas
            if (mainFont == null) {
                mainFont = new Font("Consolas", Font.PLAIN, 16);
            }
            if (titleFont == null) {
                titleFont = new Font("Consolas", Font.BOLD, 16);
            }

            // Apply main font to all UI elements
            UIManager.put("Label.font", mainFont);
            UIManager.put("Button.font", mainFont);
            UIManager.put("TextArea.font", mainFont);
            UIManager.put("TextField.font", mainFont);
            UIManager.put("ComboBox.font", mainFont);
            UIManager.put("Menu.font", mainFont);
            UIManager.put("MenuItem.font", mainFont);
            UIManager.put("TitledBorder.font", mainFont);
            UIManager.put("List.font", mainFont);
            UIManager.put("Table.font", mainFont);
            UIManager.put("CheckBox.font", mainFont);
            UIManager.put("RadioButton.font", mainFont);
            UIManager.put("TabbedPane.font", mainFont);
            UIManager.put("ToolTip.font", mainFont);

            JPanel titleBar = new JPanel() {
                @Override
                protected void paintComponent(Graphics g) {
                    super.paintComponent(g);
                    g.setColor(Color.BLACK);
                    g.fillRoundRect(0, 0, getWidth(), getHeight(), 20, 20);
                }
            };
            titleBar.setOpaque(false);
            titleBar.setLayout(new BorderLayout());
            JLabel titleLabel = new JLabel(" " + finalWindowTitle);
            titleLabel.setForeground(new Color(220,220,220));
            titleLabel.setFont(titleFont);
            titleBar.add(titleLabel, BorderLayout.WEST);

            JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 0, 0));
            buttonPanel.setOpaque(false);
            JButton minBtn = new JButton("-");
            minBtn.setForeground(Color.WHITE);
            minBtn.setBackground(Color.BLACK);
            minBtn.setFocusPainted(false);
            minBtn.setBorderPainted(false);
            minBtn.setFont(mainFont.deriveFont(Font.BOLD, 16f));
            minBtn.setPreferredSize(new Dimension(45, 28));
            minBtn.addActionListener(e -> frame.setState(Frame.ICONIFIED));
            buttonPanel.add(minBtn);
            JButton closeBtn = new JButton("X");
            closeBtn.setForeground(Color.WHITE);
            closeBtn.setBackground(Color.BLACK);
            closeBtn.setFocusPainted(false);
            closeBtn.setBorderPainted(false);
            closeBtn.setFont(mainFont.deriveFont(Font.BOLD, 16f));
            closeBtn.setPreferredSize(new Dimension(45, 28));
            closeBtn.addActionListener(e -> System.exit(0));
            buttonPanel.add(closeBtn);
            titleBar.add(buttonPanel, BorderLayout.EAST);
            titleBar.setPreferredSize(new Dimension(700, 30));

            final Point[] mouseDownCompCoords = {null};
            titleBar.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) { mouseDownCompCoords[0] = e.getPoint(); }
                public void mouseReleased(MouseEvent e) { mouseDownCompCoords[0] = null; }
            });
            titleBar.addMouseMotionListener(new MouseMotionAdapter() {
                public void mouseDragged(MouseEvent e) {
                    Point currCoords = e.getLocationOnScreen();
                    frame.setLocation(currCoords.x - mouseDownCompCoords[0].x, currCoords.y - mouseDownCompCoords[0].y);
                }
            });

            outputArea = new JTextArea();
            outputArea.setFont(mainFont);
            outputArea.setLineWrap(true);
            outputArea.setWrapStyleWord(true);
            outputArea.setEditable(true);
            Color bgColor = new Color(0, 0, 0);
            Color fgColor = new Color(220, 220, 220);
            Color caretColor = new Color(0, 255, 0);
            outputArea.setBackground(bgColor);
            outputArea.setForeground(fgColor);
            outputArea.setCaretColor(caretColor);

            JScrollPane scrollPane = new JScrollPane(outputArea);
            scrollPane.getViewport().setBackground(bgColor);
            scrollPane.setBorder(BorderFactory.createLineBorder(new Color(60,60,60)));
            JScrollBar vBar = scrollPane.getVerticalScrollBar();
            JScrollBar hBar = scrollPane.getHorizontalScrollBar();
            vBar.setUI(new javax.swing.plaf.basic.BasicScrollBarUI() {
                @Override
                protected void configureScrollBarColors() {
                    this.thumbColor = new Color(60,60,60);
                    this.trackColor = bgColor;
                }
            });
            hBar.setUI(new javax.swing.plaf.basic.BasicScrollBarUI() {
                @Override
                protected void configureScrollBarColors() {
                    this.thumbColor = new Color(60,60,60);
                    this.trackColor = bgColor;
                }
            });

            JPanel contentPanel = new JPanel(new BorderLayout());
            contentPanel.setBackground(bgColor);
            contentPanel.add(titleBar, BorderLayout.NORTH);
            contentPanel.add(scrollPane, BorderLayout.CENTER);

            frame.setContentPane(contentPanel);
            frame.getContentPane().setBackground(bgColor);

            outputArea.addKeyListener(new KeyAdapter() {
                @Override
                public void keyPressed(KeyEvent e) {
                    int caret = outputArea.getCaretPosition();
                    // Prevent backspace before prompt
                    if (e.getKeyCode() == KeyEvent.VK_BACK_SPACE && caret <= promptPosition) {
                        e.consume();
                        return;
                    }
                    if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                        int len = outputArea.getText().length();
                        if (caret >= promptPosition) {
                            String text = outputArea.getText();
                            String input = text.substring(promptPosition, len).replace("\n", "").trim();
                            synchronized (inputLock) {
                                userInput = input;
                                inputLock.notifyAll();
                            }
                            SwingUtilities.invokeLater(() -> {
                                outputArea.setCaretPosition(outputArea.getText().length());
                            });
                        }
                        e.consume();
                    }
                }
                @Override
                public void keyTyped(KeyEvent e) {
                    int caret = outputArea.getCaretPosition();
                    if (caret < promptPosition) {
                        outputArea.setCaretPosition(outputArea.getText().length());
                        e.consume();
                    }
                }
            });

            frame.setVisible(true);
            frame.toFront();
            frame.requestFocus();
            outputArea.requestFocusInWindow();

            // Show logo for 2 seconds, then start game
            new Thread(() -> {
                showLogoAndStart(finalWindowTitle);
            }).start();
        });
    }

// Show the Echo Engine logo (ASCII art from txt) centered for 2 seconds, then start the game
private static void showLogoAndStart(String windowTitle) {
    final String[] logo = {""};
    try {
        File logoFile = new File("Icons/Echo_engine_logo.txt");
        if (logoFile.exists()) {
            Scanner scanner = new Scanner(logoFile);
            StringBuilder sb = new StringBuilder();
            while (scanner.hasNextLine()) {
                sb.append(scanner.nextLine()).append("\n");
            }
            scanner.close();
            logo[0] = sb.toString();
        } else {
            logo[0] = "[Echo Engine Logo Not Found]";
        }
    } catch (Exception e) {
        logo[0] = "[Echo Engine Logo Error]";
    }

    // Center logo in outputArea (both vertically and horizontally, and fit to area)
    // Save the current font (should be the original font)
    Font originalFont = (new JTextArea()).getFont();
    float logoFontSize = Math.max(8f, originalFont.getSize2D() * 0.75f);
    Font logoFont = originalFont.deriveFont(logoFontSize);
    try {
        SwingUtilities.invokeAndWait(() -> {
            outputArea.setFont(logoFont);
            outputBuffer.setLength(0);
            outputArea.setText("");
            // Get logo lines
            String[] logoLines = logo[0].split("\n");
            // Calculate output area width in characters
            FontMetrics fm = outputArea.getFontMetrics(outputArea.getFont());
            int areaWidthPx = outputArea.getWidth();
            int charWidth = fm.charWidth('W');
            int areaWidthChars = Math.max(10, areaWidthPx / charWidth); // avoid divide by zero
            // Center each line horizontally and fit to width
            StringBuilder centeredLogo = new StringBuilder();
            int maxLogoWidth = 0;
            for (String line : logoLines) {
                if (line.length() > maxLogoWidth) maxLogoWidth = line.length();
            }
            for (String line : logoLines) {
                String trimmed = line.length() > areaWidthChars ? line.substring(0, areaWidthChars) : line;
                int pad = (areaWidthChars - trimmed.length()) / 2;
                for (int i = 0; i < pad; i++) centeredLogo.append(' ');
                centeredLogo.append(trimmed).append("\n");
            }
            // Calculate padding for vertical centering
            int lines = logoLines.length;
            int areaHeight = outputArea.getHeight();
            int fontHeight = fm.getHeight();
            int padLines = Math.max(0, (areaHeight / fontHeight - lines) / 2);
            StringBuilder pad = new StringBuilder();
            for (int i = 0; i < padLines; i++) pad.append("\n");
            outputArea.setText(pad + centeredLogo.toString());
            outputArea.setCaretPosition(0);
        });
        Thread.sleep(2000);
    } catch (Exception e) {}
    // Restore outputArea font to original size after splash
    SwingUtilities.invokeLater(() -> {
        Font restoredFont = (new JTextArea()).getFont();
        outputArea.setFont(restoredFont);
    });
    // After splash, set outputArea font to mainFont
    SwingUtilities.invokeLater(() -> {
        // mainFont is in the closure of main()'s lambda, so we need to get it from outputArea or store it elsewhere if needed
        // For now, just set it to the current font used for the rest of the app
        // outputArea.setFont(mainFont); // Uncomment if you want to force mainFont
    });
    // Start the game logic in a background thread to avoid blocking the EDT
    new Thread(() -> runGame(windowTitle)).start();
}

    // Wait for user input from the GUI
    public static String getUserInput() {
        // Print prompt
        printPrompt();
        synchronized (inputLock) {
            while (userInput == null) {
                try {
                    inputLock.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            String input = userInput;
            userInput = null;
            return input;
        }
    }

    private static void printPrompt() {
        SwingUtilities.invokeLater(() -> {
            outputBuffer.append("");
            outputArea.setText(outputBuffer.toString());
            scrollToEnd();
            promptPosition = outputArea.getText().length();
        });
    }

    // Print to the output area (with optional delay for typewriter effect and skip on space)
    public static void printToOutput(String text, int delayMs) {
        final boolean[] skip = {false};
        KeyListener skipListener = new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_SPACE) {
                    skip[0] = true;
                }
            }
        };
        outputArea.addKeyListener(skipListener);
        try {
            for (char c : text.toCharArray()) {
                if (skip[0]) {
                    outputBuffer.append(text.substring(outputBuffer.length() - outputArea.getText().length() + promptPosition));
                    outputArea.setText(outputBuffer.toString());
                    scrollToEnd();
                    promptPosition = outputArea.getText().length();
                    break;
                }
                outputBuffer.append(c);
                outputArea.setText(outputBuffer.toString());
                scrollToEnd();
                promptPosition = outputArea.getText().length();
                if (delayMs > 0) {
                    try {
                        Thread.sleep(delayMs);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        } finally {
            outputArea.removeKeyListener(skipListener);
        }
    }

    public static void printToOutput(String text) {
        printToOutput(text, 0);
    }

    public static void clearOutput() {
    outputBuffer.setLength(0);
    outputArea.setText("");
    promptPosition = 0;
    scrollToEnd();
    }

    // Main game logic (refactored from main)
    public static void runGame(String windowTitle) {
        String menuText = windowTitle + "\n\n MAIN MENU\n\n  PLAY    - [1]\n  HELP    - [2]\n  EXIT    - [3]\n  CREDITS - [4]\n  RESET   - [5]\n\n >> ";
        String helpText = "TO NAVIGATE THE WORLD, USE SIMPLE COMMANDS\n\nAVALABLE COMMANDS:\n NORTH\n SOUTH\n EAST\n WEST\n UP\n DOWN\n INVENTORY\n SEARCH\n USE\n MENU\n (ALL LOWER CASE)";
        int menuInput = 0;
        String location = " ";
        boolean menuLoop = true;

        clearOutput();
        printToOutput("CLICK AND PRESS ENTER TO START... ");
        getUserInput();
        clearOutput();

        while (menuLoop) {
            printToOutput(menuText, 10);
            String input = getUserInput();
            try {
                menuInput = Integer.parseInt(input.trim());
            } catch (NumberFormatException e) {
                menuInput = -1;
            }
            if (menuInput == 1) {
                try {
                    File file = new File("Save/Location.txt");
                    if (file.exists()) {
                        Scanner scanner1 = new Scanner(file);
                        if (scanner1.hasNextLine()) {
                            location = scanner1.nextLine();
                        } else {
                            location = "2";
                            System.err.println("Warning: Location.txt is empty. Starting at prolog.");
                        }
                        scanner1.close();
                    } else {
                        location = "2";
                        System.err.println("Warning: Location.txt not found. Starting at prolog.");
                    }
                } catch (Exception e) {
                    location = "2";
                    System.err.println("Warning: Error reading Location.txt. Starting at prolog.");
                }
                if (location.equals("2")) {
                    prolog(null);
                } else if (location.length() >= 3 && location.charAt(0) == '0') {
                    clearOutput();
                    tutorial(Character.getNumericValue(location.charAt(1)), Character.getNumericValue(location.charAt(2)), null);
                } else if (location.length() >= 4 && location.charAt(0) == '1') {
                    clearOutput();
                    game(Character.getNumericValue(location.charAt(1)), Character.getNumericValue(location.charAt(2)), Character.getNumericValue(location.charAt(3)), null);
                } else {
                    System.err.println("Warning: Location.txt has invalid content. Starting at prolog.");
                    prolog(null);
                }
            } else if (menuInput == 2) {
                clearOutput();
                printToOutput(helpText, 10);
                printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
                getUserInput();
                clearOutput();
            } else if (menuInput == 3) {
                menuLoop = false;
            } else if (menuInput == 4) {
                File creditsFile = new File("Text/Misc/Credits.txt");
                String creditsText = "";
                try {
                    Scanner scanner1 = new Scanner(creditsFile);
                    while (scanner1.hasNextLine()) {
                        creditsText += scanner1.nextLine() + "\n";
                    }
                    scanner1.close();
                } catch (FileNotFoundException e) {
                    creditsText = "Credits not found.";
                }
                printToOutput("\n\n" + creditsText);
                printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
                getUserInput();
                clearOutput();
            } else if (menuInput == 5) {
                reset();
                printToOutput("\n\nRESET\n\n PLEASE RESTART THE PROGRAM");
                getUserInput();
                System.exit(0);
            } else {
                printToOutput("\n\nTHAT IS NOT A VAILD INPUT");
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                clearOutput();
            }
        }
        System.exit(0);
    }

    public static void prolog(Scanner scanner) {
        //variables
        String displayText = " ";

        clearOutput();
        reset();
        //prolog part 1
        try {
            File file = new File("Text/Stories/Prolog/Prolog.txt");
            Scanner scanner1 = new Scanner(file);
            displayText = "";
            while (scanner1.hasNextLine()) {
                displayText += scanner1.nextLine() + "\n";
            }
            scanner1.close();
        } catch (FileNotFoundException e) {
            displayText = "Prolog not found.";
        }
        printToOutput("\n\n" + displayText, 10);
        printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
        getUserInput();
        clearOutput();
        tutorial(1, 1, scanner);
    }

    public static void tutorial(int inputY, int inputX, Scanner scanner) {
        //variables
        int x = inputX;
        int y = inputY;
        String optionsText = "\n\n INPUT >> ";
        String helpText = "\n\nAVALABLE COMMANDS:\n north\n south\n east\n west\n up\n down\n inventory\n search\n use\n menu";
        String description = " ";
        String exits = " ";
        String items = " ";
        String input = " ";
        //String journal = " ";
        boolean tutorialDone = false;

        //main
        try {
            FileWriter myWriter = new FileWriter("Save/Location.txt");
            myWriter.write("0" +y +x +"1");
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        boolean firstLoop = true;
        while (tutorialDone == false){
            //load data
            try {
                File file = new File("Text/Room_descriptions/Tutorial/y" +y +"_x" +x +"/Description.txt");
                if (file.exists()) {
                    Scanner scanner1 = new Scanner(file);
                    description = "";
                    while (scanner1.hasNextLine()) {
                        description += scanner1.nextLine() + "\n";
                    }
                    scanner1.close();
                } else {
                    description = "Room description not found.";
                }
            } catch (Exception e) {
                description = "Room description error.";
            }
            try {
                File file = new File("Text/Room_descriptions/Tutorial/y" +y +"_x" +x +"/Exits.txt");
                if (file.exists()) {
                    Scanner scanner1 = new Scanner(file);
                    if (scanner1.hasNextLine()) {
                        exits = scanner1.nextLine();
                    } else {
                        exits = "";
                    }
                    scanner1.close();
                } else {
                    exits = "";
                }
            } catch (Exception e) {
                exits = "";
            }
            //display data
            if (!firstLoop) clearOutput();
            printToOutput(description, 10);
            printToOutput("\n\n Possible Exits: " + exits);
            printToOutput(helpText);
            printToOutput(optionsText);
            firstLoop = false;
            if (scanner == null) {
                input = getUserInput();
            } else {
                if (scanner.hasNextLine()) {
                    input = scanner.nextLine();
                } else {
                    input = "";
                }
            }
            //Game options
            if (input.equals("north") || input.equals("south") || input.equals("east") || input.equals("west")) {
                int[] returned = move(input, exits, x, y, 0, "cabin");
                x = returned[0];
                y = returned[1];
                
            }
            else if (input.equals("up") || input.equals("down")){
                printToOutput("\n\nYou can't go that way.");
            }
            else if (input.equals("inventory")){
                printToOutput(inventory());
            }
            else if (input.equals("search")){
                String foundMsg = search(items, x, y, 0, "cabin");
                printToOutput("\n");
                printToOutput(foundMsg);
                if (!foundMsg.trim().equalsIgnoreCase("You found nothing")) {
                    printToOutput("\n");
                }
            }
            // else if (input.equals("journal")){
            //     printToOutput("\n\n");
            //     try {
            //         File file = new File("Text/Stories/Tutorial/Journal.txt");
            //         Scanner scanner1 = new Scanner(file);
            //         journal = "";
            //         while (scanner1.hasNextLine()) {
            //             journal += scanner1.nextLine() + "\n";
            //         }
            //         scanner1.close();
            //     } catch (FileNotFoundException e) {
            //         journal = "Journal not found.";
            //     }
            //     printToOutput(journal);
            // }
            else if (input.equals("use")){
                printToOutput("\n You can't do that here");
            } else if (input.equals("menu")) {
                printToOutput("\n\nReturning to main menu...");
                // Read the title from the text file
                String windowTitle = "";
                try {
                    File titleFile = new File("Text/Misc/Title.txt");
                    if (titleFile.exists()) {
                        Scanner titleScanner = new Scanner(titleFile);
                        if (titleScanner.hasNextLine()) {
                            windowTitle = titleScanner.nextLine();
                        } else {
                            windowTitle = "Echo Engine";
                            System.err.println("Warning: Title.txt is empty. Using default title.");
                        }
                        titleScanner.close();
                    } else {
                        windowTitle = "Echo Engine";
                        System.err.println("Warning: Title.txt not found. Using default title.");
                    }
                } catch (Exception e) {
                    windowTitle = "Echo Engine";
                    System.err.println("Warning: Error reading Title.txt. Using default title.");
                }
                runGame(windowTitle);
            } else {
                printToOutput("\n\n THAT IS NOT A VALID INPUT");
            }

            printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
            if (scanner == null) {
                getUserInput();
            } else {
                if (scanner.hasNextLine()) {
                    scanner.nextLine();
                }
            }

            //check if we're done
            if (checkInventoryTutorial()) {
                tutorialDone = true;
            }
        }

        clearOutput();
        try {
            File file = new File("Text/Stories/Tutorial/Tutorial_completed.txt");
            Scanner scanner1 = new Scanner(file);
            description = "";
            while (scanner1.hasNextLine()) {
                description += scanner1.nextLine() + "\n";
            }
            scanner1.close();
        } catch (FileNotFoundException e) {
            description = "Leaving the cabin text not found.";
        }
        printToOutput(description);
        printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
        if (scanner == null) {
            getUserInput();
        } else {
            if (scanner.hasNextLine()) {
                scanner.nextLine();
            }
        }
        game(1, 1, 1, scanner);
    }

    public static void game(int inputY, int inputX, int inputZ, Scanner scanner) {
        //variables
        Random rand = new Random();
        int damageChance = 10;
        try {
            File file = new File("Finishing/Damage_chance.txt");
            if (file.exists()) {
                Scanner scanner1 = new Scanner(file);
                if (scanner1.hasNextLine()) {
                    String line = scanner1.nextLine().trim();
                    if (!line.isEmpty()) {
                        damageChance = Integer.parseInt(line);
                    }
                }
                scanner1.close();
            }
        } catch (Exception e) {
            // ignore, fallback to 10
        }
        int toHaunt = rand.nextInt(damageChance) + 1;
        int sanity = 1;
        //int journal = 0;
        int x = inputX;
        int y = inputY;
        int z = inputZ;
        String optionsText = "\n\n INPUT >> ";
        String helpText = "\n\nAVALABLE COMMANDS:\n north\n south\n east\n west\n up\n down\n inventory\n search\n use\n menu";
        String description = " ";
        String exits = " ";
        String items = " ";
        String haunting = " ";
        String input = " ";
        // String journal2 = " ";
        // String journalTemp = " ";
        String used = " ";
        boolean gameDone = false;

        //main
        try {
            FileWriter myWriter = new FileWriter("Save/Location.txt");
            myWriter.write("1" +y +x +z);
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        // try {
        //     File file = new File("Save/Journal.txt");
        //     Scanner scanner1 = new Scanner(file);
        //     journal = Integer.parseInt(scanner1.nextLine());
        //     scanner1.close();
        // } catch (FileNotFoundException e) {
        //     e.printStackTrace();
        // }
        try {
            File file = new File("Save/Health.txt");
            Scanner scanner1 = new Scanner(file);
            sanity = Integer.parseInt(scanner1.nextLine());
            scanner1.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        while (gameDone == false){
            //load data
            try {
                File file = new File("Text/Room_descriptions/Main/floor_" +z +"/y" +y +"_x" +x +"/Description.txt");
                Scanner scanner1 = new Scanner(file);
                description = "";
                while (scanner1.hasNextLine()) {
                    description += scanner1.nextLine() + "\n";
                }
                scanner1.close();
            } catch (FileNotFoundException e) {
                description = "Room description not found.";
            }
            try {
                File file = new File("Text/Room_descriptions/Main/floor_" +z +"/y" +y +"_x" +x +"/Exits.txt");
                Scanner scanner1 = new Scanner(file);
                if (scanner1.hasNextLine()) {
                    exits = scanner1.nextLine();
                } else {
                    exits = "";
                }
                scanner1.close();
            } catch (FileNotFoundException e) {
                exits = "";
            }
            toHaunt = rand.nextInt(5) + 1;
            try {
                File file = new File("Text/Room_descriptions/Main/floor_" +z +"/y" +y +"_x" +x +"/Strange_occerance.txt");
                Scanner scanner1 = new Scanner(file);
                haunting = "";
                while (scanner1.hasNextLine()) {
                    haunting += scanner1.nextLine() + "\n";
                }
                scanner1.close();
            } catch (FileNotFoundException e) {
                haunting = "";
            }
            // try {
            //     File file = new File("Save/Journal.txt");
            //     Scanner scanner1 = new Scanner(file);
            //     if (scanner1.hasNextLine()) {
            //         journal = Integer.parseInt(scanner1.nextLine());
            //     }
            //     scanner1.close();
            // } catch (FileNotFoundException e) {
            //     // ignore
            // }
            //display data
            clearOutput();
            // Display health at the top, using '#' for each point of health
            printToOutput("HEALTH: ");
            for (int i = 0; i < sanity; i++) {
                printToOutput("#");
            }
            printToOutput("\n\n");
            printToOutput(description, 10);
            if (toHaunt == 1){
                printToOutput("\n\n" + haunting);
                printToOutput("\n\nYour health has decreased");
                if (sanity > 0){
                    sanity--;
                    try {
                        FileWriter myWriter = new FileWriter("Save/Health.txt");
                        myWriter.write(String.valueOf(sanity));
                        myWriter.close();
                    } catch (IOException e) {
                        // ignore
                    }
                }
            }
            if (sanity == 0){
                printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
                if (scanner == null) {
                    getUserInput();
                } else {
                    if (scanner.hasNextLine()) {
                        scanner.nextLine();
                    }
                }
                gameOver();
            }
            printToOutput("\n\n Possible Exits: " + exits);
            printToOutput(helpText);
            printToOutput(optionsText);
            if (scanner == null) {
                input = getUserInput();
            } else {
                if (scanner.hasNextLine()) {
                    input = scanner.nextLine();
                } else {
                    input = "";
                }
            }
            //game actions
            if (input.equals("north") || input.equals("south") || input.equals("east") || input.equals("west") || input.equals("up") || input.equals("down")) {
                int[] returned = move(input, exits, x, y, z, "mansion");
                x = returned[0];
                y = returned[1];
                z = returned[2];
            } else if (input.equals("inventory")) {
                printToOutput(inventory());
            } else if (input.equals("search")) {
                String foundMsg = search(items, x, y, z, "mansion");
                printToOutput("\n");
                printToOutput(foundMsg);
                if (!foundMsg.trim().equalsIgnoreCase("You found nothing")) {
                    printToOutput("\n");
                }
            // } else if (input.equals("journal")){
            //     printToOutput("\n\n");
            //     try {
            //         File file = new File("Text/Stories/Tutorial/Journal.txt");
            //         Scanner scanner1 = new Scanner(file);
            //         journal2 = "";
            //         while (scanner1.hasNextLine()) {
            //             journal2 += scanner1.nextLine() + "\n";
            //         }
            //         scanner1.close();
            //     } catch (FileNotFoundException e) {
            //         journal2 = "Journal not found.";
            //     }
            //     printToOutput(journal2);
            //     journalTemp = journal(journal);
            //     printToOutput(journalTemp);
            } else if (input.equals("use")) {
                used = use(x, y, z);
                printToOutput(used);
            } else if (input.equals("menu")) {
                printToOutput("\n\nReturning to main menu...");
                // Read the title from the text file
                String windowTitle = "";
                try {
                    File titleFile = new File("Text/Misc/Title.txt");
                    if (titleFile.exists()) {
                        Scanner titleScanner = new Scanner(titleFile);
                        if (titleScanner.hasNextLine()) {
                            windowTitle = titleScanner.nextLine();
                        } else {
                            windowTitle = "Echo Engine";
                            System.err.println("Warning: Title.txt is empty. Using default title.");
                        }
                        titleScanner.close();
                    } else {
                        windowTitle = "Echo Engine";
                        System.err.println("Warning: Title.txt not found. Using default title.");
                    }
                } catch (Exception e) {
                    windowTitle = "Echo Engine";
                    System.err.println("Warning: Error reading Title.txt. Using default title.");
                }
                runGame(windowTitle);
            } else {
                printToOutput("\n\n THAT IS NOT A VALID INPUT");
            }

            printToOutput("\n\nPRESS ENTER TO CONTINUE... ");
            if (scanner == null) {
                getUserInput();
            } else {
                if (scanner.hasNextLine()) {
                    scanner.nextLine();
                }
            }
        }
    }

    public static void clearScreen() {  
        clearOutput();
    }

    public static int[] move(String direction, String exits, int x, int y, int z, String location) {
        //variables
        int h = 0;
        List<String> inventoryItems = new ArrayList<>();

        //main
        try {
            File file = new File("Save/Inventory.txt");
            Scanner scanner = new Scanner(file);
            while (scanner.hasNextLine()) {
                inventoryItems.add(scanner.nextLine());
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        if (exits.contains(direction)) {
            switch (direction) {
                case "north":
                    y--; // Decrease y to move north
                    break;
                case "south":
                    y++; // Increase y to move south
                    break;
                case "east":
                    x++; // Increase x to move east
                    break;
                case "west":
                    x--; // Decrease x to move west
                    break;
                case "up":
                    z++; // Increase z to move up
                    break;
                case "down":
                    z--; // Decrease z to move down
                break;
            }
        } else {
            printToOutput("\n\nYou can't go that way.");
        }

        if (location.equals("cabin")){
            h = 0;
        }
        else if (location.equals("mansion")){
            h = 1;
        }
        try {
            FileWriter myWriter = new FileWriter("Save/Location.txt");
            myWriter.write("" +h +y +x +z);
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return new int[]{x, y, z};
    }
    

    public static String inventory() {
        //variables
        List<String> inventoryItems = new ArrayList<>();
    
        //main
        try {
            File file = new File("Save/Inventory.txt");
            Scanner scanner = new Scanner(file);
            while (scanner.hasNextLine()) {
                inventoryItems.add(scanner.nextLine());
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    
        // Return a list of the items in the inventory, or "YOUR INVENTORY IS EMPTY" if no items are in the inventory
        if (inventoryItems.isEmpty()) {
            return "\n\nYour inventory is empty";
        } else {
            return "\nYour inventory:\n" + String.join("\n", inventoryItems);
        }
    }

    public static String search(String items, int x, int y, int z, String location) {
        //variables
        Set<String> inventoryHistory = new HashSet<>();
        List<String> itemsFound = new ArrayList<>();
    
        //main
        try {
            File file = new File("Save/Inventory_history.txt");
            Scanner scanner = new Scanner(file);
            while (scanner.hasNextLine()) {
                inventoryHistory.add(scanner.nextLine());
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    
        List<String> itemsList = new ArrayList<>();

        if (location.equals("cabin")){
            try {
                File file = new File("Text/Room_descriptions/Tutorial/y" +y +"_x" +x +"/Items.txt");
                Scanner scanner = new Scanner(file);
                while (scanner.hasNextLine()) {
                    itemsList.add(scanner.nextLine());
                }
                scanner.close();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
        }
        if (location.equals("mansion")){
            try {
                File file = new File("Text/Room_descriptions/Main/Floor_" +z +"/y" +y +"_x" +x +"/Items.txt");
                Scanner scanner = new Scanner(file);
                while (scanner.hasNextLine()) {
                    itemsList.add(scanner.nextLine());
                }
                scanner.close();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
        }
    
        // for (String item : itemsList) {
        //     if (!inventoryHistory.contains(item)) {
        //         if (item.contains("Journal Entry")) {
        //             entries++; // Increment entries if the item is a Journal Entry
        //         }
        //         // The item is not in the inventory history, so add it to both files
        //         try {
        //             Files.write(Paths.get("Save/Inventory.txt"), (item + "\n").getBytes(), StandardOpenOption.APPEND);
        //             Files.write(Paths.get("Save/Inventory_history.txt"), (item + "\n").getBytes(), StandardOpenOption.APPEND);
        //             itemsFound.add(item); // Add the item to the itemsFound list
        //         } catch (IOException e) {
        //             e.printStackTrace();
        //         }
        //     }
        //     // Write entries to the file
        //     try {
        //         FileWriter myWriter = new FileWriter("Save/Journal.txt");
        //         myWriter.write(Integer.toString(entries)); // Convert entries to String
        //         myWriter.close();
        //     } catch (IOException e) {
        //         e.printStackTrace();
        //     }
        // }
    
        // Return a list of the items found, or "YOU FOUND NOTHING" if no new items were found
        if (itemsFound.isEmpty()) {
            return "\n\nYou found nothing";
        } else {
            return "\n\nYou found:\n" + String.join("\n", itemsFound);
        }
    }
    

    // public static String journal(int entries) {
    //     //variables
    //     String journalEntry = " ";
    //     String journalTotal = " ";

    //     //main
    //     for (int i = 1; i <= entries; i++){
    //         try {
    //             File file = new File("Text/Stories/Journal/" +i +".txt");
    //             Scanner scanner = new Scanner(file);
    //             journalEntry = "";
    //             while (scanner.hasNextLine()) {
    //                 journalEntry += scanner.nextLine() + "\n";
    //             }
    //             scanner.close();
    //         } catch (FileNotFoundException e) {
    //             e.printStackTrace();
    //         }
    //         journalTotal += "\n\n";
    //         journalTotal += journalEntry;
    //     }
    //     return journalTotal;
    // }

    @SuppressWarnings("resource")
    public static String use(int x, int y, int z) {
        //variables
        String result = "";

        //main
        // Load required items from Finishing/Required_items.txt (one per line)
        List<String> requiredItems = new ArrayList<>();
        try {
            File file = new File("Finishing/Required_items.txt");
            if (file.exists()) {
                Scanner scanner = new Scanner(file);
                while (scanner.hasNextLine()) {
                    String item = scanner.nextLine().trim();
                    if (!item.isEmpty()) {
                        requiredItems.add(item);
                    }
                }
                scanner.close();
            }
        } catch (Exception e) {
            // ignore
        }

        // Load required location from Finishing/Required_room.txt (x, y, z, each on a new line)
        int requiredX = -1, requiredY = -1, requiredZ = -1;
        try {
            File locFile = new File("Finishing/Required_room.txt");
            if (locFile.exists()) {
                Scanner scanner = new Scanner(locFile);
                if (scanner.hasNextLine()) requiredX = Integer.parseInt(scanner.nextLine().trim());
                if (scanner.hasNextLine()) requiredY = Integer.parseInt(scanner.nextLine().trim());
                if (scanner.hasNextLine()) requiredZ = Integer.parseInt(scanner.nextLine().trim());
                System.out.println("Required location: " + requiredX + ", " + requiredY + ", " + requiredZ);
                scanner.close();
            }
        } catch (Exception e) {
            // ignore
        }

        // Read inventory
        List<String> inventoryItems = new ArrayList<>();
        try {
            File inventoryFile = new File("Save/Inventory.txt");
            Scanner inventoryScanner = new Scanner(inventoryFile);
            while (inventoryScanner.hasNextLine()) {
                inventoryItems.add(inventoryScanner.nextLine());
            }
            inventoryScanner.close();
        } catch (FileNotFoundException e){
            e.printStackTrace();
        }

        // Only allow win if at required location and have all required items
        if (x == requiredX && y == requiredY && z == requiredZ) {
            if (inventoryItems.containsAll(requiredItems) && !requiredItems.isEmpty()) {
                win();
            } else {
                return "\n\nYou don't have all usable items for this room";
            }
        }
        else {
            try {
                // Read the usable items
                File file = new File("Text/Room_descriptions/Main/floor_" + z + "/y" + y + "_x" + x + "/Usable_Items.txt");
                Scanner scanner1 = new Scanner(file);
                if (!scanner1.hasNextLine()) {
                    return "\n\nYou have no usable items for this room";
                }
                String[] usableItems = scanner1.nextLine().split(","); // Get the first line and split by comma
                String itemDescription = scanner1.hasNextLine() ? scanner1.nextLine() : ""; // Get the second line
                String newItem = scanner1.hasNextLine() ? scanner1.nextLine() : ""; // Get the third line
                scanner1.close();

                // Check if the items are in the inventory
                List<String> missingItems = new ArrayList<>();
                for (String item : usableItems) {
                    if (!inventoryItems.contains(item.trim())) {
                        missingItems.add(item.trim());
                    }
                }

                if (missingItems.isEmpty()) {
                    // Remove the items from the inventory
                    for (String item : usableItems) {
                        inventoryItems.remove(item.trim());
                    }
                    File inventoryFile = new File("Save/Inventory.txt");
                    FileWriter inventoryWriter = new FileWriter(inventoryFile);
                    for (String item : inventoryItems) {
                        inventoryWriter.write(item + "\n");
                    }
                    inventoryWriter.close();

                    // Add the new item to the inventory and inventory history
                    FileWriter inventoryWriter2 = new FileWriter(inventoryFile, true); // Append mode
                    inventoryWriter2.write(newItem + "\n");
                    inventoryWriter2.close();

                    FileWriter inventoryHistoryWriter = new FileWriter("Save/Inventory_history.txt", true); // Append mode
                    inventoryHistoryWriter.write(newItem + "\n");
                    inventoryHistoryWriter.close();

                    // Return the result
                    result = "Used " + String.join(", ", usableItems) + ".\n\n " + itemDescription + "\n\nYou found:\n" +newItem;
                } else {
                    result = "You are missing one or more items";
                }
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        return result;
    }

    public static boolean checkInventoryTutorial() {
        // Load required items from Tutorial/required_items.txt (one per line)
        List<String> requiredItems = new ArrayList<>();
        try {
            File file = new File("Tutorial/required_items.txt");
            if (file.exists()) {
                Scanner scanner = new Scanner(file);
                while (scanner.hasNextLine()) {
                    String item = scanner.nextLine().trim();
                    if (!item.isEmpty()) {
                        requiredItems.add(item);
                    }
                }
                scanner.close();
            } else {
                System.err.println("Warning: required_items.txt not found. No required items for tutorial.");
            }
        } catch (Exception e) {
            System.err.println("Warning: Error reading required_items.txt. No required items for tutorial.");
        }

        // Read the inventory file
        List<String> inventoryItems = new ArrayList<>();
        try {
            File file = new File("Save/Inventory.txt");
            if (file.exists()) {
                Scanner scanner = new Scanner(file);
                while (scanner.hasNextLine()) {
                    inventoryItems.add(scanner.nextLine());
                }
                scanner.close();
            } else {
                System.err.println("Warning: Inventory.txt not found. Inventory is empty.");
            }
        } catch (Exception e) {
            System.err.println("Warning: Error reading Inventory.txt. Inventory is empty.");
        }

        // Check if all required items are in the inventory
        return inventoryItems.containsAll(requiredItems);
    }
    
    public static void gameOver() {
        clearOutput();
        String description = "";
        String gameOverText = "GAME OVER";

        try {
            File file = new File("Text/Stories/Ending/Game_over.txt");
            Scanner scanner1 = new Scanner(file);
            description = "";
            while (scanner1.hasNextLine()) {
                description += scanner1.nextLine() + "\n";
            }
            scanner1.close();
        } catch (FileNotFoundException e) {
            description = "Game over text not found.";
        }
        printToOutput(description);
        printToOutput("\n\n\n" + gameOverText);
        reset();
        printToOutput("\n\nPress ENTER to exit...");
        getUserInput();
        System.exit(0);
    }

    public static void win() {
        clearOutput();
        String description = "";
        String winText = "YOU WIN";

        try {
            File file = new File("Text/Stories/Ending/win.txt");
            Scanner scanner1 = new Scanner(file);
            description = "";
            while (scanner1.hasNextLine()) {
                description += scanner1.nextLine() + "\n";
            }
            scanner1.close();
        } catch (FileNotFoundException e) {
            description = "Win text not found.";
        }
        printToOutput(description);
        printToOutput("\n\n\n" + winText);
        reset();
        printToOutput("\n\nPress ENTER to exit...");
        getUserInput();
        System.exit(0);
    }

    public static void reset() {
        try {
            FileWriter myWriter = new FileWriter("Save/Location.txt");
            myWriter.write("2");
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            FileWriter myWriter = new FileWriter("Save/Inventory.txt");
            myWriter.write("");
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            FileWriter myWriter = new FileWriter("Save/Inventory_history.txt");
            myWriter.write("");
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            FileWriter myWriter = new FileWriter("Save/Journal.txt");
            myWriter.write("0");
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        // Set health to the value in defaulthealth.txt
        String defaultHealth = "20";
        try {
            File file = new File("Finishing/Default_health.txt");
            if (file.exists()) {
                Scanner scanner = new Scanner(file);
                if (scanner.hasNextLine()) {
                    defaultHealth = scanner.nextLine().trim();
                }
                scanner.close();
            }
        } catch (Exception e) {
            // ignore, fallback to 20
        }
        try {
            FileWriter myWriter = new FileWriter("Save/Health.txt");
            myWriter.write(defaultHealth);
            myWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}