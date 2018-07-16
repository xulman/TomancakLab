/***************************************************************
	VARIABLES
***************************************************************/
var maxTime = 0;										//highest end time in file
var margin = 50;										//margin of SVG - it changes during change of scale
var marginX = 50;										//margin for X - doesnt change at all
var margLife = 60;										//margin for LifeGraph
var radius = 8.5;											//radius
var stroke = 4;											//stroke of lines
var scaler = 50;										//scale on axis
var positionLine = 0;									//position of line in axis

var cells = []; 										//array of cells, which will display (chnage when using slider)
var datacells = [];										//array for storing cell arrays during parsing the file
var cellPopulation = [];								//array of all cells from file (doesnt change at all)
var lifeGraphCells = [];								//array for storing cells for lifeGraph

//variables for info about states of cells
var begin = 0;
var mitosis = 0;
var death = 0;

//zmenit nazev!
var posunuti = 60;										//Posunuti hodnot v life graphu vedle poctu ZIJE, SMRT, MITOSA...
var branching = 0;

//nastaveni
var isVertical = false;									//is vertical display choosed?
var changeMaxTime = false;								//should i change maxTime?
var showFrom = 0;
var showTo = 0;
var everywhereAxis = false;								//should i show axis everywhere?
var smallVisualisation = false;							//should i show small visualisation?
var showLifeLengthText = true;							//should i show the text of legth of life?
var showCellId = true;									//should i show the id of cell?
var displayScale = true;								//shloud i use different scale for drawing? (for abnormal division)
var showLine = true;									//should i show main red line?

//which font size is active?
var activeFontId = 1;
var activeFontLife = 1;
var activeFontText = 1;

var linearScaleX;										//Linear scale for X axis
var linearScaleY;										//Linear scale for y axis
var graphBoxWidth = 1000;								//width of graphBox
var graphBoxHeightVertical = 840;						//Height of graph box for vertical display

var description = ["BEGIN", "END", "DIVISION", "INTERPHASE"];

//colors				 BEGIN  	END 	   MITOSIS    ALIVE  	 LINE
var colors = 			["#2b83ba", "#d7191c", "#79b04e", "#984ea3", "#000000"];
var colorsHovering = 	["#87b1d4", "#ee7576", "#94cf92", "#c194c7", "#666666"];

var textHeight = ["12px", "14px", "16px", "18px", "20px"];

//Texts for dialog windows
var helpLoad =  "<h4><b>LOAD FILE</b></h4>"
				+ "To display your data, load the file using this button. Only <i><b>.txt</b></i> format is supported, and the data itself"
				+ " have to be in defined style."
				+ "<br> Which means: every line should have 4 numbers separated by space. These numbers are: ID, BEGIN, END and PARENT."
				+ "<br>The app will than display the <i>Graph of Cell Population</i>. More information about this graph is in the separate help button.";

var helpDisplay = "<h4><b>DISPLAY</b></h4>"
				+ "This button has four different options to use while displaying your data. They are divided into the two sections. <i>Orientation of graph</i> and <i>Additional options</i>."
				+ "<br><br><b>Orientation of graph</b>"
				+ "<br><b><i>Horizontal: </i></b>This button will allow you to display <i>Graph of Cell Population</i> horizontally. It is also the default orientation of displaying populations."
				+ "<br><b><i>Vertical: </i></b>This button will allow you to display <i>Graph of Cell Population</i> vertically."
				+ "<br><br><b>Additional options</b>"
				+ "<br><b><i>Toggle Miniature Visualisation: </i></b>This button will allow you to switch between default and small versions of the <i>Graph of Cell Population</i>."
				+ "<br><b><i>Toggle Axis/Axes: </i></b>With this button you can choose, if just only the one main axis will be shown, or if each cell lineage will have its own axis.";

var helpSort = "<h4><b>SORT CELLS</b></h4>"
				+ "This button has two possible options for sorting cell lineages."
				+ "<br><br><b><i>By their ID: </i></b>This otpion will sort the cell lineages upwordly by the ID's of the root cells."
				+ "<br><b><i>By their BEGIN time: </i></b>This option will sort the cell lineages upwordly by the BEGIN times of the root cells.";

var helpFont = "<h4><b>FONT</b></h4>"
				+ "With these options you can separately change the font size of either the cell ID's or Lengths of cells in interphase.";

var helpDisable = "<h4><b>DISABLE</b></h4>"
				+ "With options in this menu you can toggle the elements which are displayed in the <i>Graph of Cell Population</i>. These elements are: <i>ID's of cells, Length of cells in interphase"
				+ " </i>and<i> the red line</i>."
				+ "<br><br><b>ID of cell:</b> ID of cell displays near the BEGIN circle of the cell. In case the BEGIN circle is not in the restricted time based on slider, it shows near the beginning "
				+ "of the line, which connects BEGIN and END circles."
				+ "<br><br><b>Length of cells in interphase:</b> This number is displayd near the middle of the line connecting BEGIN and END circles of cell. In case the line is restricted with slider,"
				+ " the number won't show up."
				+ "<br><br><b>Red line: </b>Line goes through the whole <i>Graph of Cell Population</i> and indicates the actual selected frame and events (BEGIN, END, DIVISION, INTERPHASE) which happened during this frame.";

var helpSVG = "<h4><b>SAVE AS SVG</b></h4>"
				+ "This button gives you option to save the whole <i>Graph of Cell Population</i> with all enabled elements as <b><i>.svg</i></b> file. To disable some of the elements, use the <i>Disable</i> button."
				+ "<br><br> For converting SVG to PDF you can use: <a href=https://cloudconvert.com/svg-to-pdf>Cloud converter</a>";

var helpGraphOfCells = "<h4><b>GRAPH OF CELL POPULATION</b></h4>"
						+ "This graph shows the lineage of all cells from the video."
						+ "<br><br><b>Blue</b> (BEGIN) circles represents the frame (time), where the cell appeared for the first time. These circles are connected "
						+ "by black line with <b>Red</b> (END) or <b>Green</b> (DIVISION) circles. These represents the last time of cell in the video.<br>If it is <b>red</b>"
						+ " it means the cell died or went outside recordered area. <br>If it is <b>green</b> it means the cell had at least one descendant and underwent division."
						+ "<br><br> Each cell has it's <b>ID</b> besides it's BEGIN circle or if the blue circle is missing due to restriction by slider, it's near the beginning of the black line."
						+ "<br>Above the black line is showed the length of cell in <i>interphase</i> (number of frames the cell was in the video)."						
						+ "<br><br>By clickinkg on the elements in the graph, the info about that element and the cell will show up on the right.";

var helpGraphOfStates = "<h4><b>GRAPH OF STATES</b></h4>"
						+ "This graph shows what happened in the frame specified by the red line. It will provide information about"
						+ " number of cells which BEGAN in the given frame, number of cells which END, number of DIVISIONS and also number of cells currently in the INTERPHASE - "
						+ "these cells are than represented in the <i>Graph of Cells in Interphase</i>.";
						

var helpGraphOfInterphase = "<h4><b>GRAPH OF CELLS IN INTERPHASE</b></h4>"
						+ "This graph shows the minimalistic line of cells currently in the INTERPHASE. <br><br>Each line belongs to the one cell, which ID is shown"
						+ " on the left side of the black line. Next to the both ends are the frame numbers of BEGIN and END times of the cell.";

var helpSlider = "<h4><b>SLIDER</b></h4>"
						+ "The <i>Graph if Cell Population</i> can be restricted by handlers of the <b>slider</b> in the top. By moving the handlers, the graph will check if the cell"
						+ " belongs to the chosen selection. If not, the graph will adapt and remove all unapropriate cells. By moving handlers back, "
						+ "the hidden cells will show up again (after \"dropping\" the handler).";
var helpAxes = "<h4><b>AXES</b></h4>"
						+ "Each axis represents the number of frames in the video. <br>The red line represents the specific frame in that video."
						+ "<br><br>By clicking on any of the axes, the red line will change its position to that selected frame. By that, the red line will indicate what events happened in this specific frame."
						+ " Based on that the <i>Graph of States</i> and <i>Graph of Cells in Interphase</i> will be displayd."
						+ "<br><br>The position of the red line can be changed also by pressing the <b>left</b> and <b>right</b> arrow keys.";

var aboutTXT = "This CellLineage Visualisation tool was developed originally by Antonín Holík at Masaryk University, Brno, Czech Republic.<br/><br/>"
               + "HOLÍK, Antonín. <i>Vizualizace rodokmenu v buněčných populacích</i> [online]. Brno, 2016 [cit. 2018-07-16]. Available from: &lt;<a href=\"https://is.muni.cz/th/wwm19/?lang=en\">https://is.muni.cz/th/wwm19/?lang=en</a>&gt;. Bachelor's thesis. Masaryk University, Faculty of Informatics. Thesis supervisor Barbora Kozlíková.<br/><br/>"
               + "The tool reads a <u><a href=\"http://www.celltrackingchallenge.net\">Cell Tracking Challenge</a></u> lineage datafile (often called as <tt>tracks.txt</tt> or alike), visualize it, and offers to export the view on the lineage as an SVG file. "
					+ "The details on <u><a href=\"http://public.celltrackingchallenge.net/documents/Naming%20and%20file%20content%20conventions.pdf\">the input data format are explained here.</a></u>";

var interestingInfoText = "<br><b>Actual frame: </b>";



/***************************************************************
					INITIAL PREPARATIONS
***************************************************************/
//preparing jquery
$(document).ready(function() {
    //console.log( "jquery ready!" );
});

//set controling of the red line via keyboard
$(document).keydown(function(e) {
    switch(e.which) {
        case 37: // left
			if(isVertical){
				lineY(positionLine -= 1);
			} else{
				lineX(positionLine -= 1);
			}
        break;
        case 39: // right
			if(isVertical){
				lineY(positionLine += 1);
			} else{
				lineX(positionLine += 1);
			}
        break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});

//Prepare dialog for HELP
$( "#dialog" ).dialog({
    autoOpen: false,
    width:700,
    height:500,
    show: {
        effect: "blind",
        duration: 500
    },
    hide: {
        effect: "blind",
        duration: 500
    }
});

//Prepare dialog for ABOUT
$( "#dialogA" ).dialog({
    autoOpen: false,
    width:700,
    height:500,
    show: {
        effect: "blind",
        duration: 500
    },
    hide: {
        effect: "blind",
        duration: 500
    }
});

//disable all buttons except help and load
disableButtons();



/**************************************************************
	LOAD DATA
***************************************************************/
//reaction on file upload
document.getElementById('file-input')
  .addEventListener('change', readSingleFile, false);

//Load data from input
function readSingleFile(e) {
  	var file = e.target.files[0];
  	var fileName = file.name;
  	if (!file) {
    	return;
  	}

  	if(checkFileName(fileName) != 0){
  		document.getElementById("p1").innerHTML = "Not supported format - file is not <b>.txt</b>!";
  		showWarningDialog();
  		throw new Error("Not supported format - File is not .txt!");
  		return;
  	}

  	var reader = new FileReader();

  	//On load go through the file, make the cellPopulation array of all cels in file, display the graph, show the slider, enable all buttons
  	reader.onload = function(e) {  		
  		var contents = e.target.result;
  		parseData(contents);
  		changeMaxTime = true;
  		showFrom = 0;
  		showTo = maxTime;
  		cellPopulation = $.map(cells, function (obj) {
                      return $.extend(true, {}, obj);
                  });
  		display();
  		sliderManager();
  		document.getElementById("cellInfo").innerHTML = "";
  		enableAllButtons();
		branching = highestNumberOfChildren(cellPopulation);
		if(branching > 5){
			document.getElementById("p2").innerHTML = "Abnormal division is higher than 5! Visualisation may look weird... <br>The highest divison: " + branching;
  			showDivisionDialog();
		}
	};

  reader.readAsText(file);
}

//Function will check if the children of the cell are in the restriction time from slider, if not, they are removed from the list of children
//@param	cell 		cell which the function will check
function adjustChildren(cell){
	if(cell.children.length != 0){
		var k = cell.children.length - 1;
		for(k; k >= 0; k--){
			if(!(cell.children[k].begin <= showTo)){
				cell.children.splice(k, 1);
			} else{
				adjustChildren(cell.children[k]);
			}
		}
	}
}

//Function will check, if the file is .txt
function checkFileName(name){
	var length = name.length;
	var i = length - 4;
	var str1 = name.substring(i, length);
	var str2 = ".txt";
	return str1.localeCompare(str2);
}

//Function will take string array (=input file), and store all "root" cells with its children (and children of its children...)
//to "cells" array of cell objects
//@param 	text 	string array of whole .txt file
function parseData(text){
	var tmpPole = [];												//temporary array for storing all 4 numbers of cell (id, begin, end, parent)
	var tmpPromenna = "";											//temporary string for storing nummbers
	var i = 0;
	var z = 0;
	index = 0;														//variable for storing information about parent

	if(changeMaxTime){
		maxTime = 0;
		positionLine = 0;
		changeMaxTime = false;
	}

	while(datacells.length > 0){
		datacells.pop();
	}

	while(cells.length > 0){
		cells.pop();
	}

	//cycle will store each cell from text string into "tmpPole" as array with 4 values: [id,begin,end,parent]
	for(i; i < text.length; i++){

		if(text[i] == "\n"){										//is end of line?
			if(isNaN(+tmpPromenna)){
				document.getElementById("p1").innerHTML = "Not supported data! In line " + (datacells.length + 1) + " there are not only numbers!";
				showWarningDialog();
				throw new Error("Not supported data! - in row " + (datacells.length + 1) + " there are not only numbers!");
			}
			tmpPole.push(+tmpPromenna);								//store the last value int array

			if((tmpPole.length < 4) || (tmpPole.length > 4)){		//were there 4 values in the line
				document.getElementById("p1").innerHTML = "Not supported data! In line " + (datacells.length) + " there are more or less than 4 numbers!";
				showWarningDialog();
				throw new Error("Not supported data! - in row " + (datacells.length) + " there are more or less than 4 numbers!");
			}

			datacells.push(tmpPole);								//array is stored into "datacells"
			tmpPole = [];
			tmpPromenna ="";
		}

		else if(text[i] != " "){									//if it is not the break
			tmpPromenna += text[i]; 								//its digit of value -> storing to tmpPromenna

			//is it the end of array? -> solves the case when the file doesnt end with "\n" - same code as in if statement above
			if((i+1) == text.length){
				if(isNaN(+tmpPromenna)){
					document.getElementById("p1").innerHTML = "Not supported data! In line " + (datacells.length + 1) + " there are not only numbers!";
					showWarningDialog();
					throw new Error("Not supported data! - in row " + (datacells.length + 1) + " there are not only numbers!");
				}
				tmpPole.push(+tmpPromenna);								//store the last value int array

				if((tmpPole.length < 4) || (tmpPole.length > 4)){		//were there 4 values in the line
					document.getElementById("p1").innerHTML = "Not supported data! In line " + (datacells.length) + " there are more or less than 4 numbers!";
					showWarningDialog();
					throw new Error("Not supported data! - in row " + (datacells.length) + " there are more or less than 4 numbers!");
				}

				datacells.push(tmpPole);								//array is stored into "datacells"
				tmpPole = [];
				tmpPromenna ="";
				break;
			}
		}

		else{														//it is the break
			//if the last value is not the number (its char or something else) -> it is not supported file!
			if(isNaN(+tmpPromenna)){
				document.getElementById("p1").innerHTML = "Not supported data! In line " + (datacells.length + 1) + " there are not only numbers!";
				showWarningDialog();
				throw new Error("Not supported data! - in row " + (datacells.length + 1) + " there are not only numbers!");
			}
			tmpPole.push(+tmpPromenna);								//the number is stored into tmpPole
			tmpPromenna = "";
		}


	}

	//cycle will go through all cells in "datacells" array and create an array of "root" cells,
	//which will have all its children (and children of its children...) stored inside its own array
	for(z; z < datacells.length; z++){
		tmpPole = datacells[z];
		var parent;													//who's the parent

		//creating the new object of cell: ID, BEGIN TIME, END TIME, PARENT ID, ARRAY OF CHILDREN
		var cell = {
			id: tmpPole[0],
			begin: tmpPole[1],
			end: tmpPole[2],
			parentID: tmpPole[3],
			children: [],
			hasChildren: false
		}

		if(maxTime < cell.end){										//change the maxTime if the end time of cell is higher
			maxTime = cell.end;
		}


		if(cell.parentID == 0){										//cell doesnt have parent ->
			cells.push(cell);										//its the "root" cell! -> store it into cells (should be into cellPopulation, but i will create copy of it later)
		}
		else{														//cell has parent ->
			findParent(cell.parentID, cell, cells);					//it will be stored into children array of its parent
		}
	}
}

//Function will find the parent of the cell and store it inside its children array
//@param 	parentID	id of parent
//@param	cell 		cell which i want to store
//@param 	celles 		array of cells, where I look for parent

function findParent(parentID, cell, celles){
	var j = 0;
	for(j; j < celles.length; j++){
		if(celles[j].id == parentID){							//I found the parent!
			celles[j].children.push(cell);						//store the cell into parent children array
			celles[j].hasChildren = true;
			break;
		}
		else if(celles[j].children != null){					//it is not the parent but it has children
			findParent(parentID, cell, celles[j].children);		//try find the parent there!
		}
	}
}



/**************************************************************
  						 SLIDER 
***************************************************************/
//Function will remove cells array
function removeCells(){
	while(cells.length > 0){
		cells.pop();
	}
}

//function which will dislay and handle the slider
function sliderManager(){
	$("#slider-range").slider({
		range: true,
		min: 0,
		max: maxTime,
		values: [0, maxTime],

		//on slide, function will chnage the actual time values (from and to)
		slide: function(event, ui) {					
			d3.select("#textMin").text("From: " + ui.values[ 0 ]);
			d3.select("#textMax").text("To: " + ui.values[ 1 ]);
			showFrom = ui.values[ 0 ];
			showTo =  ui.values[ 1 ];

			//hide all cels which dont belong to restricted area
			d3.selectAll(".superCell").each(function(d, i){
				if(this.__data__[1] < showFrom || this.__data__[0] > showTo){
					d3.select(this).classed("superCell", false);
					d3.select(this).classed("hide", true);
					$(this).toggle(250);
				}
			})

			//unhide all cells which belong to restricted area
			d3.selectAll(".hide").each(function(d, i){
				if(this.__data__[1] >= showFrom && this.__data__[0] <= showTo){
					d3.select(this).classed("hide", false);
					d3.select(this).classed("superCell", true);
					$(this).toggle(250);
				}
			})

		},

		//on releasin the slider make new actual list of cells and display the graph
		stop: function(event, ui){			
			removeCells();
			var cellsCopy = $.map(cellPopulation, function (obj) {
                      return $.extend(true, {}, obj);
                  });
			adjustPopulationSelection(cellsCopy);
			display();
		}
	});

	//set the text fields show From and To
	d3.select("#textMin").text("From: " + $( "#slider-range" ).slider( "values", 0 ));
	d3.select("#textMax").text("To: " + $( "#slider-range" ).slider( "values", 1 ));
}

//Function will change the cell selection for display bassed on slider
//@param	population 		array of cells, from which the functoin will do the selection
function adjustPopulationSelection(population){
	var i = 0

	//cycle checks if the first "root" cell is in the restriction time from slider
	//YES: 		check if its children are in the restriction and store this "root" cell in cells
	//NO: 		if cell has children, call this function with array of children
	for(i; i < population.length; i++){
		if((population[i].begin >= showFrom && population[i].begin <= showTo) || (population[i].end >= showFrom && population[i].end <= showTo)){
			adjustChildren(population[i]);
			cells.push(population[i]);
		} else{
			if(population[i].children.length != 0){
				adjustPopulationSelection(population[i].children);
			}
		}
	}
}


/**************************************************************
   						BUTTONS
***************************************************************/

function helpLoadButton(){
	document.getElementById("helpText").innerHTML = helpLoad;
    $( "#dialog" ).dialog( "open" );
}

function helpDisplayButton(){
	document.getElementById("helpText").innerHTML = helpDisplay;
    $( "#dialog" ).dialog( "open" );
}

function helpSortButton(){
	document.getElementById("helpText").innerHTML = helpSort;
    $( "#dialog" ).dialog( "open" );
}

function helpFontButton(){
	document.getElementById("helpText").innerHTML = helpFont;
    $( "#dialog" ).dialog( "open" );
}

function helpDisableButton(){
	document.getElementById("helpText").innerHTML = helpDisable;
    $( "#dialog" ).dialog( "open" );
}

function helpSVGButton(){
	document.getElementById("helpText").innerHTML = helpSVG;
    $( "#dialog" ).dialog( "open" );
}

function helpSliderButton(){
	document.getElementById("helpText").innerHTML = helpSlider;
    $( "#dialog" ).dialog( "open" );
}

function helpAxesButton(){
	document.getElementById("helpText").innerHTML = helpAxes;
    $( "#dialog" ).dialog( "open" );
}

function helpInterphaseButton(){
	document.getElementById("helpText").innerHTML = helpGraphOfInterphase;
    $( "#dialog" ).dialog( "open" );
}

function helpCells(){
	document.getElementById("helpText").innerHTML = helpGraphOfCells;
    $( "#dialog" ).dialog( "open" );
}

function helpStates(){
	document.getElementById("helpText").innerHTML = helpGraphOfStates;
    $( "#dialog" ).dialog( "open" );
}

function changeFontId(value){
	activeFontId = value;
	display();
}

function changeFontLife(value){
	activeFontLife = value;
	display();
}

function changeFontText(){
	if(activeFontText < 2){
		activeFontText += 1;
	} else{
		activeFontText = 0;
	}
}

//Function will make SVG of the actual graph
function makeSVG(){
	//will add main axis, if there are not exes everywhere
	if(!everywhereAxis){
		disableSVGAxis();
	}
	var svg = document.getElementById("graphBoxSVG");											

	//preparation for saving, adding xmlns parameters
	var serializer = new XMLSerializer();
	var source = serializer.serializeToString(svg);
	if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)){
    	source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
	}
	if(!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)){
    	source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
	}
	source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
	var url = "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(source);

	//apply url link on SVG button
	var saver = document.getElementById("downloadLink").href = url;

	//disable main axis for SVG
	if(!everywhereAxis){
		disableSVGAxis();
	}
}

function toggleID(){
	$(".idOfCell").toggle(400);
        showCellId = !showCellId;
        setTimeout(function() {makeSVG();  }, 500);
}

function toggleLife(){	
        $(".lengthOfLifeText").toggle(400);
        showLifeLengthText = !showLifeLengthText;
        setTimeout(function() {makeSVG();  }, 500);
}

function toggleLine(){	
        $(".movingLine").toggle(400);
        showLine = !showLine;
        setTimeout(function() {makeSVG();  }, 500);
}

//
//	Functions for buttons
//
function vertical(){
	isVertical = true;
	display();
}

function horizontal(){
	isVertical = false;
	display();
}

function axisEverywhere(){
	everywhereAxis = !everywhereAxis;
	display();
}

//will change scale of display
function changeScales(){
	smallVisualisation = !smallVisualisation;
	if(smallVisualisation){
		scaler = 10;
		radius = 3;
		stroke = 1.5;

		margin = 10;
	}
	else{
		scaler = 50;
		radius = 8.5;
		stroke = 4;

		margin = 50;
	}

	if(displayScale){
		display();
	}
}

//function will display the visualisation
function display(){
	if(isVertical){
		displayVertical();
		makeSVG();
	} else{
		displayHorizontal();
		makeSVG();
	}
}

function sortByTime(){
	cells.sort(function(a,b){
		var keyA = a.begin;
		var keyB = b.begin;
		if(keyA < keyB) return -1;
    	if(keyA > keyB) return 1;
    	if(keyA == keyB) {
    		var keyC = a.id;
			var keyD = b.id;
			if(keyC < keyD) return -1;
    		if(keyC > keyD) return 1;
    		return 0;
    	}
	})

	display();
}

function sortById(){
	cells.sort(function(a,b){
		var keyA = a.id;
		var keyB = b.id;
		if(keyA < keyB) return -1;
    	if(keyA > keyB) return 1;
    	return 0;
	})
	display();
}

//sort for graph of life
function sortByIdSmth(cells){
	cells.sort(function(a,b){
		var keyA = a.id;
		var keyB = b.id;
		if(keyA < keyB) return -1;
    	if(keyA > keyB) return 1;
    	return 0;
	})
}

function lifeText(){
	showLifeLengthText = !showLifeLengthText;
	display();
}

function about(){
	document.getElementById("aboutText").innerHTML = aboutTXT;
    $( "#dialogA" ).dialog( "open" );
}



/**************************************************************
   					DISPLAYING ELEMENTS
***************************************************************/

//Function will display the line of life between the Begin and End circle
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the line in graph
function displayBeginToEndLine(cell, cellContainer, positionInGraph){
		var childrenText = getChildrenText(cell);
		var beginToEndLine = cellContainer.append("line")
										  .classed("beginToEndLine", true)
										  .on("mouseover", function() {							//Change color on hovering
        										d3.select(this).attr("stroke", colorsHovering[4]);
      				  					  })
    				  					  .on("mouseout", function(){
    											d3.select(this).attr("stroke", colors[4]);
    				  					  })
    				  					  .on("click", function(){								//On click show info about life of cell
    											d3.select("body").select(".cellInfo").selectAll("text").remove();
    											d3.select("body").select(".cellInfo").append("text").attr("font-size", textHeight[activeFontText])
    				 							.html("INTERPHASE of Cell: <b>" + cell.id + "</b><br/>BEGIN in Frame: <b>" + cell.begin + "</b><br/>END in Frame: <b>" + cell.end + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>")
    				  					  })
    				  					  .attr("stroke-width", stroke)
                      					  .attr("stroke", colors[4]); 

        //check if the slider doesnt caused the restricted drawing
        //YES: draw from/to place based on actual time in slider
        //NO: draw normally 
        var positionBegin;
        var positionEnd;
        if(cell.begin < showFrom){
        	positionBegin = showFrom;		
        } else{
        	positionBegin = cell.begin;
        }

        if(cell.end > showTo){
        	positionEnd = showTo;
        } else{
        	positionEnd = cell.end;
        }

		if(isVertical){
			beginToEndLine.attr("x1", positionInGraph)
						  .attr("y1", linearScaleY(positionBegin) + marginX/2)
						  .attr("x2", positionInGraph)
						  .attr("y2", linearScaleY(positionEnd) + marginX/2)
		} else{
			beginToEndLine.attr("x1", linearScaleX(positionBegin) + marginX/2)
						  .attr("y1", positionInGraph)
						  .attr("x2", linearScaleX(positionEnd) + marginX/2)
						  .attr("y2", positionInGraph);
		}
}

//Function will show the lenght of life
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the text in graph
function displayLengthOfLife(cell, cellContainer, positionInGraph){
		var timeDisplay = cellContainer.append("text").classed("lengthOfLifeText", true).attr("font-family", "sans-serif").attr("font-weight", "bold")
    								   .text(function(){
    										var result = cell.end - cell.begin + 1;
    										if(result < 2 || (result < 5 && maxTime > 20)){
    											return "";
    										}
    										else{
    											return result;}
    										})
    								    .attr("font-size", textHeight[activeFontLife])
   										.attr("id", "life" + cell.id)
   										.attr("fill", colors[3])
   										.attr("text-align", "right");
   		if(isVertical){
   			timeDisplay.attr("x", positionInGraph - 23 - activeFontLife)
    				   .attr("y", linearScaleY((cell.end - cell.begin)/2 + cell.begin) + marginX/2)
   		} else {
   			timeDisplay.attr("x", linearScaleX((cell.end - cell.begin)/2 + cell.begin) + marginX/2)
    				   .attr("y", positionInGraph + 15 + activeFontLife);
   		}
}

//Function will display the Begin circle
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the circle in graph
function displayBegin(cell, cellContainer, positionInGraph){
	var childrenText = getChildrenText(cell);		//list of cells in text
	var beginCircle = cellContainer.append("circle").classed("BeginCircle", true)
									.on("mouseover", function() {					//change of color on hovering
        									d3.select(this).attr("fill", colorsHovering[0]);
      								})
    								.on("mouseout", function() {
         									d3.select(this).attr("fill", colors[0]);
    								})
    								.on("click", function(){
    									d3.select("body").select(".cellInfo").selectAll("text").remove();
    									d3.select("body").select(".cellInfo").append("text").attr("font-size", textHeight[activeFontText])
    													.html("BEGIN of Cell: <b>" + cell.id + "</b><br/>BEGIN in Frame: <b>" + cell.begin + "</b><br/>END in Frame: <b>" + cell.end + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>")
    								})
    								.attr("r", radius)
			   						.attr("fill", colors[0]);

	if(isVertical){
		beginCircle.attr("cx", positionInGraph)
				   .attr("cy", linearScaleY(cell.begin)+ marginX/2);

	} else{
		beginCircle.attr("cx", linearScaleX(cell.begin) + marginX/2)
				   .attr("cy", positionInGraph);
	}
}

//Function will display the Begin circle
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the circle in graph
function displayBothBeginEnd(cell, cellContainer, positionInGraph){
	var childrenText = getChildrenText(cell);		//list of cells in text
	var outerCircle = cellContainer.append("circle").classed("BeginCircle", true)
									.on("mouseover", function() {					//change of color on hovering
        									d3.select(this).attr("fill", colorsHovering[0]);
      								})
    								.on("mouseout", function() {
         									d3.select(this).attr("fill", colors[0]);
    								})
    								.on("click", function(){
    									d3.select("body").select(".cellInfo").selectAll("text").remove();
    									d3.select("body").select(".cellInfo").append("text").attr("font-size", textHeight[activeFontText])
    													.html("BEGIN and END of Cell: <b>" + cell.id + "</b><br/>BEGIN and END in Frame: <b>" + cell.begin + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>")
    								})
    								.attr("r", function() {
    									if(smallVisualisation){
    										return radius + 2;
    									}
    									return radius + 2;
    								})
			   						.attr("fill", colors[0]);

	var innerCircle = cellContainer.append("circle").classed("BeginCircle", true)
									.on("mouseover", function() {					//change of color on hovering
        									d3.select(this).attr("fill", function(){
			   							if(cell.children.length != 0){
			   								return colorsHovering[2];
			   							}
			   							return colorsHovering[1];
			   						});
      								})
    								.on("mouseout", function() {
         									d3.select(this).attr("fill", function(){
			   							if(cell.children.length != 0){
			   								return colors[2];
			   							}
			   							return colors[1];
			   						});
    								})
    								.on("click", function(){
    									d3.select("body").select(".cellInfo").selectAll("text").remove();
    									d3.select("body").select(".cellInfo").append("text").attr("font-size", textHeight[activeFontText])
    													.html("BEGIN and END of Cell: <b>" + cell.id + "</b><br/>BEGIN and END in Frame: <b>" + cell.begin + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>")
    								})
    								.attr("r", function() {
    									if(smallVisualisation){
    										return radius;
    									}
    									return radius - 1;
    								})
			   						.attr("fill", function(){
			   							if(cell.children.length != 0){
			   								return colors[2];
			   							}
			   							return colors[1];
			   						});

	if(isVertical){
		outerCircle.attr("cx", positionInGraph)
				   .attr("cy", linearScaleY(cell.begin)+ marginX/2);

		innerCircle.attr("cx", positionInGraph)
				   .attr("cy", linearScaleY(cell.begin)+ marginX/2);


	} else{
		outerCircle.attr("cx", linearScaleX(cell.begin) + marginX/2)
				   .attr("cy", positionInGraph);

		innerCircle.attr("cx", linearScaleX(cell.begin) + marginX/2)
				   .attr("cy", positionInGraph);
	}
}


//Function will display the Id of cell
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the id
function displayIdOfCell(cell, cellContainer, positionInGraph){
	var idOfCell = cellContainer.append("text")
								.attr("class", "idOfCell")
								.text(cell.id)
			   					.attr("font-size", textHeight[activeFontId])
			   					.attr("text-anchor", "right")
			   					.attr("font-family", "sans-serif")
			   					.attr("font-weight", "bold");

	//check if slider didint changed position of drawing
	//YES: draw it on new position
	//NO: draw it normally
	var positionBegin = cell.begin;
	if(cell.begin < showFrom){
		positionBegin = showFrom;
	}

	if(isVertical){
		idOfCell.attr("x", positionInGraph + 10)
			   	.attr("y", linearScaleY(positionBegin) + marginX - 7);
	} else{
		idOfCell.attr("x", linearScaleX(positionBegin) + marginX - 20)
			   	.attr("y", positionInGraph - 10);
	}
}

//Function will display the mitosis circle
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the circle
function displayMitosis(cell, cellContainer, positionInGraph){
	var childrenText = getChildrenText(cell);
	var mitosisCircle = cellContainer.append("circle")
								 	 .attr("class", "MitosisCircle")
								 	 .on("mouseover", function() {				//Zmena barvy po najeti na prvek
        								d3.select(this).attr("fill", colorsHovering[2])
      							 	 })
    							 	 .on("mouseout", function() {
         								d3.select(this).attr("fill", colors[2]);
    							 	 })
    							 	 .on("click", function(){					//Po kliknuti se zobrazi info
    									d3.select("body").select(".cellInfo").selectAll("text").remove();
    									d3.select("body").select(".cellInfo").append("text")
    													.attr("font-size", textHeight[activeFontText])
    													.html("DIVISION of Cell: <b>" + cell.id + "</b><br/>BEGIN in Frame: <b>" + cell.begin + "</b><br/>END in Frame: <b>" + cell.end + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>");
    							 	 })
    							 	 .attr("r", radius)
			   					 	 .attr("fill", colors[2]);

	if(isVertical){
		mitosisCircle.attr("cx", positionInGraph)
					 .attr("cy", linearScaleY(cell.end) + marginX/2);

	} else{
		mitosisCircle.attr("cx", linearScaleX(cell.end) + marginX/2)
					 .attr("cy", positionInGraph);
	}
}

//Function will display the End circle
//@param 	cell 			actual displaying cell
//@param	cellContainer	svg container of the cell
//@param	positionInGraph where to place the circle
function displayEnd(cell, cellContainer, positionInGraph){
	var childrenText = getChildrenText(cell);
	var endCircle = cellContainer.append("circle")
								 .attr("class", "EndCircle")
								 .on("mouseover", function() {					//Zmena barvy po najeti na prvek
        							d3.select(this).attr("fill", colorsHovering[1]);
      							 })
    							 .on("mouseout", function() {
         							d3.select(this).attr("fill", colors[1]);
    							 })
    							 .on("click", function(){			//Po klinuti se zobrazi info
    								d3.select("body").select(".cellInfo").selectAll("text").remove();
    								d3.select("body").select(".cellInfo").append("text").attr("font-size", textHeight[activeFontText])
    												 .html("END of Cell: <b>" + cell.id + "</b><br/>BEGIN in Frame: <b>" + cell.begin + "</b><br/>END in Frame: <b>" + cell.end + "</b><br/>Parent: <b>" + cell.parentID + "</b><br/>Children: <b>" + childrenText+"</b>")
    							 })
    							 .attr("r", radius)
			   					 .attr("fill", colors[1]);

    if(isVertical){
    	endCircle.attr("cx", positionInGraph)
				 .attr("cy", linearScaleY(cell.end) + marginX/2);

    } else{
    	endCircle.attr("cx", linearScaleX(cell.end) + marginX/2)
				 .attr("cy", positionInGraph);
    }
}

//Funkce, ktera vytvori linku spoje mezi bodem mitotickeho deleni a nove vyniklou bunkou
//@param	positionInGraph 	pozice vykresleni
//@param 	ancestor 	 		bunka, ze ktere vznikly nove bunky
//@param	container 			svg, do ktereho linku vlozit
//@param	repairer			Y souradnice konce linky
//@param	child 				new cell
function connectParentChild(positionInGraph, ancestor, container, repairer, child){
	var ancestorLine = container.append("line")
								.attr("class", "ancestorLine")
								.attr("stroke-width", stroke)
                        		.attr("stroke", colors[4])
                        		.classed("superCell", true).datum([child.begin, child.end]);

    if(isVertical){
    	ancestorLine.attr("x1", positionInGraph)
					.attr("y1", linearScaleY(ancestor.end) + marginX/2)
					.attr("x2", repairer)
					.attr("y2", linearScaleY(child.begin) + marginX/2);
    } else{
    	ancestorLine.attr("x1", linearScaleX(ancestor.end) + marginX/2)
					.attr("y1", positionInGraph)
					.attr("x2", linearScaleX(child.begin) + marginX/2)
					.attr("y2", repairer);
    }
}

//function will display the main red X line
//param@	svgContainer		to what container to add the line
//param@	height 				height of graph
function displayLineX(svgContainer, height){
	svgContainer.append("line")
			.attr("x1", linearScaleX(positionLine) + marginX/2)
			.attr("y1", 5)
			.attr("x2", linearScaleX(positionLine) + marginX/2)
			.attr("y2", height)
			.attr("stroke-width", 1.5)
			.attr("stroke", "#e41a1c")
			.attr("id", "movingLine")
			.attr("class", "movingLine");
}

//Function, which will change the position of the line in axis graph
//@param 	position 	new position in the graph
function lineX(position){
	//is position out of axis?
	if(position > maxTime){
		position = maxTime;
	} else if((position) < 0){
		position = 0;
	}

	positionLine = position;

	//change position of the line
	d3.select("#movingLine")
		.attr("x1", linearScaleX(positionLine) + marginX/2)
		.attr("x2", linearScaleX(positionLine) + marginX/2);

	getAdditionalData(positionLine);
}

//function will display the main red Y line
//param@	svgContainer		to what container to add the line
//param@	height 				height of graph
function displayLineY(svgContainer, height){
	svgContainer.append("line")
			.attr("x1", 5)
			.attr("y1", linearScaleY(positionLine) + marginX/2)
			.attr("x2", height)
			.attr("y2", linearScaleY(positionLine) + marginX/2)
			.attr("stroke-width", 1.5)
			.attr("stroke", "#e41a1c")
			.attr("id", "movingLine")
			.attr("class", "movingLine");
}

//Function, which will change the position of the line in Y axis graph
//@param 	position 	new position in the graph
//@param 	svgAxis		axisGraph where the line is
function lineY(position){
	//is position out of axis?
	if(position > maxTime){
		position = maxTime;
	}
	else if((position) < 0){
		position = 0;
	}
	positionLine = position;

	//change position of the line
	d3.select("#movingLine")
		.attr("y1", linearScaleY(positionLine) + marginX/2)
		.attr("y2", linearScaleY(positionLine) + marginX/2);

	getAdditionalData(position);
}

//function will create blank svg space
function displayBlock(){
	var svgBlok = d3.select("body").select(".graphBox").append("svg")
									.attr("width", graphBoxWidth)
									.attr("height", 30);
}



/**************************************************************
   						AXES
***************************************************************/

//function will display the main X axis
function displayXAxis(){

	var xScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxWidth - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxWidth - marginX])
							.range([0, maxTime]);

	//SVG for axis
	var svgAxis = d3.select("body").select(".graphBox").append("svg")
									.attr("width", graphBoxWidth)
									.attr("height", 35)
									.attr("class", "svgAxis")
									.on("click", function(){
										lineX(Math.round(lineScaler(d3.mouse(this)[0] - marginX/2 + 2)));
	});

	//check the ticks
	var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}

	//variables for axis
	var xAxis = d3.svg.axis()
					.scale(xScale)
					.orient("bottom")
					.ticks(numberOfTicks);

	//call the 
	svgAxis.append("g").attr("class", "axis")
			.attr("transform", "translate("+ marginX/2 + "," + 5 + ")")
			.call(xAxis);

	axisStyling();	
}

//functin will draw the main X axis for SVG saver
function svgXAxis(){

	var xScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxWidth - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxWidth - marginX])
							.range([0, maxTime]);

	var svgAxis = d3.select(".graphBoxSVG").append("g").attr("class", "axisSVG")
									.attr("width", graphBoxWidth)
									.attr("height", 35)
									.on("click", function(){
										lineX(Math.round(lineScaler(d3.mouse(this)[0] - marginX/2 + 2)));
	});

	var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}

	//variables for axis
	var xAxis = d3.svg.axis()
					.scale(xScale)
					.orient("bottom")
					.ticks(numberOfTicks);

	svgAxis.append("g").attr("class", "axis")
			.attr("transform", "translate("+ marginX/2 + "," + 5 + ")")
			.call(xAxis);

	axisStyling();	
}

//Function will display X axis for each graph 
//param@ 	svgContainer		to what container store the axis
//param@	position 			position in main graph
function displayEverywhereXAxis(svgContainer, position){
	var xScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxWidth - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxWidth - marginX])
							.range([0, maxTime]);

	var svgAxis = svgContainer.append("svg")						
							.attr("class", "xAxis")
							.on("click", function(){
										lineX(Math.round(lineScaler(d3.mouse(this)[0] - marginX/2 + 2)));
							});

	svgAxis.append("rect")
    		.attr("width", graphBoxWidth)
    		.attr("height", 30)
    		.attr("transform", "translate("+ marginX/6 + "," + (5 + position) + ")")
    		.attr("opacity", 0);


    var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}
	
	var xAxis = d3.svg.axis()
					.scale(xScale)
					.orient("bottom")
					.ticks(numberOfTicks);

	svgAxis.append("g")
			.attr("class", "axis")			
			.attr("transform", "translate("+ marginX/2 + "," + (5 + position) + ")")
			.call(xAxis);
	axisStyling();	
}


//Function will display main Y axis of Vertical graph
function displayYAxis(){
	var yScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxHeightVertical - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxHeightVertical - marginX])
							.range([0, maxTime]);

	var svgYAxis = d3.select("body").select(".graphBox").append("svg")
									.attr("width", 35)
									.attr("height", graphBoxHeightVertical)
									.attr("class", "svgYAxis")
									.on("click", function(){
										lineY(Math.round(lineScaler(d3.mouse(this)[1] - marginX/2 + 2)));
	});

	var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}

	var yAxis = d3.svg.axis()
					.scale(yScale)
					.orient("left")
					.ticks(numberOfTicks);

	svgYAxis.append("g").attr("render-order", "1")
			.attr("class", "axis")
			.attr("transform", "translate("+ 30 + "," + marginX/2 + ")")
			.call(yAxis);

	axisStyling();
}

//functin will draw the main Y axis for SVG saver
function svgYAxis(){
	var yScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxHeightVertical - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxHeightVertical - marginX])
							.range([0, maxTime]);

	var svgYAxis = d3.select(".graphBoxSVG").append("g").attr("class", "axisSVG")
									.attr("width", 35)
									.attr("height", graphBoxHeightVertical)
									.on("click", function(){
										lineY(Math.round(lineScaler(d3.mouse(this)[1] - marginX/2 + 2)));
	});

	var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}

	//variables for axis
	var yAxis = d3.svg.axis()
					.scale(yScale)
					.orient("left")
					.ticks(numberOfTicks);

	svgYAxis.append("g").attr("render-order", "1")
			.attr("class", "axis")
			.attr("transform", "translate("+ 30 + "," + marginX/2 + ")")
			.call(yAxis);
	axisStyling();	
}

//Function will display Y axis for each graph 
//param@ 	svgContainer		to what container store the axis
//param@	position 			position in main graph
function displayEverywhereYAxis(svgContainer, position){
	var yScale = d3.scale.linear()
						.domain([0, maxTime])
						.range([0, graphBoxHeightVertical - marginX]);

	var lineScaler = d3.scale.linear()
							.domain([0, graphBoxHeightVertical - marginX])
							.range([0, maxTime]);

	var svgAxis = svgContainer.append("svg").attr("class", "yAxis").on("click", function(){
										lineY(Math.round(lineScaler(d3.mouse(this)[1] - marginX/2 + 2)));
	});

	svgAxis.append("rect")
    		.attr("width", 30)
    		.attr("height", graphBoxHeightVertical)
    		.attr("transform", "translate("+ (position - 20) + "," + 0 + ")")
    		.attr("fill", "white");


    var numberOfTicks = 30;
	if(maxTime < 30){
		numberOfTicks = maxTime;
	}
	
	var yAxis = d3.svg.axis()
					.scale(yScale)
					.orient("left")
					.ticks(numberOfTicks);

	svgAxis.append("g")
			.attr("class", "axis")
			.attr("transform", "translate("+ (5 + position) + "," + marginX/2 + ")")
			.call(yAxis);
	axisStyling();	
}



/**************************************************************
   			HORIZONTAL AND VERTICAL DISPLAY
***************************************************************/

//function will display the cellLineage horizontally
function displayHorizontal(){
	d3.selectAll("svg").remove();
	var m = 0;

	linearScaleX = d3.scale.linear()								//prepare scale for X axis
						.domain([0, maxTime])
						.range([0, graphBoxWidth - marginX]);

	//show only the main axis
	if(!everywhereAxis || smallVisualisation){
		displayXAxis();
	}

	var tmpScaler = false;

	//prepare the height of graph
	var positionInGraphBoxSVG = 35;
	widthOfGraphBox = widthOfGraphBoxSVG()  + positionInGraphBoxSVG;

	//add height of all axes
	if(everywhereAxis && !smallVisualisation){
		widthOfGraphBox += cells.length * 30;
	}

	//svg canvas for all cells
	var graphBoxSVG = d3.select("body").select(".graphBox").append("svg")
										.attr("width",  graphBoxWidth)
										.attr("id", "graphBoxSVG")
										.attr("height", widthOfGraphBox)
										.attr("class", "graphBoxSVG")
										.attr("version", 1.1)
        								.attr("xmlns", "http://www.w3.org/2000/svg");

    //draw axis fro SVG saver and hide it
    svgXAxis();
    disableSVGAxis();


	//blank SVG for positioning
	displayBlock();

	//draw each cell population
	for(m; m < cells.length; m++){

		//check the branching, if its high -> change scale for this cellPopulation to save some space and make it look better
		branching = highestNumberOfChildren([cells[m]]);
		if((branching > 3) ||(cells[m].children.length > 3)){
			tmpScaler = true;
			changeScaleBranch(true);
		}
		if(branching < 2){
			branching = 2;
		}

		//check the depth of population
		var depth = depthFinder(cells[m]);
		
		if(depth < 2){
			depth = 2;
		}

		//height of this cell graph
		var h = (Math.pow(branching,  depth) * scaler) - margin*(depth-1);
		/*
		if(cells[m].children.length == 0){
			if(smallVisualisation){
				h = 10;
			} else{
				h = 45;
			}
		}	*/	

		//preparation of container for this population
		var svgContainer = d3.select("body").select(".graphBoxSVG").append("g").datum(cells[m].id).attr("class", "svgContainer").attr("id", "svgContainer"+cells[m].id);

		//display it!
		displayPopulation(cells[m], (h)/2 + positionInGraphBoxSVG, svgContainer, h/cells[m].children.length, positionInGraphBoxSVG);

		positionInGraphBoxSVG += h;

		//draw axes everywhere		
		if(everywhereAxis && !smallVisualisation){
			displayEverywhereXAxis(svgContainer, positionInGraphBoxSVG);
			positionInGraphBoxSVG += 30;
		}
		//change scalet to normal if it was changed
		if(tmpScaler){
			tmpScaler = false;
			changeScaleBranch(false);
		}

	}
	//show the main red line and hide it if its disabled
	displayLineX(svgContainer, widthOfGraphBox);
	if(!showLine){
		$(".movingLine").toggle(0);
	}

	//hide texts if they are disabled
	if(!showLifeLengthText){
       	$(".lengthOfLifeText").toggle(0);
    }
    if(!showCellId){
		$(".idOfCell").toggle(0);
	}

	//show Graph of States and Graph of Life
	getAdditionalData(positionLine);
}

//Function will display Vertical graph of all cell population 
function displayVertical(){
	d3.selectAll("svg").remove();
	var m = 0;
	linearScaleY = d3.scale.linear()							//scaler for vertical display
						 .domain([0, maxTime])
						 .range([0, graphBoxHeightVertical - marginX]);

	//display main axis
	if(!everywhereAxis || smallVisualisation){
		displayYAxis();
	}	
	var tmpScaler = false;

	//prepare the width of the graph
	var positionInGraphBoxSVG = 35;
	widthOfGraphBox = widthOfGraphBoxSVG()  + positionInGraphBoxSVG;
	if(everywhereAxis && !smallVisualisation){
		widthOfGraphBox += cells.length * 30;
	}

	//create svg
	var graphBoxSVG = d3.select("body").select(".graphBox").append("svg")
										.attr("width", widthOfGraphBox)
										.attr("height", graphBoxHeightVertical)
										.attr("class", "graphBoxSVG")
										.attr("id", "graphBoxSVG")
										.attr("version", 1.1)
        								.attr("xmlns", "http://www.w3.org/2000/svg");

    //draw and than hide the axis for SVG saver
  	svgYAxis();
  	disableSVGAxis();

  	//display all populations
	for(m; m < cells.length; m++){

		//check the branching 
		branching = highestNumberOfChildren([cells[m]]);
		if(branching > 2){
			tmpScaler = true;
			changeScaleBranch(true);
		}
		if(branching < 2){
			branching = 2;
		}

		//check the depth
		var depth = depthFinder(cells[m]);
		if(depth < 3){
			depth = 2;
		}

		//width of this cell graph
		var w = (Math.pow(branching,  depth) * scaler) - margin*(depth-1);			

		/*
		if(cells[m].children.length == 0){
			if(smallVisualisation){
				w = 10;
			} else{
				w = 50;
			}
		}*/

		//create svg container
		var svgContainer = d3.select("body").select(".graphBoxSVG").append("g").datum(cells[m].id);
		if(everywhereAxis && !smallVisualisation){
			displayEverywhereYAxis(svgContainer, positionInGraphBoxSVG);

		}

		//display the population
		displayPopulation(cells[m], (w)/2 + positionInGraphBoxSVG, svgContainer, w/cells[m].children.length, positionInGraphBoxSVG);
		positionInGraphBoxSVG += w;

		if(everywhereAxis && !smallVisualisation){
			positionInGraphBoxSVG += 30;
		}

		//change scaler to normal if it was changed
		if(tmpScaler){
			tmpScaler = false;
			changeScaleBranch(false);
		}

	}
	
	//display main Y line
	displayLineY(svgContainer, widthOfGraphBox);
	
	//hide elements if they are disabled
	if(!showLine){
		$(".movingLine").toggle(0);
	}
	if(!showLifeLengthText){
       	$(".lengthOfLifeText").toggle(0);
    }
    if(!showCellId){
		$(".idOfCell").toggle(0);
	}

	//display graph of life and states
	getAdditionalData(positionLine);
}

//Function will display all elements of CellLineage Graph
//@param	cell 	 				actual displaying cell
//@param	positionY				where to place the elements in the main graph (horizontal: where on y; vertical: where on x)
//@param	container 				in which container to store all elements
//@param 	repairer				width/height of place for children
//@param 	positionInGraphBoxSVG	position of begining of this cell in main graph
function displayPopulation(cell, positionY, container, repairer, positionInGraphBoxSVG){
	//container for one cell
	var superCell = container.append("g").classed("superCell", true).datum([cell.begin, cell.end]);		
	var tmpPosition = positionInGraphBoxSVG;
	displayBeginToEndLine(cell, superCell, positionY);

    if(!smallVisualisation && (cell.begin >= showFrom) && (cell.end <= showTo)){
       	displayLengthOfLife(cell, superCell, positionY);       	
	}

	if((cell.end != cell.begin) && (cell.begin >= showFrom)){
		displayBegin(cell, superCell, positionY);
	}

	if(!smallVisualisation && (cell.begin == showFrom || showFrom != showTo)){
		displayIdOfCell(cell, superCell, positionY);
		
   	}

   	tmpPosition += repairer/2;

   	if(cell.children.length != 0){			//cell has children -> draw them before continuing
   		var i = 0;
   		
   		if(cell.children.length == 1){
   			connectParentChild(positionY, cell, superCell, tmpPosition - repairer/4, cell.children[i]);
   			displayPopulation(cell.children[i], tmpPosition - repairer/4, container, (repairer/cell.children[i].children.length), tmpPosition - repairer/2);
   			tmpPosition = tmpPosition + repairer;
   		} else{
   			
   			for(i; i < cell.children.length; i++){
   				connectParentChild(positionY, cell, superCell, tmpPosition, cell.children[i]);
   				displayPopulation(cell.children[i], tmpPosition, container, (repairer/cell.children[i].children.length), tmpPosition - repairer/2);
   				tmpPosition = tmpPosition + repairer;
   			}
   		}  		
		if(cell.end != cell.begin && (cell.end <=showTo)){
			displayMitosis(cell, superCell, positionY);
		}
	} else{
		tmpPosition += repairer;		
	  	if((cell.end != maxTime) && (cell.end != cell.begin) && (cell.end <= showTo)){
	  		if(cell.hasChildren){
	  			displayMitosis(cell, superCell, positionY);
	  		} else{
	  			if(cell.end <= showTo){
   					displayEnd(cell, superCell, positionY);
   				}
   			}
		}
   	}

   	if(cell.end == cell.begin){
   		displayBothBeginEnd(cell, superCell, positionY);
   	}
}


//function will chceck the highest number of division in the array of cells
//param 	cellArray		array of cells
function highestNumberOfChildren(cellArray){
	var highestNumber = cellArray[0].children.length;
	var i = 0;
	for(i; i < cellArray.length; i++){
		if(highestNumber < cellArray[i].children.length){
			highestNumber = cellArray[i].children.length;
		}
		if(cellArray[i].children.length != 0){
			var highestOfChildren = highestNumberOfChildren(cellArray[i].children);
			if(highestNumber < highestOfChildren){
				highestNumber = highestOfChildren;
			}
		}
	}
	return highestNumber;
}

//Function will find the deph of the population 
//@param 	cell 	root cell of population
function depthFinder(cell){
	if(cell.children.length != 0){						//it has children
		var a = depthFinder(cell.children[0]);
		var i = 1;

		//go through all its children
		for(i; i < cell.children.length; i++){
			var b = depthFinder(cell.children[i]);
			if(a < b){
				a = b;
			}
		}
		return 1 + a;
	}	
	return 1;	
}

//function will change the scale of drawing
//@param 	value 			indicates to which scaler to change
function changeScaleBranch(value){
	if(value){
		if(smallVisualisation){
			scaler = 3;
		} else{
		scaler = 10;
		}
	} else{
		if(smallVisualisation){
			scaler = 10;
		} else{
		scaler = 50;
		}
	}
}

//Function will count the width of GraphBoxSVG
//@return	result		counted width
function widthOfGraphBoxSVG(){
	var i = 0;
	var result = 0;
	var tmpScaler = false;
	//adding width of every graph to the result
	for(i; i < cells.length; i++){
		
			branching = highestNumberOfChildren([cells[i]]);
			if(branching < 2){
				branching = 2;
			}
			var tmpDepth = depthFinder(cells[i]);
			if(tmpDepth < 3){
				tmpDepth = 2;
			}
			if(branching > 3){
				tmpScaler = true;
				changeScaleBranch(true);
			}
			result += Math.pow(branching,  tmpDepth) * scaler - scaler*(tmpDepth-1);
			if(tmpScaler){
				tmpScaler = false;
				changeScaleBranch(false);
			}
		
	}
	return result;
}

//function will apply css styles for axes
function axisStyling(){
	d3.selectAll(".axis text").attr("font-family", "sans-serif").attr("font-size", "12px");
	d3.selectAll(".axis path").attr("stroke", "black").attr("fill", "none").attr("shape-rendering", "crispEdges");
	d3.selectAll(".axis line").attr("stroke", "black").attr("fill", "none").attr("shape-rendering", "crispEdges");
}

//Function will get the text list of children of the cell
//@parent 	parent of the children
//@return	text of children
function getChildrenText(parent){
	if(parent.children.length != 0){
		var text = "" + parent.children[0].id + "";
		var i = 1;
		for(i; i < parent.children.length; i++){
			text += ", " + parent.children[i].id;
		}
		return text;	
	}
	return "None";
}

/**************************************************************
   GRAPH OF STATES + LIFE GRAPH
***************************************************************/

//Function will get info about all cells in certain time and show the graph of states and graph of lives of living cells
//@param 	position 	in what time we want to the info
function getAdditionalData(position){
	begin = 0;
	mitosis = 0;
	death = 0;
	var c = 0;

	while(lifeGraphCells.length > 0){
		lifeGraphCells.pop();
	}

	//we will chceck all cells and get the data
	for(c; c < cells.length; c++){
		checkCell(cells[c], position);
	}

	var dataStates = [begin, death, mitosis, lifeGraphCells.length];		//info about possible states\

	document.getElementById("interestingInfoText").innerHTML = interestingInfoText + positionLine +  " ";

	d3.selectAll(".stats").remove();

	//creating svg of graph of states
	var life = d3.select("body").select(".interestingInfo").append("svg")
					.attr("width", 350)
					.attr("height", 105)
					.attr("class", "stats")
					.attr("id", "stat");

	//display bars of states
	for(var i = 0; i < 4; i++){
		life.append("rect")
			.attr("x", 25 + margLife + posunuti)
			.attr("y", (i * 25) + 5 )
			.attr("width", 5 * dataStates[i])
			.attr("height", 20)
			.attr("fill", colors[i])

		life.append("text")
				.text(dataStates[i])
				.attr("x", posunuti + margLife)
				.attr("y", (i * 25) + 20)
				.attr("font-family", "sans-serif")
				.attr("font-size", 15)
				.attr("fill", "black");

		life.append("text")
				.text(description[i])
				.attr("x", 5)
				.attr("y", (i * 25) + 20 )
				.attr("font-family", "sans-serif")
				.attr("font-size", 15)
				.attr("fill", "black");
	}

	//Display life Graph of living cells
	d3.select('#deleteLife').remove();
	if(lifeGraphCells.length != 0){
		displayLifeGraph();
	}
}

//Function will display life graph of living cells in certain time
function displayLifeGraph(){
	var c = 0;
	var lifeLinearX = d3.scale.linear().domain([0, maxTime]).range([0, 310]);

	sortByIdSmth(lifeGraphCells);

	var lifeHeight = lifeGraphCells.length*20 + 20;

	var lifeGraph = d3.select("body").select(".lifeGraph").append("svg")
						.attr("width", 430)
						.attr("height",  lifeHeight)
						.attr("class", "lifeGraphg")
						.attr("id", "deleteLife");

	//we will display life of every living cell (array of lifeGraphCells)
	for(c; c < lifeGraphCells.length; c++){
		var lifeContainer = lifeGraph.append("g").attr("class", "cellLife");

		var idText = lifeContainer.append("text")
										.text(lifeGraphCells[c].id + ": ")
										.attr("x", 5)
			   							.attr("y", c * 20 + 25)
			   							.attr("font-family", "sans-serif")
   										.attr("font-size", textHeight[activeFontText]);

		var lifeLine = lifeContainer.append("line")
						.attr("x1", function(){
							return lifeLinearX(lifeGraphCells[c].begin) + 20 + margLife;
						})
						.attr("y1", function(){
							return c * 20 + 20;
						})
						.attr("x2", function(){
							return lifeLinearX(lifeGraphCells[c].end) +20 + margLife;
						})
						.attr("y2", function(){
							return c * 20 + 20;
						})
						.attr("stroke-width", 1)
						.attr("stroke", "black");

		var lifeBegin = lifeContainer.append("line")
						.attr("x1",function(){
							return lifeLinearX(lifeGraphCells[c].begin) + 20 + margLife;
						})
						.attr("y1", function(){
							return c * 20 + 15;
						})
						.attr("x2",function(){
							return lifeLinearX(lifeGraphCells[c].begin) + 20 + margLife;
						})
						.attr("y2", function(){
							return c * 20 + 25;
						})
						.attr("stroke-width", 1)
						.attr("stroke", "black");

		var lifeBeginText = lifeContainer.append("text")
										.text(lifeGraphCells[c].begin)
										.attr("x", lifeLinearX(lifeGraphCells[c].begin) - 10 + margLife)
			   							.attr("y", c * 20 + 25)
			   							.attr("font-family", "sans-serif")
   										.attr("font-size", textHeight[activeFontText]);

		var lifeEnd = lifeContainer.append("line")
						.attr("x1",function(){
							return lifeLinearX(lifeGraphCells[c].end) +20 + margLife;
						})
						.attr("y1", function(){
							return c * 20 + 15;
						})
						.attr("x2",function(){
							return lifeLinearX(lifeGraphCells[c].end) +20 + margLife;
						})
						.attr("y2", function(){
							return c * 20 + 25;
						})
						.attr("stroke-width", 1)
						.attr("stroke", "black");

		var lifeEndText = lifeContainer.append("text")
										.text(lifeGraphCells[c].end)
										.attr("x", lifeLinearX(lifeGraphCells[c].end) + 25 + margLife)
			   							.attr("y", c * 20 + 25)
			   							.attr("font-family", "sans-serif")
   										.attr("font-size", textHeight[activeFontText]);
	}

	var wholeLine = lifeContainer.append("line")
							.attr("x1", function(){
								return lifeLinearX(positionLine) + 20 + margLife;
							})
							.attr("y", function(){return 0;})
							.attr("x2", function(){return lifeLinearX(positionLine) + 20 + margLife;})
							.attr("y2", function(){return 1200;})
							.attr("stroke-width", 1)
							.attr("stroke", "#e41a1c");
}

//Function will save info about cell in certain time
//@param	cell 		cell we want to know info about
//@param	position 	in what time we want to know what is happening
function checkCell(cell, position){
	//was cell born?
	if(cell.begin == position && (cell.begin >= showFrom && cell.begin <= showTo)){
			begin++;
	}

	//Or was it its death or mitosis?
	if((cell.end == position) && (cell.end != maxTime) && (cell.end >= showFrom && cell.end <= showTo)){
		if(cell.children.length > 0){
			mitosis++;
		}
		else{
			death++;
		}
	}

	//or was it alive?
	else if(((position > cell.begin) && (position < cell.end)) || ((cell.end == position) && (cell.end == maxTime))){
		if(position >= showFrom && position <= showTo){
			lifeGraphCells.push(cell);
		}
	}


	//check what happend to its children
	else{
		if((cell.children.length > 0) && (position > cell.end)){
			var d = 0;
			for(d; d<cell.children.length; d++){
				checkCell(cell.children[d], position);
			}
		}
	}
}



/**************************************************************
   OTHER FUNCTIONS
***************************************************************/
function enableAllButtons(){
	$('button').prop('disabled', false);
}

function disableButtons(){
	$("#disable").prop('disabled', true);
	$("#svgSaver").prop('disabled', true);
	$("#fontchanger").prop('disabled', true);
	$("#sortcells").prop('disabled', true);
	$("#displayOptions").prop('disabled', true);
}

function disableSVGAxis(){
	$(".axisSVG").toggle();
}

//Dialogs 
function showWarningDialog(){
	$( "#warningDialog" ).dialog({
      resizable: false,
      width:500,
      height:230,
      modal: true,
      buttons: {
        "Close": function() {
          $( this ).dialog( "close" );
        }
      }
    });
}

function showDivisionDialog(){
	$( "#divisionDialog" ).dialog({
      resizable: false,
      width:500,
      height:250,
      modal: true,
      buttons: {
        "Close": function() {
          $( this ).dialog( "close" );
        }
      }
    });
}