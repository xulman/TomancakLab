package de.mpicbg.tomancaklab.graphexport;

public interface GraphExportable
{
	/** grid stepping along x */
	int xColumnWidth = 50;
	/** grid stepping along y */
	int yLineStep = 100;
	/** the bending point along y */
	int defaultBendingPointAbsoluteOffsetY = -80;

	int defaultNodeWidth  = 30;
	int defaultNodeHeight = 30;
	int defaultNodeColour = 0xCCCCCC;

	/** adds node whose color should have a meaning
	    when read in hexadecimal 0xRRGGBB format; default
	    width and height of the node graphics shall be used */
	void addNode(final String id,
	             final String label, final int colorRGB,
	             final int x, final int y);

	/** adds node whose color should have a meaning
	    when read in hexadecimal 0xRRGGBB format */
	void addNode(final String id,
	             final String label, final int colorRGB,
	             final int x, final int y,
	             final int width, final int height);


	void addStraightLine(final String fromId, final String toId);

	/** adds a new node and connects the given parent with this node;
	    default size of the node is expected */
	void addStraightLineConnectedVertex(final String parentNodeID,
	                                    final String newNodeID,
	                                    final String label, final int colorRGB,
	                                    final int x, final int y);


	/** adds bended line where the bending shall happen at
	    [toX + defaultNodeWidth/2 , toY + defaultBendingPointAbsoluteOffsetY ] */
	void addBendedLine(final String fromId, final String toId,
	                   final int toX, final int toY);

	/** adds bended line where the bending shall happen at
	    [toX + defaultNodeWidth/2 , toY + bendingOffsetY ] */
	void addBendedLine(final String fromId, final String toId,
	                   final int toX, final int toY, final int bendingOffsetY);

	/** adds a new node and connects the given parent with this node;
	    default size of the node is expected as well as default bending point */
	void addBendedLineConnectedVertex(final String parentNodeID,
	                                  final String newNodeID,
	                                  final String label, final int colorRGB,
	                                  final int x, final int y);

	/** optional, whether to leave empty or implement depends on the underlying export mechanism */
	void close();

	/*
	static void runExample()
	{
		System.out.println("graph export example started");

		//the main root of the tree
		addNode("A", "A",defaultNodeColour, 200,0);

		//left subtree: straight lines
		addStraightLineConnectedVertex("A" , "AL" , "AL" ,defaultNodeColour, 100,200,0);
		addStraightLineConnectedVertex("AL", "ALL", "ALL",defaultNodeColour,  50,400,0);
		addStraightLineConnectedVertex("AL", "ALR", "ALR",defaultNodeColour, 150,400,0);

		//right subtree: bended lines
		addBendedLineConnectedVertex( "A" , "AR" , "AR" ,defaultNodeColour, 300,200,0);
		addBendedLineConnectedVertex( "AR", "ARL", "ARL",defaultNodeColour, 250,400,0);
		addBendedLineConnectedVertex( "AR", "ARR", "ARR",defaultNodeColour, 350,400,0);

		System.out.println("graph export example stopped");
	}
	*/
}
