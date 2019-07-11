package de.mpicbg.tomancaklab.graphexport;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class yEdGraphMLWriter implements GraphExportable
{
	// -----------------------------------------------------------------------------
	private BufferedWriter file;

	public yEdGraphMLWriter(final String outputGraphMLFile)
	{
		try {
			file = new BufferedWriter( new FileWriter( outputGraphMLFile  ) );

			//write header
			file.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n");
			file.write("<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:java=\"http://www.yworks.com/xml/yfiles-common/1.0/java\" xmlns:sys=\"http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0\" xmlns:x=\"http://www.yworks.com/xml/yfiles-common/markup/2.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:y=\"http://www.yworks.com/xml/graphml\" xmlns:yed=\"http://www.yworks.com/xml/yed/3\" xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd\">\n");
			file.write("  <key for=\"node\" id=\"d6\" yfiles.type=\"nodegraphics\"/>\n");
			file.write("  <key for=\"edge\" id=\"d10\" yfiles.type=\"edgegraphics\"/>\n");
			file.write("  <graph edgedefault=\"directed\" id=\"G\">\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	boolean closed = false;

	@Override
	public void close()
	{
		try {
			//write footer
			file.write("  </graph>\n");
			file.write("</graphml>\n");
			file.close();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			closed = true;
		}
	}

	public void finalize()
	{
		if (!closed) close();
	}
	// -----------------------------------------------------------------------------

	/** assuming the input color "value" has meaning
	    when read in hexadecimal 0xRRGGBB format */
	String colorToString(final int colorRGB)
	{
		return String.format( "#%06X", colorRGB );
	}

	String colorToString(final int r, final int g, final int b)
	{
		return String.format( "#%02X%02X%02X", r,g,b );
	}
	// -----------------------------------------------------------------------------

	/** extra addNode() that places the node at [0,0] */
	public void addNode(final String id,
	             final String label)
	{
		addNode(id, label,defaultNodeColour, 0,0, defaultNodeWidth,defaultNodeHeight);
	}

	/** extra addNode() that places the node at [0,0] */
	public void addNode(final String id,
	             final String label, final int colorRGB)
	{
		addNode(id, label,colorRGB, 0,0, defaultNodeWidth,defaultNodeHeight);
	}

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
		try {
			file.write("    <node id=\""+id+"\">\n");
			file.write("      <data key=\"d6\">\n");
			file.write("        <y:ShapeNode>\n");
			file.write("          <y:Geometry height=\""+height+"\" width=\""+width+"\" x=\""+x+"\" y=\""+y+"\"/>\n");
			file.write("          <y:Fill color=\""+colorToString(colorRGB)+"\" transparent=\"false\"/>\n");
			file.write("          <y:BorderStyle color=\"#000000\" raised=\"false\" type=\"line\" width=\"1.0\"/>\n");
			file.write("          <y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontFamily=\"Dialog\" fontSize=\"12\" fontStyle=\"plain\" hasBackgroundColor=\"false\" hasLineColor=\"false\" horizontalTextPosition=\"center\" iconTextGap=\"4\" modelName=\"custom\" textColor=\"#000000\" verticalTextPosition=\"bottom\" visible=\"true\">"+label+"</y:NodeLabel>\n");
			file.write("          <y:Shape type=\"ellipse\"/>\n");
			file.write("        </y:ShapeNode>\n");
			file.write("      </data>\n");
			file.write("    </node>\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	// -----------------------------------------------------------------------------

	/** straight edge */
	void writeEdge(final String id,
	               final String fromId, final String toId)
	{
		try {
			file.write("    <edge id=\""+id+"\" source=\""+fromId+"\" target=\""+toId+"\">\n");
			file.write("      <data key=\"d10\">\n");
			file.write("        <y:PolyLineEdge>\n");
			file.write("          <y:Path sx=\"0.0\" sy=\"0.0\" tx=\"0.0\" ty=\"0.0\"/>\n");
			file.write("          <y:LineStyle color=\"#000000\" type=\"line\" width=\"1.0\"/>\n");
			file.write("          <y:Arrows source=\"none\" target=\"none\"/>\n");
			file.write("          <y:BendStyle smoothed=\"false\"/>\n");
			file.write("        </y:PolyLineEdge>\n");
			file.write("      </data>\n");
			file.write("    </edge>\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/** edge bending around the point [bx,by] */
	void writeEdge(final String id,
	               final String fromId, final String toId,
	               final int bx, final int by)
	{
		try {
			file.write("    <edge id=\""+id+"\" source=\""+fromId+"\" target=\""+toId+"\">\n");
			file.write("      <data key=\"d10\">\n");
			file.write("        <y:PolyLineEdge>\n");
			file.write("          <y:Path sx=\"0.0\" sy=\"0.0\" tx=\"0.0\" ty=\"0.0\"><y:Point x=\""+bx+"\" y=\""+by+"\"/></y:Path>\n");
			file.write("          <y:LineStyle color=\"#000000\" type=\"line\" width=\"1.0\"/>\n");
			file.write("          <y:Arrows source=\"none\" target=\"none\"/>\n");
			file.write("          <y:BendStyle smoothed=\"false\"/>\n");
			file.write("        </y:PolyLineEdge>\n");
			file.write("      </data>\n");
			file.write("    </edge>\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	// -----------------------------------------------------------------------------

	@Override
	public void addStraightLine(final String fromId, final String toId)
	{
		writeEdge(fromId.concat(toId), fromId, toId);
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
		writeEdge(fromId.concat(toId), fromId, toId, toX+defaultNodeWidth/2,toY+bendingOffsetY);
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
		System.out.println("GraphML started");

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

		System.out.println("GraphML stopped");
	}
}
