package pl.umk.mat.martinp.reactics;

import edu.uci.ics.jung.algorithms.layout.*;
import edu.uci.ics.jung.algorithms.layout.util.Relaxer;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import edu.uci.ics.jung.visualization.VisualizationViewer;
import edu.uci.ics.jung.visualization.control.DefaultModalGraphMouse;
import edu.uci.ics.jung.visualization.control.ModalGraphMouse;
import edu.uci.ics.jung.visualization.decorators.ToStringLabeller;
import edu.uci.ics.jung.visualization.renderers.Renderer;
import org.apache.commons.collections15.Transformer;

import javax.swing.JPanel;
import javax.swing.JToolTip;
import javax.swing.Icon;
import javax.swing.border.EtchedBorder;
import java.awt.*;
import java.util.HashMap;


public class TransitionSystemViewer extends JPanel {

    //---------------------------------------------------------------
    // Visual configuration settings
    //---------------------------------------------------------------

    private static final Color pickedNodeColor = Color.yellow;
    private static final Color edgeColor = Color.black;
    private static final Font nodeLabelFont = new Font("Helvetica", Font.BOLD, 20);
    private static final Font toolTipFont = new Font("Helvetica", Font.PLAIN, 14);
    private static final Stroke basicEdgeArrow = new BasicStroke(3.0f);

    private static Dimension initialEditorSize;

    private VisualizationViewer<TSState, TSTransition> graphViewer;
    private Layout<TSState, TSTransition> graphLayout;
    DefaultModalGraphMouse graphMouse;

    //---------------------------------------------------------------
    // Transition system graph
    //---------------------------------------------------------------

    private DirectedSparseGraph<TSState, TSTransition> tsGraph;
    private boolean isCompressed;

    // Is transition system already computed?
    // Used to avoid unnecessary computation of the same graph.
    private boolean computed = false;

    //   compressed == true => context automaton state is not taken into account.
    public TransitionSystemViewer(Dimension size, boolean compressed) {
        this.setLayout(new BorderLayout());
        tsGraph = new DirectedSparseGraph<TSState, TSTransition>();
        this.isCompressed = compressed;
        initialEditorSize = size;

        createGraphViever();
        lockNodesPositions(false);
    }

    // Is transition system graph already computed?
    boolean isComputed() { return computed; }

    private void createGraphViever() {
        graphLayout = new FRLayout<TSState, TSTransition>(tsGraph);

        graphViewer = new VisualizationViewer<TSState, TSTransition>(graphLayout, initialEditorSize) {
            public JToolTip createToolTip() {
                JToolTip tooltip = super.createToolTip();
                tooltip.setFont(toolTipFont);
                return tooltip;
            }
        };

        // Nodes labels
        graphViewer.getRenderContext().setVertexLabelTransformer(
                new ToStringLabeller<TSState>());
        graphViewer.getRenderer().getVertexLabelRenderer()
                .setPosition(Renderer.VertexLabel.Position.CNTR);
        graphViewer.getRenderContext().setVertexFontTransformer(
                new Transformer<TSState,Font>() {
                    public Font transform(TSState st) {
                        return nodeLabelFont;
                    }
                });

        // Nodes colour, background, etc.
        graphViewer.getRenderContext().setVertexIconTransformer(new Transformer<TSState,Icon>() {
            public Icon transform(final TSState v) {
                Color nodeColor = null;

                if(graphViewer.getPickedVertexState().isPicked(v))
                    nodeColor = pickedNodeColor;
                else
                    nodeColor = v.getFillColor();

                return (v.isInitial() ? new SquareIcon(nodeColor, v.getWidth()) : new CircleIcon(nodeColor, v.getWidth()));

            }});

        graphViewer.getRenderContext().setEdgeShapeTransformer(new ConditionalEdgeShape<>(1.5f));

        // Edges
        graphViewer.getRenderContext().setEdgeArrowStrokeTransformer(new Transformer<TSTransition, Stroke>() {
            public Stroke transform(TSTransition tr) {
                return basicEdgeArrow;
            }
        });

        // For interactive graph editing
        graphMouse = new DefaultModalGraphMouse();
        graphViewer.setGraphMouse(graphMouse);
        graphMouse.setMode(ModalGraphMouse.Mode.PICKING);

        graphViewer.setVertexToolTipTransformer(new Transformer<TSState, String>() {
            public String transform(TSState st) {
                return st.getTooltipText();
            }
        });

        graphViewer.setBackground(Color.white);
        graphViewer.setBorder(new EtchedBorder(EtchedBorder.LOWERED));

        add(graphViewer, BorderLayout.CENTER);
    }


    public void updateTransitionSystemStructure(String tsString) {
        // Clear graph
        clear();

        // Load graph structure
        int nextId = 1;

        HashMap<String, TSState> nodes = new HashMap<>();
        TSState src = null;

        for (String line : tsString.split("\\R")) {
            char type = line.charAt(0);
            line = line.substring(2).strip();
            int end = line.lastIndexOf('}');
            String automatonState = line.substring(end + 1, line.length() - 1).strip();
            String stateStr = line.substring(line.indexOf('{'), end + 1);
            TSState state = nodes.get( isCompressed ? stateStr : line);

            if (state == null) {
                state = new TSState(nextId++, stateStr, isCompressed ? null : automatonState);
                nodes.put(isCompressed ? stateStr : line, state);
                tsGraph.addVertex(state);
            }

            if (type == 'G') {
                src = state;
            }
            else if (type == 's') {
                tsGraph.addEdge(new TSTransition(), src, state);
            }
        }

        // Find the initial state
        for (TSState state : tsGraph.getVertices()) {
            if (tsGraph.getInEdges(state).size() == 0) {
                state.setAsInitial();
                break;
            }
        }

        relax();
        graphViewer.repaint();
        computed = true;
    }


    public void lockNodesPositions(boolean lock) {
        if (lock)
            graphMouse.setMode(ModalGraphMouse.Mode.TRANSFORMING);
        else
            graphMouse.setMode(ModalGraphMouse.Mode.PICKING);
    }


    public void clear() {
        for (TSState st : new java.util.ArrayList<TSState>(tsGraph.getVertices())) {
            tsGraph.removeVertex(st);
        }

        repaint();
    }


    /** For better vertex placement */
    private void relax() {
        graphLayout.initialize();
        graphLayout.setSize(graphViewer.getSize());
        Relaxer relaxer = graphViewer.getModel().getRelaxer();

        if (relaxer != null) {
            relaxer.stop();
            relaxer.prerelax();
            relaxer.relax();
        }
    }


    //---------------------------------------------------------------------------------------------
    // For drawing the initial state
    //---------------------------------------------------------------------------------------------

    static class SquareIcon implements Icon {
        private final Color fillColor;
        private final int width;

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
        private final Color fillColor;
        private final int radius;

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


//-------------------------------------------------------------------------------------------------
// Single node of the Transition system graph
//-------------------------------------------------------------------------------------------------

class TSState {

    public final static Color fillColor = Color.lightGray;
    public final static Color initialColor = new Color(102, 178, 255);

    private static final int nodeWidth = 30;
    private static final int nodeHeight = 30;

    private final int id;
    private final String rsDetails;
    private final String aState;
    private boolean initial = false;

    public TSState(int id, String stateStr) {
        this.id = id;
        this.rsDetails = formatRSDetails(stateStr.substring(1, stateStr.length() - 1).strip());
        this.aState = null;
    }

    public TSState(int id, String stateStr, String aState) {
        this.id = id;
        this.rsDetails = formatRSDetails(stateStr.substring(1, stateStr.length() - 1).strip());
        this.aState = aState;
    }

    public boolean isInitial() {
        return initial;
    }

    public void setAsInitial() {
        initial = true;
    }

    public String toString() {
        return String.valueOf(id);
    }

    public int getWidth() {
        return nodeWidth;
    }

    public int getHeight() {
        return nodeHeight;
    }

    Color getFillColor() {
        return initial ? initialColor : fillColor;
    }

    public String getTooltipText() {
        if (aState != null)
            return "<html>"+
                    "<b>CA</b> " + aState+ "<br/><hr>" + rsDetails +
                    "</html>";
        else
            return "<html>"+
                    rsDetails +
                    "</html>";
    }

    private String formatRSDetails(String rsDetails) {
        return rsDetails.replaceAll("\\} (proc\\d+=\\{)", "}<br/>$1");
    }
}


//-------------------------------------------------------------------------------------------------
// Single edge of the Transition system graph
//-------------------------------------------------------------------------------------------------

class TSTransition { }
