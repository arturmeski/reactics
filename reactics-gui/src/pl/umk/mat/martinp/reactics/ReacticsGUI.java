/** Main application window */

package pl.umk.mat.martinp.reactics;

import org.w3c.dom.Document;
import org.xml.sax.SAXException;
import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Collection;
import java.util.TreeSet;


public class ReacticsGUI extends JFrame {
    public final static String ApplicationName = "ReactICS GUI";
    public final static String ApplicationVersion = "0.1";
    public final static String ApplicationReleaseDate = "2025";

    private static final String defaultConfigFileName = "reactics.conf";

    private JFrame window;
    private JTabbedPane modulePane;
    private ReactantSetPanel reactantSetPanel;
    private ReactionSystemEditor reactionSystemEditor;
    private ContextAutomatonEditor contextAutomatonEditor;
    private TransitionSystemViewer transitionSystemViewer;
    private TransitionSystemViewer compressedTransitionSystemViewer;
    private FormulaEditor formulaEditor;

    private FileSelector fileSelector;

    private ReactionSystem reactionSystem;
    private ReacticsRuntime reactics;


    public ReacticsGUI() {
        super(ApplicationName);

        reactionSystem = ReactionSystem.getInstance();

        try {
            reactics = ReacticsRuntime.getInstance();
        }
        catch (ReacticsRuntimeException rre) {
            JOptionPane.showMessageDialog(this,
                    rre.getMessage(),
                    "Reactics Runtime Error", JOptionPane.ERROR_MESSAGE);
        }

        Dimension screenSize =  Toolkit.getDefaultToolkit().getScreenSize();
        setSize(new Dimension(screenSize.width-200, screenSize.height-200));
        createMenuBar();
        createContentPane();

        fileSelector = FileSelector.getInstance();

        try {
            reactics.loadConfig(defaultConfigFileName);
        }
        catch (ConfigReadingError cre) {
            System.err.println("[ReactICS] Error reading configuration: " + cre.getMessage());
            JOptionPane.showMessageDialog(this,
                    "Could not read configuration\n" + cre.getMessage(),
                    "Reactics Runtime Error", JOptionPane.ERROR_MESSAGE);
        }
        catch (InvalidRuntimeException ire) {
            System.err.println("[ReactICS] ReactICS runtime cannot be executed" + ire.getMessage());
            JOptionPane.showMessageDialog(this,
                    "Invalid ReactICS runtime patn\n" + ire.getMessage() +
                            "\nYou may proceed with editing reaction system structure," +
                            "however not model checking will be possible.",
                    "Reactics Runtime Error", JOptionPane.ERROR_MESSAGE);
        }

        window = this;
    }

    private void createMenuBar() {
        JMenuBar menuBar = new JMenuBar();

        JMenu fileMenu = new JMenu("File");
        menuBar.add(fileMenu);

        JMenuItem xmlLoadItem = new JMenuItem("Load from XML file");
        xmlLoadItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                loadFromXML();
            }
        });
        fileMenu.add(xmlLoadItem);

        JMenuItem xmlsaveItem = new JMenuItem("Save to XML file");
        xmlsaveItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                saveAsXML();
            }
        });
        fileMenu.add(xmlsaveItem);

        JMenuItem rsslImportItem = new JMenuItem("Import from RSSL file");
        rsslImportItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                importFromRSSL();
            }
        });
        fileMenu.add(rsslImportItem);

        JMenuItem rsslExportItem = new JMenuItem("Save to RSSL file");
        rsslExportItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                exportToRSSLFile();
            }
        });
        fileMenu.add(rsslExportItem);

        JMenuItem isplExportItem = new JMenuItem("Export to ISPL file");
        isplExportItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { exportToISPLFile(); }
        });
        fileMenu.add(isplExportItem);

        JMenuItem exitItem = new JMenuItem("Exit");
        exitItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                System.exit(0);
            }
        });
        fileMenu.addSeparator();
        fileMenu.add(exitItem);

        JMenu helpMenu = new JMenu("Help");
        menuBar.add(helpMenu);

        JMenuItem helpItem = new JMenuItem("Help");
        helpItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { showHelpWindow(); }
        });
        helpMenu.add(helpItem);

        JMenuItem aboutItem = new JMenuItem("About");
        aboutItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { showAboutWindow(); }
        });
        helpMenu.add(aboutItem);

        setJMenuBar(menuBar);
    }

    private void createContentPane() {
        modulePane = new JTabbedPane();
        modulePane.setTabPlacement(JTabbedPane.NORTH);

        //-----------------------------------------------------------------------------------------
        // Reaction System Editor
        //-----------------------------------------------------------------------------------------

        reactionSystemEditor = new ReactionSystemEditor();
        modulePane.addTab("Reaction System", reactionSystemEditor);
        reactionSystem.addObserver(reactionSystemEditor);


        //-----------------------------------------------------------------------------------------
        // Context Automaton Editor
        //-----------------------------------------------------------------------------------------

        contextAutomatonEditor = new ContextAutomatonEditor(getSize());
        modulePane.addTab("Context Automaton", contextAutomatonEditor);
        reactionSystem.addObserver(contextAutomatonEditor);


        //-----------------------------------------------------------------------------------------
        // Transition System Viewer
        //-----------------------------------------------------------------------------------------

        JPanel transitionSystemPanel = new JPanel(new BorderLayout());
        transitionSystemViewer = new TransitionSystemViewer(getSize(), false);
        transitionSystemPanel.add(transitionSystemViewer, BorderLayout.CENTER);
        reactionSystem.addObserver(transitionSystemViewer);

        JPanel tsCtrlPanel = new JPanel();
        JButton tsUpdateBtn = new JButton("Update transition system");
        tsUpdateBtn.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { updateTransitionSystem(); }
        });
        tsCtrlPanel.add(tsUpdateBtn);

        JCheckBox tsLockCBox = new JCheckBox("Lock relative nodes positions");
        tsLockCBox.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                transitionSystemViewer.lockNodesPositions(tsLockCBox.isSelected());
            }
        });
        tsCtrlPanel.add(tsLockCBox);

        transitionSystemPanel.add(tsCtrlPanel, BorderLayout.NORTH);
        modulePane.addTab("Transition System", transitionSystemPanel);

        //-----------------------------------------------------------------------------------------
        // Compressed Transition System Viewer
        //-----------------------------------------------------------------------------------------

        JPanel compressedTransitionSystemPanel = new JPanel(new BorderLayout());
        compressedTransitionSystemViewer = new TransitionSystemViewer(getSize(), true);
        compressedTransitionSystemPanel.add(compressedTransitionSystemViewer, BorderLayout.CENTER);
        reactionSystem.addObserver(compressedTransitionSystemViewer);

        JPanel ctsCtrlPanel = new JPanel();
        JButton ctsUpdateBtn = new JButton("Update transition system");
        ctsUpdateBtn.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { updateTransitionSystem(); }
        });
        ctsCtrlPanel.add(ctsUpdateBtn);

        JCheckBox ctsLockCBox = new JCheckBox("Lock relative nodes positions");
        ctsLockCBox.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                compressedTransitionSystemViewer.lockNodesPositions(ctsLockCBox.isSelected());
            }
        });
        ctsCtrlPanel.add(ctsLockCBox);

        compressedTransitionSystemPanel.add(ctsCtrlPanel, BorderLayout.NORTH);
        modulePane.addTab("Compressed Transition System", compressedTransitionSystemPanel);

        //-----------------------------------------------------------------------------------------
        // Formula Editor
        //-----------------------------------------------------------------------------------------

        JPanel formulaEditorPanel = new JPanel();
        formulaEditorPanel.setLayout(new BorderLayout());
        formulaEditor = new FormulaEditor(reactionSystem);
        reactionSystem.addObserver(formulaEditor);
        formulaEditorPanel.add(formulaEditor, BorderLayout.CENTER);

        JPanel formulaCtrlPanel = new JPanel();
        JButton addButton = new JButton("Add formula");
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { formulaEditor.addFormula(window); }
        });
        formulaCtrlPanel.add(addButton);

        JButton edtButton = new JButton("Edit formula");
        edtButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                formulaEditor.editFormula(window);
            }
        });
        formulaCtrlPanel.add(edtButton);

        JButton rmButton = new JButton("Remove formulas");
        rmButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                formulaEditor.removeFormulas();
            }
        });
        formulaCtrlPanel.add(rmButton);

        JButton evalButton = new JButton("Evaluate");
        evalButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                evaluateFormulas();
            }
        });
        formulaCtrlPanel.add(evalButton);

        JButton resetButton = new JButton("Reset");
        resetButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                formulaEditor.resetFormulasStatus();
            }
        });
        formulaCtrlPanel.add(resetButton);

        formulaEditorPanel.add(formulaCtrlPanel, BorderLayout.NORTH);

        //-----------------------------------------------------------------------------------------
        // Split the main window into two parts. The upper one contains details of the reaction
        // system. The bottom part contains the list of formulas for model checking.
        //-----------------------------------------------------------------------------------------

        JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT, modulePane, formulaEditorPanel);
        splitPane.setResizeWeight(0.75);
//        splitPane.setOneTouchExpandable(true);
        splitPane.setDividerSize(8);

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(splitPane, BorderLayout.CENTER);

        //-----------------------------------------------------------------------------------------
        // Update button + Reactant Set Viewer
        //-----------------------------------------------------------------------------------------

        JPanel topPanel = new JPanel();
        topPanel.setLayout(new BorderLayout());
        JPanel buttonPanel = new JPanel();
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));

        JButton updateButton = new JButton("<html><center>Update<br>Reaction System</center></html>");
        updateButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                updateReactionSystem();
            }
        });
        buttonPanel.add(updateButton);
        topPanel.add(buttonPanel, BorderLayout.WEST);
        reactantSetPanel = new ReactantSetPanel();
        topPanel.add(reactantSetPanel, BorderLayout.CENTER);
        getContentPane().add(topPanel, BorderLayout.NORTH);
    }

    private boolean isModified() {
        return reactionSystemEditor.isModified() || contextAutomatonEditor.isModified();
    }

    private void clearModificationStatus() {
        reactionSystemEditor.clearModificationStatus();
        contextAutomatonEditor.clearModificationStatus();
        transitionSystemViewer.clearModificationStatus();
        compressedTransitionSystemViewer.clearModificationStatus();
    }

    private void updateReactionSystem()  {
        System.out.println("[ReactICS] Update reaction system structure");

        Path rsslFile = reactics.getRSSLFile();

        try {
            Files.writeString(rsslFile, "");

            PrintWriter rsslStream = new PrintWriter(Files.newBufferedWriter(rsslFile));
            printRSStructure(rsslStream);
            rsslStream.close();
        }
        catch (IOException ie) {
            System.err.println("[ReactICS] Could not read transition system structure: " + ie.getMessage());

            JOptionPane.showMessageDialog(this,
                    "Could not read transition system structure\n" + ie.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }

        reactionSystem.notifyObservers();
        updateReactantSet();
        clearModificationStatus();
    }

    private void updateReactantSet() {
        TreeSet<String> rset = new TreeSet<String>();

        rset.addAll(reactionSystemEditor.getReactantsSet());
        rset.addAll(contextAutomatonEditor.getReactantsSet());
        rset.remove("");
        reactantSetPanel.updateReactants(rset);
    }

    private void updateTransitionSystem() {
        if (isModified()) {
            updateReactionSystem();
        }
        else if (transitionSystemViewer.isComputed()) {
            // Skip re-computing transition system structure
            return;
        }

        try {
            String tsStructure = reactics.getTransitionSystemStructure();
            transitionSystemViewer.updateTransitionSystemStructure(tsStructure);
            compressedTransitionSystemViewer.updateTransitionSystemStructure(tsStructure);
        }
        catch (IOException ioe) {
            System.out.println("[ReactICS] I/O Error: " + ioe.getMessage());
            JOptionPane.showMessageDialog(this,
                    "Could not write reaction system structure to a temporary file\n" + ioe.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
        catch (ReacticsRuntimeException rre) {
            System.out.println("[ReactICS] Runtime Error: " + rre.getMessage());
            JOptionPane.showMessageDialog(this,
                    rre.getMessage(),
                    "Reactics Runtime Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void evaluateFormulas() {
        Collection<Formula> formulas = formulaEditor.getSelectedFormulas();

        if (isModified())
            updateReactionSystem();

        Path rsslFile = reactics.getRSSLFile();
        long originalSize = -1;

        try {
            originalSize = Files.size(rsslFile);
        }
        catch (IOException ioe) {
            System.err.println("[ReactICS] Error: " + ioe.getMessage());
            JOptionPane.showMessageDialog(this, ioe.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }

        for (Formula ff : formulas) {
            try {
                System.out.println("[ReactICS] Evaluate formula: " + ff.label);

                Files.writeString(rsslFile, ff.toRSSLString() + "\n", StandardCharsets.UTF_8, StandardOpenOption.APPEND);

                ReacticsRuntime.EvalResult result = reactics.evaluateFormula(ff.label);
                ff.status = result.result();
                ff.mcTime = result.mcTime() + " s";
                ff.totalTime = result.totalTime() + " s";
                ff.memory = result.memory() + " MB";
                formulaEditor.refreshStatus();
            }
            catch(IOException ioe) {
                System.err.println("[ReactICS] Error: " + ioe.getMessage());
                JOptionPane.showMessageDialog(this, ioe.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
            catch(ReacticsRuntimeException rre) {
                System.err.println("[ReactICS] Runtime error: " + rre.getMessage());
                JOptionPane.showMessageDialog(this,
                        rre.getMessage(),
                        "Reactics Runtime Error", JOptionPane.ERROR_MESSAGE);

                ff.status = Formula.FormulaStatus.Invalid;
            }
            finally {
                try {
                    RandomAccessFile raf = new RandomAccessFile(rsslFile.toFile(), "rw");
                    raf.setLength(originalSize);
                }
                catch (IOException ioe) {
                    System.err.println("[ReactICS] Error: " + ioe.getMessage());
                    JOptionPane.showMessageDialog(this, ioe.getMessage(),
                            "Error", JOptionPane.ERROR_MESSAGE);
                }
            }
        }
    }

    private void saveAsXML() {
        File outFile = fileSelector.selectOutputFile(this, new File(System.getProperty("user.dir")),
                new FileNameExtensionFilter("Reaction System (XML)", "xml"));

        if(outFile == null)
            return;

        System.out.println("[ReactICS] Save to XML file: " + outFile.getName());

        try {
            PrintWriter xmlOut = new PrintWriter(new FileWriter(outFile));
            xmlOut.println("<xml version=\"1.0\">");
            reactionSystemEditor.exportToXML(xmlOut);
            contextAutomatonEditor.exportToXML(xmlOut);
            formulaEditor.exportToXML(xmlOut);
            xmlOut.println("</xml>");
            xmlOut.flush();
            xmlOut.close();
        }
        catch(IOException ioe) {
            JOptionPane.showMessageDialog(this, ioe.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void loadFromXML() {
        FileNameExtensionFilter fileTypeFilter = new FileNameExtensionFilter("Reaction System (XML)", "xml");
        JFileChooser fc = new JFileChooser();
        fc.addChoosableFileFilter(fileTypeFilter);
        fc.setAcceptAllFileFilterUsed(true);
        fc.setCurrentDirectory(new File(System.getProperty("user.dir")));


        if(fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File xmlFile = fc.getSelectedFile();
            loadFromXMLFile(xmlFile);
            setTitle("ReactICS GUI : " + xmlFile.getName());
        }

        modulePane.setSelectedIndex(0);
        clearModificationStatus();
    }


    private void loadFromXMLFile(File xmlFile) {
        reactionSystemEditor.clear();
        contextAutomatonEditor.clear();
        reactantSetPanel.clear();
        transitionSystemViewer.clear();
        compressedTransitionSystemViewer.clear();

        try {
            DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
            Document doc = dBuilder.parse(xmlFile);
            doc.getDocumentElement().normalize();
            reactionSystemEditor.loadFromXML(doc);
            contextAutomatonEditor.loadFromXML(doc);
            formulaEditor.loadFromXML(doc);
            updateReactionSystem();
        }
        catch(IOException ioe) {
            System.err.println("[ReactICS] Error: " + ioe.getMessage());

            JOptionPane.showMessageDialog(this, "Error reading file: " + xmlFile.getName() + "\n" + ioe.getMessage(),
                    "Input error", JOptionPane.ERROR_MESSAGE);

            reactionSystemEditor.clear();
            contextAutomatonEditor.clear();
            reactantSetPanel.clear();
        }
        catch(ParserConfigurationException pce) {
            System.err.println("[ReactICS] Parse Configuration Error: " + pce.getMessage());

            JOptionPane.showMessageDialog(this, pce.getMessage(),
                    "Parse Configuration Error", JOptionPane.ERROR_MESSAGE);

            reactionSystemEditor.clear();
            contextAutomatonEditor.clear();
            reactantSetPanel.clear();
        }
        catch(SAXException se) {
            System.err.println("[ReactICS] SAXException: " + se.getMessage());

            JOptionPane.showMessageDialog(this, se.getMessage(),
                    "Parse error", JOptionPane.ERROR_MESSAGE);

            reactionSystemEditor.clear();
            contextAutomatonEditor.clear();
            reactantSetPanel.clear();
        }
        catch(FileStructureError err) {
            System.err.println("[ReactICS]: File Structure Error: " + err.getMessage());

            JOptionPane.showMessageDialog(this, err.getMessage(),
                    "XML file structure error", JOptionPane.ERROR_MESSAGE);

            reactionSystemEditor.clear();
            contextAutomatonEditor.clear();
            reactantSetPanel.clear();
        }
        catch(Exception e) {
            System.out.println("[ReactICS] Error: " + e.getMessage());

            JOptionPane.showMessageDialog(this, "Unexpected error reading file: " + xmlFile.getName() +
                            " " + e.getMessage(),
                    "Input error", JOptionPane.ERROR_MESSAGE);

            reactionSystemEditor.clear();
            contextAutomatonEditor.clear();
            reactantSetPanel.clear();
        }
    }


    private void importFromRSSL() {
        FileNameExtensionFilter fileTypeFilter = new FileNameExtensionFilter("Reaction System Specification Language (rs)", "rs");
        JFileChooser fc = new JFileChooser();
        fc.addChoosableFileFilter(fileTypeFilter);
        fc.setAcceptAllFileFilterUsed(true);
        fc.setCurrentDirectory(new File(System.getProperty("user.dir")));


        if(fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File rsslFile = fc.getSelectedFile();

            try {
                File xmlFile = reactics.convertToXMLFile(rsslFile);
                loadFromXMLFile(xmlFile);
            } catch (IOException e) {
                System.err.println("IOException: " + e.getMessage());
                e.printStackTrace();
            } catch (ReacticsRuntimeException e) {
                System.err.println("ReacticsRuntimeException: " + e.getMessage());
                e.printStackTrace();
            }

            setTitle("ReactICS GUI : " + rsslFile.getName());
            contextAutomatonEditor.recalculateCoordinates();
        }

        modulePane.setSelectedIndex(0);
        clearModificationStatus();
    }


    private void exportToRSSLFile() {
        File outFile = fileSelector.selectOutputFile(this, new File(System.getProperty("user.dir")),
                new FileNameExtensionFilter("Reaction System Specification Language (RSSL)", "rs"));

        if(outFile == null)
            return;

        System.out.println("[ReactICS] Export to RSSL file: " + outFile.getName());

        try {
            PrintWriter rsslOut = new PrintWriter(new FileWriter(outFile));
            printRSStructure(rsslOut);
            rsslOut.close();
        }
        catch(IOException ioe) {
            System.err.println("[ReactICS] Error: " + ioe.getMessage());
            JOptionPane.showMessageDialog(this, ioe.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }


    private void exportToISPLFile() {
        updateReactionSystem();

        if (!reactionSystem.isplTranslationAllowed()) {
            JOptionPane.showMessageDialog(this,
                    "Context automaton contains guards for some transitions.\n" +
                    "Current version of ReactICS does not support translation to ISPL format in this case.\n",
                    "Translation is not possible", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        File outFile = fileSelector.selectOutputFile(this, new File(System.getProperty("user.dir")),
                new FileNameExtensionFilter("Interpreted System Programming Language (ISPL)", "ispl"));

        if (outFile == null)
            return;

        System.out.println("[ReactICS] Export to ISPL file: " + outFile.getAbsolutePath());

        try {
            if (!outFile.exists() && !outFile.createNewFile()) {
                System.err.println("[ReactICS] Error: The file "+ outFile.getName() + " could not be created.");
                JOptionPane.showMessageDialog(this,
                        "The file " + outFile.getName() + " could not be created.",
                        "Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (!outFile.canWrite()){
                System.err.println("[ReactICS] Error: Cannot write to the file " + outFile.getName());
                JOptionPane.showMessageDialog(this,
                        "Cannot write to the file " + outFile.getName(),
                        "Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            reactics.exportToISPLFile(outFile);
        }
        catch(IOException ioe) {
            System.err.println("[ReactICS] Error: " + ioe.getMessage());
            JOptionPane.showMessageDialog(this, ioe.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
        catch(ReacticsRuntimeException rre) {
            System.err.println("[ReactICS] Runtime error: " + rre.getMessage());
            JOptionPane.showMessageDialog(this,
                    rre.getMessage(),
                    "ReactICS Runtime Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void printRSStructure(PrintWriter outStream) {
        outStream.println("options { use-context-automaton; make-progressive; };\n");
        outStream.println(reactionSystemEditor.toRSSLString());
        outStream.println(contextAutomatonEditor.toRSSLString());
//        outStream.println(formulaEditor.toRSSLString());
    }

    private void showAboutWindow() {
        AboutWindow awin = AboutWindow.getInstance();
        awin.show(this);
    }

    private void showHelpWindow() {
        HelpWindow hwin = HelpWindow.getInstance();
        hwin.show(this);
    }

    public static void main(String args[]) {
        ReacticsGUI wnd = new ReacticsGUI();
        wnd.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        wnd.setLocationRelativeTo(null);
        wnd.setVisible(true);
    }

}


//-------------------------------------------------------------------------------------------------
// Class responsible for selecting a file to load / save the reaction system structure
//-------------------------------------------------------------------------------------------------

class FileSelector {
    private enum Status {SELECT, APPROVE, CANCEL}

    private static FileSelector instance = null;

    public static synchronized FileSelector getInstance() {
        if (instance == null)
            instance = new FileSelector();

        return instance;
    }

    private FileSelector() { }

    public File selecInputFile(Component parent, File rootDir, FileNameExtensionFilter filter) {
        Status opStatus = Status.SELECT;
        JFileChooser fc = new JFileChooser();
        fc.addChoosableFileFilter(filter);
        fc.setAcceptAllFileFilterUsed(true);
        fc.setCurrentDirectory(rootDir);
        File outFile = null;

        do {
            if (fc.showOpenDialog(parent) != JFileChooser.APPROVE_OPTION) {
                opStatus = Status.CANCEL;
                break;
            }

            outFile = fc.getSelectedFile();
            opStatus = Status.APPROVE;

            if(outFile.exists()) {
                if (JOptionPane.showConfirmDialog(parent,
                        "The file " + outFile.getName() + " already exists.\n" +
                                "Do you wish to overwrite it?", "Warning",
                        JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE) == JOptionPane.NO_OPTION) {
                    opStatus = Status.SELECT;
                }
            }
        } while(opStatus == Status.SELECT);

        if(opStatus != Status.APPROVE)
            outFile = null;

        return outFile;
    }

    public File selectOutputFile(Component parent, File rootDir, FileNameExtensionFilter filter) {
        Status opStatus = Status.SELECT;
        JFileChooser fc = new JFileChooser();
        fc.addChoosableFileFilter(filter);
        fc.setAcceptAllFileFilterUsed(true);
        fc.setCurrentDirectory(rootDir);
        File outFile = null;

        do {
            if (fc.showSaveDialog(parent) != JFileChooser.APPROVE_OPTION) {
                opStatus = Status.CANCEL;
                break;
            }

            outFile = fc.getSelectedFile();
            opStatus = Status.APPROVE;

            if(outFile.exists()) {
                if (JOptionPane.showConfirmDialog(parent,
                        "The file " + outFile.getName() + " already exists.\n" +
                                "Do you wish to overwrite it?", "Warning",
                        JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE) == JOptionPane.NO_OPTION) {
                    opStatus = Status.SELECT;
                }
            }
        } while(opStatus == Status.SELECT);

        if(opStatus != Status.APPROVE)
            outFile = null;

        return outFile;
    }
}


/**
 * General exception class for any error related to input XML file
 */
class FileStructureError extends Exception {
    public FileStructureError(String message) {
        super(message);
    }
}