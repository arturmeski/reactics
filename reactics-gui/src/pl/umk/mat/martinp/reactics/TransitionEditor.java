package pl.umk.mat.martinp.reactics;

import javax.swing.*;
import javax.swing.table.AbstractTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.*;


class TransitionEditor extends JDialog {
    private JTable transitionsList;
    private TransitionTableModel transitionsModel;
    private Vector<Transition> transitions;

    public TransitionEditor() {
        super();

        // Create reactions list component
        transitionsModel = new TransitionTableModel();
        transitionsList = new JTable(transitionsModel);

        Font cellFont = transitionsList.getFont();
        Font headerFont = transitionsList.getTableHeader().getFont();

        transitionsList.setFont(new Font("Monospaced", 0, cellFont.getSize() + 2));
        transitionsList.getTableHeader().setFont(new Font(headerFont.getFamily(), Font.BOLD, headerFont.getSize() + 2));
        transitionsList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);

        getContentPane().setLayout(new BorderLayout());

        JButton addButton = new JButton("Add transition");
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { addTransition(); }
        });

        JButton edtButton = new JButton("Edit transition");
        edtButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { editTransition(); }
        });

        JButton rmButton = new JButton("Remove transition");
        rmButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { removeTransitions(); }
        });

        JButton closeButton = new JButton("Close");
        closeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) { setVisible(false); }
        });

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(addButton);
        buttonPanel.add(edtButton);
        buttonPanel.add(rmButton);
        buttonPanel.add(closeButton);

        getContentPane().add(buttonPanel, BorderLayout.NORTH);
        getContentPane().add(new JScrollPane(transitionsList), BorderLayout.CENTER);

        setPreferredSize(new Dimension(-1, 200));
        setSize(new Dimension(600, 200));
        setTitle("Transitions");
    }

    public void showTransitionEditDialog(Component parent, Collection<Transition> trans, String from, String to) {
        setTitle("Transitions for (" + from + " -> " + to + ")");
        transitions = (Vector<Transition>) trans;
        transitionsModel.fireTableDataChanged();
        setLocationRelativeTo(parent);
        setVisible(true);
    }

    private void addTransition() {
        Transition tr = new Transition("", "");

        if (!showTransitionEditDialog(tr))
            return;

        transitions.add(tr);
        transitionsModel.fireTableDataChanged();
    }

    private void editTransition() {
        int[] selected = transitionsList.getSelectedRows();

        if (selected.length != 1) {
            JOptionPane.showMessageDialog(this, "Select a single transition to edit.", "Select transition", JOptionPane.WARNING_MESSAGE);
            return;
        }

        Transition tr = transitions.get(selected[0]);
        transitionsList.clearSelection();
        if (!showTransitionEditDialog(tr)) {
            return;
        }

        transitions.setElementAt(tr, selected[0]);
        transitionsModel.fireTableDataChanged();
    }

    private void removeTransitions() {
        int[] selected = transitionsList.getSelectedRows();

        for (int trIdx : selected) {
            transitions.remove(trIdx);
            transitionsList.clearSelection();
        }

        transitionsModel.fireTableDataChanged();
    }

    private boolean showTransitionEditDialog(Transition tr) {
        final int Select = 0;
        final int Approve = 1;

        JTextField contextInput = new JTextField(30);
        JTextField guardInput = new JTextField(30);

        String contextStr = tr.context;
        String guardStr = tr.guard;

        contextInput.setToolTipText("<html>Additional entities for processes</html>");
        guardInput.setToolTipText("<html>Initial conditions for the transition in rsCTL format.</html>");

        JPanel myPanel = new JPanel(new GridBagLayout());
        GridBagConstraints cs = new GridBagConstraints();

        cs.insets = new Insets(5, 5, 5, 5);
        cs.anchor = GridBagConstraints.WEST;
        cs.gridx = 0;
        cs.gridy = 0;
        myPanel.add(new JLabel("Context"), cs);

        cs.gridx = 1;
        cs.gridy = 0;
        myPanel.add(contextInput, cs);

        cs.gridx = 0;
        cs.gridy = 1;
        myPanel.add(new JLabel("Guards"), cs);

        cs.gridx = 1;
        cs.gridy = 1;
        myPanel.add(guardInput, cs);

        int opStatus = Select;

        do {
            contextInput.setText(contextStr);
            guardInput.setText(guardStr);

            int result = JOptionPane.showConfirmDialog(null, myPanel,
                    "Reaction details", JOptionPane.OK_CANCEL_OPTION);

            if (result != JOptionPane.OK_OPTION) {
                return false;
            }

            contextStr = contextInput.getText();
            guardStr = guardInput.getText();

            //TODO: Validate the data entered to the text fields
            tr.context = contextStr;
            tr.guard = guardStr;

            opStatus = Approve;
        }
        while(opStatus == Select);

        return true;
    }


    class TransitionTableModel extends AbstractTableModel {

        private final String[] columnNames = {"Context", "Guard"};

        public String getColumnName(int colIdx) {
            return columnNames[colIdx];
        }

        public int getRowCount() {
            return transitions.size();
        }

        public int getColumnCount() {
            return columnNames.length;
        }


        public Object getValueAt(int row, int column) {
            Transition tr = transitions.get(row);

            return switch (column) {
                case 0 -> tr.context;
                case 1 -> tr.guard;
                default -> "";
            };
        }

        public boolean isCellEditable(int rowIndex, int columnIndex) {
            return false;
        }
    }

}

