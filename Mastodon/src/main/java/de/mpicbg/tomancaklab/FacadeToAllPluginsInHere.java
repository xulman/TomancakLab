package de.mpicbg.tomancaklab;

import static org.mastodon.app.ui.ViewMenuBuilder.item;
import static org.mastodon.app.ui.ViewMenuBuilder.menu;
import org.mastodon.app.ui.ViewMenuBuilder;
import org.mastodon.plugin.MastodonPlugin;
import org.mastodon.plugin.MastodonPluginAppModel;
import org.mastodon.revised.mamut.Mastodon;
import org.mastodon.revised.mamut.MamutAppModel;
import org.mastodon.project.MamutProject;

import net.imagej.ImageJ;
import org.scijava.AbstractContextual;
import org.scijava.command.CommandService;
import org.scijava.log.LogService;
import org.scijava.plugin.Plugin;
import org.scijava.ui.behaviour.util.Actions;
import org.scijava.ui.behaviour.util.AbstractNamedAction;
import org.scijava.ui.behaviour.util.RunnableAction;

import javax.swing.*;
import java.io.File;
import java.util.*;
import java.util.List;


@Plugin( type = FacadeToAllPluginsInHere.class )
public class FacadeToAllPluginsInHere extends AbstractContextual implements MastodonPlugin
{
	//"IDs" of all plug-ins wrapped in this class
	private static final String SVopen = "LoPaT-OpenSimViewer";
	private static final String t2gyEd = "LoPaT-Time2Gen-yEd";
	private static final String t2gGS  = "LoPaT-Time2Gen-GSOutlook";
	private static final String t2len  = "LoPaT-LineageLengths";
	//------------------------------------------------------------------------

	@Override
	public List< ViewMenuBuilder.MenuItem > getMenuItems()
	{
		//this places the plug-in's menu items into the menu,
		//the titles of the items are defined right below
		return Arrays.asList(
				menu( "Plugins",
						item( SVopen ),
						item( t2gyEd ), item ( t2gGS ),
						item( t2len ) ) );
	}

	/** titles of this plug-in's menu items */
	private static Map< String, String > menuTexts = new HashMap<>();
	static
	{
		menuTexts.put( SVopen, "Connect to SimViewer" );
		menuTexts.put( t2gyEd, "Time-decimated lineage to yEd" );
		menuTexts.put( t2gGS,  "Time-decimated lineage to outlook window" );
		menuTexts.put( t2len,  "Export lineage lengths" );
	}

	@Override
	public Map< String, String > getMenuTexts()
	{
		return menuTexts;
	}
	//------------------------------------------------------------------------

	private final AbstractNamedAction actionOpen;
	private final AbstractNamedAction actionLengths;
	private final AbstractNamedAction actionyEd,actionGS;

	/** default c'tor: creates Actions available from this plug-in */
	public FacadeToAllPluginsInHere()
	{
		actionOpen    = new RunnableAction( SVopen, this::simviewerConnection );
		actionLengths = new RunnableAction( t2len,  this::exportLengths );
		actionyEd     = new RunnableAction( t2gyEd, this::time2Gen2yEd );
		actionGS      = new RunnableAction( t2gGS,  this::time2Gen2GSwindow );
		updateEnabledActions();
	}

	/** register the actions to the application (with no shortcut keys) */
	@Override
	public void installGlobalActions( final Actions actions )
	{
		final String[] noShortCut = { "not mapped" };
		actions.namedAction( actionOpen,    "C" );
		actions.namedAction( actionLengths, noShortCut );
		actions.namedAction( actionyEd,     noShortCut );
		actions.namedAction( actionGS,      noShortCut );
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
		actionOpen.setEnabled(    appModel != null );
		actionLengths.setEnabled( appModel != null );
		actionyEd.setEnabled(     appModel != null );
		actionGS.setEnabled(      appModel != null );
	}
	//------------------------------------------------------------------------

	private void simviewerConnection()
	{
		this.getContext().getService(CommandService.class).run(
			OpenSimViewerAndSendTracking.class, true,
			"pluginAppModel", pluginAppModel);
	}

	private void exportLengths()
	{
		this.getContext().getService(CommandService.class).run(
			LineageLengthExporter.class, true,
			"appModel", pluginAppModel.getAppModel());
	}

	private void time2Gen2yEd()
	{
		this.getContext().getService(CommandService.class).run(
			LineageExporter.class, true,
			"appModel", pluginAppModel.getAppModel(),
			"logServiceRef", this.getContext().getService(LogService.class).log(),
			"doyEdExport", true);
	}

	private void time2Gen2GSwindow()
	{
		this.getContext().getService(CommandService.class).run(
			LineageExporter.class, true,
			"appModel", pluginAppModel.getAppModel(),
			"logServiceRef", this.getContext().getService(LogService.class).log(),
			"doyEdExport", false,
			"graphMLfile", new File(""));
	}
	//------------------------------------------------------------------------

	public static void main( final String[] args ) throws Exception
	{
		//start up our own Fiji/Imagej2
		final ImageJ ij = new net.imagej.ImageJ();
		ij.ui().showUI();

		Locale.setDefault( Locale.US );
		UIManager.setLookAndFeel( UIManager.getSystemLookAndFeelClassName() );

		//final MamutProject project = new MamutProject( null, new File( "x=1000 y=1000 z=100 sx=1 sy=1 sz=10 t=400.dummy" ) );
		final MamutProject project = new MamutProject(
		/*
				new File( "/Users/ulman/DATA/Mette/dataset.mastodon" ),
				new File( "/Users/ulman/DATA/Mette/dataset_hdf5.xml" ) );
		*/
				new File( "/Users/ulman/p_Johannes/Polyclad/2019-09-06_EcNr2_NLSH2B-GFP_T-OpenSPIM_singleTP.mastodon" ),
				new File( "/Users/ulman/p_Johannes/Polyclad/2019-09-06_EcNr2_NLSH2B-GFP_T-OpenSPIM_singleTP.xml" ) );

		final Mastodon mastodon = (Mastodon)ij.command().run(Mastodon.class, true).get().getCommand();
		mastodon.setExitOnClose();
		mastodon.openProject( project );
	}
}
