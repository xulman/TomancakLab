package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;
import org.mastodon.app.ui.ViewMenuBuilder;
import org.mastodon.plugin.MastodonPlugin;
import org.mastodon.plugin.MastodonPluginAppModel;

import org.mastodon.revised.mamut.Mastodon;
import org.mastodon.revised.mamut.MamutAppModel;
import org.mastodon.revised.mamut.MamutViewTrackScheme;

import org.mastodon.revised.trackscheme.TrackSchemeEdge;
import org.mastodon.revised.trackscheme.TrackSchemeVertex;
import org.mastodon.revised.ui.coloring.GraphColorGeneratorAdapter;

import org.mastodon.revised.model.mamut.Model;
import org.mastodon.revised.model.mamut.ModelGraph;
import org.mastodon.revised.model.mamut.Spot;
import org.mastodon.revised.model.mamut.Link;
import org.mastodon.spatial.SpatioTemporalIndex;

import org.mastodon.project.MamutProject;

import org.scijava.AbstractContextual;
import org.scijava.Context;
import org.scijava.plugin.Plugin;
import org.scijava.ui.behaviour.util.Actions;
import org.scijava.ui.behaviour.util.AbstractNamedAction;
import org.scijava.ui.behaviour.util.RunnableAction;

import javax.swing.*;
import java.io.PrintWriter;
import java.io.BufferedWriter;
import java.io.StringWriter;
import java.io.File;
import java.util.*;

import org.zeromq.SocketType;
import org.zeromq.ZMQ;
import org.zeromq.ZMQException;


@Plugin( type = OpenSimViewerAndSendTracking.class )
public class OpenSimViewerAndSendTracking extends AbstractContextual implements MastodonPlugin
{
	//"IDs" of all plug-ins wrapped in this class
	private static final String PluginID_open = "SV-OpenSimViewer";
	private static final String PluginID_senB = "SV-SendFrameOnBackwardTPmove";
	private static final String PluginID_senF = "SV-SendFrameOnForwardTPmove";
	//------------------------------------------------------------------------

	@Override
	public List< ViewMenuBuilder.MenuItem > getMenuItems()
	{
		//this places the plug-in's menu items into the menu,
		//the titles of the items are defined right below
		return Arrays.asList(
				menu( "Plugins",
						item( PluginID_open ) ) );
	}

	/** titles of this plug-in's menu items */
	private static Map< String, String > menuTexts = new HashMap<>();
	static
	{
		menuTexts.put( PluginID_open, "Connect to SimViewer" );
	}

	@Override
	public Map< String, String > getMenuTexts()
	{
		return menuTexts;
	}
	//------------------------------------------------------------------------

	private final AbstractNamedAction actionOpen;
	private final AbstractNamedAction actionSendB;
	private final AbstractNamedAction actionSendF;

	/** default c'tor: creates Actions available from this plug-in */
	public OpenSimViewerAndSendTracking()
	{
		actionOpen  = new RunnableAction( PluginID_open, this::workerOpen );
		actionSendB = new RunnableAction( PluginID_senB, this::workerTimePrev );
		actionSendF = new RunnableAction( PluginID_senF, this::workerTimeNext );
		updateEnabledActions();
	}

	/** register the actions to the application (with no shortcut keys) */
	@Override
	public void installGlobalActions( final Actions actions )
	{
		//final String[] noShortCut = new String[] {};
		actions.namedAction( actionOpen,  "C" );
		actions.namedAction( actionSendB, "N" );
		actions.namedAction( actionSendF, "M" );
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

		minTimePoint = pluginAppModel.getAppModel().getMinTimepoint();
		maxTimePoint = pluginAppModel.getAppModel().getMaxTimepoint();
	}

	/** enables/disables menu items based on the availability of some project */
	private void updateEnabledActions()
	{
		final MamutAppModel appModel = ( pluginAppModel == null ) ? null : pluginAppModel.getAppModel();
		actionOpen.setEnabled(  appModel != null );
		actionSendB.setEnabled( appModel != null );
		actionSendF.setEnabled( appModel != null );
	}


	//---------------------------------------------------------------------------------------
	//---------------------------------- ZERO MQ stuff --------------------------------------
	private ZMQ.Socket socket = null;

	/** opens (again) the SimViewer */
	private void workerOpen()
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

			socket.connect("tcp://localhost:8765");
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

			//open a TrackScheme window that shall be under our control,
			//and retrieve a handle on the current GraphColorGeneratorAdapter
			myOwnTSWindow = pluginAppModel.getWindowManager().createTrackScheme();
			myOwnColorProvider = myOwnTSWindow.getGraphColorGeneratorAdapter();

			if (myOwnColorProvider == null)
				throw new RuntimeException("TrackScheme window created without GraphColorGeneratorAdaptor!?");

			//also register that this connection should be closed on this window close
			myOwnTSWindow.onClose( this::workerClose );

			myOwnTSWindow.getColoringModel().listeners().add( this::workerSend );
			myOwnTSWindow.onClose( () -> myOwnTSWindow.getColoringModel().listeners().remove( this::workerSend ) );

			//finally, send the current content to the SimViewer
			this.workerSend();
		}
		else
			System.out.println("Mastodon network sender: NOT connected to SimViewer");
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
	private int timePoint = 36; //current timepoint

	public int deltaBackPoints = 0;
	public int deltaForwardPoints = 0;


	private void workerTimePrev()
	{
		if (timePoint == -1) timePoint = minTimePoint;

		if (timePoint > minTimePoint)
		{
			--timePoint;
			workerSend();
		}
	}

	private void workerTimeNext()
	{
		if (timePoint == -1) timePoint = minTimePoint;

		if (timePoint < maxTimePoint)
		{
			++timePoint;
			workerSend();
		}
	}

	/** sends some stuff to the SimViewer */
	private void workerSend()
	{
		if (timePoint == -1) timePoint = minTimePoint;

		final Model model = pluginAppModel.getAppModel().getModel();
		final ModelGraph modelGraph = model.getGraph();
		final SpatioTemporalIndex< Spot > spots = model.getSpatioTemporalIndex();

		// -------------- nodes --------------

		float[] pos  = new float[3]; //for nodes and edges
		float[] posB = new float[3]; //for edges

		//DEBUG STATS:
		float[] minPos = {+100000,+100000,+100000};
		float[] maxPos = {-100000,-100000,-100000};

		final int defaultColor = 0x00404040;
		final float defaultRadius = 5;

		//send nodes from the current timepoint
		for ( final Spot spot : spots.getSpatialIndex( timePoint ) )
		{
			//spot position
			spot.localize(pos);

			//spot radius
			//final float radius = spot.edges().size() > 2 ? 2*defaultRadius : defaultRadius;
			final float radius = (float)Math.sqrt(spot.getBoundingSphereRadiusSquared());

			//spot color
			int color = myOwnColorProvider.spotColor( spot );
			if (color == 0) color = defaultColor;

			appendNodeToMsg(pos,radius,color);

			//DEBUG STATS:
			for (int i=0; i < 3; ++i)
			{
				minPos[i] = Math.min(minPos[i],pos[i]);
				maxPos[i] = Math.max(maxPos[i],pos[i]);
			}
		}

		//DEBUG STATS:
		System.out.println("spatial span @ "+timePoint+": "
				+minPos[0]+"-"+maxPos[0]+"  x  "
				+minPos[1]+"-"+maxPos[1]+"  x  "
				+minPos[2]+"-"+maxPos[2]);


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


	public static void main( final String[] args ) throws Exception
	{
		Locale.setDefault( Locale.US );
		UIManager.setLookAndFeel( UIManager.getSystemLookAndFeelClassName() );

		//final MamutProject project = new MamutProject( null, new File( "x=1000 y=1000 z=100 sx=1 sy=1 sz=10 t=400.dummy" ) );
		final MamutProject project = new MamutProject(
		/*
				new File( "/Users/ulman/DATA/Mette/dataset.mastodon" ),
				new File( "/Users/ulman/DATA/Mette/dataset_hdf5.xml" ) );
		*/
				new File( "/Users/ulman/p_Johannes/Polyclad/2019-09-06_EcNr2_NLSH2B-GFP_T-OpenSPIM_singleTP_newer.mastodon" ),
				new File( "/Users/ulman/p_Johannes/Polyclad/2019-09-06_EcNr2_NLSH2B-GFP_T-OpenSPIM_singleTP.xml" ) );

		final Mastodon mastodon = new Mastodon();
		new Context().inject( mastodon );
		mastodon.run();
		mastodon.setExitOnClose();
		mastodon.openProject( project );
	}
}
