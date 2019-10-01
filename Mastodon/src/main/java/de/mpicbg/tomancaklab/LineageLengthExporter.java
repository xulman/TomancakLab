package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;

import de.mpicbg.tomancaklab.graphexport.GraphExportable;
import de.mpicbg.tomancaklab.graphexport.yEdGraphMLWriter;
import de.mpicbg.tomancaklab.graphexport.GraphStreamViewer;
import org.mastodon.app.ui.ViewMenuBuilder;
import org.mastodon.collection.*;
import org.mastodon.collection.ref.IntRefHashMap;
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


@Plugin( type = LineageLengthExporter.class )
public class LineageLengthExporter extends AbstractContextual implements MastodonPlugin
{
	//"IDs" of all plug-ins wrapped in this class
	private static final String t2len = "LoPaT-LineageLengths";
	//------------------------------------------------------------------------

	@Override
	public List< ViewMenuBuilder.MenuItem > getMenuItems()
	{
		//this places the plug-in's menu items into the menu,
		//the titles of the items are defined right below
		return Arrays.asList(
				menu( "Plugins",
						item( t2len ) ) );
	}

	/** titles of this plug-in's menu items */
	private static Map< String, String > menuTexts = new HashMap<>();
	static
	{
		menuTexts.put( t2len, "Export lineage lengths" );
	}

	@Override
	public Map< String, String > getMenuTexts()
	{
		return menuTexts;
	}
	//------------------------------------------------------------------------

	private final AbstractNamedAction actionLengths;

	/** default c'tor: creates Actions available from this plug-in */
	public LineageLengthExporter()
	{
		actionLengths = new RunnableAction( t2len, this::exportLengths );
		updateEnabledActions();
	}

	/** register the actions to the application (with no shortcut keys) */
	@Override
	public void installGlobalActions( final Actions actions )
	{
		final String[] noShortCut = { "not mapped" };
		actions.namedAction( actionLengths, noShortCut );
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
		actionLengths.setEnabled( appModel != null );
	}
	//------------------------------------------------------------------------

	/** facade to the main workhorse */
	private void exportLengths()
	{
		final String columnSep = "\t";

		//borrow a spot "placeholder" (and return it at the very end!)
		final Spot parent = pluginAppModel.getAppModel().getModel().getGraph().vertices().createRef();
		final Spot rRef = pluginAppModel.getAppModel().getModel().getGraph().vertices().createRef();
		final Spot sRef = pluginAppModel.getAppModel().getModel().getGraph().vertices().createRef();
		final Link lRef = pluginAppModel.getAppModel().getModel().getGraph().edges().createRef();

		//finds the starting spot
		pluginAppModel.getAppModel().getFocusModel().getFocusedVertex( parent );
		System.out.println("Going to export the tree from the spot: "+parent.getLabel()
		                  +" (timepoint "+parent.getTimepoint()+")");

		//sets up the sweeping data structures
		//timepoint to spot, sorted accoring to timepoints (and position in trackScheme for the same timepoints)
		final RefList<Spot> discoveredDivPoints
			= RefCollections.createRefList(pluginAppModel.getAppModel().getModel().getGraph().vertices());

		//spot to spot
		final RefRefMap< Spot, Spot > trackStarters
			= RefMaps.createRefRefMap(pluginAppModel.getAppModel().getModel().getGraph().vertices(), 500);

		//starts the export by moving to the earliest division point (for which we don't have its starter)
		if (browseDownstreamTillNextDivisionEvent(parent,sRef,lRef) > 1) discoveredDivPoints.add( parent );

		while (discoveredDivPoints.size() > 0)
		{
			//get the oldest division point on the list
			discoveredDivPoints.remove( 0, parent );

			if (trackStarters.containsKey( parent ))
			{
				//report this track
				final Spot starter = trackStarters.get( parent );
				System.out.println(starter.getLabel()+columnSep
				                  +starter.getTimepoint()+columnSep
				                  +parent.getLabel()+columnSep
				                  +parent.getTimepoint()+columnSep
				                  +(parent.getTimepoint()-starter.getTimepoint()));
			}

			//parent is for sure a division point,
			//enumerate its daughters and enlist them
			for (int n=0; n < parent.incomingEdges().size(); ++n)
			{
				parent.incomingEdges().get(n, lRef).getSource( rRef );
				if (rRef.getTimepoint() > parent.getTimepoint() && browseDownstreamTillNextDivisionEvent( rRef, sRef, lRef ) > 1)
				{
					enlistSpot( discoveredDivPoints, rRef );
					trackStarters.put( rRef, parent );
				}
			}
			for (int n=0; n < parent.outgoingEdges().size(); ++n)
			{
				parent.outgoingEdges().get(n, lRef).getTarget( rRef );
				if (rRef.getTimepoint() > parent.getTimepoint() && browseDownstreamTillNextDivisionEvent( rRef, sRef, lRef ) > 1)
				{
					enlistSpot( discoveredDivPoints, rRef );
					trackStarters.put( rRef, parent );
				}
			}
		}

		pluginAppModel.getAppModel().getModel().getGraph().edges().releaseRef( lRef );
		pluginAppModel.getAppModel().getModel().getGraph().vertices().releaseRef( sRef );
		pluginAppModel.getAppModel().getModel().getGraph().vertices().releaseRef( rRef );
		pluginAppModel.getAppModel().getModel().getGraph().vertices().releaseRef( parent );
	}

	private void enlistSpot(final RefList< Spot > list, final Spot cell)
	{
		int i = 0;
		while (i < list.size() && list.get(i).getTimepoint() <= cell.getTimepoint()) ++i;
		list.add(i,cell);
	}

	/** moves the cell downstream until the cell has 0 or 2 or more descendants,
	    and returns the number of discovered descendants;
	    r(running)Ref is the one that's gonna be moved downstream,
	    sRef anf lRef are additional spot and link aux variables to facilitate the search */
	private int browseDownstreamTillNextDivisionEvent(final Spot rRef, final Spot sRef, final Link lRef)
	{
		int edgeCnt;
		do {
			edgeCnt = 0;
			for (int n=0; n < rRef.incomingEdges().size(); ++n)
			{
				rRef.incomingEdges().get(n, lRef).getSource( sRef );
				if (sRef.getTimepoint() > rRef.getTimepoint()) ++edgeCnt;
			}
			for (int n=0; n < rRef.outgoingEdges().size(); ++n)
			{
				rRef.outgoingEdges().get(n, lRef).getTarget( sRef );
				if (sRef.getTimepoint() > rRef.getTimepoint()) ++edgeCnt;
			}

			if (edgeCnt == 1) rRef.refTo( sRef );
		} while (edgeCnt == 1);

		return edgeCnt;
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
