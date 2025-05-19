package pl.umk.mat.martinp.reactics;

import javax.swing.*;
import javax.swing.border.*;
import javax.swing.table.AbstractTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.PrintWriter;
import java.util.*;


//-------------------------------------------------------------------------------------------------
// Graphical component for editing a single process (list of reactions)
//-------------------------------------------------------------------------------------------------

class ProcessEditor extends JPanel {
    private JTable reactionList;
    private RSTableModel reactionsModel;
    private Vector<Reaction> reactions;

    private final int id;
    private String label;
    private boolean modified = false;

    private JCheckBox selectBox;
    private TitledBorder outBorder;

    private final Color borderColor = new Color(24, 104, 92);;
    private final Color selectedBorderColor = new Color(150, 10, 10);
    private static final int borderThickness = 4;

    private static int nextId = 1;


    public ProcessEditor() {
        id = nextId;
        ++nextId;
        label = new String("Process_" + id);
        init();
    }

    ProcessEditor(String name) {
        id = nextId;
        ++nextId;
        label = name;
        init();
    }

    ProcessEditor(ProcessEditor procEdt) {
        id = nextId;
        ++nextId;
        label = "Copy_of_" + procEdt.label;
        init();
        reactions.addAll(procEdt.reactions);
        reactionsModel.fireTableDataChanged();
        modified = procEdt.modified;
    }

    public boolean isSelected() {
        return selectBox.isSelected();
    }

    public boolean isModified() { return modified; }

    public void clearModificationStatus() { modified = false; }

    public String getLabel() {
        return label;
    }

    public void addReaction(Reaction rr) {
        reactions.add(rr);
        reactionsModel.fireTableDataChanged();
    }

    private void init() {
        // Create border for the component
        outBorder = BorderFactory.createTitledBorder(label);
        Font font = outBorder.getTitleFont();
        Font newFont = new Font (font.getFamily(), Font.BOLD, font.getSize() + 2);
        outBorder.setTitleFont(new Font (font.getFamily(), Font.BOLD, font.getSize() + 2));
        outBorder.setTitleColor(borderColor);
        outBorder.setBorder(new LineBorder(borderColor, borderThickness, true));
        setBorder(outBorder);

        // Create reactions list component
        reactions = new Vector<Reaction>();
        reactionsModel = new RSTableModel();
        reactionList = new JTable(reactionsModel);

        Font cellFont = reactionList.getFont();
        Font headerFont = reactionList.getTableHeader().getFont();

        reactionList.setFont(new Font("Monospaced", 0, cellFont.getSize() + 2));
        reactionList.getTableHeader().setFont(new Font(headerFont.getFamily(), Font.BOLD, headerFont.getSize() + 2));
        reactionList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        JPanel buttonPanel = new JPanel();

        JButton addButton = new JButton("Add reaction");
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { addReaction(); }
        });
        buttonPanel.add(addButton);

        JButton edtButton = new JButton("Edit reaction");
        edtButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                editReaction();
            }
        });
        buttonPanel.add(edtButton);

        JButton rmButton = new JButton("Remove reaction");
        rmButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                removeReactions();
            }
        });
        buttonPanel.add(rmButton);

        JButton optButton = new JButton("Options");
        optButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                editOptions();
            }
        });
        buttonPanel.add(optButton);

        selectBox = new JCheckBox("Select");
        selectBox.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                toggleSelection();
            }
        });
        buttonPanel.add(selectBox);

        add(buttonPanel);

        add(new JScrollPane(reactionList));

        setPreferredSize(new Dimension(-1, 200));
    }

    private boolean showReactionEditDialog(Reaction rr) {
        final int Select = 0;
        final int Approve = 1;

        JTextField reactantsInput = new JTextField(30);
        JTextField inhibitorsInput = new JTextField(30);
        JTextField productsInput = new JTextField(30);

        String reactantsStr = "";
        String inhibitorsStr = "";
        String productsStr = "";

        Iterator<?> it = rr.reactants.iterator();
        StringBuilder dataStr = new StringBuilder();

        while (it.hasNext())
            dataStr.append(it.next()).append(" ");

        reactantsStr = dataStr.toString();

        it = rr.inhibitors.iterator();
        dataStr.setLength(0);

        while (it.hasNext())
            dataStr.append(it.next()).append(" ");

        inhibitorsStr = dataStr.toString();

        it = rr.products.iterator();
        dataStr.setLength(0);

        while (it.hasNext())
            dataStr.append(it.next()).append(" ");

        productsStr = dataStr.toString();

        reactantsInput.setToolTipText("<html>Space separated list of reactants</html>");
        inhibitorsInput.setToolTipText("<html>Space separated list of inhibitors</html>");
        productsInput.setToolTipText("<html>Space separated list of products</html>");

        JPanel myPanel = new JPanel(new GridBagLayout());
        GridBagConstraints cs = new GridBagConstraints();

        cs.insets = new Insets(5, 5, 5, 5);
        cs.anchor = GridBagConstraints.WEST;
        cs.gridx = 0;
        cs.gridy = 0;
        myPanel.add(new JLabel("Reactants"), cs);

        cs.gridx = 1;
        cs.gridy = 0;
        myPanel.add(reactantsInput, cs);

        cs.gridx = 0;
        cs.gridy = 1;
        myPanel.add(new JLabel("Inhibitors"), cs);

        cs.gridx = 1;
        cs.gridy = 1;
        myPanel.add(inhibitorsInput, cs);

        cs.gridx = 0;
        cs.gridy = 2;
        myPanel.add(new JLabel("Products"), cs);

        cs.gridx = 1;
        cs.gridy = 2;
        myPanel.add(productsInput, cs);

        int opStatus = Select;

        do {
            reactantsInput.setText(reactantsStr);
            inhibitorsInput.setText(inhibitorsStr);
            productsInput.setText(productsStr);

            int result = JOptionPane.showConfirmDialog(null, myPanel,
                    "Reaction details", JOptionPane.OK_CANCEL_OPTION);

            if (result != JOptionPane.OK_OPTION) {
                return false;
            }

            reactantsStr = reactantsInput.getText();
            inhibitorsStr = inhibitorsInput.getText();
            productsStr = productsInput.getText();

            HashSet<String> reactantsSet = new HashSet<String>(Arrays.asList(reactantsStr.trim().split("\\s+")));
            HashSet<String> inhibitorsSet = new HashSet<String>(Arrays.asList(inhibitorsStr.trim().split("\\s+")));
            HashSet<String> productsSet = new HashSet<String>(Arrays.asList(productsStr.trim().split("\\s+")));

            // Verify that reactant and inhibitor sets have empty intersection
            boolean intersection = false;

            for (String entity : inhibitorsSet) {
                if (reactantsSet.contains(entity)) {
                    intersection = true;
                    break;
                }
            }

            if (intersection) {
                JOptionPane.showMessageDialog(this, "Reactant and inhibitor sets have to be disjoint.", "Error", JOptionPane.ERROR_MESSAGE);
                continue;
            }

            //TODO: Validate entities names against a regular expression

            rr.reactants.clear();
            rr.reactants.addAll(reactantsSet);
            rr.inhibitors.clear();
            rr.inhibitors.addAll(inhibitorsSet);
            rr.products.clear();
            rr.products.addAll(productsSet);



            opStatus = Approve;
        }
        while(opStatus == Select);

        return true;
    }

    public Set<String> getReactantsSet() {
        HashSet<String> rset = new HashSet<String>();

        for (Reaction rr : reactions)
            rset.addAll(rr.getReactantsSet());

        return rset;
    }

    public void exportToXML(PrintWriter output) {
        output.println("        <process name=\"" + this.label + "\">");

        for (Reaction rr : reactions)
            rr.exportToXML(output);

        output.println("        </process>");
    }

    public String toRSSLString() {
        StringBuilder rsslString = new StringBuilder("    " + this.label + " {\n");

        for (Reaction rr : reactions) {
            rsslString.append(rr.toRSSLString());
        }

        rsslString.append("    };\n");

        return rsslString.toString();
    }

    private void editOptions() {
        String idRegex = "[a-zA-Z][a-zA-Z_0-9:-]*";
        boolean idOk = false;

        do {
            String newLabel = JOptionPane.showInputDialog(this, "Process name", label);
            if (newLabel == null)
                return;

            newLabel = newLabel.trim();

            if (!newLabel.matches(idRegex)) {
                JOptionPane.showMessageDialog(this,
                        "<html>Process name should start with a letter and may contain only:<br/>" +
                                "letters, numbers, colons (:), underscores (_) and hyphens (-)</html>",
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
            else {
                idOk = true;
                label = newLabel;
                outBorder.setTitle(label);
            }
        }
        while (!idOk);

        modified = true;
        this.repaint();
    }

    // Add new reaction
    private void addReaction() {
        Reaction rr = new Reaction();
        if (!showReactionEditDialog(rr))
            return;

        reactions.add(rr);
        modified = true;
        reactionsModel.fireTableDataChanged();
    }

    // Edit details of an existing reaction
    private void editReaction() {
        int rIdx = reactionList.getSelectedRow();

        if (rIdx == -1) {
            JOptionPane.showMessageDialog(this, "Select the reaction to edit.", "Select reaction", JOptionPane.WARNING_MESSAGE);
            return;
        }

        Reaction rr = new Reaction(reactions.get(rIdx));
        reactionList.clearSelection();
        if (!showReactionEditDialog(rr)) {
            return;
        }

        reactions.setElementAt(rr, rIdx);
        modified = true;
        reactionsModel.fireTableDataChanged();
    }

    // Remove an existing reaction
    private void removeReactions() {
        int rIdx = reactionList.getSelectedRow();

        if (rIdx == -1) {
            JOptionPane.showMessageDialog(this, "Select the reaction to be removed.", "Select reaction", JOptionPane.WARNING_MESSAGE);
            return;
        }

        reactions.remove(rIdx);
        reactionList.clearSelection();
        reactionsModel.fireTableDataChanged();
        modified = true;
        this.repaint();
    }

    private void toggleSelection() {
        if (selectBox.isSelected()) {
            outBorder.setTitleColor(selectedBorderColor);
            outBorder.setBorder(new LineBorder(selectedBorderColor, borderThickness, true));
        }
        else {
            outBorder.setTitleColor(borderColor);
            outBorder.setBorder(new LineBorder(borderColor, borderThickness, true));
        }

        this.repaint();
    }

    class RSTableModel extends AbstractTableModel {

        private String columnNames[] = {"Reactants", "Inhibitors", "Results"};
        private Vector<String>[] data;

        public String getColumnName(int colIdx) {
            return columnNames[colIdx];
        }

        public int getRowCount() {
            return reactions.size();
        }

        public int getColumnCount() {
            return columnNames.length;
        }

        public Object getValueAt(int row, int column) {
            Reaction rr = reactions.get(row);

            return switch (column) {
                case 0 -> rr.reactants;
                case 1 -> rr.inhibitors;
                case 2 -> rr.products;
                default -> "";
            };
        }

        public boolean isCellEditable(int rowIndex, int columnIndex) {
            return false;
        }
    }

}


//-------------------------------------------------------------------------------------------------
// Object representing a single reaction
//-------------------------------------------------------------------------------------------------

class Reaction {
    LinkedList<String> reactants;
    LinkedList<String> inhibitors;
    LinkedList<String> products;

    public Reaction() {
        reactants = new LinkedList<String>();
        inhibitors = new LinkedList<String>();
        products = new LinkedList<String>();
    }

    public Reaction(Reaction rr) {
        reactants = new LinkedList<String>(rr.reactants);
        inhibitors = new LinkedList<String>(rr.inhibitors);
        products = new LinkedList<String>(rr.products);
    }

    public Set<String> getReactantsSet() {
        Set<String> rset = new HashSet<String>();
        rset.addAll(reactants);
        rset.addAll(inhibitors);
        rset.addAll(products);

        return rset;
    }

    public String toRSSLString() {
        return "        {" + "{" + reactants.toString().replace("[", "").replace("]", "") + "}, " +
                "{" + inhibitors.toString().replace("[", "").replace("]", "") + "} -> " +
                "{" + products.toString().replace("[", "").replace("]", "") + "}" +
                "};\n";
    }

    public void exportToXML(PrintWriter output) {
        output.println("            <reaction>");

        for (String str : reactants)
            output.println("                <reactant>" + str + "</reactant>");

        for (String str : inhibitors)
            output.println("                <inhibitor>" + str + "</inhibitor>");

        for (String str : products)
            output.println("                <product>" + str + "</product>");

        output.println("            </reaction>");
    }
}
