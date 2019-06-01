



function バウンド化() {
	function 色域赤() {
		// =======================================================
		var idClrR = charIDToTypeID("ClrR");
		var desc15 = new ActionDescriptor();
		var idFzns = charIDToTypeID("Fzns");
		desc15.putInteger(idFzns, 200);
		var idMnm = charIDToTypeID("Mnm ");
		var desc16 = new ActionDescriptor();
		var idLmnc = charIDToTypeID("Lmnc");
		desc16.putDouble(idLmnc, 54.290000);
		var idA = charIDToTypeID("A   ");
		desc16.putDouble(idA, 80.800000);
		var idB = charIDToTypeID("B   ");
		desc16.putDouble(idB, 69.900000);
		var idLbCl = charIDToTypeID("LbCl");
		desc15.putObject(idMnm, idLbCl, desc16);
		var idMxm = charIDToTypeID("Mxm ");
		var desc17 = new ActionDescriptor();
		var idLmnc = charIDToTypeID("Lmnc");
		desc17.putDouble(idLmnc, 54.290000);
		var idA = charIDToTypeID("A   ");
		desc17.putDouble(idA, 80.800000);
		var idB = charIDToTypeID("B   ");
		desc17.putDouble(idB, 69.900000);
		var idLbCl = charIDToTypeID("LbCl");
		desc15.putObject(idMxm, idLbCl, desc17);
		var idcolorModel = stringIDToTypeID("colorModel");
		desc15.putInteger(idcolorModel, 0);
		executeAction(idClrR, desc15, DialogModes.NO);

	}

	function 塗りつぶし() {
		// =======================================================
		var idFl = charIDToTypeID("Fl  ");
		var desc111 = new ActionDescriptor();
		var idUsng = charIDToTypeID("Usng");
		var idFlCn = charIDToTypeID("FlCn");
		var idFrgC = charIDToTypeID("FrgC");
		desc111.putEnumerated(idUsng, idFlCn, idFrgC);
		var idOpct = charIDToTypeID("Opct");
		var idPrc = charIDToTypeID("#Prc");
		desc111.putUnitDouble(idOpct, idPrc, 100.000000);
		var idMd = charIDToTypeID("Md  ");
		var idBlnM = charIDToTypeID("BlnM");
		var idNrml = charIDToTypeID("Nrml");
		desc111.putEnumerated(idMd, idBlnM, idNrml);
		executeAction(idFl, desc111, DialogModes.NO);

	}


	function 選択解除() {
		// =======================================================
		var idsetd = charIDToTypeID("setd");
		var desc26 = new ActionDescriptor();
		var idnull = charIDToTypeID("null");
		var ref12 = new ActionReference();
		var idChnl = charIDToTypeID("Chnl");
		var idfsel = charIDToTypeID("fsel");
		ref12.putProperty(idChnl, idfsel);
		desc26.putReference(idnull, ref12);
		var idT = charIDToTypeID("T   ");
		var idOrdn = charIDToTypeID("Ordn");
		var idNone = charIDToTypeID("None");
		desc26.putEnumerated(idT, idOrdn, idNone);
		executeAction(idsetd, desc26, DialogModes.NO);


	}

	for (var n = 0; n < activeDocument.layers.length; n++) {
		layer = activeDocument.layers[n];
		if (layer != activeDocument.activeLayer) {
			layer.visible = false
		}
	}

	色域赤()
	b = activeDocument.selection.bounds
	x1 = Number(b[0]);
	y1 = Number(b[1]);
	x2 = Number(b[2]);
	y2 = Number(b[3]);
	selReg = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
	activeDocument.selection.select(selReg)
	塗りつぶし()
	選択解除()

	for (var n = 0; n < activeDocument.layers.length; n++) {
		activeDocument.layers[n].visible = true;
	}
}

function 上のレイヤーを選択() {
	// =======================================================
	var idslct = charIDToTypeID("slct");
	var desc1071 = new ActionDescriptor();
	var idnull = charIDToTypeID("null");
	var ref148 = new ActionReference();
	var idLyr = charIDToTypeID("Lyr ");
	var idOrdn = charIDToTypeID("Ordn");
	var idFrwr = charIDToTypeID("Frwr");
	ref148.putEnumerated(idLyr, idOrdn, idFrwr);
	desc1071.putReference(idnull, ref148);
	var idMkVs = charIDToTypeID("MkVs");
	desc1071.putBoolean(idMkVs, false);
	var idLyrI = charIDToTypeID("LyrI");
	var list58 = new ActionList();
	list58.putInteger(389);
	desc1071.putList(idLyrI, list58);
	executeAction(idslct, desc1071, DialogModes.NO);
}

function active() {
    return activeDocument.activeLayer
}
function 全コマバウンド化() {
	//レイヤー1を選択
	// =======================================================
	var idslct = charIDToTypeID("slct");
	var desc107 = new ActionDescriptor();
	var idnull = charIDToTypeID("null");
	var ref36 = new ActionReference();
	var idLyr = charIDToTypeID("Lyr ");
	ref36.putName(idLyr, "レイヤー 1");
	desc107.putReference(idnull, ref36);
	var idMkVs = charIDToTypeID("MkVs");
	desc107.putBoolean(idMkVs, false);
	var idLyrI = charIDToTypeID("LyrI");
	var list3 = new ActionList();
	list3.putInteger(4);
	desc107.putList(idLyrI, list3);
	executeAction(idslct, desc107, DialogModes.NO);

	for (var i = 0; i < activeDocument.layers.length; i++) {
		if ((active().name == "レイヤー 0")||(active().name == "背景")) {
			break
		}
		バウンド化()
		上のレイヤーを選択()
	}

	for (var n = 0; n < activeDocument.layers.length; n++) {
		activeDocument.layers[n].visible = true;
	}
}


全コマバウンド化()