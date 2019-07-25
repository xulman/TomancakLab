package de.mpicbg.tomancaklab.graphexport;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.implementations.DefaultGraph;
import org.graphstream.ui.view.Viewer;

import java.awt.*;

public class GraphStreamViewer implements GraphExportable
{
	// -----------------------------------------------------------------------------
	private final Graph graph;

	public GraphStreamViewer(final String windowTitle)
	{
		graph = new DefaultGraph(windowTitle);
		graph.display( false ).setCloseFramePolicy(Viewer.CloseFramePolicy.CLOSE_VIEWER);
	}

	@Override
	public void close() {}
	// -----------------------------------------------------------------------------

	private final int yAxisStretchFactor = 3;

	@Override
	public void addNode(final String id,
	             final String label, final int colorRGB,
	             final int x, final int y)
	{
		addNode(id, label,colorRGB, x,y, defaultNodeWidth,defaultNodeHeight);
	}

	@Override
	public void addNode(final String id,
	             final String label, final int colorRGB,
	             final int x, final int y,
	             final int width, final int height)
	{
		final Node n = graph.addNode( id );
		n.addAttribute( "xyz", x,-y *yAxisStretchFactor,0 );
		n.addAttribute( "ui.style", "size: "+width+","+height+";" );
		n.addAttribute( "ui.style", "stroke-mode: plain; stroke-color: #000000;" );
		n.addAttribute( "ui.style", "fill-color: rgb("
		                                 +((colorRGB>>16)&0xFF)+","
		                                 +((colorRGB>> 8)&0xFF)+","
		                                 +((colorRGB    )&0xFF)+");" );

		n.addAttribute( "ui.style", "text-alignment: center;" );
		n.addAttribute( "ui.style", "text-offset: "+(-width)+",0;" );
		n.addAttribute( "ui.label", label );
	}
	// -----------------------------------------------------------------------------

	@Override
	public void addStraightLine(final String fromId, final String toId)
	{
		graph.addEdge(fromId.concat(toId), fromId, toId);
		System.out.println(fromId+" -> "+toId);
	}

	@Override
	public void addStraightLineConnectedVertex(final String parentNodeID,
	                                           final String newNodeID,
	                                           final String label, final int colorRGB,
	                                           final int x, final int y)
	{
		addNode(newNodeID, label,colorRGB, x,y);
		addStraightLine(parentNodeID, newNodeID);
	}
	// -----------------------------------------------------------------------------

	@Override
	public void addBendedLine(final String fromId, final String toId,
	                          final int toX, final int toY)
	{
		addBendedLine(fromId,toId, toX,toY, defaultBendingPointAbsoluteOffsetY);
	}

	@Override
	public void addBendedLine(final String fromId, final String toId,
	                          final int toX, final int toY, final int bendingOffsetY)
	{
		//ID of the hidden node -- the "bender"
		final String benderNodeID = toId.concat("hidden");
		final Node n = graph.addNode( benderNodeID );
		n.addAttribute( "xyz", toX,(-toY-bendingOffsetY) *yAxisStretchFactor,0 );
		n.addAttribute( "ui.hide" );

		graph.addEdge( fromId.concat( benderNodeID ), fromId, benderNodeID );
		graph.addEdge( benderNodeID.concat( toId ),   benderNodeID, toId );
		System.out.println(fromId+" -> "+toId);
	}

	@Override
	public void addBendedLineConnectedVertex(final String parentNodeID,
														  final String newNodeID,
	                                         final String label, final int colorRGB,
	                                         final int x, final int y)
	{
		addNode(newNodeID, label,colorRGB, x,y);
		addBendedLine(parentNodeID, newNodeID, x,y);
	}
	// -----------------------------------------------------------------------------

	public void runExample()
	{
		System.out.println("gsApp started");

		//coords are:
		// x - horizontal, higher means more right
		// y - vertical, higher means more up
		// ([0,0] is bottom-left corner)

		//the main root of the tree
		addNode("A", "A",defaultNodeColour, 200,0);

		//left subtree: straight lines
		addStraightLineConnectedVertex("A" , "AL" , "AL" ,defaultNodeColour, 100,200);
		addStraightLineConnectedVertex("AL", "ALL", "ALL",defaultNodeColour,  50,400);
		addStraightLineConnectedVertex("AL", "ALR", "ALR",defaultNodeColour, 150,400);

		//right subtree: bended lines
		addBendedLineConnectedVertex( "A" , "AR" , "AR" ,defaultNodeColour, 300,200);
		addBendedLineConnectedVertex( "AR", "ARL", "ARL",defaultNodeColour, 250,400);
		addBendedLineConnectedVertex( "AR", "ARR", "ARR",defaultNodeColour, 350,400);

		System.out.println("gsApp stopped");
	}
}
