package de.mpicbg.tomancaklab;

import de.mpicbg.tomancaklab.graphexport.GraphExportable;
import de.mpicbg.tomancaklab.graphexport.yEdGraphMLWriter;
import de.mpicbg.tomancaklab.graphexport.GraphStreamViewer;

import org.mastodon.spatial.SpatioTemporalIndex;
import org.mastodon.mamut.MamutAppModel;
import org.mastodon.mamut.model.Model;
import org.mastodon.mamut.model.ModelGraph;
import org.mastodon.mamut.model.Spot;
import org.mastodon.mamut.model.Link;

import org.scijava.command.Command;
import org.scijava.command.DynamicCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;
import org.scijava.log.LogService;
import org.scijava.widget.FileWidget;

import java.io.File;


@Plugin( type = Command.class, name = "Export lineage with time axis converted to generations axis" )
public class LineageExporter extends DynamicCommand
{
	@Parameter(persist = false)
	private MamutAppModel appModel;

	@Parameter(persist = false)
	private boolean doyEdExport = true;

	@Parameter(style = FileWidget.OPEN_STYLE)
	private File graphMLfile = new File("/tmp/mastodon.graphml");

	@Parameter
	private LogService logServiceRef;

	@Override
	public void run()
	{
		if (doyEdExport)
		{
			if (graphMLfile != null)
			{
				//opens the GraphML file
				final GraphExportable ge = new yEdGraphMLWriter(graphMLfile.getPath());
				time2Gen2GraphExportable( ge );
			}
			else
				throw new RuntimeException("Should never get here!");
		}
		else
		{
			final GraphExportable ge = new GraphStreamViewer("Mastodon Generation Lineage");
			time2Gen2GraphExportable( ge );
		}
	}

	/** implements the "LineageExporter" functionality */
	private void time2Gen2GraphExportable(final GraphExportable ge)
	{
		//NB: this method could be in a class of its own... later...

		//shortcuts to the data
		final int timeFrom = appModel.getMinTimepoint();
		final int timeTill = appModel.getMaxTimepoint();
		final Model      model      = appModel.getModel();
		final ModelGraph modelGraph = model.getGraph();

		//aux Mastodon data: shortcuts and caches/proxies
		final SpatioTemporalIndex< Spot > spots = model.getSpatioTemporalIndex();
		final Link lRef = modelGraph.edgeRef();              //link reference
		final Spot sRef = modelGraph.vertices().createRef(); //aux spot reference

		int xLeftBound = 0;
		final int[] xIgnoreCoords = new int[1];

		//over all time points
		for (int time = timeFrom; time <= timeTill; ++time)
		{
			//over all spots in the current time point
			for ( final Spot spot : spots.getSpatialIndex( time ) )
			{
				//find how many backward-references (time-wise) this spot has
				int countBackwardLinks = 0;

				for (int n=0; n < spot.incomingEdges().size(); ++n)
				{
					spot.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() < time)
					{
						++countBackwardLinks;
					}
				}
				for (int n=0; n < spot.outgoingEdges().size(); ++n)
				{
					spot.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() < time)
					{
						++countBackwardLinks;
					}
				}

				//can this spot be root?
				if (countBackwardLinks == 0)
				{
					logServiceRef.info("Discovered root "+spot.getLabel());
					xLeftBound += discoverEdge(ge,modelGraph, spot, 0,xLeftBound, xIgnoreCoords,0);
				}
			}
		}

		modelGraph.vertices().releaseRef(sRef);
		modelGraph.releaseRef(lRef);

		ge.close();

		logServiceRef.info("generation graph rendered");
		modelGraph.notifyGraphChanged();
	}


	/** returns width of the tree induced with the given 'root' */
	private int discoverEdge(final GraphExportable ge, final ModelGraph modelGraph,
	                         final Spot root,
	                         final int generation,
	                         final int xLeftBound,
	                         final int[] xCoords, final int xCoordsPos)
	{
		final Spot spot = modelGraph.vertices().createRef(); //aux spot reference
		final Spot fRef = modelGraph.vertices().createRef(); //spot's ancestor buddy (forward)
		final Link lRef = modelGraph.edgeRef();              //link reference

		spot.refTo( root );

		while (true)
		{
			//shortcut to the time of the current node/spot
			final int time = spot.getTimepoint();

			//find how many forward-references (time-wise) this spot has
			int countForwardLinks = 0;

			for (int n=0; n < spot.incomingEdges().size(); ++n)
			{
				spot.incomingEdges().get(n, lRef).getSource( fRef );
				if (fRef.getTimepoint() > time)
				{
					++countForwardLinks;
				}
			}
			for (int n=0; n < spot.outgoingEdges().size(); ++n)
			{
				spot.outgoingEdges().get(n, lRef).getTarget( fRef );
				if (fRef.getTimepoint() > time)
				{
					++countForwardLinks;
				}
			}

			if (countForwardLinks == 1)
			{
				//just a vertex on "a string", move over it
				spot.refTo( fRef );
			}
			else
			{
				int xRightBound = xLeftBound;
				final int[] childrenXcoords = new int[countForwardLinks];

				//we're leaf or branching point
				if (countForwardLinks > 1)
				{
					int childCnt = 0;
					//branching point -> enumerate all ancestors and restart searches from them
					for (int n=0; n < spot.incomingEdges().size(); ++n)
					{
						spot.incomingEdges().get(n, lRef).getSource( fRef );
						if (fRef.getTimepoint() > time)
						{
							xRightBound += discoverEdge(ge,modelGraph, fRef, generation+1,xRightBound, childrenXcoords,childCnt);
							++childCnt;
						}
					}
					for (int n=0; n < spot.outgoingEdges().size(); ++n)
					{
						spot.outgoingEdges().get(n, lRef).getTarget( fRef );
						if (fRef.getTimepoint() > time)
						{
							xRightBound += discoverEdge(ge,modelGraph, fRef, generation+1,xRightBound, childrenXcoords,childCnt);
							++childCnt;
						}
					}
				}
				else
				{
					//we're a leaf -> pretend a subtree of single column width
					xRightBound += ge.xColumnWidth;
				}

				final String rootID = Integer.toString(root.getInternalPoolIndex());
				xCoords[xCoordsPos] = countForwardLinks == 0
				                      ? (xRightBound + xLeftBound)/2
				                      : (childrenXcoords[0] + childrenXcoords[countForwardLinks-1])/2;
				//gsv.graph.addNode(rootID).addAttribute("xyz", new int[] {!,!,0});
				ge.addNode(rootID, root.getLabel(),ge.defaultNodeColour,
				           xCoords[xCoordsPos],ge.yLineStep*generation);

				if (countForwardLinks > 1)
				{
					int childCnt = 0;
					//enumerate all ancestors (children) and connect them (to this parent)
					for (int n=0; n < spot.incomingEdges().size(); ++n)
					{
						spot.incomingEdges().get(n, lRef).getSource( fRef );
						if (fRef.getTimepoint() > time)
						{
							//edge
							System.out.print("generation: "+generation+"   ");
							//ge.addStraightLine( rootID, Integer.toString(fRef.getInternalPoolIndex())
							ge.addBendedLine( rootID, Integer.toString(fRef.getInternalPoolIndex())
							                  ,childrenXcoords[childCnt++],ge.yLineStep*(generation+1)
							                );
						}
					}
					for (int n=0; n < spot.outgoingEdges().size(); ++n)
					{
						spot.outgoingEdges().get(n, lRef).getTarget( fRef );
						if (fRef.getTimepoint() > time)
						{
							//edge
							System.out.print("generation: "+generation+"   ");
							//ge.addStraightLine( rootID, Integer.toString(fRef.getInternalPoolIndex())
							ge.addBendedLine( rootID, Integer.toString(fRef.getInternalPoolIndex())
							                  ,childrenXcoords[childCnt++],ge.yLineStep*(generation+1)
							                );
						}
					}
				}
				else
				{
					//leaf is just a vertex node (there's no one to connect to)
					System.out.println("Discovered \"leaf\" "+root.getLabel());
				}

				//clean up first before exiting
				modelGraph.vertices().releaseRef(spot);
				modelGraph.vertices().releaseRef(fRef);
				modelGraph.releaseRef(lRef);

				return (xRightBound - xLeftBound);
			}
		}
	}
}
