package pl.umk.mat.martinp.reactics;

import javax.swing.*;
import javax.swing.border.*;
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;
import java.net.*;


public class HelpWindow extends JFrame {
    private static final long serialVersionUID = 327019113533268901L;
    private static final String startDocument = "index.html";
    private static final String docPath = "/help/";

    private static HelpWindow instance = null;
    private static JTextPane helpPane = new JTextPane();;

    public static synchronized HelpWindow getInstance() {
        if (instance == null)
            instance = new HelpWindow();

        return instance;
    }

    private HelpWindow() {
        super("ReactICS GUI Help");

        getContentPane().setLayout(new BorderLayout());

        JPanel mainPanel = new JPanel();
        mainPanel.setLayout(new BorderLayout());
        EtchedBorder panelBorder = new EtchedBorder(EtchedBorder.LOWERED);
        mainPanel.setBorder(panelBorder);

        helpPane.setEditable(false);
        helpPane.addHyperlinkListener(new HyperlinkListener() {
            public void hyperlinkUpdate(HyperlinkEvent hle) {
                if (hle.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
                    String target = hle.getDescription();

                    if (target.startsWith("#")) {
                        helpPane.scrollToReference(target.substring(1));
                    }
                }
            }
        });

        try {
            URL helpUrl = this.getClass().getResource(docPath + startDocument);
            helpPane.setPage(helpUrl);
        }
        catch (Exception e) {
            System.out.println("Exception: " + e.getMessage());
            JOptionPane.showMessageDialog(null, "Can not load help content",
                    "Help", JOptionPane.ERROR_MESSAGE);
        }

        JScrollPane helpScroller = new JScrollPane();
        JViewport helpVp = new JViewport();
        Dimension screenSize =  Toolkit.getDefaultToolkit().getScreenSize();
        helpVp.setPreferredSize(new Dimension(screenSize.width/2, screenSize.height-200));
        helpVp.add(helpPane);
        helpScroller.setViewport(helpVp);
        mainPanel.add(helpScroller, BorderLayout.CENTER);
        getContentPane().add(mainPanel, BorderLayout.CENTER);

        pack();
    }

    public void show(Component parent) {
        setLocationRelativeTo(parent);
        setVisible(true);
    }

}


class AboutWindow extends JFrame {
    private static AboutWindow instance = null;

    public static synchronized AboutWindow getInstance() {
        if (instance == null)
            instance = new AboutWindow();

        return instance;
    }

    private AboutWindow() {
        super("About ...");

        getContentPane().setLayout(new BorderLayout());

        JPanel infoPanel = new JPanel();
        infoPanel.add(new JLabel("<html><h1>" + ReacticsGUI.ApplicationName + "</h1>"
                + "<h2>version " + ReacticsGUI.ApplicationVersion + " (" + ReacticsGUI.ApplicationReleaseDate + ")</h2>"
                + "<h3>Model Checker for Reaction Systems</h3>"
                + "<h3>ReactICS Research Team (CC BY 4.0)</h3>"
                + "<h3><a href=\"https://reactics.org\">https://reactics.org</a></h3></html>"));
        getContentPane().add(infoPanel, BorderLayout.CENTER);

        JButton closeButton = new JButton("Close");
        closeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                setVisible(false);
            }
        });
        JPanel ctrlPanel = new JPanel();
        ctrlPanel.add(closeButton);
        ctrlPanel.setAlignmentX(SwingConstants.RIGHT);
        getContentPane().add(ctrlPanel, BorderLayout.SOUTH);

        setSize(new Dimension(400, 250));
        setResizable(false);
        this.setAlwaysOnTop(true);
        this.setUndecorated(true);
    }

    public void show(Component parent) {
        setLocationRelativeTo(parent);
        setVisible(true);
    }
}