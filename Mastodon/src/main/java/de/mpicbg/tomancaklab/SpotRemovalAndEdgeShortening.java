package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;

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

		//opens the GraphStreamer window
		GraphStreamViewer gsv = new GraphStreamViewer();

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

		int treeCnt = 0;

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
					discoverEdge(gsv,modelGraph, spot, spot, 0,treeCnt*1000);
					++treeCnt;
				}
			}
		}

		modelGraph.vertices().releaseRef(sRef);
		modelGraph.releaseRef(lRef);

		logServiceRef.info("generation graph rendered");
		modelGraph.notifyGraphChanged();
	}


	private void discoverEdge(final GraphStreamViewer gsv, final ModelGraph modelGraph,
	                          final Spot root, final Spot parent,
	                          final int generation,
	                          final int x)
	{
		final Spot spot = modelGraph.vertices().createRef(); //aux spot reference
		final Spot fRef = modelGraph.vertices().createRef(); //spot's ancestor buddy (forward)
		final Link lRef = modelGraph.edgeRef();              //link reference

		spot.refTo( root );

		boolean keepGoing = true;
		while (keepGoing)
		{
			//find how many forward-references (time-wise) this spot has
			int countForwardLinks = 0;

			final int time = spot.getTimepoint();

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
				//we're leaf or branching point
				keepGoing = false;

				//add edge if the spot is different from the parent
				if (generation == 0)
				{
					//first generation is just a vertex node (there's no one to connect to)
					final String rootID = Integer.toString(spot.getInternalPoolIndex());
					System.out.println("root node "+rootID);
					gsv.graph.addNode(rootID).addAttribute("xyz", new int[] {x,0,0});
				}
				else
				{
					//every next generation is a vertex node connected to its parent
					System.out.print("generation: "+generation+"   ");
					gsv.addStraightLineConnectedVertex(
						Integer.toString(parent.getInternalPoolIndex()),
						Integer.toString(spot.getInternalPoolIndex()),
						x, -700*generation, 0);
				}

				//branching point?
				if (countForwardLinks > 1)
				{
					//width at this generation level:
					final int width = (int)(1000.0 / Math.pow(2,generation));

					//x position of the left most branch
					final int X = x - (int)(0.5*width);

					//n branches gives rise to n+1 spaces around them,
					//countForwardLinks is the number of the separating spaces
					++countForwardLinks;

					//current position of the branches
					int cnt = 1;

					//enumerate all ancestors and restart searches from them
					for (int n=0; n < spot.incomingEdges().size(); ++n)
					{
						spot.incomingEdges().get(n, lRef).getSource( fRef );
						if (fRef.getTimepoint() > time)
						{
							discoverEdge(gsv,modelGraph, fRef, spot, generation+1, X +(cnt*width/countForwardLinks));
							++cnt;
						}
					}
					for (int n=0; n < spot.outgoingEdges().size(); ++n)
					{
						spot.outgoingEdges().get(n, lRef).getTarget( fRef );
						if (fRef.getTimepoint() > time)
						{
							discoverEdge(gsv,modelGraph, fRef, spot, generation+1, X +(cnt*width/countForwardLinks));
							++cnt;
						}
					}
				}
			}
		}

		modelGraph.vertices().releaseRef(spot);
		modelGraph.vertices().releaseRef(fRef);
		modelGraph.releaseRef(lRef);
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
