package pl.umk.mat.martinp.reactics;

import edu.uci.ics.jung.algorithms.layout.FRLayout;
import edu.uci.ics.jung.algorithms.layout.GraphElementAccessor;
import edu.uci.ics.jung.algorithms.layout.Layout;
import edu.uci.ics.jung.algorithms.layout.StaticLayout;
import edu.uci.ics.jung.algorithms.layout.util.Relaxer;
import edu.uci.ics.jung.graph.Graph;
import edu.uci.ics.jung.graph.util.Context;
import edu.uci.ics.jung.graph.util.Pair;
import edu.uci.ics.jung.visualization.VisualizationViewer;
import edu.uci.ics.jung.visualization.control.DefaultModalGraphMouse;
import edu.uci.ics.jung.visualization.control.ModalGraphMouse;
import edu.uci.ics.jung.visualization.decorators.EdgeShape;
import edu.uci.ics.jung.visualization.decorators.ToStringLabeller;
import edu.uci.ics.jung.visualization.picking.PickedState;
import edu.uci.ics.jung.visualization.renderers.Renderer;
import org.apache.commons.collections15.Transformer;
import org.w3c.dom.Document;
import javax.swing.*;
import javax.swing.border.EtchedBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.AffineTransform;
import java.awt.geom.Point2D;
import java.io.PrintWriter;
import java.util.*;


public class ContextAutomatonEditor extends JPanel implements RSObserver {
    private enum EditorState {STATE, EDGE, DELETE, CLEAR, NONE}

    private static final long serialVersionUID = 1L;

    private ReactionSystem rs;

    //---------------------------------------------------------------
    // Visual configuration settings
    //---------------------------------------------------------------
    private static final Color pickedNodeColor = Color.yellow;
    //private static final Color pickedEdgeColor = Color.red;
    private static final Color pickedEdgeColor = Color.black;
    private static final Color edgeColor = Color.black;
    private static final Color emptyEdgeColor = Color.lightGray;
    private static final Font nodeLabelFont = new Font("Helvetica", Font.BOLD, 20);
    private static final Font edgeLabelFont = new Font("Helvetica", Font.BOLD, 15);
    private static final Font toolTipFont = new Font("Helvetica", Font.PLAIN, 14);
    private static final float[] dash = {10.0f, 10.0f};
    private static final Stroke basicEdgeStroke = new BasicStroke(3.0f,BasicStroke.CAP_ROUND,BasicStroke.JOIN_ROUND);
    private static final Stroke emptyEdgeStroke = new BasicStroke(3.0f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND, 10.0f, dash, 0.f);
    private static final Stroke basicEdgeArrow = new BasicStroke(3.0f);
    private static final Stroke emptyEdgeArrow = new BasicStroke(3.0f, BasicStroke.CAP_BUTT, BasicStroke.JOIN_ROUND, 10.0f, dash, 10.0f);

    private static Dimension initialEditorSize;

    private VisualizationViewer<CAState, CAEdge> graphViewer;
    private Layout<CAState, CAEdge> gLayout;
    DefaultModalGraphMouse graphMouse;
    private ContextAutomatonGraph graph;

    // Context menus for transitions, places and edges
    private JPopupMenu stateContextMenu;
    private JPopupMenu edgeContextMenu;
    private TransitionEditor transitionEditor = null;

    private EditorState edtState;
    private Vector<EditorModeButton> modeButtons;

    private CAState lastPickedNode = null;


    public ContextAutomatonEditor(Dimension size) {
        this.setLayout(new BorderLayout());
        initialEditorSize = size;

        edtState = EditorState.NONE;
        graph = new ContextAutomatonGraph();

        createGraphEditor();
        createModeButtonsPanel();
        createContextMenus();

        rs = ReactionSystem.getInstance();
    }

    public boolean isModified() { return graph.isModified(); }

    public void clearModificationStatus() { graph.clearModificationStatus(); }

    public String toRSSLString() {
        return graph.toRSSLString();
    }

    public void exportToXML(PrintWriter output) {
        updateNodesLocations();
        graph.exportToXML(output);
    }

    public void loadFromXML(Document input) throws ContextAutomatonStructureError {
        clear();
        graph.loadFromXML(input);
    }


    public void recalculateCoordinates() {
        Layout<CAState, CAEdge> autoLayout = new FRLayout<CAState, CAEdge>(graph, graphViewer.getSize());
        autoLayout.initialize();

        for (CAState state : graph.getVertices()) {
            Point2D pos = autoLayout.transform(state);
            state.updateLocation(pos);
        }
    }


    public void clear() {
        graph.clear();

        for (EditorModeButton emb : modeButtons)
            emb.setSelected(false);

        graphViewer.repaint();
    }

    public void lockNodesPositions(boolean lock) {
        if (lock)
            graphMouse.setMode(ModalGraphMouse.Mode.TRANSFORMING);
        else
            graphMouse.setMode(ModalGraphMouse.Mode.PICKING);
    }

    public Set<String> getReactantsSet() { return graph.getReactantsSet(); }

    //--------------------------------------------------------------------------
    // Creates visualization viewer for context automaton graph display/edition
    //--------------------------------------------------------------------------
    private void createGraphEditor() {
        gLayout = new StaticLayout<CAState, CAEdge>(graph,
                new Transformer<CAState, Point2D>() {
                    public Point2D transform(CAState node) {
                        return node.getLocation();
                    }
                });

        graphViewer = new VisualizationViewer<CAState, CAEdge>(gLayout, initialEditorSize) {
            public JToolTip createToolTip() {
                JToolTip tooltip = super.createToolTip();
                tooltip.setFont(toolTipFont);
                return tooltip;
            }
        };

        // Nodes labels
        graphViewer.getRenderContext().setVertexLabelTransformer(
                new ToStringLabeller<CAState>());
        graphViewer.getRenderer().getVertexLabelRenderer()
                .setPosition(Renderer.VertexLabel.Position.CNTR);
        graphViewer.getRenderContext().setVertexFontTransformer(
                new Transformer<CAState,Font>() {
                    public Font transform(CAState v) {
                        return nodeLabelFont;
                    }
                });

        // Nodes colour, background, etc.
        graphViewer.getRenderContext().setVertexIconTransformer(new Transformer<CAState,Icon>() {
            public Icon transform(final CAState v) {
                Color nodeColor = null;

                if(graphViewer.getPickedVertexState().isPicked(v))
                    nodeColor = pickedNodeColor;
                else
                    nodeColor = v.getFillColor();

                return (v.isInitial() ? new SquareIcon(nodeColor, v.getWidth()) : new CircleIcon(nodeColor, v.getWidth()));

            }});

        // Edge color, shape and weight
        graphViewer.getRenderContext().setEdgeDrawPaintTransformer(new Transformer<CAEdge, Paint>() {
            public Paint transform(CAEdge e) {
                return edgeColor;
            }
        });

        graphViewer.getRenderContext().setEdgeStrokeTransformer(new Transformer<CAEdge, Stroke>() {
            public Stroke transform(CAEdge e) {
                return basicEdgeStroke;
            }
        });

        graphViewer.getRenderContext().setEdgeArrowStrokeTransformer(new Transformer<CAEdge, Stroke>() {
            public Stroke transform(CAEdge e) {
                return basicEdgeArrow;
            }
        });

        graphViewer.getRenderContext().setArrowFillPaintTransformer(new Transformer<CAEdge, Paint>() {
            public Paint transform(CAEdge caEdge) {
                if (caEdge.hasTransition())
                    return edgeColor;
                else
                    return emptyEdgeColor;
            }
        });

        graphViewer.getRenderContext().setEdgeShapeTransformer(new ConditionalEdgeShape<>(1.5f));

        // Edge labels
        graphViewer.getRenderContext().setEdgeLabelTransformer(new ToStringLabeller<CAEdge>());
        graphViewer.getRenderContext().getEdgeLabelRenderer().setRotateEdgeLabels(true);
        graphViewer.getRenderContext().setLabelOffset(20);

        graphViewer.getRenderContext().setEdgeFontTransformer(new Transformer<CAEdge, Font>() {
            public Font transform(CAEdge CAEdge) {
                return edgeLabelFont;
            }
        });

        // For interactive graph editing
        graphMouse = new DefaultModalGraphMouse();
        graphViewer.setGraphMouse(graphMouse);

        graphMouse.setMode(ModalGraphMouse.Mode.PICKING);

        graphViewer.setVertexToolTipTransformer(new Transformer<CAState, String>() {
            public String transform(CAState caState) {
                return caState.getTooltipText();
            }
        });

        graphViewer.setEdgeToolTipTransformer(new Transformer<CAEdge, String>() {
            public String transform(CAEdge caEdge) {
                return caEdge.getTooltipText();
            }
        });

        graphViewer.setBackground(Color.white);
        graphViewer.setBorder(new EtchedBorder(EtchedBorder.LOWERED));
        graphViewer.addMouseListener(new EditorMouseListener());

        add(graphViewer,BorderLayout.CENTER);
    }

    //---------------------------------------------------------------
    // Create panel with buttons alowing editing mode choice
    //---------------------------------------------------------------
    private void createModeButtonsPanel() {
        modeButtons = new Vector<EditorModeButton>();
        modeButtons.add(new EditorModeButton("STATE",new CircleIcon(CAState.baseFillColor, 15), EditorState.STATE, 0));
        modeButtons.add(new EditorModeButton("EDGE", EditorState.EDGE, 1));
        modeButtons.add(new EditorModeButton("DELETE", EditorState.DELETE, 2));
        modeButtons.add(new EditorModeButton("CLEAR", EditorState.CLEAR, 3));

        ModeButtonsListener mbListener = new ModeButtonsListener();

        for(int i=0;i<modeButtons.size();++i)
            modeButtons.elementAt(i).addActionListener(mbListener);

        JPanel btnPanel = new JPanel();
        btnPanel.setLayout(new FlowLayout());

        for(int i=0;i<modeButtons.size();++i)
            btnPanel.add(modeButtons.elementAt(i));

        JCheckBox posLockCBox = new JCheckBox("Lock relative nodes positions");
        posLockCBox.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent actionEvent) {
                lockNodesPositions(posLockCBox.isSelected());
            }
        });
        btnPanel.add(posLockCBox);

        add(btnPanel,BorderLayout.NORTH);
    }

    //---------------------------------------------------------------
    // Create context menus for transitions, places and edges
    //---------------------------------------------------------------
    private void createContextMenus() {
        stateContextMenu = new JPopupMenu();

        JMenuItem stateInitialItem = new JMenuItem("Set as initial");
        stateInitialItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                PickedState<CAState> pickedVertexState = graphViewer.getPickedVertexState();
                Set<CAState> pickedNodes = pickedVertexState.getPicked();
                Iterator<CAState> it = pickedNodes.iterator();

                if(!it.hasNext()) {
                    return;
                }

                CAState editedNode = it.next();
                pickedVertexState.clear();

                graph.setInitialState(editedNode);
            }
        });

        JMenuItem setLabelItem = new JMenuItem("Set label");
        setLabelItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                PickedState<CAState> pickedVertexState = graphViewer.getPickedVertexState();
                Set<CAState> pickedNodes = pickedVertexState.getPicked();
                Iterator<CAState> it = pickedNodes.iterator();

                if(!it.hasNext()) {
                    return;
                }

                CAState state = it.next();
                pickedVertexState.clear();

                showStateLabelEditDialog(state);
            }
        });

        stateContextMenu.add(stateInitialItem);
        stateContextMenu.add(setLabelItem);
        stateContextMenu.setVisible(false);

        edgeContextMenu = new JPopupMenu();
        JMenuItem edgeLabelEditItem = new JMenuItem("Nondeterministic transitions");
        edgeLabelEditItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                PickedState<CAEdge> pickedEdgeState = graphViewer.getPickedEdgeState();
                Set<CAEdge> pickedEdges = pickedEdgeState.getPicked();
                Iterator<CAEdge> it = pickedEdges.iterator();

                if(!it.hasNext()) {
                    return;
                }

                CAEdge editedEdge = it.next();
                pickedEdgeState.clear();
                showEdgeLabelEditDialog(editedEdge);
            }
        });

        edgeContextMenu.add(edgeLabelEditItem);
        edgeContextMenu.setVisible(false);

        transitionEditor = new TransitionEditor();
    }

    private void showStateLabelEditDialog(CAState state) {
        String idRegex = "[a-zA-Z][a-zA-Z_0-9:-]*";
        boolean idOk = false;

        do {
            String newLabel = JOptionPane.showInputDialog(this, "State label", state.getLabel());

            if (newLabel == null)
                return;

            newLabel = newLabel.trim();

            if (!newLabel.matches(idRegex)) {
                JOptionPane.showMessageDialog(this,
                        "<html>State label should start with a letter and may contain only:<br/>" +
                                "letters, numbers, colons (:), underscores (_) and hyphens (-)</html>",
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
            else {
                idOk = true;
                state.setLabel(newLabel);
            }
        }
        while (!idOk);

        graph.markAsModified();
        this.repaint();
    }

    //---------------------------------------------------------------
    // Creates a simple dialog window for editing edge labels
    //---------------------------------------------------------------
    private void showEdgeLabelEditDialog(CAEdge edge) {
        Pair<CAState> endPoints = graph.getEndpoints(edge);
        transitionEditor.showTransitionEditDialog(this, edge.getTransitions(), endPoints.getFirst().getLabel(), endPoints.getSecond().getLabel());
        graph.markAsModified();
        graphViewer.repaint();
    }

    /** Updates coordinates stored in each graph node (eg. after interactive graph modification).
     *  Called before each storing net structure to the file. */
    private void updateNodesLocations() {
        Collection<CAState> nodes = graph.getVertices();

        for(CAState n : nodes) {
            n.updateLocation(gLayout.transform(n));
        }
    }

    /** For better vertex placement */
    private void relax() {
        Layout<CAState, CAEdge> layout = graphViewer.getGraphLayout();
        layout.initialize();
        layout.setSize(graphViewer.getSize());
        Relaxer relaxer = graphViewer.getModel().getRelaxer();
        if (relaxer != null) {
            relaxer.stop();
            relaxer.prerelax();
            relaxer.relax();
        }
    }

    public void onRSUpdate() {
        repaint();
    }

    //---------------------------------------------------------------------------------------------


    static class EditorModeButton extends JToggleButton {
        private EditorState mode;
        int seqNum;

        public EditorModeButton(String label, EditorState mode) {
            super(label);

            this.mode = mode;
            seqNum = 0;
        }

        public EditorModeButton(String label, EditorState mode, int seqNum) {
            super(label);

            this.mode = mode;
            this.seqNum = seqNum;
        }

        public EditorModeButton(String label, Icon icon, EditorState mode, int seqNum) {
            super(label, icon);

            this.mode = mode;
            this.seqNum = seqNum;
        }

        public EditorState getMode() {
            return mode;
        }

        public int getSeqNum() {
            return seqNum;
        }
    }


    //---------------------------------------------------------------------------------------------


    class ModeButtonsListener implements ActionListener {

        public void actionPerformed(ActionEvent changeEvent) {
            EditorModeButton emb = (EditorModeButton) changeEvent.getSource();

            if(emb.isSelected()) {
                int num = emb.getSeqNum();

                for(int i=0;i<modeButtons.size();++i)
                    if(i != num || emb.mode == EditorState.CLEAR)
                        modeButtons.elementAt(i).setSelected(false);

                edtState = emb.getMode();
            }
            else {
                edtState = EditorState.NONE;
            }

            if (edtState == EditorState.CLEAR) {
                graph.clear();
                repaint();
                edtState = EditorState.NONE;
            }
        }

    };


    //---------------------------------------------------------------------------------------------
    // Mouse event handler. To allow interactive net editing
    //---------------------------------------------------------------------------------------------
    class EditorMouseListener extends MouseAdapter {

        public void mouseClicked(MouseEvent me) {
            int btnClicked = me.getButton();

            if(btnClicked == MouseEvent.BUTTON1)
                leftButtonClicked(me);
            else if(btnClicked == MouseEvent.BUTTON3)
                rightButtonClicked(me);
        }

        private void leftButtonClicked(MouseEvent me) {
            Point clickPt = me.getPoint();
            GraphElementAccessor<CAState, CAEdge> pickSupport = null;
            Layout<CAState, CAEdge> layout = null;
            CAState node = null;
            CAEdge edge = null;

            switch(edtState) {
                case STATE:
                    try {
                        // Transform screen coordinates to layout coordinates.
                        // Necessary for possible automaton structure viewer scaling.
                        Point2D nodeLocation = graphViewer.getRenderContext().getMultiLayerTransformer().inverseTransform(clickPt);
                        graph.addState(new CAState(nodeLocation));
                    } catch (ContextAutomatonStructureError e) {
                        JOptionPane.showMessageDialog(null,
                                e.getMessage(),
                                "Error", JOptionPane.ERROR_MESSAGE);
                    }
                    break;

                case EDGE:
                    PickedState<CAState> pickedVertexState = graphViewer.getPickedVertexState();

                    pickSupport = graphViewer.getPickSupport();
                    layout = graphViewer.getGraphLayout();
                    node = pickSupport.getVertex(layout, clickPt.getX(), clickPt.getY());

                    if (node != null) {
                        if (lastPickedNode == null) {
                            lastPickedNode = node;
                        } else {
                            graph.addEdge(lastPickedNode, node);
                            lastPickedNode = null;
                            pickedVertexState.pick(node,false);
                        }
                    } else {
                        lastPickedNode = null;
                    }

                    break;

                case DELETE:
                    pickSupport = graphViewer.getPickSupport();
                    layout = graphViewer.getGraphLayout();
                    node = pickSupport.getVertex(layout, clickPt.getX(), clickPt.getY());
                    edge = pickSupport.getEdge(layout, clickPt.getX(), clickPt.getY());

                    if (node != null) {
                        Collection<CAEdge> edges = graph.getIncidentEdges(node);

                        for (CAEdge e : edges)
                            rs.removeCAEdge(e);

                        graph.removeState(node);
                    }
                    else if (edge != null) {
                        graph.removeEdge(edge);
                        rs.removeCAEdge(edge);
                    }

                    break;

                case NONE:
                default:
                    break;
            }

            me.consume();
        }

        private void rightButtonClicked(MouseEvent me) {
            GraphElementAccessor<CAState, CAEdge> pickSupport = graphViewer.getPickSupport();
            Layout<CAState, CAEdge> layout = graphViewer.getGraphLayout();
            CAState node = pickSupport.getVertex(layout, me.getX(), me.getY());
            CAEdge edge = pickSupport.getEdge(layout, me.getX(), me.getY());

            if (node != null) {
                PickedState<CAState> pickedVertexState = graphViewer.getPickedVertexState();
                pickedVertexState.clear();
                pickedVertexState.pick(node,true);
                stateContextMenu.show(graphViewer, me.getX(), me.getY());
            }
            else if (edge != null) {
                PickedState<CAEdge> pickedEdgeState = graphViewer.getPickedEdgeState();
                pickedEdgeState.clear();
                pickedEdgeState.pick(edge, true);
                edgeContextMenu.show(graphViewer, me.getX(), me.getY());
            }

            me.consume();
        }

    };

    //---------------------------------------------------------------------------------------------
    // For drawing the initial state
    //---------------------------------------------------------------------------------------------

    static class SquareIcon implements Icon {
        private Color fillColor;
        private int width;

        public SquareIcon(Color fColor, int width) {
            fillColor = fColor;
            this.width = width;
        }

        public void paintIcon(Component c, Graphics g, int x, int y) {
            g.setColor(fillColor);
            g.fillRect(x, y, width, width);
            g.setColor(Color.black);
            g.drawRect(x, y, width, width);
        }

        public int getIconWidth() {
            return width;
        }

        public int getIconHeight() {
            return width;
        }
    }

    //---------------------------------------------------------------------------------------------
    // For drawing all non-initial states
    //---------------------------------------------------------------------------------------------

    static class CircleIcon implements Icon {
        private Color fillColor;
        private int radius;

        public CircleIcon(Color fColor, int radius) {
            fillColor = fColor;
            this.radius = radius;
        }

        public void paintIcon(Component c, Graphics g, int x, int y) {
            g.setColor(fillColor);
            g.fillOval(x, y, radius, radius);
            g.setColor(Color.black);
            g.drawOval(x, y, radius, radius);
        }

        public int getIconWidth() {
            return radius;
        }

        public int getIconHeight() {
            return radius;
        }

    }

}


class ConditionalEdgeShape<V, E> implements Transformer<Context<Graph<V, E>, E>, Shape> {

    private final EdgeShape.Loop<V, E> loopShape;
    private final Transformer<Context<Graph<V, E>, E>, Shape> defaultShape;
    private final float loopScale;

    public ConditionalEdgeShape(float loopScale) {
        this.loopShape = new EdgeShape.Loop<>();
        this.defaultShape = new EdgeShape.QuadCurve<>();  // or Line<>
        this.loopScale = loopScale;
    }

    public Shape transform(Context<Graph<V, E>, E> context) {
        Graph<V, E> graph = context.graph;
        E edge = context.element;
        V src = graph.getSource(edge);
        V dst = graph.getDest(edge);

        if (src.equals(dst)) {
            // Scale the self-loop
            Shape baseLoop = loopShape.transform(context);

            Rectangle bounds = baseLoop.getBounds();
            double centerX = bounds.getCenterX();
            double centerY = bounds.getCenterY();

            AffineTransform at = new AffineTransform();
            at.translate(centerX, centerY);
            at.scale(loopScale, loopScale);
            at.translate(-centerX, -centerY);

            return at.createTransformedShape(baseLoop);
        } else {
            return defaultShape.transform(context);
        }
    }
}
