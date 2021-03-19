package de.mpicbg.tomancaklab;

import org.mastodon.mamut.plugin.MamutPluginAppModel;
import org.mastodon.mamut.MamutViewTrackScheme;
import org.mastodon.ui.coloring.ColoringModel;
import org.mastodon.ui.coloring.GraphColorGenerator;
import org.mastodon.model.TimepointListener;
import org.mastodon.mamut.model.Model;
import org.mastodon.mamut.model.ModelGraph;
import org.mastodon.mamut.model.Spot;
import org.mastodon.mamut.model.Link;
import org.mastodon.spatial.SpatioTemporalIndex;
import org.mastodon.collection.RefSet;
import org.mastodon.collection.ref.RefSetImp;

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
	private MamutPluginAppModel pluginAppModel;

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
			myOwnTSWindow = pluginAppModel.getWindowManager().createTrackScheme();
			//
			//and retrieve a handle on the current GraphColorGenerator
			if (myOwnTSWindow.getGraphColorGeneratorAdapter() == null)
				throw new RuntimeException("TrackScheme window created without GraphColorGeneratorAdaptor!?");

			final AbstractNamedAction actionSendB = new RunnableAction( SVsenB, this::workerTimePrev );
			final AbstractNamedAction actionSendF = new RunnableAction( SVsenF, this::workerTimeNext );
			pluginAppModel.getAppModel().getAppActions().namedAction( actionSendB, "N" );
			pluginAppModel.getAppModel().getAppActions().namedAction( actionSendF, "M" );

			JPanel controlPanel = new JPanel();
			controlPanel.setLayout(new GridLayout(3,4));

			//radius spinners to be used later
			final Label lblRadiusOwn     = new Label("  Own radius:");
			final Label lblRadiusScaling = new Label("Radius scale:");
			final JSpinner spnRadiusOwn     = new JSpinner( new SpinnerNumberModel(radiusOwnValue,      0.01, 100.0, 1.0) );
			final JSpinner spnRadiusScaling = new JSpinner( new SpinnerNumberModel(radiusScalingFactor, 0.01, 100.0, 0.1) );

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

			//3rd row
			miniGrp = new JPanel();
			l = new Label("Show past edges:");
			l.setAlignment( Label.RIGHT );
			miniGrp.add(l);
			//
			final JSpinner pastEdgesSpinner = new JSpinner(new SpinnerNumberModel(deltaBackPoints, 0, 1000, 1));
			pastEdgesSpinner.addChangeListener( (action) -> {
				deltaBackPoints = (int)(pastEdgesSpinner.getModel().getValue());
				workerCurrentTime();
			});
			miniGrp.add( pastEdgesSpinner );
			controlPanel.add( miniGrp );

			miniGrp = new JPanel();
			l = new Label("Show future edges:");
			l.setAlignment( Label.RIGHT );
			miniGrp.add(l);
			//
			final JSpinner futureEdgesSpinner = new JSpinner(new SpinnerNumberModel(deltaForwardPoints, 0, 1000, 1));
			futureEdgesSpinner.addChangeListener( (action) -> {
				deltaForwardPoints = (int)futureEdgesSpinner.getValue();
				workerCurrentTime();
			});
			miniGrp.add( futureEdgesSpinner );
			controlPanel.add( miniGrp );

			btn = new Button("  Choose links color when not from spots  ");
			btn.addActionListener( (action) -> {
				colorForNotColoredLinks = getRGBviaDialog(colorForNotColoredLinks);
				workerCurrentTime();
			} );
			controlPanel.add( btn );

			final Checkbox linksColorToggle = new Checkbox("Links take color from spots");
			linksColorToggle.setState(colorLinksAreFromSpots);
			linksColorToggle.addItemListener( (action) -> {
				colorLinksAreFromSpots = linksColorToggle.getState();
				System.out.println("new button state: "+ colorLinksAreFromSpots);
				workerCurrentTime();
			} );
			controlPanel.add( linksColorToggle );

			myOwnTSWindow.getFrame().add(controlPanel, BorderLayout.SOUTH);

			//also register that this connection should be closed on this window close
			myOwnTSWindow.onClose( this::workerClose );

			//on coloring style change, repaint the currently sent time point
			//NB: one explicit reference so that add() and remove() can really complement themselves
			final ColoringModel.ColoringChangedListener listenerRefOnWorkerSend = this::workerSend;
			myOwnTSWindow.getColoringModel().listeners().add( listenerRefOnWorkerSend );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getColoringModel().listeners().remove( listenerRefOnWorkerSend ) );

			//on time point change, repaint the current time point
			//NB: see above...
			final TimepointListener listenerRefOnWorkerCurrentTime = this::workerCurrentTime;
			myOwnTSWindow.getTimepointModel().listeners().add( listenerRefOnWorkerCurrentTime );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getTimepointModel().listeners().remove( listenerRefOnWorkerCurrentTime ));

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
	private GraphColorGenerator<Spot, Link> myOwnColorProvider = null;

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
	private final Vector<Float> msgNodes = new Vector<>(1000*msgNodesChunkSize, 200*msgNodesChunkSize);

	//stores repeating xyzxyzC chunks of node definitions
	private final int msgLinesChunkSize = 7;
	private final Vector<Float> msgLines = new Vector<>(1000*msgLinesChunkSize, 200*msgLinesChunkSize);

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

	public int deltaBackPoints = 0;
	public int deltaForwardPoints = 0;
	public int colorForNotColoredLinks = 0x002D4084;
	public boolean colorLinksAreFromSpots = true;

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

	/** sends some stuff to the SimViewer */
	private void workerSend()
	{
		//assure that the timePoint is valid
		timePoint = Math.min( Math.max( timePoint, minTimePoint ), maxTimePoint );

		//get fresh/current "color service"
		myOwnColorProvider = myOwnTSWindow.getGraphColorGeneratorAdapter().getColorGenerator();

		final Model model = pluginAppModel.getAppModel().getModel();
		final ModelGraph modelGraph = model.getGraph();
		final SpatioTemporalIndex< Spot > spots = model.getSpatioTemporalIndex();

		// -------------- nodes --------------

		float[] pos  = new float[3]; //for nodes and edges
		float[] posB = new float[3]; //for edges

		//DEBUG STATS:
		float[] minPos = {+100000,+100000,+100000};
		float[] maxPos = {-100000,-100000,-100000};

		//for links:
		final Link lRef = modelGraph.edgeRef();              //link reference
		final Spot sRef = modelGraph.vertices().createRef(); //aux spot reference
		final Spot sREF = modelGraph.vertices().createRef(); //aux spot reference

		//send nodes from the current timepoint
		for ( final Spot spot : spots.getSpatialIndex( timePoint ) )
		{
			//spot color
			int color = colorWhenNoStyleIsUsed;
			int linkColor = colorForNotColoredLinks;
			if ( ! myOwnTSWindow.getColoringModel().noColoring() )
			{
				//some color style is used, take color from it
				color = myOwnColorProvider.color( spot );

				//did this spot got some color, that is, is it colored in this style?
				if (color == 0)
				{
					//no color, use either default or skip drawing of this spot
					if (alwaysShowAllNodes) color = colorForNotColoredNodes;
					else continue;
				}

				if (colorLinksAreFromSpots) linkColor = color;
			}

			//spot position
			spot.localize(pos);

			//spot radius
			final float radius = useOwnRadiusInsteadOfSpotsOwn ?
				radiusOwnValue : radiusScalingFactor * (float)Math.sqrt(spot.getBoundingSphereRadiusSquared());

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

			RefSet<Spot> todoSpots = new RefSetImp<>(modelGraph.vertices().getRefPool(),10);

			//edges - backward
			todoSpots.add( spot );
			while (todoSpots.size() > 0)
			{
				//take one from the pool
				sREF.refTo( todoSpots.iterator().next() );
				todoSpots.remove( sREF );

				//cache its position & time
				sREF.localize(pos);
				int currTime = sREF.getTimepoint();

				for (int n=0; n < sREF.incomingEdges().size(); ++n)
				{
					sREF.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() < currTime && sRef.getTimepoint() >= (timePoint-deltaBackPoints))
					{
						sRef.localize(posB);
						appendLineToMsg(pos,posB, linkColor);
						todoSpots.add( sRef );
					}
				}
				for (int n=0; n < sREF.outgoingEdges().size(); ++n)
				{
					sREF.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() < currTime && sRef.getTimepoint() >= (timePoint-deltaBackPoints))
					{
						sRef.localize(posB);
						appendLineToMsg(pos,posB, linkColor);
						todoSpots.add( sRef );
					}
				}
			}

			//edges - forward
			todoSpots.add( spot );
			while (todoSpots.size() > 0)
			{
				//take one from the pool
				sREF.refTo( todoSpots.iterator().next() );
				todoSpots.remove( sREF );

				//cache its position & time
				sREF.localize(pos);
				int currTime = sREF.getTimepoint();

				for (int n=0; n < sREF.incomingEdges().size(); ++n)
				{
					sREF.incomingEdges().get(n, lRef).getSource( sRef );
					if (sRef.getTimepoint() > currTime && sRef.getTimepoint() <= (timePoint+deltaForwardPoints))
					{
						sRef.localize(posB);
						appendLineToMsg(pos,posB, linkColor);
						todoSpots.add( sRef );
					}
				}
				for (int n=0; n < sREF.outgoingEdges().size(); ++n)
				{
					sREF.outgoingEdges().get(n, lRef).getTarget( sRef );
					if (sRef.getTimepoint() > currTime && sRef.getTimepoint() <= (timePoint+deltaForwardPoints))
					{
						sRef.localize(posB);
						appendLineToMsg(pos,posB, linkColor);
						todoSpots.add( sRef );
					}
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

		sendAndClearAllMsgs();

		modelGraph.releaseRef( sREF );
		modelGraph.releaseRef( sRef );
		modelGraph.releaseRef( lRef );
	}
}
