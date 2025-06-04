/** A component for editing the reaction system details */

package pl.umk.mat.martinp.reactics;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.PrintWriter;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.Vector;


//-------------------------------------------------------------------------------------------------
/** A graphical component allowing edition and display of a distributed reaction system.
 *  A distributed reaction system contains a number of processes.
 *  Each process contains a list of reactions.
 */
public class ReactionSystemEditor extends JPanel implements RSObserver {
    ReactionSystem rs;
    private Vector<ProcessEditor> procEditors = new Vector<ProcessEditor>();
    private JPanel processPanel = new JPanel();


    public ReactionSystemEditor() {
        rs = ReactionSystem.getInstance();

        processPanel.setLayout(new BoxLayout(processPanel, BoxLayout.Y_AXIS));

        final Dimension buttonSize = new Dimension(150, 25);

        JButton addButton = new JButton("New process");
        addButton.setMaximumSize(buttonSize);
        addButton.setPreferredSize(buttonSize);
        addButton.setMaximumSize(buttonSize);
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                createProcess();
            }
        });

        JButton rmButton = new JButton("Remove");
        rmButton.setMaximumSize(buttonSize);
        rmButton.setPreferredSize(buttonSize);
        rmButton.setMaximumSize(buttonSize);
        rmButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                removeProcesses();
            }
        });

        JButton copyButton = new JButton("Copy");
        copyButton.setMaximumSize(buttonSize);
        copyButton.setPreferredSize(buttonSize);
        copyButton.setMaximumSize(buttonSize);
        copyButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                copyProcesses();
            }
        });

        JButton renameButton = new JButton("Rename");
        renameButton.setMaximumSize(buttonSize);
        renameButton.setPreferredSize(buttonSize);
        renameButton.setMaximumSize(buttonSize);
        renameButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                renameProcess();
            }
        });

        JButton upButton = new JButton("Move up");
        upButton.setMaximumSize(buttonSize);
        upButton.setPreferredSize(buttonSize);
        upButton.setMaximumSize(buttonSize);
        upButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                moveSelectedUp();
            }
        });

        JButton downButton = new JButton("Move down");
        downButton.setMaximumSize(buttonSize);
        downButton.setPreferredSize(buttonSize);
        downButton.setMaximumSize(buttonSize);
        downButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                moveSelectedDown();
            }
        });

        JPanel buttonPanel = new JPanel();
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));

        buttonPanel.add(addButton);
        buttonPanel.add(rmButton);
        buttonPanel.add(copyButton);
        buttonPanel.add(renameButton);
        buttonPanel.add(upButton);
        buttonPanel.add(downButton);

        this.setLayout(new BorderLayout());
        this.add(new JScrollPane(processPanel), BorderLayout.CENTER);
        this.add(buttonPanel, BorderLayout.WEST);

        createProcess();
    }

    public boolean isModified() {
        boolean procModified = false;

        for (ProcessEditor pe : procEditors)
            procModified |= pe.isModified();

        return rs.modified | procModified;
    }

    public void clearModificationStatus() {
        for (ProcessEditor pe : procEditors)
            pe.clearModificationStatus();

        rs.modified = false;
    }

    public Set<String> getReactantsSet() {
        HashSet<String> rset = new HashSet<String>();

        for (ProcessEditor pe : procEditors)
            rset.addAll(pe.getReactantsSet());

        return rset;
    }

    public void exportToXML(PrintWriter output) {
        output.println("    <reaction-system>");

        for (ProcessEditor process : procEditors)
            process.exportToXML(output);

        output.println("    </reaction-system>");
    }

    public void loadFromXML(Document input) throws ReactionSystemStructureError {
        NodeList rsSections = input.getElementsByTagName("reaction-system");

        if (rsSections.getLength() == 0 || rsSections.getLength() > 1) {
            throw new ReactionSystemStructureError("An XML file should contain a single reaction system description.");
        }

        NodeList processList = rsSections.item(0).getChildNodes();

        for (int idx=0; idx<processList.getLength(); ++idx) {
            Node processNode = processList.item(idx);

            if (processNode.getNodeType() != Node.ELEMENT_NODE)
                continue;

            String procName = processNode.getAttributes().getNamedItem("name").getNodeValue();
            ProcessEditor processEditor = new ProcessEditor(rs.createProcess(procName));

            //----------------------------------------------------------------------------------------------------------
            // Reactions details
            //----------------------------------------------------------------------------------------------------------

            NodeList reactionList = processNode.getChildNodes();

            for (int rIdx=0; rIdx<reactionList.getLength(); ++rIdx) {
                Node reactionNode = reactionList.item(rIdx);

                if (reactionNode.getNodeType() != Node.ELEMENT_NODE)
                    continue;

                Reaction reaction = new Reaction();

                NodeList substrateNodes = reactionNode.getChildNodes();

                for (int sIdx=0; sIdx<substrateNodes.getLength(); ++sIdx) {
                    Node sNode = substrateNodes.item(sIdx);

                    if (sNode.getNodeType() != Node.ELEMENT_NODE)
                        continue;

                    String nodeName = sNode.getNodeName();
                    String nodeContent = sNode.getTextContent();

                    switch (nodeName) {
                        case "reactant":
                            reaction.reactants.add(nodeContent);
                            break;
                        case "inhibitor":
                            reaction.inhibitors.add(nodeContent);
                            break;
                        case "product":
                            reaction.products.add(nodeContent);
                            break;
                        default:
                            throw new ReactionSystemStructureError("Unexpected node type: " + nodeName);
                    }
                }

                processEditor.addReaction(reaction);
            }

            procEditors.add(processEditor);
            processPanel.add(processEditor);
        }

        revalidate();
    }

    public String toRSSLString() {
        StringBuilder rsString = new StringBuilder("reactions {\n");

        for (ProcessEditor pe : procEditors) {
            rsString.append(pe.toRSSLString());
        }

        rsString.append("};\n");

        return rsString.toString();
    }

    public void clear() {
        processPanel.removeAll();
        procEditors.clear();
        rs.clearProcesses();
    }

    private void createProcess() {
        ProcessEditor newProcEdt = new ProcessEditor(rs.createProcess());
        procEditors.add(newProcEdt);
        processPanel.add(newProcEdt);
        rs.modified = true;
        revalidate();
    }

    private void createProcess(String label) {
        ProcessEditor newProcEdt = new ProcessEditor(rs.createProcess(label));
        procEditors.add(newProcEdt);
        processPanel.add(newProcEdt);
        rs.modified = true;
        revalidate();
    }

    private void removeProcesses() {
        Vector<ProcessEditor> toRemove = new Vector<ProcessEditor>();
        for (ProcessEditor edt : procEditors) {
            if (edt.isSelected()) {
                toRemove.add(edt);
            }
        }

        if (toRemove.size() == procEditors.size()) {
            JOptionPane.showMessageDialog(this, "There should be at least a single process in the system.",
                    "Warning", JOptionPane.WARNING_MESSAGE);
            return;
        }

        for (ProcessEditor edt : toRemove) {
            if (rs.removeProcess(edt.getProcess())) {
                processPanel.remove(edt);
                procEditors.remove(edt);
            }
            else {
                JOptionPane.showMessageDialog(this, "Process " + edt.getLabel() +
                                " appears in a formula or a context automaton guard.\n" +
                                "Update them before removing the process.",
                        "Warning", JOptionPane.WARNING_MESSAGE);
            }
        }

        rs.modified = true;
        revalidate();
    }

    private void copyProcesses() {
        Vector<ProcessEditor> toBeCopied = new Vector<ProcessEditor>();

        for (ProcessEditor edt : procEditors) {
            if (edt.isSelected()) {
                toBeCopied.add(edt);
            }
        }

        for (ProcessEditor edt : toBeCopied) {
            ProcessEditor newEdt = new ProcessEditor(rs.copyProcess(edt.getProcess()));
            processPanel.add(newEdt);
            procEditors.add(newEdt);
        }

        rs.modified = true;
        revalidate();
    }

    private void renameProcess() {
        ProcessEditor toRename = null;
        boolean fail = false;

        for (ProcessEditor edt : procEditors) {
            if (edt.isSelected()) {
                if (toRename == null) {
                    toRename = edt;
                }
                else {
                    fail = true;
                    break;
                }
            }
        }

        if (fail || toRename == null) {
            JOptionPane.showMessageDialog(this, "Select a single process to rename.", "Select process", JOptionPane.WARNING_MESSAGE);
            return;
        }

        String idRegex = "[a-zA-Z][a-zA-Z_0-9:-]*";
        boolean idOk = false;

        do {
            String newLabel = JOptionPane.showInputDialog(this, "Process name", toRename.getProcess().label);
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
                rs.renameProcess(toRename.getProcess(), newLabel);
                toRename.rename(newLabel);
                rs.notifyObservers();
            }
        }
        while (!idOk);

    }

    private void moveSelectedUp() {
        Vector<Integer> toBeMovedIds = new Vector<Integer>();
        for (int i = 0; i< procEditors.size(); ++i) {
            if (procEditors.elementAt(i).isSelected())
                toBeMovedIds.add(i);
        }

        for (int pos : toBeMovedIds) {
            if (pos == 0 || procEditors.elementAt(pos-1).isSelected())
                continue;

            Collections.swap(procEditors, pos, pos-1);
        }

        processPanel.removeAll();

        for (ProcessEditor edt : procEditors) {
            processPanel.add(edt);
        }

        rs.modified = true;
        revalidate();
    }

    private void moveSelectedDown() {
        Vector<Integer> toBeMovedIds = new Vector<Integer>();

        for (int i = procEditors.size()-1; i>=0; --i) {
            if (procEditors.elementAt(i).isSelected())
                toBeMovedIds.add(i);
        }

        for (int pos : toBeMovedIds) {
            if (pos == procEditors.size()-1 || procEditors.elementAt(pos+1).isSelected())
                continue;

            Collections.swap(procEditors, pos, pos+1);
        }

        processPanel.removeAll();

        for (ProcessEditor edt : procEditors) {
            processPanel.add(edt);
        }

        rs.modified = true;
        revalidate();
    }

    public void onRSUpdate() {
        repaint();
    }

}


class ReactionSystemStructureError extends FileStructureError {
    public ReactionSystemStructureError(String message) {
        super(message);
    }
}