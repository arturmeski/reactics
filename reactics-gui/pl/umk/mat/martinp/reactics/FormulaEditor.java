package pl.umk.mat.martinp.reactics;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.EtchedBorder;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;
import javax.swing.table.*;
import java.awt.*;
import java.io.*;
import java.util.Collection;
import java.util.Vector;


public class FormulaEditor extends JPanel {
    private FormulaTableModel ftModel;
    private JTable formTable;
    private Vector<Formula> formulaList;

    boolean modified = false;

    static final Color TableHeaderBackgroundColor = Color.gray;
    static final Color TableHeaderFontColor = Color.white;
    static final Color BaseFormulaBackgroundColor = Color.white;
    static final Color TrueFormulaBackgroundColor = new Color(138, 242, 183);
    static final Color FalseFormulaBackgroundColor = new Color(240, 141, 141);
    static final Color InvalidFormulaBackgroundColor = new Color(124, 124, 124);
    static final Border  emptyBorder = BorderFactory.createEmptyBorder(1, 1, 1, 1);
    static final Border  selectedBorder = BorderFactory.createLineBorder(Color.RED, 2);


    public FormulaEditor() {
        formulaList = new Vector<Formula>();

        // Create the table for displaying formulas. Prevent default selection modes.
        ftModel = new FormulaTableModel();
        formTable = new JTable(ftModel, new FormulaColumnModel());
        formTable.setCellSelectionEnabled(false);
        formTable.setRowSelectionAllowed(true);

        Font headerFont = formTable.getTableHeader().getFont();
        Font cellFont = formTable.getFont();
        JTableHeader formHeader = formTable.getTableHeader();
        formTable.setFont(new Font("Monospaced", Font.PLAIN, cellFont.getSize() + 2));
        formHeader.setFont(new Font(headerFont.getFamily(), Font.BOLD, headerFont.getSize() + 2));
        formHeader.setBackground(TableHeaderBackgroundColor);
        formHeader.setForeground(TableHeaderFontColor);
        formHeader.setReorderingAllowed(false);
        formHeader.setResizingAllowed(true);
        formHeader.setBorder(new EtchedBorder(EtchedBorder.LOWERED));

        FormulaTableCellRenderer renderer = new FormulaTableCellRenderer();
        formTable.setDefaultRenderer(Object.class, renderer);
        formTable.createDefaultColumnsFromModel();

        setLayout(new BorderLayout());
        add(formTable, BorderLayout.CENTER);
    }

    public boolean isModified() { return modified; }

    public void clearModificationStatus() { modified = false; }

    public String toRSSLString() {
        StringBuilder rsslString = new StringBuilder();

        for (Formula f: formulaList)
            rsslString.append(f.toRSSLString()).append("\n");

        return rsslString.toString();
    }

    public void exportToXML(PrintWriter output) {
        output.println("    <formulas>");

        for (Formula f : formulaList)
            output.println("        " + f.toXMLString());

        output.println("    </formulas>");
    }

    public void loadFromXML(Document input) {
        formulaList.clear();

        NodeList formulaTags = input.getElementsByTagName("formula");

        for (int idx = 0; idx < formulaTags.getLength(); ++idx) {
            Node formulaNode = formulaTags.item(idx);

            if (formulaNode.getNodeType() != Node.ELEMENT_NODE) {
                continue;
            }

            Element formulaElement = (Element) formulaNode;

            String label = formulaElement.getAttribute("label");
            String formula = formulaElement.getTextContent();
            formulaList.add(new Formula(label, formula));
        }

        ftModel.fireTableDataChanged();
    }

    private boolean showFormulaEditDialog(Formula ff) {
        final int Select = 0;
        final int Approve = 1;

        JTextField labelInput = new JTextField(30);
        JTextField formulaInput = new JTextField(30);

        String labelStr = "";
        String formulaStr = "";

        labelStr = ff.label;
        formulaStr = ff.formula;

        labelInput.setToolTipText("<html>A unique label of the formula</html>");
        formulaInput.setToolTipText("<html>Formula to be evaluated</html>");

        JPanel myPanel = new JPanel(new GridBagLayout());
        GridBagConstraints cs = new GridBagConstraints();

        cs.insets = new Insets(5, 5, 5, 5);
        cs.anchor = GridBagConstraints.WEST;
        cs.gridx = 0;
        cs.gridy = 0;
        myPanel.add(new JLabel("Label"), cs);

        cs.gridx = 1;
        cs.gridy = 0;
        myPanel.add(labelInput, cs);

        cs.gridx = 0;
        cs.gridy = 1;
        myPanel.add(new JLabel("Formula"), cs);

        cs.gridx = 1;
        cs.gridy = 1;
        myPanel.add(formulaInput, cs);

        int opStatus = Select;

        do {
            labelInput.setText(labelStr);
            formulaInput.setText(formulaStr);

            int result = JOptionPane.showConfirmDialog(null, myPanel,
                    "Formula details", JOptionPane.OK_CANCEL_OPTION);

            if (result != JOptionPane.OK_OPTION) {
                return false;
            }

            labelStr = labelInput.getText();
            formulaStr = formulaInput.getText();

            //TODO: Validate the data entered to the text fields

            ff.label = labelStr;
            ff.formula = formulaStr;

            opStatus = Approve;
        }
        while(opStatus == Select);

        return true;
    }

    public void addFormula() {
        Formula ff = new Formula();

        if (showFormulaEditDialog(ff)) {
            formulaList.add(ff);
            modified = true;
            ftModel.fireTableDataChanged();
        }
    }

    // If more than one formula is selected throw an exception only the first can be edited
    public void editFormula() {
        int[] selected = formTable.getSelectedRows();

        if (selected.length != 1) {
            JOptionPane.showMessageDialog(this, "Select a single formula to edit.", "Select formula", JOptionPane.WARNING_MESSAGE);
            return;
        }

        Formula fEdt = formulaList.get(formTable.convertRowIndexToModel(selected[0]));

        if (fEdt == null)
            return;

        showFormulaEditDialog(fEdt);
        fEdt.status = Formula.FormulaStatus.None;
        modified = true;
        ftModel.fireTableDataChanged();
    }

    public void removeFormulas() {
        int[] viewRows = formTable.getSelectedRows();

        // Remove formulas starting from the last to avoid indexes updates
        for (int vIdx = viewRows.length - 1; vIdx>=0; --vIdx) {
            int mr = formTable.convertRowIndexToModel(viewRows[vIdx]);
            formulaList.remove(mr);
        }

        modified = true;
        ftModel.fireTableDataChanged();
    }

    public Collection<Formula> getSelectedFormulas() {
        Vector<Formula> selected = new Vector<Formula>();
        int[] viewRows = formTable.getSelectedRows();

        for (int vr : viewRows) {
            int mr = formTable.convertRowIndexToModel(vr);
            selected.add(formulaList.get(mr));
        }

        return selected;
    }

    // Needed to repaint JTable. Called after content modification by an external object.
    public void refreshStatus() {
        ftModel.fireTableDataChanged();
    }

    public void resetFormulasStatus() {
        for (Formula ff : formulaList) {
            ff.status = Formula.FormulaStatus.None;
            ff.mcTime = ff.totalTime = ff.memory = "-";
        }

        ftModel.fireTableDataChanged();
    }


    static class FormulaColumnModel extends DefaultTableColumnModel {
        int colno = 0;

        public void addColumn(TableColumn tc) {
            switch (colno) {
                case 0 -> {
                    tc.setMinWidth(60);
                    tc.setMaxWidth(Integer.MAX_VALUE / 10);
                    tc.setPreferredWidth(100);
                }
                case 1 -> {
                    tc.setMinWidth(100);
                    tc.setMaxWidth(Integer.MAX_VALUE);
                }
                case 2, 3, 4, 5 -> {
                    tc.setMinWidth(50);
                    tc.setPreferredWidth(50);
                    tc.setMaxWidth(Integer.MAX_VALUE / 10);
                }
            }

            super.addColumn(tc);
            ++colno;
        }
    }


    class FormulaTableModel extends AbstractTableModel implements TableModelListener {
        private final String[] columnNames = {"Label", "Formula", "Status", "MC Time (s)", "Total Time (s)", "Memory (MB)"};

        public String getColumnName(int colIdx) {
            return columnNames[colIdx];
        }

        public int getRowCount() {
            return formulaList.size();
        }

        public int getColumnCount() {
            return columnNames.length;
        }

        public Object getValueAt(int row, int column) {
            Formula ff = formulaList.get(row);

            return switch (column) {
                case 0 -> ff.label;
                case 1 -> ff.formula;
                case 2 -> ff.status;
                case 3 -> ff.mcTime;
                case 4 -> ff.totalTime;
                case 5 -> ff.memory;
                default -> "";
            };
        }

        public void setValueAt(Object value, int row, int column) {
//            fireTableDataChanged();
        }

        public boolean isCellEditable(int rowIndex, int columnIndex) { return false; }

        public Class getColumnClass(int column) {
            return getValueAt(0, column).getClass();
        }

        public void tableChanged(TableModelEvent tableModelEvent) {  }
    }


    // To properly display the content of the table containing formulas
    class FormulaTableCellRenderer extends JLabel implements TableCellRenderer {

        public FormulaTableCellRenderer() {
            // Allows background to be visible
            setOpaque(true);
        }

        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
            String statusStr = "";
            Formula ff = formulaList.get(row);

            setForeground(Color.black);

            if (isSelected) {
                setBorder(selectedBorder);
            }
            else {
                setBorder(emptyBorder);
            }

            // Set cell background and formula evaluation status
            if (column == 2) {
                switch (ff.status) {
                    case None -> {
                        statusStr = "?";
                        setBackground(BaseFormulaBackgroundColor);
                    }
                    case True -> {
                        statusStr = "True";
                        setBackground(TrueFormulaBackgroundColor);
                    }
                    case False -> {
                        statusStr = "False";
                        setBackground(FalseFormulaBackgroundColor);
                    }
                    case Invalid -> {
                        statusStr = "Invalid";
                        setBackground(InvalidFormulaBackgroundColor);
                    }
                }

                setText(statusStr);
            }
            else {
                setText((String) value);
                setBackground(BaseFormulaBackgroundColor);
            }

            if (column > 2) {
                setHorizontalAlignment(SwingConstants.RIGHT);
            } else {
                setHorizontalAlignment(SwingConstants.LEFT);
            }

            return this;
        }
    }
}


class Formula {
    public enum FormulaStatus {None, True, False, Invalid};

    String label;
    String formula;
    FormulaStatus status;
    String mcTime;
    String totalTime;
    String memory;

    public Formula() {
        this("", "");
    }

    public Formula(String label, String formula) {
        this.label = label;
        this.formula = formula;
        this.status = FormulaStatus.None;
        this.mcTime = this.totalTime = this.memory = "-";
    }

    public String toRSSLString() {
        return "rsctlk-property { " + label + " : " + formula + " };";
    }

    public String toXMLString() {
        return "<formula label=\"" + label +"\">" +
                formula.replaceAll("<", "&lt;").replaceAll(">", "&gt;") +
                "</formula>";
    }
}

