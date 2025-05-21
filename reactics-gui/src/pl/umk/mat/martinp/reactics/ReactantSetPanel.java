package pl.umk.mat.martinp.reactics;

import javax.swing.*;
import javax.swing.border.LineBorder;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.util.*;


public class ReactantSetPanel extends JPanel {
    private final int borderThickness = 2;

    JTextArea textArea = new JTextArea();

    public ReactantSetPanel() {
        textArea.setEditable(false);
        textArea.setLineWrap(true);
        textArea.setWrapStyleWord(false);
        Font textFont = textArea.getFont();
        textArea.setFont(new Font(textFont.getFamily(), Font.BOLD, textFont.getSize()+2));

        this.setPreferredSize(new Dimension(-1, 75));

        this.setLayout(new BorderLayout());
        this.add(new JScrollPane(textArea), BorderLayout.CENTER);

        TitledBorder outBorder = BorderFactory.createTitledBorder("Reactants");
        Font borderFont = outBorder.getTitleFont();
        outBorder.setTitleFont(new Font (borderFont.getFamily(), Font.BOLD, borderFont.getSize()+2));
        outBorder.setBorder(new LineBorder(Color.black, borderThickness, true));
        setBorder(outBorder);
    }

    public void updateReactants(Set<String> reactantsSet) {
        textArea.setText("");
        textArea.setText(Arrays.toString(reactantsSet.toArray()));
    }

    public void clear() {
        textArea.setText("");
    }
}