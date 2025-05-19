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
public class ReactionSystemEditor extends JPanel {
    private Vector<ProcessEditor> processes = new Vector<ProcessEditor>();
    private JPanel processPanel = new JPanel();
    private boolean modified = false;


    public ReactionSystemEditor() {
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
        buttonPanel.add(upButton);
        buttonPanel.add(downButton);

        this.setLayout(new BorderLayout());
        this.add(new JScrollPane(processPanel), BorderLayout.CENTER);
        this.add(buttonPanel, BorderLayout.WEST);

        createProcess();
    }

    public boolean isModified() {
        boolean procModified = false;

        for (ProcessEditor pe : processes)
            procModified |= pe.isModified();

        return modified | procModified;
    }

    public void clearModificationStatus() {
        for (ProcessEditor pe : processes)
            pe.clearModificationStatus();

        modified = false;
    }

    public Set<String> getReactantsSet() {
        HashSet<String> rset = new HashSet<String>();

        for (ProcessEditor pe : processes)
            rset.addAll(pe.getReactantsSet());

        return rset;
    }

    public void exportToXML(PrintWriter output) {
        output.println("    <reaction-system>");

        for (ProcessEditor process : processes)
            process.exportToXML(output);

        output.println("    </reaction-system>");
    }

    public void loadFromXML(Document input) throws ReactionSystemStructureError {
        NodeList rsSextions = input.getElementsByTagName("reaction-system");

        if (rsSextions.getLength() == 0 || rsSextions.getLength() > 1) {
            throw new ReactionSystemStructureError("An XML file should contain a single reaction system description.");
        }

        NodeList processList = rsSextions.item(0).getChildNodes();

        for (int idx=0; idx<processList.getLength(); ++idx) {
            Node processNode = processList.item(idx);

            if (processNode.getNodeType() != Node.ELEMENT_NODE)
                continue;

            String procName = processNode.getAttributes().getNamedItem("name").getNodeValue();
            ProcessEditor processEditor = new ProcessEditor(procName);

            //----------------------------------------------------------------------------------------------------------
            // Reactins details
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

            processes.add(processEditor);
            processPanel.add(processEditor);
        }

        revalidate();
    }

    public String toRSSLString() {
        StringBuilder rsString = new StringBuilder("reactions {\n");

        for (ProcessEditor pe : processes) {
            rsString.append(pe.toRSSLString());
        }

        rsString.append("};\n");

        return rsString.toString();
    }

    public void clear() {
        processPanel.removeAll();
        processes.clear();
    }

    private void createProcess() {
        ProcessEditor newProcess = new ProcessEditor();
        processes.add(newProcess);
        processPanel.add(newProcess);
        modified = true;
        revalidate();
    }

    private void createProcess(String label) {
        ProcessEditor newProcess = new ProcessEditor(label);
        processes.add(newProcess);
        processPanel.add(newProcess);
        modified = true;
        revalidate();
    }

    private void removeProcesses() {
        Vector<ProcessEditor> toRemove = new Vector<ProcessEditor>();
        for (ProcessEditor edt : processes) {
            if (edt.isSelected()) {
                toRemove.add(edt);
            }
        }

        if (toRemove.size() == processes.size()) {
            JOptionPane.showMessageDialog(this, "There should be at least a single process in the system.",
                    "Warning", JOptionPane.WARNING_MESSAGE);
            return;
        }

        for (ProcessEditor edt : toRemove) {
            processPanel.remove(edt);
            processes.remove(edt);
        }

        modified = true;
        revalidate();
    }

    private void copyProcesses() {
        Vector<ProcessEditor> toBeCopied = new Vector<ProcessEditor>();

        for (ProcessEditor edt : processes) {
            if (edt.isSelected()) {
                toBeCopied.add(edt);
            }
        }

        for (ProcessEditor edt : toBeCopied) {
            ProcessEditor newEdt = new ProcessEditor(edt);
            processPanel.add(newEdt);
            processes.add(newEdt);
        }

        modified = true;
        revalidate();
    }

    private void moveSelectedUp() {
        Vector<Integer> toBeMovedIds = new Vector<Integer>();
        for (int i=0; i<processes.size(); ++i) {
            if (processes.elementAt(i).isSelected())
                toBeMovedIds.add(i);
        }

        for (int pos : toBeMovedIds) {
            if (pos == 0 || processes.elementAt(pos-1).isSelected())
                continue;

            Collections.swap(processes, pos, pos-1);
        }

        processPanel.removeAll();

        for (ProcessEditor edt : processes) {
            processPanel.add(edt);
        }

        modified = true;
        revalidate();
    }

    private void moveSelectedDown() {
        Vector<Integer> toBeMovedIds = new Vector<Integer>();

        for (int i=processes.size()-1; i>=0; --i) {
            if (processes.elementAt(i).isSelected())
                toBeMovedIds.add(i);
        }

        for (int pos : toBeMovedIds) {
            if (pos == processes.size()-1 || processes.elementAt(pos+1).isSelected())
                continue;

            Collections.swap(processes, pos, pos+1);
        }

        processPanel.removeAll();

        for (ProcessEditor edt : processes) {
            processPanel.add(edt);
        }

        modified = true;
        revalidate();
    }

}


class ReactionSystemStructureError extends FileStructureError {
    public ReactionSystemStructureError(String message) {
        super(message);
    }
}