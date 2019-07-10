package de.mpicbg.tomancaklab.graphexport;

import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;
import org.graphstream.graph.implementations.DefaultGraph;
import org.graphstream.ui.view.Viewer;

public class GraphStreamViewer
{
	final Graph graph;

	public GraphStreamViewer()
	{
		graph = new DefaultGraph("Mastodon Generation Lineage");
		graph.display( false ).setCloseFramePolicy(Viewer.CloseFramePolicy.CLOSE_VIEWER);
	}

	public void runExample()
	{
		System.out.println("gsApp started");

		//coords are:
		// x - horizontal, higher means more right
		// y - vertical, higher means more up
		// ([0,0] is bottom-left corner)

		//the main root of the tree
		graph.addNode("A").addAttribute("xyz", new int[] {20,0,0} );

		//left subtree: straight lines
		addStraightLineConnectedVertex("A" , "AL",  10,-20,0);
		addStraightLineConnectedVertex("AL", "ALL",  5,-40,0);
		addStraightLineConnectedVertex("AL", "ALR", 15,-40,0);

		//right subtree: bended lines
		addBendedLineConnectedVertex( "A" , "AR",  30,-20,0);
		addBendedLineConnectedVertex( "AR", "ARL", 25,-40,0);
		addBendedLineConnectedVertex( "AR", "ARR", 35,-40,0);

		System.out.println("gsApp stopped");
	}


	public void addStraightLineConnectedVertex(final String parentNodeID,
															 final String newNodeID,
															 final int... xyz)
	{
		graph.addNode( newNodeID ).addAttribute( "xyz", xyz );
		graph.addEdge( parentNodeID.concat( newNodeID ), parentNodeID, newNodeID );
		System.out.println(parentNodeID+" -> "+newNodeID);
	}


	final float bendingPointRelativeFraction = 0.1f;

	public void addBendedLineConnectedVertex(final String parentNodeID,
														  final String newNodeID,
														  final int... xyz)
	{
		//ID of the hidden node -- the "bender"
		final String benderNodeID = newNodeID.concat("hidden_");

		//y-coordinate of the "parent"/root vertex
		Node n = graph.getNode( parentNodeID );
		if (n == null)
			throw new RuntimeException("Couldn't find the vertex: "+parentNodeID);
		//
		float y = ((int[])n.getAttribute( "xyz" ))[1];

		//y-coordinate of the (hidden) bending vertex
		y *= 1.0f - bendingPointRelativeFraction;
		y += bendingPointRelativeFraction * (float)xyz[1];

		n = graph.addNode( benderNodeID );
		//n.addAttribute( "xyz", new int[] { xyz[0], (int)y, xyz[2] } );
		n.addAttribute( "xyz", xyz[0], (int)y, xyz[2] );
		n.addAttribute( "ui.hide" );

		graph.addNode( newNodeID ).addAttribute( "xyz", xyz );

		graph.addEdge( parentNodeID.concat( benderNodeID ), parentNodeID, benderNodeID );
		graph.addEdge( benderNodeID.concat( newNodeID ),    benderNodeID, newNodeID );
	}
}
