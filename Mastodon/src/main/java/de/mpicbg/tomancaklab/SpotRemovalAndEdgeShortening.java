package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;

import de.mpicbg.tomancaklab.graphexport.GraphExportable;
import de.mpicbg.tomancaklab.graphexport.yEdGraphMLWriter;
import de.mpicbg.tomancaklab.graphexport.GraphStreamViewer;
import org.mastodon.app.ui.ViewMenuBuilder;
import org.mastodon.plugin.MastodonPlugin;
import org.mastodon.plugin.MastodonPluginAppModel;

import org.mastodon.project.MamutProject;
import org.mastodon.revised.mamut.Mastodon;
import org.mastodon.spatial.SpatioTemporalIndex;
import org.mastodon.revised.mamut.MamutAppModel;
import org.mastodon.revised.model.mamut.Model;
import org.mastodon.revised.model.mamut.ModelGraph;
import org.mastodon.revised.model.mamut.Spot;
import org.mastodon.revised.model.mamut.Link;

import org.scijava.AbstractContextual;
import org.scijava.Context;
import org.scijava.plugin.Plugin;
import org.scijava.ui.behaviour.util.Actions;
import org.scijava.ui.behaviour.util.AbstractNamedAction;
import org.scijava.ui.behaviour.util.RunnableAction;
import org.scijava.log.LogService;

import javax.swing.*;
import java.io.File;
import java.util.*;


@Plugin( type = SpotRemovalAndEdgeShortening.class )
public class SpotRemovalAndEdgeShortening extends AbstractContextual implements MastodonPlugin
{
	//"IDs" of all plug-ins wrapped in this class
	private static final String PluginID = "LoPaT-SpotRemovalEdgeShortening";
	//------------------------------------------------------------------------

	@Override
	public List< ViewMenuBuilder.MenuItem > getMenuItems()
	{
		//this places the plug-in's menu items into the menu,
		//the titles of the items are defined right below
		return Arrays.asList(
				menu( "Plugins",
						item( PluginID ) ) );
	}

	/** titles of this plug-in's menu items */
	private static Map< String, String > menuTexts = new HashMap<>();
	static
	{
		menuTexts.put( PluginID, "Spots Removal & Edge Shortenings" );
	}

	@Override
	public Map< String, String > getMenuTexts()
	{
		return menuTexts;
	}
	//------------------------------------------------------------------------

	private final AbstractNamedAction actionSRES; //Spot Removal Edge Shortening

	/** default c'tor: creates Actions available from this plug-in */
	public SpotRemovalAndEdgeShortening()
	{
		actionSRES = new RunnableAction( PluginID, this::workerSRES );
		updateEnabledActions();
	}

	/** register the actions to the application (with no shortcut keys) */
	@Override
	public void installGlobalActions( final Actions actions )
	{
		final String[] noShortCut = new String[] {};
		actions.namedAction( actionSRES, noShortCut );
	}

	/** reference to the currently available project in Mastodon */
	private MastodonPluginAppModel pluginAppModel;

	/** learn about the current project's params */
	@Override
	public void setAppModel( final MastodonPluginAppModel model )
	{
		//the application reports back to us if some project is available
		this.pluginAppModel = model;
		updateEnabledActions();
	}

	/** enables/disables menu items based on the availability of some project */
	private void updateEnabledActions()
	{
		final MamutAppModel appModel = ( pluginAppModel == null ) ? null : pluginAppModel.getAppModel();
		actionSRES.setEnabled( appModel != null );
	}
	//------------------------------------------------------------------------
	private LogService logServiceRef; //(re)defined with every call to this.workerSRES()


	/** implements the "SpotRemovalAndEdgeShortening" functionality */
	private void workerSRES()
	{
		//NB: this method could be in a class of its own... later...

		//opens the GraphML file
		GraphExportable ge = new yEdGraphMLWriter("/tmp/mastodon.graphml");
		//GraphExportable ge = new GraphStreamViewer("Mastodon Generation Lineage");

		//aux Fiji services
		logServiceRef = this.getContext().getService(LogService.class).log();

		//shortcuts to the data
		final int timeFrom = pluginAppModel.getAppModel().getMinTimepoint();
		final int timeTill = pluginAppModel.getAppModel().getMaxTimepoint();
		final Model      model      = pluginAppModel.getAppModel().getModel();
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


	public static void main( final String[] args ) throws Exception
	{
		Locale.setDefault( Locale.US );
		UIManager.setLookAndFeel( UIManager.getSystemLookAndFeelClassName() );

		//final MamutProject project = new MamutProject( new File( "/tmp/test.mastodon" ), new File( "x=1000 y=1000 z=100 sx=1 sy=1 sz=10 t=400.dummy" ) );
		final MamutProject project = new MamutProject(
				new File( "/Users/ulman/DATA/Mette/dataset.mastodon" ),
				new File( "/Users/ulman/DATA/Mette/dataset_hdf5.xml" ) );

		final Mastodon mastodon = new Mastodon();
		new Context().inject( mastodon );
		mastodon.run();
		mastodon.setExitOnClose();
		mastodon.openProject( project );
	}
}
