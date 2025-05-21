package pl.umk.mat.martinp.reactics;


import edu.uci.ics.jung.graph.DirectedSparseGraph;
import edu.uci.ics.jung.graph.util.Pair;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import java.awt.*;
import java.awt.geom.Point2D;
import java.io.PrintWriter;
import java.util.*;


class ContextAutomatonGraph extends DirectedSparseGraph<CAState, CAEdge> {
    private static final long serialVersionUID = 1L;

    HashMap<Integer, CAState> states = new HashMap<>();
    private CAState initialState = null;
    boolean modified = false;

    public ContextAutomatonGraph() {
        super();
    }

    public boolean isModified() { return modified; }

    public void markAsModified() { modified = true; }

    public void clearModificationStatus() { modified = false; }

    String toRSSLString() {
        StringBuilder rsslString = new StringBuilder("context-automaton {\n");

        rsslString.append("    states { ");
        Collection<CAState> allStates = states.values();
        Iterator<CAState> it = allStates.iterator();
        if (it.hasNext()) {
            rsslString.append(it.next().getLabel());
        }
        while (it.hasNext()) {
            rsslString.append(", ").append(it.next().getLabel());
        }
        rsslString.append(" };\n");

        rsslString.append("    init-state { ").append(initialState != null ? initialState.getLabel() : "").append(" };\n");
        rsslString.append("    transitions {\n");

        for (CAEdge edge : this.getEdges()) {
            for (Transition tr : edge.getTransitions()) {
                rsslString.append("        { ").append(tr.context).append(" }: ");
                rsslString.append(this.getSource(edge).label).append(" -> ").append(this.getDest(edge).label);

                String guard = tr.guard;

                if (guard.length() > 0) {
                    rsslString.append(" : ").append(guard);
                }

                rsslString.append(";\n");
            }
        }
        rsslString.append("    };\n");

        rsslString.append("};\n");

        return rsslString.toString();
    }

    public void exportToXML(PrintWriter output) {
        output.println("    <context-automaton>");

        for (CAState state : states.values()) {
            Point2D pos = state.getLocation();
            output.print("        <state");
            output.print(" id=\"" + state.getId() + "\"");
            output.print(" name=\"" + state.getLabel() + "\"");
            output.print(" x=\"" + pos.getX() + "\"");
            output.print(" y=\"" + pos.getY() + "\"");

            if (state.isInitial())
                output.print(" initial=\"true\"");

            output.println("/>");
        }

        for (CAEdge edge : edges.keySet()) {
            Pair<CAState> endPts = this.getEndpoints(edge);
            output.print("        <edge");
            output.print(" from=\"" + endPts.getFirst().getLabel() + "\"");
            output.print(" to=\"" + endPts.getSecond().getLabel() + "\"");
            output.println(">");

            for (Transition tr : edge.getTransitions()) {
                output.print("            <transition");
                output.print(" context=\"" + tr.context + "\"");
                output.print(" guard=\"" + tr.guard + "\"");
                output.println("/>");
            }
            output.println("        </edge>");
        }

        output.println("    </context-automaton>");
    }

    /**
     * Reads the context automaton structure from the XML file.
     *
     * @param input An XML file containing a valid description of a context automaton.
     * @throws ContextAutomatonStructureError In the case of <b>inputFile</b> structure error, eg. \
     *                                        more than one context-automaton section, more than one \
     *                                        initial state, repeating state identifiers, \
     *                                        edge between non-existing nodes, etc.
     */
    public void loadFromXML(Document input) throws ContextAutomatonStructureError {
        NodeList caSections = input.getElementsByTagName("context-automaton");

        if (caSections.getLength() == 0 || caSections.getLength() > 1) {
            throw new ContextAutomatonStructureError("An XML file should contain a single context automaton description.");
        }

        //--------------------------------------------------------------------------------------------------------------
        // Retrieve the states
        //--------------------------------------------------------------------------------------------------------------

        HashMap<String, CAState> states = new HashMap<String, CAState>();
        NodeList stateList = input.getElementsByTagName("state");
        boolean hasInitialState = false;

        for (int idx = 0; idx < stateList.getLength(); ++idx) {
            Node stateNode = stateList.item(idx);

            if (stateNode.getNodeType() != Node.ELEMENT_NODE) {
                continue;
            }

            Element stateElement = (Element) stateNode;

            int id = Integer.parseInt(stateElement.getAttribute("id"));
            double x = Double.parseDouble(stateElement.getAttribute("x"));
            double y = Double.parseDouble(stateElement.getAttribute("y"));
            String name = stateElement.getAttribute("name");
            String initial = stateElement.getAttribute("initial");

            if (states.containsKey(name)) {
                throw new ContextAutomatonStructureError("State name <" + name + "> already used.");
            }

            CAState newState = new CAState(id, name, new Point2D.Double(x, y));
            this.addState(newState);
            states.put(name, newState);

            if (initial.equals("true")) {
                if (hasInitialState)
                    throw new ContextAutomatonStructureError("There should not be more than one initial state.");

                hasInitialState = true;
                this.setInitialState(newState);
            }
        }

        //--------------------------------------------------------------------------------------------------------------
        // Retrieve the edges
        //--------------------------------------------------------------------------------------------------------------

        NodeList edgeList = input.getElementsByTagName("edge");

        for (int idx = 0; idx < edgeList.getLength(); ++idx) {
            Node edgeNode = edgeList.item(idx);

            if (edgeNode.getNodeType() != Node.ELEMENT_NODE) {
                continue;
            }

            Element edgeElement = (Element) edgeNode;

            String from = edgeElement.getAttribute("from");
            String to = edgeElement.getAttribute("to");

            // Retrieve all child nodes describing nondeterministic transitions related to this edge
            NodeList childNodeList = edgeNode.getChildNodes();
            Vector<Transition> transitionList = new Vector<Transition>();

            for (int cIdx=0; cIdx < childNodeList.getLength(); ++ cIdx) {
                Node childNode = childNodeList.item(cIdx);

                if (childNode.getNodeType() != Node.ELEMENT_NODE) {
                    continue;
                }

                Element transElement = (Element) childNode;
                transitionList.add(new Transition(transElement.getAttribute("context"), transElement.getAttribute("guard")));
            }

            CAState stateFrom = states.get(from);
            CAState stateTo = states.get(to);

            if (stateFrom == null || stateTo == null)
                throw new ContextAutomatonStructureError("An edge may be created only between existing nodes.");

            this.addEdge(stateFrom, stateTo, transitionList);
        }
    }

    public Set<String> getReactantsSet() {
        Set<String> reactants = new HashSet<String>();

        for (CAEdge edge : getEdges()) {
            for (Transition trans : edge.getTransitions()) {
                int start = trans.context.indexOf("{");
                int end = trans.context.indexOf("}");

                if (start != -1 && end != -1 && start < end) {
                    reactants.addAll(Arrays.asList(trans.context.substring(start + 1, end).split("\\s*,\\s*")));
                }
            }
        }

        return reactants;
    }

    public void setInitialState(CAState state) {
        if (initialState != null)
            initialState.setInitial(false);

        state.setInitial(true);
        initialState = state;
        modified = true;
    }

    public CAState getInitialState() {
        return initialState;
    }

    /**
     * Clears the entire automaton structure structure
     */
    public void clear() {
        for (CAState st : states.values())
            removeVertex(st);

        states.clear();
        CAState.resetIdCounter();
        modified = true;
    }

    public boolean addEdge(CAState from, CAState to) {
        modified = true;

        return this.addEdge(new CAEdge(), from, to);
    }

    public void addEdge(CAState from, CAState to, Collection<Transition> transitionList) {
        CAEdge edge = this.findEdge(from, to);

        if (edge == null)
            this.addEdge(new CAEdge(transitionList), from, to);
        else
            edge.addTransitions(transitionList);

        modified = true;
    }

    public void addState(CAState state) throws ContextAutomatonStructureError {
        int stateId = state.getId();

        if (states.get(stateId) != null)
            throw new ContextAutomatonStructureError("State id " + stateId + " already in use.");

        states.put(stateId, state);
        this.addVertex(state);
        modified = true;
    }

    public boolean removeState(CAState state) {
        if (states.get(state.getId()) != null) {
            states.remove(state.getId());
        }

        modified = true;

        // Remove the state with all connected edges
        return this.removeVertex(state);
    }

}


//-------------------------------------------------------------------------------------------------
// Single node of the context automaton graph
//-------------------------------------------------------------------------------------------------

class CAState {
    public final static Color baseFillColor = Color.lightGray;
    public final static Color selectedFillColor = Color.lightGray;
    public final static Color initStateFillColor = new Color(102, 178, 255);

    private static final int nodeWidth = 30;
    private static final int nodeHeight = 30;
    protected static int nextId = 1;

    /** Unique auto incremented identifier of the node */
    protected int id;

    /** User defined label of the node displayed as a tool tip and used in RSSL and XML files */
    protected String label;

    protected Point2D location;
    private boolean isInitial = false;

    /** A state created from the description stored in a file. */
    public CAState(int id, String label, Point2D location) {
        this.id = id;
        this.label = label;
        this.location = location;

        // To avoid duplicate node identifiers
        if (id >= nextId)
            nextId = id + 1;
    }

    /** A state created by clicking in graphical component. */
    public CAState(Point2D location) {
        this.id = nextId;
        this.label = "q" + id;
        this.location = location;
        ++nextId;
    }

    public Point2D getLocation() { return location; }
    public void updateLocation(Point2D location) { this.location = location; }

    public boolean isInitial() { return isInitial; }
    public void setInitial(boolean status) { isInitial = status; }

    public int getWidth() { return nodeWidth; }
    public int getHeight() { return nodeHeight; }

    public String getLabel() { return label; }
    public void setLabel(String newLabel) { label = newLabel; }

    public int getId() { return id; }

    static void resetIdCounter() { nextId = 1; }

    public String toString() { return Integer.toString(id); }

    public String getTooltipText() {
        return "<html>"+
                "<b>State</b> " + id + "<br/><hr>" + getLabel() + //"<hr>"+
                "</html>";
    }

    Color getFillColor() {
        return isInitial ? initStateFillColor : baseFillColor;
    }
}


//-------------------------------------------------------------------------------------------------
// Single edge of the context automaton graph.
// Each edge can represent a number of single transitions between the same pair of automaton states.
//-------------------------------------------------------------------------------------------------

class CAEdge {
    protected static int nextId = 0;

    protected int id;

    // The list of all nondeterministic transitions represented by this edge
    private Vector<Transition> transitions = new Vector<Transition>();

    public boolean hasTransition() { return transitions.size() > 0; }


    public CAEdge() {
        this.id = nextId++;
    }

    public CAEdge(Collection<Transition> transitionList) {
        this.transitions.addAll(transitionList);
    }

    Vector<Transition> getTransitions() {
        return transitions;
    }

    public int getId() {
        return id;
    }

    public String toString() {
        // Update this if you need any label displayed together with graph edge
        return "";
    }

    public String getTooltipText() {
        StringBuilder tooTip = new StringBuilder("<html><hr/><center><b>Context <font color=\"red\">:</font> Guard</b></center><hr/>");

        for (Transition tr : transitions) {
            tooTip.append(tr.context).append(" <b><font color=\"red\">:</font></b> ").append(tr.guard).append("<br/><hr/>");
        }

        tooTip.append("</html>");

        return tooTip.toString();
    }

    public void addTransitions(Collection<Transition> transitionList) {
        transitions.addAll(transitionList);
    }
}


//-------------------------------------------------------------------------------------------------
// Single transition. To be included in a multiedge.
//-------------------------------------------------------------------------------------------------

class Transition {
    String context;
    String guard;

    public Transition(String ctx, String grd) {
        context = ctx;
        guard = grd;
    }
}


class ContextAutomatonStructureError extends FileStructureError {
    public ContextAutomatonStructureError(String message) {
        super(message);
    }
}