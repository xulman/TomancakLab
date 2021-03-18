package de.mpicbg.tomancaklab;

import org.mastodon.collection.*;
import org.mastodon.ui.util.FileChooser;
import org.mastodon.mamut.MamutAppModel;
import org.mastodon.mamut.model.Spot;
import org.mastodon.mamut.model.Link;

import org.scijava.ItemVisibility;
import org.scijava.command.Command;
import org.scijava.command.DynamicCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;


@Plugin( type = Command.class, name = "Export lineage as lengths between divisions" )
public class LineageLengthExporter extends DynamicCommand
{
	@Parameter(persist = false)
	private MamutAppModel appModel;

	@Parameter(label = "Do not report anything before this time point:",
	           min = "0")
	private int timePointFrom = 0;

	@Parameter(label = "Do not report anything beyond this time point:",
	           description = "Value of -1 means no limit.", min = "-1")
	private int timePointTill = -1;

	@Parameter(label = "Time step, physical time between time points:")
	private float timeStep = 90.0f;

	@Parameter(visibility = ItemVisibility.MESSAGE, persist = false, required = false)
	private String fileOpenInfo = "The plugin will additionally ask for file to save the lineage.";

	/** the main workhorse */
	public void run()
	{
		final String columnSep = "\t";
		if (timePointTill == -1) timePointTill = appModel.getMaxTimepoint();
		try {

		//borrow a spot "placeholder" (and return it at the very end!)
		final Spot parent = appModel.getModel().getGraph().vertices().createRef();
		final Spot rRef = appModel.getModel().getGraph().vertices().createRef();
		final Spot sRef = appModel.getModel().getGraph().vertices().createRef();
		final Link lRef = appModel.getModel().getGraph().edges().createRef();

		//finds the starting spot
		appModel.getFocusModel().getFocusedVertex( parent );
		System.out.println("Going to export the tree from the spot: "+parent.getLabel()
		                  +" (timepoint "+parent.getTimepoint()+")");

		final File oFile = FileChooser.chooseFile(null,"LineageOf_"+parent.getLabel()+".txt", null, "Save the lineage as...", FileChooser.DialogType.SAVE );
		final BufferedWriter jout = oFile != null? new BufferedWriter(new FileWriter(oFile)) : null;

		//sets up the sweeping data structures
		//timepoint to spot, sorted accoring to timepoints (and position in trackScheme for the same timepoints)
		final RefList<Spot> discoveredDivPoints
			= RefCollections.createRefList(appModel.getModel().getGraph().vertices());

		//spot to spot
		final RefRefMap< Spot, Spot > trackStarters
			= RefMaps.createRefRefMap(appModel.getModel().getGraph().vertices(), 500);

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

				//only if it fits the timepoint range
				if (starter.getTimepoint() >= timePointFrom && parent.getTimepoint() <= timePointTill)
				{
					final String msg = starter.getLabel()+columnSep
					                 + starter.getTimepoint()+columnSep
					                 + parent.getLabel()+columnSep
					                 + parent.getTimepoint()+columnSep
					                 + (parent.getTimepoint()-starter.getTimepoint())+columnSep
					                 + (parent.getTimepoint()-starter.getTimepoint())*timeStep;
					if (jout != null)
					{
						jout.write( msg );
						jout.newLine();
					}
					System.out.println( msg );
				}
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

		appModel.getModel().getGraph().edges().releaseRef( lRef );
		appModel.getModel().getGraph().vertices().releaseRef( sRef );
		appModel.getModel().getGraph().vertices().releaseRef( rRef );
		appModel.getModel().getGraph().vertices().releaseRef( parent );

		if (jout != null)
		{
			jout.flush();
			jout.close();
		}

		} catch (IOException e) {
			System.out.println("Some file writing problem: "+e.getMessage());
		}
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
}
