package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;

import org.mastodon.app.ui.ViewMenuBuilder;
import org.mastodon.plugin.MastodonPlugin;
import org.mastodon.plugin.MastodonPluginAppModel;

import org.mastodon.spatial.SpatioTemporalIndex;
import org.mastodon.revised.mamut.MamutAppModel;
import org.mastodon.revised.model.mamut.Model;
import org.mastodon.revised.model.mamut.ModelGraph;
import org.mastodon.revised.model.mamut.Spot;
import org.mastodon.revised.model.mamut.Link;

import org.scijava.AbstractContextual;
import org.scijava.plugin.Plugin;
import org.scijava.ui.behaviour.util.Actions;
import org.scijava.ui.behaviour.util.AbstractNamedAction;
import org.scijava.ui.behaviour.util.RunnableAction;
import org.scijava.log.LogService;

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
		final Spot bRef = modelGraph.vertices().createRef(); //spot's predecessor buddy (backward)
		final Spot fRef = modelGraph.vertices().createRef(); //spot's ancestor buddy (forward)

		//over all time points
		for (int time = timeFrom; time <= timeTill; ++time)
		{
			//over all spots in the current time point
			for ( final Spot spot : spots.getSpatialIndex( time ) )
			{
				//find how many back- and forward-references (time-wise) this spot has
				int countBackwardLinks = 0;
				int countForwardLinks = 0;

				for (int n=0; n < spot.incomingEdges().size(); ++n)
				{
					spot.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= timeFrom)
					{
						++countBackwardLinks;
						bRef.refTo( sRef );
					}
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= timeTill)
					{
						++countForwardLinks;
						fRef.refTo( sRef );
					}
				}
				for (int n=0; n < spot.outgoingEdges().size(); ++n)
				{
					spot.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= timeFrom)
					{
						++countBackwardLinks;
						bRef.refTo( sRef );
					}
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= timeTill)
					{
						++countForwardLinks;
						fRef.refTo( sRef );
					}
				}

				//can this spot be reduced?
				if (countBackwardLinks == 1 && countForwardLinks == 1)
				{
					//yes, has exactly one bRef and one fRef neigbors
					logServiceRef.trace("removing spot...TODO");

					//create a "bypass" link/edge
					modelGraph.addEdge(bRef,fRef);

					//and remove the spot
					//TODO, hope it does not screw up the iteration order of spots.getSpatialIndex()
					modelGraph.remove(spot);
				}
			}
		}

		/*
		//again, over all time points
		final double[] pos = new double[3];
		for (int time = timeFrom; time <= timeTill; ++time)
		{
			//over all spots in the current time point
			for ( final Spot spot : spots.getSpatialIndex( time ) )
			{
				//find how many back- and forward-references (time-wise) this spot has
				int countBackwardLinks = 0;
				int countForwardLinks = 0;

				for (int n=0; n < spot.incomingEdges().size(); ++n)
				{
					spot.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= timeFrom)
					{
						++countBackwardLinks;
						bRef.refTo( sRef );
					}
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= timeTill)
					{
						++countForwardLinks;
						fRef.refTo( sRef );
					}
				}
				for (int n=0; n < spot.outgoingEdges().size(); ++n)
				{
					spot.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= timeFrom)
					{
						++countBackwardLinks;
						bRef.refTo( sRef );
					}
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= timeTill)
					{
						++countForwardLinks;
						fRef.refTo( sRef );
					}
				}

				//TODO: for now, deal with only 1 forward link
				//root spot?
				if (countBackwardLinks == 0 && countForwardLinks == 1)
				{
					logServiceRef.trace("found root spot...TODO");
					//this does not work, cannot re-init, and don't see other way to adjust the timepoint
					//spot.localize(pos);
					//spot.init(0,pos,Math.sqrt(spot.getBoundingSphereRadiusSquared()) );
				}
				else
				if (countBackwardLinks == 1)
				{
					logServiceRef.trace("adjusting time of spot...TODO");
					//this does not work, cannot re-init, and don't see other way to adjust the timepoint
					//spot.localize(pos);
					//spot.init(spot.getTimepoint()+1,pos,Math.sqrt(spot.getBoundingSphereRadiusSquared()) );
				}
			}
		}
		*/

		modelGraph.vertices().releaseRef(sRef);
		modelGraph.vertices().releaseRef(bRef);
		modelGraph.vertices().releaseRef(fRef);
		modelGraph.releaseRef(lRef);

		logServiceRef.info("edges were shortened.");
		modelGraph.notifyGraphChanged();
	}
}
