// Jack Murray | Nova Foundry
// Echo Engine
// v 3.0.0

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Text;
using System.IO;
using System.Media;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace EchoEngine
{
    public partial class MainForm : Form
    {
        private TextBox outputArea;
        private StringBuilder outputBuffer = new StringBuilder();
        private volatile string userInput = null;
        private readonly object inputLock = new object();
        private int promptPosition = 0;

        // Always scroll to the end of the output area
        private void ScrollToEnd()
        {
            this.Invoke((MethodInvoker)delegate
            {
                outputArea.SelectionStart = outputArea.Text.Length;
                outputArea.ScrollToCaret();
            });
        }

        public MainForm()
        {
            InitializeComponent();

            // Read the title from the text file
            string windowTitle = "";
            try
            {
                string titlePath = Path.Combine("Text", "Misc", "Title.txt");
                if (File.Exists(titlePath))
                {
                    using (StreamReader titleReader = new StreamReader(titlePath))
                    {
                        windowTitle = titleReader.ReadLine() ?? "Echo Engine";
                        if (string.IsNullOrEmpty(windowTitle))
                        {
                            windowTitle = "Echo Engine";
                            Console.Error.WriteLine("Warning: Title.txt is empty. Using default title.");
                        }
                    }
                }
                else
                {
                    windowTitle = "Echo Engine";
                    Console.Error.WriteLine("Warning: Title.txt not found. Using default title.");
                }
            }
            catch (Exception)
            {
                windowTitle = "Echo Engine";
                Console.Error.WriteLine("Warning: Error reading Title.txt. Using default title.");
            }

            this.Text = windowTitle;

            // Start playing sound in the background
            Thread soundThread = new Thread(() =>
            {
                try
                {
                    SoundPlayer player = new SoundPlayer(Path.Combine("Sounds", "Background.wav"));
                    player.PlayLooping();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
            });
            soundThread.IsBackground = true;
            soundThread.Start();

            // Setup GUI
            try
            {
                Application.SetCompatibleTextRenderingDefault(false);
            }
            catch { }

            this.FormBorderStyle = FormBorderStyle.None;
            this.WindowState = FormWindowState.Maximized;

            // Set app icon
            try
            {
                Icon icon = null;
                string iconPath = Path.Combine("Icons", "Icon.png");
                if (File.Exists(iconPath))
                {
                    icon = new Icon(iconPath);
                }
                else
                {
                    string defaultIconPath = Path.Combine("Icons", "Default_icon.png");
                    if (File.Exists(defaultIconPath))
                    {
                        icon = new Icon(defaultIconPath);
                    }
                }
                if (icon != null)
                {
                    this.Icon = icon;
                }
            }
            catch { }

            // Load custom fonts if available, else fallback
            PrivateFontCollection privateFonts = new PrivateFontCollection();
            Font? mainFont = null;
            Font? titleFont = null;
            try
            {
                string fontPath = Path.Combine("Fonts", "Font.ttf");
                if (File.Exists(fontPath))
                {
                    privateFonts.AddFontFile(fontPath);
                    mainFont = new Font(privateFonts.Families[0], 16f, FontStyle.Regular);
                }
            }
            catch
            {
                mainFont = null;
            }
            try
            {
                string titleFontPath = Path.Combine("Fonts", "Title_font.ttf");
                if (File.Exists(titleFontPath))
                {
                    privateFonts.AddFontFile(titleFontPath);
                    titleFont = new Font(privateFonts.Families[0], 16f, FontStyle.Bold);
                }
            }
            catch
            {
                titleFont = null;
            }
            // Fallback to Default.ttf if needed
            if (mainFont == null)
            {
                try
                {
                    string defaultFontPath = Path.Combine("Fonts", "Default.ttf");
                    if (File.Exists(defaultFontPath))
                    {
                        privateFonts.AddFontFile(defaultFontPath);
                        mainFont = new Font(privateFonts.Families[0], 16f, FontStyle.Regular);
                    }
                }
                catch
                {
                    mainFont = null;
                }
            }
            if (titleFont == null)
            {
                try
                {
                    string defaultFontPath = Path.Combine("Fonts", "Default.ttf");
                    if (File.Exists(defaultFontPath))
                    {
                        privateFonts.AddFontFile(defaultFontPath);
                        titleFont = new Font(privateFonts.Families[0], 16f, FontStyle.Regular);
                    }
                }
                catch
                {
                    titleFont = null;
                }
            }
            // Final fallback to Consolas
            if (mainFont == null)
            {
                mainFont = new Font("Consolas", 16f, FontStyle.Regular);
            }
            if (titleFont == null)
            {
                titleFont = new Font("Consolas", 16f, FontStyle.Bold);
            }

            Panel titleBar = new Panel
            {
                Dock = DockStyle.Top,
                Height = 30,
                BackColor = Color.Transparent
            };
            titleBar.Paint += (sender, e) =>
            {
                e.Graphics.FillRectangle(Brushes.Black, 0, 0, titleBar.Width, titleBar.Height);
            };

            Label titleLabel = new Label
            {
                Text = " " + windowTitle,
                ForeColor = Color.FromArgb(220, 220, 220),
                Font = titleFont,
                Dock = DockStyle.Left,
                AutoSize = true
            };
            titleBar.Controls.Add(titleLabel);

            Panel buttonPanel = new Panel
            {
                Dock = DockStyle.Right,
                BackColor = Color.Transparent
            };
            Button minBtn = new Button
            {
                Text = "-",
                ForeColor = Color.White,
                BackColor = Color.Black,
                FlatStyle = FlatStyle.Flat,
                Width = 45,
                Height = 28
            };
            minBtn.FlatAppearance.BorderSize = 0;
            minBtn.Click += (s, e) => this.WindowState = FormWindowState.Minimized;
            buttonPanel.Controls.Add(minBtn);

            Button closeBtn = new Button
            {
                Text = "X",
                ForeColor = Color.White,
                BackColor = Color.Black,
                FlatStyle = FlatStyle.Flat,
                Width = 45,
                Height = 28
            };
            closeBtn.FlatAppearance.BorderSize = 0;
            closeBtn.Click += (s, e) => Application.Exit();
            buttonPanel.Controls.Add(closeBtn);
            closeBtn.Dock = DockStyle.Right;
            minBtn.Dock = DockStyle.Right;

            titleBar.Controls.Add(buttonPanel);

            Point? mouseDownCompCoords = null;
            titleBar.MouseDown += (s, e) => mouseDownCompCoords = e.Location;
            titleBar.MouseUp += (s, e) => mouseDownCompCoords = null;
            titleBar.MouseMove += (s, e) =>
            {
                if (mouseDownCompCoords.HasValue)
                {
                    Point currCoords = titleBar.PointToScreen(e.Location);
                    this.Location = new Point(currCoords.X - mouseDownCompCoords.Value.X, currCoords.Y - mouseDownCompCoords.Value.Y);
                }
            };

            outputArea = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                WordWrap = true,
                AcceptsReturn = true,
                Font = mainFont,
                BackColor = Color.Black,
                ForeColor = Color.FromArgb(220, 220, 220),
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle
            };

            Panel contentPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.Black
            };
            contentPanel.Controls.Add(outputArea);
            contentPanel.Controls.Add(titleBar);

            this.Controls.Add(contentPanel);
            this.BackColor = Color.Black;

            outputArea.KeyDown += OutputArea_KeyDown;
            outputArea.KeyPress += OutputArea_KeyPress;

            this.Shown += (s, e) =>
            {
                outputArea.Focus();
                new Thread(() => ShowLogoAndStart(windowTitle)).Start();
            };
        }

        private void OutputArea_KeyPress(object? sender, KeyPressEventArgs e)
        {
            if (outputArea.SelectionStart < promptPosition)
            {
                outputArea.SelectionStart = outputArea.Text.Length;
                e.Handled = true;
            }
        }

        private void OutputArea_KeyDown(object? sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Back && outputArea.SelectionStart <= promptPosition)
            {
                e.Handled = true;
                return;
            }
            if (e.KeyCode == Keys.Enter)
            {
                if (outputArea.SelectionStart >= promptPosition)
                {
                    string text = outputArea.Text;
                    string input = text.Substring(promptPosition).Replace("\n", "").Trim();
                    lock (inputLock)
                    {
                        userInput = input;
                        Monitor.PulseAll(inputLock);
                    }
                    outputArea.SelectionStart = outputArea.Text.Length;
                }
                e.Handled = true;
            }
        }

        // Show the Echo Engine logo (ASCII art from txt) centered for 2 seconds, then start the game
        private void ShowLogoAndStart(string windowTitle)
        {
            string logo = "";
            try
            {
                string logoPath = Path.Combine("Icons", "Echo_engine_logo.txt");
                if (File.Exists(logoPath))
                {
                    logo = File.ReadAllText(logoPath);
                }
                else
                {
                    logo = "[Echo Engine Logo Not Found]";
                }
            }
            catch
            {
                logo = "[Echo Engine Logo Error]";
            }

            // Center logo in outputArea (both vertically and horizontally, and fit to area)
            Font originalFont = outputArea.Font;
            float logoFontSize = Math.Max(8f, originalFont.Size * 0.75f);
            Font logoFont = new Font(originalFont.FontFamily, logoFontSize);

            this.Invoke((MethodInvoker)delegate
            {
                outputArea.Font = logoFont;
                outputBuffer.Length = 0;
                outputArea.Text = "";
                // Get logo lines
                string[] logoLines = logo.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
                // Calculate output area width in characters
                using (Graphics g = outputArea.CreateGraphics())
                {
                    int areaWidthPx = outputArea.Width;
                    float charWidthF = g.MeasureString("W", outputArea.Font).Width;
                    int charWidth = (int)charWidthF;
                    int areaWidthChars = Math.Max(10, areaWidthPx / charWidth); // avoid divide by zero
                    // Center each line horizontally and fit to width
                    StringBuilder centeredLogo = new StringBuilder();
                    int maxLogoWidth = 0;
                    foreach (string line in logoLines)
                    {
                        if (line.Length > maxLogoWidth) maxLogoWidth = line.Length;
                    }
                    foreach (string line in logoLines)
                    {
                        string trimmed = line.Length > areaWidthChars ? line.Substring(0, areaWidthChars) : line;
                        int horizontalPadding = (areaWidthChars - trimmed.Length) / 2;
                        for (int i = 0; i < horizontalPadding; i++) centeredLogo.Append(' ');
                        centeredLogo.AppendLine(trimmed);
                    }
                    // Calculate padding for vertical centering
                    int lines = logoLines.Length;
                    int areaHeight = outputArea.Height;
                    float fontHeightF = g.MeasureString("A", outputArea.Font).Height;
                    int fontHeight = (int)fontHeightF;
                    int padLines = Math.Max(0, (areaHeight / fontHeight - lines) / 2);
                    StringBuilder verticalPad = new StringBuilder();
                    for (int i = 0; i < padLines; i++) verticalPad.AppendLine();
                    outputArea.Text = verticalPad + centeredLogo.ToString();
                    outputArea.SelectionStart = 0;
                }
            });
            Thread.Sleep(2000);

            this.Invoke((MethodInvoker)delegate
            {
                outputArea.Font = originalFont;
            });

            new Thread(() => RunGame(windowTitle)).Start();
        }

        // Wait for user input from the GUI
        public string GetUserInput()
        {
            PrintPrompt();
            lock (inputLock)
            {
                while (userInput == null)
                {
                    Monitor.Wait(inputLock);
                }
                string input = userInput!;
                userInput = null;
                return input;
            }
        }

        private void PrintPrompt()
        {
            this.Invoke((MethodInvoker)delegate
            {
                outputBuffer.Append("");
                outputArea.Text = outputBuffer.ToString();
                ScrollToEnd();
                promptPosition = outputArea.Text.Length;
            });
        }

        // Print to the output area (with optional delay for typewriter effect and skip on space)
        public void PrintToOutput(string text, int delayMs = 0)
        {
            text = text.Replace("\n", Environment.NewLine);
            bool skip = false;
            KeyEventHandler skipHandler = delegate(object? sender, KeyEventArgs e)
            {
                if (e.KeyCode == Keys.Space)
                {
                    skip = true;
                }
            };
            outputArea.KeyDown += skipHandler;
            try
            {
                int index = 0;
                while (index < text.Length)
                {
                    if (skip)
                    {
                        this.Invoke((MethodInvoker)delegate
                        {
                            outputBuffer.Append(text.Substring(index));
                            outputArea.Text = outputBuffer.ToString();
                            ScrollToEnd();
                            promptPosition = outputArea.Text.Length;
                        });
                        break;
                    }
                    char c = text[index++];
                    this.Invoke((MethodInvoker)delegate
                    {
                        outputBuffer.Append(c);
                        outputArea.Text = outputBuffer.ToString();
                        ScrollToEnd();
                        promptPosition = outputArea.Text.Length;
                    });
                    if (delayMs > 0)
                    {
                        Thread.Sleep(delayMs);
                    }
                }
            }
            finally
            {
                outputArea.KeyDown -= skipHandler;
            }
        }

        public void ClearOutput()
        {
            this.Invoke((MethodInvoker)delegate
            {
                outputBuffer.Length = 0;
                outputArea.Text = "";
                promptPosition = 0;
                ScrollToEnd();
            });
        }

        // Main game logic (refactored from main)
        public void RunGame(string windowTitle)
        {
            string menuText = windowTitle + Environment.NewLine + Environment.NewLine + " MAIN MENU" + Environment.NewLine + Environment.NewLine + "  PLAY    - [1]" + Environment.NewLine + "  HELP    - [2]" + Environment.NewLine + "  EXIT    - [3]" + Environment.NewLine + "  CREDITS - [4]" + Environment.NewLine + "  RESET   - [5]" + Environment.NewLine + Environment.NewLine + " >> ";
            string helpText = "TO NAVIGATE THE WORLD, USE SIMPLE COMMANDS" + Environment.NewLine + Environment.NewLine + "AVALABLE COMMANDS:" + Environment.NewLine + " north" + Environment.NewLine + " south" + Environment.NewLine + " east" + Environment.NewLine + " west" + Environment.NewLine + " up" + Environment.NewLine + " down" + Environment.NewLine + " inventory" + Environment.NewLine + " search" + Environment.NewLine + " use" + Environment.NewLine + " menu";
            int menuInput = 0;
            string? location = null;
            bool menuLoop = true;

            ClearOutput();
            PrintToOutput("CLICK AND PRESS ENTER TO START... ");
            GetUserInput();
            ClearOutput();

            while (menuLoop)
            {
                PrintToOutput(menuText, 10);
                string input = GetUserInput();
                if (int.TryParse(input.Trim(), out menuInput))
                {
                    // parsed
                }
                else
                {
                    menuInput = -1;
                }
                if (menuInput == 1)
                {
                    try
                    {
                        string filePath = Path.Combine("Save", "Location.txt");
                        if (File.Exists(filePath))
                        {
                            using (StreamReader reader = new StreamReader(filePath))
                            {
                                location = reader.ReadLine();
                                if (string.IsNullOrEmpty(location))
                                {
                                    location = "2";
                                    Console.Error.WriteLine("Warning: Location.txt is empty. Starting at prolog.");
                                }
                            }
                        }
                        else
                        {
                            location = "2";
                            Console.Error.WriteLine("Warning: Location.txt not found. Starting at prolog.");
                        }
                    }
                    catch
                    {
                        location = "2";
                        Console.Error.WriteLine("Warning: Error reading Location.txt. Starting at prolog.");
                    }
                    if (location == "2")
                    {
                        Prolog(null);
                    }
                    else if (location.Length >= 3 && location[0] == '0')
                    {
                        ClearOutput();
                        Tutorial(location[1] - '0', location[2] - '0', null);
                    }
                    else if (location.Length >= 4 && location[0] == '1')
                    {
                        ClearOutput();
                        Game(location[1] - '0', location[2] - '0', location[3] - '0', null);
                    }
                    else
                    {
                        Console.Error.WriteLine("Warning: Location.txt has invalid content. Starting at prolog.");
                        Prolog(null);
                    }
                }
                else if (menuInput == 2)
                {
                    ClearOutput();
                    PrintToOutput(helpText, 10);
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
                    GetUserInput();
                    ClearOutput();
                }
                else if (menuInput == 3)
                {
                    menuLoop = false;
                }
                else if (menuInput == 4)
                {
                    string creditsPath = Path.Combine("Text", "Misc", "Credits.txt");
                    string creditsText = "";
                    try
                    {
                        if (File.Exists(creditsPath))
                        {
                            creditsText = File.ReadAllText(creditsPath).Replace("\n", Environment.NewLine);
                        }
                        else
                        {
                            creditsText = "Credits not found.";
                        }
                    }
                    catch
                    {
                        creditsText = "Credits not found.";
                    }
                    PrintToOutput(Environment.NewLine + Environment.NewLine + creditsText);
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
                    GetUserInput();
                    ClearOutput();
                }
                else if (menuInput == 5)
                {
                    Reset();
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "RESET" + Environment.NewLine + Environment.NewLine + " PLEASE RESTART THE PROGRAM");
                    GetUserInput();
                    Application.Exit();
                }
                else
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "THAT IS NOT A VAILD INPUT");
                    Thread.Sleep(2000);
                    ClearOutput();
                }
            }
            Application.Exit();
        }

        public void Prolog(StreamReader? scanner)
        {
            string displayText = " ";

            ClearOutput();
            Reset();
            //prolog part 1
            try
            {
                string filePath = Path.Combine("Text", "Stories", "Prolog", "Prolog.txt");
                displayText = File.ReadAllText(filePath).Replace("\n", Environment.NewLine);
            }
            catch
            {
                displayText = "Prolog not found.";
            }
            PrintToOutput(Environment.NewLine + Environment.NewLine + displayText, 10);
            PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
            GetUserInput();
            ClearOutput();
            Tutorial(1, 1, scanner);
        }

        public void Tutorial(int inputY, int inputX, StreamReader? scanner)
        {
            int x = inputX;
            int y = inputY;
            string optionsText = Environment.NewLine + Environment.NewLine + " INPUT >> ";
            string helpText = Environment.NewLine + Environment.NewLine + "AVALABLE COMMANDS:" + Environment.NewLine + " north" + Environment.NewLine + " south" + Environment.NewLine + " east" + Environment.NewLine + " west" + Environment.NewLine + " up" + Environment.NewLine + " down" + Environment.NewLine + " inventory" + Environment.NewLine + " search" + Environment.NewLine + " use" + Environment.NewLine + " menu";
            string description = " ";
            string exits = " ";
            string items = " ";
            string input = " ";
            bool tutorialDone = false;

            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Location.txt")))
                {
                    writer.Write("0" + y + x + "1");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            bool firstLoop = true;
            while (!tutorialDone)
            {
                //load data
                try
                {
                    string descPath = Path.Combine("Text", "Room_descriptions", "Tutorial", "y" + y + "_x" + x, "Description.txt");
                    if (File.Exists(descPath))
                    {
                        description = File.ReadAllText(descPath).Replace("\n", Environment.NewLine);
                    }
                    else
                    {
                        description = "Room description not found.";
                    }
                }
                catch
                {
                    description = "Room description error.";
                }
                try
                {
                    string exitsPath = Path.Combine("Text", "Room_descriptions", "Tutorial", "y" + y + "_x" + x, "Exits.txt");
                    if (File.Exists(exitsPath))
                    {
                        using (StreamReader reader = new StreamReader(exitsPath))
                        {
                            exits = reader.ReadLine() ?? "";
                        }
                    }
                    else
                    {
                        exits = "";
                    }
                }
                catch
                {
                    exits = "";
                }
                //display data
                if (!firstLoop) ClearOutput();
                PrintToOutput(description, 10);
                PrintToOutput(Environment.NewLine + Environment.NewLine + " Possible Exits: " + exits);
                PrintToOutput(helpText);
                PrintToOutput(optionsText);
                firstLoop = false;
                if (scanner == null)
                {
                    input = GetUserInput();
                }
                else
                {
                    input = scanner.ReadLine() ?? "";
                }
                //Game options
                if (input == "north" || input == "south" || input == "east" || input == "west")
                {
                    int[] returned = Move(input, exits, x, y, 0, "cabin");
                    x = returned[0];
                    y = returned[1];
                }
                else if (input == "up" || input == "down")
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "You can't go that way.");
                }
                else if (input == "inventory")
                {
                    PrintToOutput(Inventory());
                }
                else if (input == "search")
                {
                    string foundMsg = Search(items, x, y, 0, "cabin");
                    PrintToOutput("\n");
                    PrintToOutput(foundMsg);
                    if (!foundMsg.Trim().Equals("You found nothing", StringComparison.OrdinalIgnoreCase))
                    {
                        PrintToOutput("\n");
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
                else if (input == "use")
                {
                    PrintToOutput("\n You can't do that here");
                }
                else if (input == "menu")
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "Returning to main menu...");
                    // Read the title from the text file
                    string winTitle = "";
                    try
                    {
                        string titlePath = Path.Combine("Text", "Misc", "Title.txt");
                        if (File.Exists(titlePath))
                        {
                            using (StreamReader titleReader = new StreamReader(titlePath))
                            {
                                winTitle = titleReader.ReadLine() ?? "Echo Engine";
                            }
                        }
                        else
                        {
                            winTitle = "Echo Engine";
                        }
                    }
                    catch
                    {
                        winTitle = "Echo Engine";
                    }
                    RunGame(winTitle);
                }
                else
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + " THAT IS NOT A VALID INPUT");
                }

                PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
                if (scanner == null)
                {
                    GetUserInput();
                }
                else
                {
                    scanner.ReadLine();
                }

                //check if we're done
                if (CheckInventoryTutorial())
                {
                    tutorialDone = true;
                }
            }

            ClearOutput();
            string desc = "";
            try
            {
                string filePath = Path.Combine("Text", "Stories", "Tutorial", "Tutorial_completed.txt");
                desc = File.ReadAllText(filePath).Replace("\n", Environment.NewLine);
            }
            catch
            {
                desc = "Leaving the cabin text not found.";
            }
            PrintToOutput(desc);
            PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
            if (scanner == null)
            {
                GetUserInput();
            }
            else
            {
                scanner.ReadLine();
            }
            Game(1, 1, 1, scanner);
        }

        public void Game(int inputY, int inputX, int inputZ, StreamReader? scanner)
        {
            Random rand = new Random();
            int damageChance = 10;
            try
            {
                string filePath = Path.Combine("Finishing", "Damage_chance.txt");
                if (File.Exists(filePath))
                {
                    using (StreamReader reader = new StreamReader(filePath))
                    {
                        string? line = reader.ReadLine()?.Trim();
                        if (!string.IsNullOrEmpty(line))
                        {
                            damageChance = int.Parse(line);
                        }
                    }
                }
            }
            catch { }
            int toHaunt = rand.Next(damageChance) + 1;
            int sanity = 1;
            int x = inputX;
            int y = inputY;
            int z = inputZ;
            string optionsText = Environment.NewLine + Environment.NewLine + " INPUT >> ";
            string helpText = Environment.NewLine + Environment.NewLine + "AVALABLE COMMANDS:" + Environment.NewLine + " north" + Environment.NewLine + " south" + Environment.NewLine + " east" + Environment.NewLine + " west" + Environment.NewLine + " up" + Environment.NewLine + " down" + Environment.NewLine + " inventory" + Environment.NewLine + " search" + Environment.NewLine + " use" + Environment.NewLine + " menu";
            string description = " ";
            string exits = " ";
            string items = " ";
            string haunting = " ";
            string input = " ";
            string used = " ";
            bool gameDone = false;

            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Location.txt")))
                {
                    writer.Write("1" + y + x + z);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            try
            {
                string healthPath = Path.Combine("Save", "Health.txt");
                if (File.Exists(healthPath))
                {
                    string? line = File.ReadAllText(healthPath).Trim();
                    if (!string.IsNullOrEmpty(line))
                    {
                        sanity = int.Parse(line);
                    }
                }
            }
            catch { }

            while (!gameDone)
            {
                //load data
                try
                {
                    string descPath = Path.Combine("Text", "Room_descriptions", "Main", "floor_" + z, "y" + y + "_x" + x, "Description.txt");
                    description = File.ReadAllText(descPath).Replace("\n", Environment.NewLine);
                }
                catch
                {
                    description = "Room description not found.";
                }
                try
                {
                    string exitsPath = Path.Combine("Text", "Room_descriptions", "Main", "floor_" + z, "y" + y + "_x" + x, "Exits.txt");
                    using (StreamReader reader = new StreamReader(exitsPath))
                    {
                        exits = reader.ReadLine() ?? "";
                    }
                }
                catch
                {
                    exits = "";
                }
                toHaunt = rand.Next(5) + 1;
                try
                {
                    string hauntPath = Path.Combine("Text", "Room_descriptions", "Main", "floor_" + z, "y" + y + "_x" + x, "Strange_occerance.txt");
                    haunting = File.ReadAllText(hauntPath).Replace("\n", Environment.NewLine);
                }
                catch
                {
                    haunting = "";
                }
                //display data
                ClearOutput();
                PrintToOutput("HEALTH: ");
                for (int i = 0; i < sanity; i++)
                {
                    PrintToOutput("#");
                }
                PrintToOutput(Environment.NewLine + Environment.NewLine);
                PrintToOutput(description, 10);
                if (toHaunt == 1)
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + haunting);
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "Your health has decreased");
                    if (sanity > 0)
                    {
                        sanity--;
                        try
                        {
                            using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Health.txt")))
                            {
                                writer.Write(sanity.ToString());
                            }
                        }
                        catch { }
                    }
                }
                if (sanity == 0)
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
                    if (scanner == null)
                    {
                        GetUserInput();
                    }
                    else
                    {
                        scanner.ReadLine();
                    }
                    GameOver();
                }
                PrintToOutput(Environment.NewLine + Environment.NewLine + " Possible Exits: " + exits);
                PrintToOutput(helpText);
                PrintToOutput(optionsText);
                if (scanner == null)
                {
                    input = GetUserInput();
                }
                else
                {
                    input = scanner.ReadLine() ?? "";
                }
                //game actions
                if (input == "north" || input == "south" || input == "east" || input == "west" || input == "up" || input == "down")
                {
                    int[] returned = Move(input, exits, x, y, z, "mansion");
                    x = returned[0];
                    y = returned[1];
                    z = returned[2];
                }
                else if (input == "inventory")
                {
                    PrintToOutput(Inventory());
                }
                else if (input == "search")
                {
                    string foundMsg = Search(items, x, y, z, "mansion");
                    PrintToOutput("\n");
                    PrintToOutput(foundMsg);
                    if (!foundMsg.Trim().Equals("You found nothing", StringComparison.OrdinalIgnoreCase))
                    {
                        PrintToOutput("\n");
                    }
                }
                // else if (input == "journal"){
                //     PrintToOutput("\n\n");
                //     string journal2 = "";
                //     try {
                //         string filePath = Path.Combine("Text", "Stories", "Tutorial", "Journal.txt");
                //         journal2 = File.ReadAllText(filePath);
                //     }
                //     catch
                //     {
                //         journal2 = "Journal not found.";
                //     }
                //     PrintToOutput(journal2);
                //     string journalTemp = Journal(journal);
                //     PrintToOutput(journalTemp);
                // }
                else if (input == "use")
                {
                    used = Use(x, y, z);
                    PrintToOutput(used);
                }
                else if (input == "menu")
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + "Returning to main menu...");
                    // Read the title from the text file
                    string winTitle = "";
                    try
                    {
                        string titlePath = Path.Combine("Text", "Misc", "Title.txt");
                        if (File.Exists(titlePath))
                        {
                            using (StreamReader titleReader = new StreamReader(titlePath))
                            {
                                winTitle = titleReader.ReadLine() ?? "Echo Engine";
                            }
                        }
                        else
                        {
                            winTitle = "Echo Engine";
                        }
                    }
                    catch
                    {
                        winTitle = "Echo Engine";
                    }
                    RunGame(winTitle);
                }
                else
                {
                    PrintToOutput(Environment.NewLine + Environment.NewLine + " THAT IS NOT A VALID INPUT");
                }

                PrintToOutput(Environment.NewLine + Environment.NewLine + "PRESS ENTER TO CONTINUE... ");
                if (scanner == null)
                {
                    GetUserInput();
                }
                else
                {
                    scanner.ReadLine();
                }
            }
        }

        public void ClearScreen()
        {
            ClearOutput();
        }

        public new int[] Move(string direction, string exits, int x, int y, int z, string location)
        {
            int h = 0;
            List<string> inventoryItems = new List<string>();

            try
            {
                string invPath = Path.Combine("Save", "Inventory.txt");
                inventoryItems = new List<string>(File.ReadAllLines(invPath));
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            if (exits.Contains(direction))
            {
                switch (direction)
                {
                    case "north":
                        y--;
                        break;
                    case "south":
                        y++;
                        break;
                    case "east":
                        x++;
                        break;
                    case "west":
                        x--;
                        break;
                    case "up":
                        z++;
                        break;
                    case "down":
                        z--;
                        break;
                }
            }
            else
            {
                PrintToOutput(Environment.NewLine + Environment.NewLine + "You can't go that way.");
            }

            if (location == "cabin")
            {
                h = 0;
            }
            else if (location == "mansion")
            {
                h = 1;
            }
            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Location.txt")))
                {
                    writer.Write("" + h + y + x + z);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            return new int[] { x, y, z };
        }

        public string Inventory()
        {
            List<string> inventoryItems = new List<string>();

            try
            {
                string invPath = Path.Combine("Save", "Inventory.txt");
                inventoryItems = new List<string>(File.ReadAllLines(invPath));
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            if (inventoryItems.Count == 0)
            {
                return Environment.NewLine + Environment.NewLine + "Your inventory is empty";
            }
            else
            {
                return Environment.NewLine + "Your inventory:" + Environment.NewLine + string.Join(Environment.NewLine, inventoryItems);
            }
        }

        public string Search(string items, int x, int y, int z, string location)
        {
            HashSet<string> inventoryHistory = new HashSet<string>();
            List<string> itemsFound = new List<string>();
            int entries = 0;

            try
            {
                string histPath = Path.Combine("Save", "Inventory_history.txt");
                foreach (string line in File.ReadLines(histPath))
                {
                    inventoryHistory.Add(line);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            List<string> itemsList = new List<string>();

            if (location == "cabin")
            {
                try
                {
                    string itemsPath = Path.Combine("Text", "Room_descriptions", "Tutorial", "y" + y + "_x" + x, "Items.txt");
                    itemsList = new List<string>(File.ReadAllLines(itemsPath));
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
            }
            else if (location == "mansion")
            {
                try
                {
                    string itemsPath = Path.Combine("Text", "Room_descriptions", "Main", "Floor_" + z, "y" + y + "_x" + x, "Items.txt");
                    itemsList = new List<string>(File.ReadAllLines(itemsPath));
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
            }

            foreach (string item in itemsList)
            {
                if (!inventoryHistory.Contains(item))
                {
                    if (item.Contains("Journal Entry"))
                    {
                        entries++;
                    }
                    try
                    {
                        string invPath = Path.Combine("Save", "Inventory.txt");
                        File.AppendAllText(invPath, item + Environment.NewLine);
                        string histPath = Path.Combine("Save", "Inventory_history.txt");
                        File.AppendAllText(histPath, item + Environment.NewLine);
                        itemsFound.Add(item);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                }
            }
            try
            {
                File.WriteAllText(Path.Combine("Save", "Journal.txt"), entries.ToString());
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            if (itemsFound.Count == 0)
            {
                return Environment.NewLine + Environment.NewLine + "You found nothing";
            }
            else
            {
                return Environment.NewLine + Environment.NewLine + "You found:" + Environment.NewLine + string.Join(Environment.NewLine, itemsFound);
            }
        }

        // public string Journal(int entries)
        // {
        //     string journalEntry = " ";
        //     string journalTotal = " ";

        //     for (int i = 1; i <= entries; i++)
        //     {
        //         try
        //         {
        //             string filePath = Path.Combine("Text", "Stories", "Journal", i + ".txt");
        //             journalEntry = File.ReadAllText(filePath);
        //         }
        //         catch (Exception ex)
        //         {
        //             Console.WriteLine(ex.ToString());
        //         }
        //         journalTotal += "\n\n";
        //         journalTotal += journalEntry;
        //     }
        //     return journalTotal;
        // }

        public string Use(int x, int y, int z)
        {
            string result = "";

            // Load required items from Finishing/Required_items.txt (one per line)
            List<string> requiredItems = new List<string>();
            try
            {
                string reqPath = Path.Combine("Finishing", "Required_items.txt");
                if (File.Exists(reqPath))
                {
                    foreach (string line in File.ReadLines(reqPath))
                    {
                        string item = line.Trim();
                        if (!string.IsNullOrEmpty(item))
                        {
                            requiredItems.Add(item);
                        }
                    }
                }
            }
            catch { }

            // Load required location from Finishing/Required_room.txt (x, y, z, each on a new line)
            int requiredX = -1, requiredY = -1, requiredZ = -1;
            try
            {
                string locPath = Path.Combine("Finishing", "Required_room.txt");
                if (File.Exists(locPath))
                {
                    string[] lines = File.ReadAllLines(locPath);
                    if (lines.Length > 0) int.TryParse(lines[0].Trim(), out requiredX);
                    if (lines.Length > 1) int.TryParse(lines[1].Trim(), out requiredY);
                    if (lines.Length > 2) int.TryParse(lines[2].Trim(), out requiredZ);
                }
            }
            catch { }

            // Read inventory
            List<string> inventoryItems = new List<string>();
            try
            {
                string invPath = Path.Combine("Save", "Inventory.txt");
                inventoryItems = new List<string>(File.ReadAllLines(invPath));
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            // Only allow win if at required location and have all required items
            if (x == requiredX && y == requiredY && z == requiredZ)
            {
                bool hasAll = true;
                foreach (string req in requiredItems)
                {
                    if (!inventoryItems.Contains(req))
                    {
                        hasAll = false;
                        break;
                    }
                }
                if (hasAll && requiredItems.Count > 0)
                {
                    Win();
                    return "";
                }
                else
                {
                    return Environment.NewLine + Environment.NewLine + "You don't have all usable items for this room";
                }
            }
            else
            {
                try
                {
                    // Read the usable items
                    string usablePath = Path.Combine("Text", "Room_descriptions", "Main", "floor_" + z, "y" + y + "_x" + x, "Usable_Items.txt");
                    if (!File.Exists(usablePath))
                    {
                        return Environment.NewLine + Environment.NewLine + "You have no usable items for this room";
                    }
                    string[] lines = File.ReadAllLines(usablePath);
                    if (lines.Length == 0)
                    {
                        return Environment.NewLine + Environment.NewLine + "You have no usable items for this room";
                    }
                    string[] usableItems = lines[0].Split(',');
                    string itemDescription = lines.Length > 1 ? lines[1] : "";
                    string newItem = lines.Length > 2 ? lines[2] : "";

                    // Check if the items are in the inventory
                    List<string> missingItems = new List<string>();
                    foreach (string item in usableItems)
                    {
                        string trimmed = item.Trim();
                        if (!inventoryItems.Contains(trimmed))
                        {
                            missingItems.Add(trimmed);
                        }
                    }

                    if (missingItems.Count == 0)
                    {
                        // Remove the items from the inventory
                        foreach (string item in usableItems)
                        {
                            inventoryItems.Remove(item.Trim());
                        }
                        string invPath = Path.Combine("Save", "Inventory.txt");
                        File.WriteAllLines(invPath, inventoryItems);

                        // Add the new item to the inventory and inventory history
                        File.AppendAllText(invPath, newItem + Environment.NewLine);

                        string histPath = Path.Combine("Save", "Inventory_history.txt");
                        File.AppendAllText(histPath, newItem + Environment.NewLine);

                        // Return the result
                        result = "Used " + string.Join(", ", usableItems) + "." + Environment.NewLine + Environment.NewLine + " " + itemDescription + Environment.NewLine + Environment.NewLine + "You found:" + Environment.NewLine + newItem;
                    }
                    else
                    {
                        result = "You are missing one or more items";
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                    result = "Error using items.";
                }
            }

            return result;
        }

        public bool CheckInventoryTutorial()
        {
            List<string> requiredItems = new List<string>();
            try
            {
                string reqPath = Path.Combine("Tutorial", "required_items.txt");
                if (File.Exists(reqPath))
                {
                    foreach (string line in File.ReadLines(reqPath))
                    {
                        string item = line.Trim();
                        if (!string.IsNullOrEmpty(item))
                        {
                            requiredItems.Add(item);
                        }
                    }
                }
                else
                {
                    Console.Error.WriteLine("Warning: required_items.txt not found. No required items for tutorial.");
                }
            }
            catch
            {
                Console.Error.WriteLine("Warning: Error reading required_items.txt. No required items for tutorial.");
            }

            List<string> inventoryItems = new List<string>();
            try
            {
                string invPath = Path.Combine("Save", "Inventory.txt");
                if (File.Exists(invPath))
                {
                    inventoryItems = new List<string>(File.ReadAllLines(invPath));
                }
                else
                {
                    Console.Error.WriteLine("Warning: Inventory.txt not found. Inventory is empty.");
                }
            }
            catch
            {
                Console.Error.WriteLine("Warning: Error reading Inventory.txt. Inventory is empty.");
            }

            // Check if all required items are in the inventory
            return inventoryItems.ContainsAll(requiredItems);
        }

        public void GameOver()
        {
            ClearOutput();
            string description = "";
            string gameOverText = "GAME OVER";

            try
            {
                string filePath = Path.Combine("Text", "Stories", "Ending", "Game_over.txt");
                description = File.ReadAllText(filePath).Replace("\n", Environment.NewLine);
            }
            catch
            {
                description = "Game over text not found.";
            }
            PrintToOutput(description);
            PrintToOutput(Environment.NewLine + Environment.NewLine + Environment.NewLine + gameOverText);
            Reset();
            PrintToOutput(Environment.NewLine + Environment.NewLine + "Press ENTER to exit...");
            GetUserInput();
            Application.Exit();
        }

        public void Win()
        {
            ClearOutput();
            string description = "";
            string winText = "YOU WIN";

            try
            {
                string filePath = Path.Combine("Text", "Stories", "Ending", "win.txt");
                description = File.ReadAllText(filePath).Replace("\n", Environment.NewLine);
            }
            catch
            {
                description = "Win text not found.";
            }
            PrintToOutput(description);
            PrintToOutput(Environment.NewLine + Environment.NewLine + Environment.NewLine + winText);
            Reset();
            PrintToOutput(Environment.NewLine + Environment.NewLine + "Press ENTER to exit...");
            GetUserInput();
            Application.Exit();
        }

        public void Reset()
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Location.txt")))
                {
                    writer.Write("2");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Inventory.txt")))
                {
                    writer.Write("");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Inventory_history.txt")))
                {
                    writer.Write("");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            // try
            // {
            //     using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Journal.txt")))
            //     {
            //         writer.Write("0");
            //     }
            // }
            // catch (Exception ex)
            // {
            //     Console.WriteLine(ex.ToString());
            // }
            string defaultHealth = "20";
            try
            {
                string defPath = Path.Combine("Finishing", "Default_health.txt");
                if (File.Exists(defPath))
                {
                    defaultHealth = File.ReadAllText(defPath).Trim();
                }
            }
            catch { }
            try
            {
                using (StreamWriter writer = new StreamWriter(Path.Combine("Save", "Health.txt")))
                {
                    writer.Write(defaultHealth);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();
            this.ClientSize = new Size(800, 600);
            this.Name = "MainForm";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.ResumeLayout(false);
        }
    }

    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }

    static class ListExtensions
    {
        public static bool ContainsAll<T>(this List<T> list, List<T> other)
        {
            foreach (T item in other)
            {
                if (!list.Contains(item))
                    return false;
            }
            return true;
        }
    }
}