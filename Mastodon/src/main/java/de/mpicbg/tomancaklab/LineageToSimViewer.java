package de.mpicbg.tomancaklab;

import org.mastodon.plugin.MastodonPluginAppModel;
import org.mastodon.revised.mamut.MamutViewTrackScheme;
import org.mastodon.revised.trackscheme.TrackSchemeEdge;
import org.mastodon.revised.trackscheme.TrackSchemeVertex;
import org.mastodon.revised.ui.coloring.GraphColorGeneratorAdapter;
import org.mastodon.revised.model.mamut.Model;
import org.mastodon.revised.model.mamut.ModelGraph;
import org.mastodon.revised.model.mamut.Spot;
import org.mastodon.revised.model.mamut.Link;
import org.mastodon.spatial.SpatioTemporalIndex;
import org.mastodon.collection.IntRefMap;
import org.mastodon.collection.RefMaps;

import org.scijava.ItemVisibility;
import org.scijava.command.Command;
import org.scijava.command.DynamicCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;
import org.scijava.ui.behaviour.util.AbstractNamedAction;
import org.scijava.ui.behaviour.util.RunnableAction;

import javax.swing.*;
import java.awt.*;
import java.io.PrintWriter;
import java.io.BufferedWriter;
import java.io.StringWriter;
import java.util.*;

import org.zeromq.SocketType;
import org.zeromq.ZMQ;
import org.zeromq.ZMQException;


@Plugin( type = Command.class, name = "Display lineage in SimViewer" )
public class LineageToSimViewer extends DynamicCommand
{
	@Parameter(persist = false)
	private MastodonPluginAppModel pluginAppModel;

	@Parameter
	private String connectURL = "localhost:8765";

	@Parameter(visibility = ItemVisibility.MESSAGE, persist = false, required = false)
	private String fileOpenInfo = "If the Trackscheme window appears without additional controls, try to resize it.";

	//---------------------------------------------------------------------------------------
	//---------------------------------- ZERO MQ stuff --------------------------------------
	private ZMQ.Socket socket = null;

	private static final String SVsenB = "LoPaT-SendFrameOnBackwardTPmove";
	private static final String SVsenF = "LoPaT-SendFrameOnForwardTPmove";

	/** opens (again) the SimViewer */
	@Override
	public void run()
	{
		//just close if something was opened (making a reset in this way)
		workerClose();

		System.out.println("Mastodon network sender: connecting to SimViewer");
		boolean connected = false;

		//init the communication side
		final ZMQ.Context zmqContext = ZMQ.context(1);
		try
		{
			socket = zmqContext.socket(SocketType.PAIR);
			if (socket == null)
				throw new Exception("Mastodon network sender: Cannot obtain local socket.");

			socket.connect("tcp://"+connectURL);
			connected = true;
		}
		catch (ZMQException e) {
			System.out.println("Mastodon network sender: Crashed with ZeroMQ error: " + e.getMessage());
		}
		catch (InterruptedException e) {
			System.out.println("Mastodon network sender: Interrupted: " + e.getMessage());
		}
		catch (Exception e) {
			System.out.println("Mastodon network sender: Error: " + e.getMessage());
			e.printStackTrace();
		}
		finally {
			if (connected == false) workerClose();
		}

		if (connected)
		{
			System.out.println("Mastodon network sender: connected to SimViewer");

			minTimePoint = pluginAppModel.getAppModel().getMinTimepoint();
			maxTimePoint = pluginAppModel.getAppModel().getMaxTimepoint();

			//open a TrackScheme window that shall be under our control,
			//and retrieve a handle on the current GraphColorGeneratorAdapter
			myOwnTSWindow = pluginAppModel.getWindowManager().createTrackScheme();
			myOwnColorProvider = myOwnTSWindow.getGraphColorGeneratorAdapter();

			final AbstractNamedAction actionSendB = new RunnableAction( SVsenB, this::workerTimePrev );
			final AbstractNamedAction actionSendF = new RunnableAction( SVsenF, this::workerTimeNext );
			pluginAppModel.getAppModel().getAppActions().namedAction( actionSendB, "N" );
			pluginAppModel.getAppModel().getAppActions().namedAction( actionSendF, "M" );

			if (myOwnColorProvider == null)
				throw new RuntimeException("TrackScheme window created without GraphColorGeneratorAdaptor!?");

			JPanel controlPanel = new JPanel();
			controlPanel.setLayout(new GridLayout(2,4));

			//radius spinners to be used later
			final Label lblRadiusOwn     = new Label("  Own radius:");
			final Label lblRadiusScaling = new Label("Radius scale:");
			final JSpinner spnRadiusOwn     = new JSpinner( new SpinnerNumberModel(radiusOwnValue,      0.01, 100.0, 1.0) );
			final JSpinner spnRadiusScaling = new JSpinner( new SpinnerNumberModel(radiusScalingFactor, 0.01, 100.0, 1.0) );

			//1st row
			Checkbox cb = new Checkbox("Use fixed radius instead of spot's own");
			cb.setState( useOwnRadiusInsteadOfSpotsOwn );
			cb.addItemListener((event) -> {
				useOwnRadiusInsteadOfSpotsOwn = ((Checkbox)event.getSource()).getState();
				spnRadiusOwn.setEnabled( useOwnRadiusInsteadOfSpotsOwn );
				spnRadiusScaling.setEnabled( !useOwnRadiusInsteadOfSpotsOwn );
				lblRadiusOwn.setEnabled( useOwnRadiusInsteadOfSpotsOwn );
				lblRadiusScaling.setEnabled( !useOwnRadiusInsteadOfSpotsOwn );
				workerCurrentTime();
			} );
			controlPanel.add( cb );

			JPanel miniGrp = new JPanel();
			lblRadiusOwn.setEnabled( useOwnRadiusInsteadOfSpotsOwn );
			lblRadiusOwn.setAlignment( Label.RIGHT );
			miniGrp.add( lblRadiusOwn );
			//
			spnRadiusOwn.setEnabled( useOwnRadiusInsteadOfSpotsOwn );
			spnRadiusOwn.addChangeListener( (action) -> {
				radiusOwnValue = ((Double)spnRadiusOwn.getModel().getValue()).floatValue();
				workerCurrentTime();
			});
			miniGrp.add( spnRadiusOwn );
			controlPanel.add( miniGrp );

			Button btn = new Button("  Choose color when View is None  ");
			btn.addActionListener( (action) -> {
				colorWhenNoStyleIsUsed = getRGBviaDialog(colorWhenNoStyleIsUsed);
				workerCurrentTime();
			} );
			controlPanel.add( btn );

			Label l = new Label("   Connected to "+connectURL);
			controlPanel.add(l);

			//2nd row
			cb = new Checkbox("Show always all spots");
			cb.setState( alwaysShowAllNodes );
			cb.addItemListener((event) -> {
				alwaysShowAllNodes = ((Checkbox)event.getSource()).getState();
				workerCurrentTime();
			} );
			controlPanel.add( cb );

			miniGrp = new JPanel();
			lblRadiusScaling.setEnabled( !useOwnRadiusInsteadOfSpotsOwn );
			lblRadiusScaling.setAlignment( Label.RIGHT );
			miniGrp.add( lblRadiusScaling );
			//
			spnRadiusScaling.setEnabled( !useOwnRadiusInsteadOfSpotsOwn );
			spnRadiusScaling.addChangeListener( (action) -> {
				radiusScalingFactor = ((Double)spnRadiusScaling.getModel().getValue()).floatValue();
				workerCurrentTime();
			});
			miniGrp.add( spnRadiusScaling );
			controlPanel.add( miniGrp );

			btn = new Button("  Choose color for Not-colored spots  ");
			btn.addActionListener( (action) -> {
				colorForNotColoredNodes = getRGBviaDialog(colorForNotColoredNodes);
				workerCurrentTime();
			} );
			controlPanel.add( btn );

			btn = new Button("  Refresh SimViewer  ");
			btn.addActionListener( (action) -> { workerCurrentTime(); } );
			controlPanel.add( btn );

			myOwnTSWindow.getFrame().add(controlPanel, BorderLayout.SOUTH);

			//also register that this connection should be closed on this window close
			myOwnTSWindow.onClose( this::workerClose );

			//on coloring style change, repaint the currently sent time point
			myOwnTSWindow.getColoringModel().listeners().add( this::workerSend );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getColoringModel().listeners().remove( this::workerSend ) );
			myOwnTSWindow.getColoringModel().listeners().add( this::reportPairs );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getColoringModel().listeners().remove( this::reportPairs ) );

			//on time point change, repaint the current time point
			myOwnTSWindow.getTimepointModel().listeners().add( this::workerCurrentTime );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getTimepointModel().listeners().remove( this::workerCurrentTime ));

			//finally, send the current content to the SimViewer
			this.workerCurrentTime();
		}
		else
			System.out.println("Mastodon network sender: NOT connected to SimViewer");
	}

	private
	int getRGBviaDialog(final int currentColor)
	{
		final Color newColor = JColorChooser.showDialog(myOwnTSWindow.getFrame(),
				"Spot color in SimViewer", new Color(currentColor));
		return (newColor != null? (newColor.getRGB() & 0x00FFFFFF) : currentColor);
	}

	private
	void showRGB(final int c)
	{
		int r = (c >> 16) & 0x000000FF;
		int g = (c >>  8) & 0x000000FF;
		int b =     c     & 0x000000FF;
		System.out.println(c+" -> "+r+","+g+","+b);
	}

	private MamutViewTrackScheme myOwnTSWindow = null;
	private GraphColorGeneratorAdapter<Spot, Link, TrackSchemeVertex, TrackSchemeEdge> myOwnColorProvider = null;

	private void workerClose()
	{
		if (socket != null)
		{
			System.out.println("Mastodon network sender: Disconnecting...");
			socket.disconnect("tcp://localhost:8765");
			socket.close();
			socket = null;
		}
	}


	//stores repeating xyzRC chunks of node definitions
	private final int msgNodesChunkSize = 5;
	private final Vector<Float> msgNodes = new Vector<>(400*msgNodesChunkSize, 20*msgNodesChunkSize);

	//stores repeating xyzxyzC chunks of node definitions
	private final int msgLinesChunkSize = 7;
	private final Vector<Float> msgLines = new Vector<>(400*msgLinesChunkSize, 20*msgLinesChunkSize);

	private void appendNodeToMsg(float[] pos, float radius, int color)
	{
		msgNodes.addAll( Arrays.asList(pos[0],pos[1],pos[2],radius,(float)color) );
	}

	private void appendLineToMsg(float[] from, float[] to, int color)
	{
		msgLines.addAll( Arrays.asList(from[0],from[1],from[2],to[0],to[1],to[2],(float)color) );
	}

	private final float[] rgb = new float[3]; //rgb[0] = r, rgb[2] = b
	private void packedIntColorToRGB(final int color)
	{
		rgb[2] = (float)(    color     & 0x000000FF) / 255.f;
		rgb[1] = (float)((color >>  8) & 0x000000FF) / 255.f;
		rgb[0] = (float)((color >> 16) & 0x000000FF) / 255.f;
	}

	private void sendAndClearAllMsgs()
	{
		if (socket != null)
		{
			if (msgNodes.size() > 0)
			{
				final StringWriter msgContainer = new StringWriter();
				final PrintWriter msgComposer = new PrintWriter(new BufferedWriter(msgContainer));

				msgComposer.print("v2 points "+(msgNodes.size()/msgNodesChunkSize)+" dim 3");
				int id=1;
				Iterator<Float> i = msgNodes.iterator();
				while (i.hasNext())
				{
					//node ID
					msgComposer.print(" ");
					msgComposer.print((id++)<<17);

					//pos
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());

					//radius
					msgComposer.print(" ");
					msgComposer.print(i.next());

					//color
					packedIntColorToRGB(i.next().intValue());
					msgComposer.print(" "+rgb[0]+" "+rgb[1]+" "+rgb[2]);
				}
				msgComposer.flush();

				socket.send( msgContainer.toString() );
			}

			if (msgLines.size() > 0)
			{
				final StringWriter msgContainer = new StringWriter();
				final PrintWriter msgComposer = new PrintWriter(new BufferedWriter(msgContainer));

				msgComposer.print("v2 lines "+(msgLines.size()/msgLinesChunkSize)+" dim 3");
				int id=1;
				Iterator<Float> i = msgLines.iterator();
				while (i.hasNext())
				{
					//node ID
					msgComposer.print(" ");
					msgComposer.print((id++)<<17);

					//pos from
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());

					//pos to
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());
					msgComposer.print(" ");
					msgComposer.print(i.next());

					//color
					packedIntColorToRGB(i.next().intValue());
					msgComposer.print(" "+rgb[0]+" "+rgb[1]+" "+rgb[2]);
				}
				msgComposer.flush();

				socket.send( msgContainer.toString() );
			}

			socket.send("v1 tick Mastodon sent you "+msgNodes.size()/msgNodesChunkSize
			            +" nodes with "+msgLines.size()/msgLinesChunkSize+" edges");
		}

		msgNodes.clear();
		msgLines.clear();
	}
	//---------------------------------- ZERO MQ stuff --------------------------------------
	//---------------------------------------------------------------------------------------


	private int minTimePoint,maxTimePoint;
	private int timePoint = -1; //if not set earlier, workerSend() will fix it to minTimePoint

	// --------- future GUI control points ---------
	//
	public int deltaBackPoints = 0;
	public int deltaForwardPoints = 0;

	public boolean useOwnRadiusInsteadOfSpotsOwn = false;
	//if yes:
	public float radiusOwnValue = 2.f;
	//if no:
	public float radiusScalingFactor = 1.f;

	public int colorWhenNoStyleIsUsed = 0x00FFFFFF;
	//else if color styles are used:
	public boolean alwaysShowAllNodes = true;
	//if yes:
	public int colorForNotColoredNodes = 0x002D4084;
	//if no: nodes not covered/colored with the current style are not displayed

	public boolean reportSpotsRangeStats = true;
	//
	// --------- future GUI control points ---------


	private void workerTimePrev()
	{
		if (timePoint > minTimePoint)
		{
			--timePoint;
			workerSend();
		}
	}

	private void workerTimeNext()
	{
		if (timePoint < maxTimePoint)
		{
			++timePoint;
			workerSend();
		}
	}

	private void workerCurrentTime()
	{
		timePoint = myOwnTSWindow.getTimepointModel().getTimepoint();
		workerSend();
	}


	IntRefMap<Spot> pairs = null;
	IntRefMap<Spot> firstElems = null;
	Spot sRef = null; //to avoid their re-creation with every call of isThisSpotMyNeighbor()
	Link lRef = null;
	private void reportPairs()
	{
		System.out.println("reporting some cell:");

		final Model model = pluginAppModel.getAppModel().getModel();
		final SpatioTemporalIndex< Spot > spots = model.getSpatioTemporalIndex();
		final Spot spotB = model.getGraph().vertexRef();

		sRef = model.getGraph().vertexRef();
		lRef = model.getGraph().edgeRef();

		if (pairs == null)
		{
			pairs      = RefMaps.createIntRefMap( model.getGraph().vertices(), -1, 50 );
			firstElems = RefMaps.createIntRefMap( model.getGraph().vertices(), -1, 50 );
		}

		//for every color, this will be the first element of the latest observed pair of spots
		firstElems.clear();

		//color to 0 - Mother, 1 - daughter of the first spot, 2 - daughter of the second spot
		final HashMap< Integer,Integer > colorToRole = new HashMap<>(10);

		for (int t = minTimePoint; t <= maxTimePoint; ++t)
		{
			//discover new pairs for this timepoint
			pairs.clear();
			int nextDaughterRole = -1;
			for ( final Spot spot : spots.getSpatialIndex( t ) )
			{
				//pairs are established based on the color, so consider only colored spots
				final int color = myOwnColorProvider.spotColor( spot );
				if (color != 0)
				{
					if ( pairs.containsKey( color ) )
					{
						//(at least) 2nd spot of the same color,
						//we have a pair with spotB:
						pairs.get( color, spotB );

						//so we have now 'spot' and 'spotB' that form a pair,
						//check who is gonna be reported first and store it in the 'spot'
						if (firstElems.containsKey(color))
						{
							if (isThisSpotMyNeighbor(spotB, firstElems.get(color)))
							{
								//switch them...
								sRef.refTo(spot);
								spot.refTo(spotB);
								spotB.refTo(sRef);
							}
						}
						firstElems.put(color, spot);

						//first time seeing this color? define a role for it
						if (colorToRole.get(color) == null)
						{
							if (colorToRole.size() == 0)
							{
								//so far no pair was seen, we must be mother
								colorToRole.put(color,0);
							}
							else
							if (colorToRole.size() == 1)
							{
								//so far only mother was recorded with the following color
								final int mColor = colorToRole.keySet().iterator().next();
								firstElems.get( mColor, sRef );

								//sRef is mother's first spot
								if (isThisSpotMyNeighbor(spot, sRef))
								{
									//I am the first daughter
									colorToRole.put(color,1);
									nextDaughterRole = 2;
								}
								else
								{
									//I am the first daughter
									colorToRole.put(color,2);
									nextDaughterRole = 1;
								}

								System.out.println("# division here at timepoint "+t);
							}
							else
							{
								//second observed daughter
								colorToRole.put(color, nextDaughterRole);
							}
						}


						double dist = 0;
						for (int dim = 0; dim < 3; ++dim)
						{
							final double dx = spot.getDoublePosition(dim) - spotB.getDoublePosition(dim);
							dist += dx*dx;
						}
						dist = Math.sqrt( dist );

						System.out.println(t+" "+colorToRole.get(color)+" "+spot.getLabel()+" "+spotB.getLabel()
								+" "+Math.sqrt(spot.getBoundingSphereRadiusSquared())
								+" "+dist+" "+Math.sqrt(spotB.getBoundingSphereRadiusSquared()));
					}
					else
					{
						//first element of a potential pair
						pairs.put( color, spot );
					}
				}
			}
		}

		model.getGraph().releaseRef( lRef ); lRef = null;
		model.getGraph().releaseRef( sRef ); sRef = null;
		model.getGraph().releaseRef( spotB );
	}

	private boolean isThisSpotMyNeighbor(final Spot myself, final Spot potentialNeig)
	{
	    final int nPI = potentialNeig.getInternalPoolIndex();

		for (int n=0; n < myself.incomingEdges().size(); ++n)
		{
			myself.incomingEdges().get(n, lRef).getSource( sRef );
			if (sRef.getInternalPoolIndex() == nPI) return true;
		}
		for (int n=0; n < myself.outgoingEdges().size(); ++n)
		{
			myself.outgoingEdges().get(n, lRef).getTarget( sRef );
			if (sRef.getInternalPoolIndex() == nPI) return true;
		}

		return false;
	}


	/** sends some stuff to the SimViewer */
	private void workerSend()
	{
		//assure that the timePoint is valid
		timePoint = Math.min( Math.max( timePoint, minTimePoint ), maxTimePoint );

		final Model model = pluginAppModel.getAppModel().getModel();
		final ModelGraph modelGraph = model.getGraph();
		final SpatioTemporalIndex< Spot > spots = model.getSpatioTemporalIndex();

		// -------------- nodes --------------

		float[] pos  = new float[3]; //for nodes and edges
		float[] posB = new float[3]; //for edges

		//DEBUG STATS:
		float[] minPos = {+100000,+100000,+100000};
		float[] maxPos = {-100000,-100000,-100000};

		//send nodes from the current timepoint
		for ( final Spot spot : spots.getSpatialIndex( timePoint ) )
		{
			//spot color
			int color = colorWhenNoStyleIsUsed;
			if ( ! myOwnTSWindow.getColoringModel().noColoring() )
			{
				//some color style is used, take color from it
				color = myOwnColorProvider.spotColor( spot );

				//did this spot got some color, that is, is it colored in this style?
				if (color == 0)
				{
					//no color, use either default or skip drawing of this spot
					if (alwaysShowAllNodes) color = colorForNotColoredNodes;
					else continue;
				}
			}

			//spot position
			spot.localize(pos);

			//spot radius
			final float radius = useOwnRadiusInsteadOfSpotsOwn ?
				( spot.edges().size() > 2 ? 2*radiusOwnValue : radiusOwnValue )
				:
				radiusScalingFactor * (float)Math.sqrt(spot.getBoundingSphereRadiusSquared());

			appendNodeToMsg(pos,radius,color);

			//DEBUG STATS:
			if (reportSpotsRangeStats)
			{
				for (int i=0; i < 3; ++i)
				{
					minPos[i] = Math.min(minPos[i],pos[i]);
					maxPos[i] = Math.max(maxPos[i],pos[i]);
				}
			}
		}

		//DEBUG STATS:
		if (reportSpotsRangeStats)
		{
			System.out.println("spatial span @ "+timePoint+": "
			    +minPos[0]+"-"+maxPos[0]+"  x  "
			    +minPos[1]+"-"+maxPos[1]+"  x  "
			    +minPos[2]+"-"+maxPos[2]);
		}


		// -------------- edges --------------

		final Link lRef = modelGraph.edgeRef();              //link reference
		final Spot sRef = modelGraph.vertices().createRef(); //aux spot reference

		//send edges backward up to a desired no. of timepoints
		for (int time = timePoint; time > (timePoint-deltaBackPoints) && time > minTimePoint; --time)
		{
			//over all spots in the current time point
			for ( final Spot spot : spots.getSpatialIndex( time ) )
			{
				for (int n=0; n < spot.incomingEdges().size(); ++n)
				{
					spot.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= (timePoint-deltaBackPoints))
					{
						spot.localize(pos);
						sRef.localize(posB);
						appendLineToMsg(pos,posB, 4);
					}
				}
				for (int n=0; n < spot.outgoingEdges().size(); ++n)
				{
					spot.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() < time && sRef.getTimepoint() >= (timePoint-deltaBackPoints))
					{
						spot.localize(pos);
						sRef.localize(posB);
						appendLineToMsg(pos,posB, 4);
					}
				}
			}
		}

		//send edges forward up to a desired no. of timepoints
		for (int time = timePoint; time < (timePoint+deltaForwardPoints) && time < maxTimePoint; ++time)
		{
			//over all spots in the current time point
			for ( final Spot spot : spots.getSpatialIndex( time ) )
			{
				for (int n=0; n < spot.incomingEdges().size(); ++n)
				{
					spot.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= (timePoint+deltaForwardPoints))
					{
						spot.localize(pos);
						sRef.localize(posB);
						appendLineToMsg(pos,posB, 5);
					}
				}
				for (int n=0; n < spot.outgoingEdges().size(); ++n)
				{
					spot.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() > time && sRef.getTimepoint() <= (timePoint+deltaForwardPoints))
					{
						spot.localize(pos);
						sRef.localize(posB);
						appendLineToMsg(pos,posB, 5);
					}
				}
			}
		}

		sendAndClearAllMsgs();
	}
}
