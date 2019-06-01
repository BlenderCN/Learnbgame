/*
メモ
フォルダ
フォルダ＝LayerSet
Document.layerSets[0].artLayers....
				    [0].layerSets

・レイヤー入れ替えるとその瞬間から元の配列番号でアクセスできないから注意
・JSは明示しないとローカル変数にならない！クソ仕様。


*/

/*

	同フォルダ内の画像を収集・整列する。
	../koma/内の情報を利用してコママスクを切る。（コマ分け.jsxにて生成）
	forwardが名前の中にある場合一番上のひとつ下＝下絵の下にもってくる。
*/



//開いてるドキュメント分実行
var repeat = documents.length
for (var d = 0; d < repeat; d++) {
    if (activeDocument.name != "レンダ読み込み.psd") {
        continue
    }

	exec();
	//保存して閉じる
	activeDocument.save();
	activeDocument.close(SaveOptions.SAVECHANGES);
}




function exec(){
	//リフレッシュ処理
	//統合
	var idFltI = charIDToTypeID( "FltI" );
	executeAction( idFltI, undefined, DialogModes.NO );
	
	layers = activeDocument.artLayers;
	//レイヤー1の作成
	layers.add();
	
	//レイヤーの除去
	for(var n = 0; n < layers.length; n++){
		layer = layers[n];
		if(layer.name != "レイヤー 1"){
			layer.remove();
			n--;
		}
	}
	
	
	
	
	//まず現在のドキュメントの名前確保
	var basedoc = activeDocument;
	
	if(basedoc){
		//表示名、フィルタ、マルチの有無　->ファイルパスが配列でかえる。
		//openPath = new File(activeDocument.path);
		//filename = openPath.openDlg("挿入する画像の選択","*.png",true);
		openPath = new Folder(activeDocument.path);
		filename = openPath.getFiles("*.png");
		
		//ファイルをソート
		//filename = filename.sort().reverse();
		filename = filename.sort();
		
		//ファイルの読み込み
		if (filename.length != 0) {
			//パス文字列がなくなるまでループ
			for(i = 0; i < 256; i++){
				//特定のファイルをスキップ
				if(String(filename[i]).match("untitled") != null){continue;}
				if(String(filename[i]).match("page_") != null){continue;}
				
				img = loadimg(filename[i])
				if(img == false){break;}
			}
		}
	}
	
	
	//レイヤーの除去
	layers = activeDocument.artLayers;
	//一枚しかなかったら消せないので飛ばす
	if(layers.length != 1){
		for(var n = 0; n < layers.length; n++){
			layer = layers[n];
			if(layer.name == "レイヤー 1"){layer.remove();}
		}
	}
	
	/*
		フォルダを選択するとpngを一枚開いて、
		そこにどんどんフォルダ内のファイルを読み込み
		フォルダ構成いじったり、_allを一つのフォルダにまとめて非表示にしたりして
		unite.psdみたいな名前で保存する
		
		
		ってよくよく考えたらここまでは既存のでやってこっから処理したほうがいいのでは
		
	*/
	
	layers = activeDocument.artLayers;
	folders = new Array();
	//フォルダ作成
	//makefolder("");
//	キャラ3D = makefolder(activeDocument,"キャラ3D");

	//フォルダ作成
	for(var n = 0; n < layers.length;n++){
		var layer = layers[n];
		//名前の分解
		//num = layer.name.split("_")[0];
		numbase = layer.name.split("_");
		num = numbase[0];
		if(numbase[1] != null){
			num += "_"+numbase[1];
		}

		var found = false;
		for(var i = 0; i < folders.length;i++){
			folder = folders[i];
			if(folder.name == num){
				found = true;
				break;
			}
		}
		if(!found){
			//リストになかったのでフォルダーを作成する
			folderObj = activeDocument.layerSets.add();
			folderObj.name = num;
			folders.push(folderObj);
		}
	}
	//一番上を乗算にする
	//乗算();

	//下地の対象をどれにするか
	var 下地ターゲット = "_solid"
	for(var n = 0; n < layers.length;n++){
		layer = layers[n];
		var tmptargetname = ""
		tmptargetname = "_solid"
		if(layer.name.match(tmptargetname) != null){
			下地ターゲット = tmptargetname;
			break;
		}
		tmptargetname = "_flatcolor"
		if(layer.name.match(tmptargetname) != null){
			下地ターゲット = tmptargetname;
			break;
		}
		tmptargetname = "_shadow"
		if(layer.name.match(tmptargetname) != null){
			下地ターゲット = tmptargetname;
			break;
		}
	}

	//レイヤーの移動
	for(var n = 0; n < layers.length;n++){
		layer = layers[n];
		numbase = layer.name.split("_");
		num = numbase[0];
		if(numbase[1] != null){
			num += "_"+numbase[1];
		}

		for(var i = 0; i < folders.length;i++){
			folder = folders[i];
			if(folder.name == num){
				if(layer.name.match(下地ターゲット ) != null){
					dup = layer.duplicate();
					activeDocument.activeLayer = dup;
					dup.move(folder,ElementPlacement.PLACEATEND);
					//下地
					dup = layer;
					dup.name += "下地"
					activeDocument.activeLayer = dup;
					レベル補正白();
					マージ();
					dup.move(folder,ElementPlacement.PLACEATEND);
					n--;
				}else{
					layer.move(folder,ElementPlacement.PLACEATBEGINNING);
					n--;
				}
				if(layer.name.match("_materials") != null){
					layer.visible = false;
				}

				break;
			}
		}
	}


	/*
		再びコマの移動
		
		コマごとにフォルダ分け。
		
	*/
	//元フォルダの回収
	basefolderslist = new Array()
	basenumlist = new Array()
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 folder = activeDocument.layerSets[n];
		 
		 //名前からコマ数を取得する
		 num = folder.name.split("_")[0].match(/\d+/i)
		 if(num != null){
			 basenumlist.push(num)
			 basefolderslist.push(folder)
		 }
	}
	//重複削除
	numlist = new Array()
	for(var n = 0; n < basenumlist.length; n++){
		num = basenumlist[n];
		
		var found = false
		for(var i = 0; i < numlist.length; i++){
			if(""+num == ""+numlist[i]){
				found = true
				break
			}
		}
		if(found == false){
			numlist.push(num)
		}
	}
	
	
//	alert(numlist.join())
	numlist.reverse()
	for(var n = 0; n < numlist.length; n++){
		num = numlist[n];
		//コマフォルダ作成
		makefolder(activeDocument,"コマ"+num)
	}
	
	
	
	
//	for(var n = 0; n < basefolderslist.length; n++){
//		folder = basefolderslist[n];
	targetnames = new Array
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		folder = activeDocument.layerSets[n];
		if(folder.name.match(/コマ/)!=null){continue}
		if(folder == undefined){continue}
		if(folder == null){continue}
//		alert(folder.name)
		 num = folder.name.split("_")[0].match(/\d+/i)
//		alert(folder.name+":"+num)
		 if(num != null){
		 	targetnames.push(folder.name)
//			komafolder = getfolderobj("コマ"+num)
////			alert(komafolder.typename)
//			if(komafolder != null){
				
//				moveLayerSet(folder,komafolder)
//			 	alert(folder.name + "/" + num + ":" + komafolder.name)
//				activeDocument.activeLayer = folder;
//				folder.moveAfter(komafolder)
//				activeDocument.activeLayer = folder;
//				前面()

//				folder.move(komafolder, ElementPlacement.INSIDE)

//				moveLayerSet( folder, komafolder) 
//				folder.moveToEnd(komafolder)
//activeDocument.layers[0].moveToEnd(komafolder)
//				layer = komafolder.artLayers.add()
//				activeDocument.activeLayer = komafolder;
//				folder.move(komafolder, ElementPlacement.INSIDE)
//				folder.moveAfter(layer)
//				folder.move(komafolder.layerSets, ElementPlacement.INSIDE)
//				activeDocument.layerSets[2].move(activeDocument.layerSets[0],ElementPlacement.PLACEATEND)
//				folder.moveToEnd(komafolder)
//			}
		 }
	}
//	alert(targetnames.join())
	for(var n = 0; n < targetnames.length; n++){
		folder = getfolderobj(targetnames[n]);
		num = folder.name.split("_")[0].match(/\d+/i)
		if(num != null){
			komafolder = getfolderobj("コマ"+num)
			if(komafolder != null){
//				alert(folder.name+":"+komafolder.name)
				movebyname(folder,komafolder)
			}
		}
	}

	
	
//	komalist = new Array()
//	for(var num in numlist){
//		komalist.push(makefolder(activeDocument,"コマ"+num))
//	}
//	
	//フォルダの移動
	
	
	
	ベタ塗り("背景")
	ラスタライズ()
	マスク適用()
	最背面()
	最背面()
	最背面()
	最背面()
	
	//背景ロード
	docpath =new String( activeDocument.path)
	parent_dir = docpath.replace(new String(activeDocument.path.name),"")
	if(loadimg(parent_dir+"background.png") != false){
		最前面()
		最前面()
		乗算()
	}
	
//	不透明度(30)
	komamask()
	
	/*
		例外処理
		フォルダ名にforwardって入ってたら一番上にもってくるべき。
	*/
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerSets = activeDocument.layerSets[i];
		for(var j = 0; j < layerSets.layerSets.length; j++){
			var subSets = layerSets.layerSets[j];
			if(subSets.name.match("forward") != null){
				activeDocument.activeLayer = subSets
				最前面()
				最前面()
				最前面()
				最前面()
				最前面()
				最前面()
				背面()
			}
		}
	}
	
	
	
	
	/*後付カスタム処理*/
	
	後付カスタム処理()
	
	
	
}

function komamask(){
	/*
	コマにマスクかける処理
	*/
	komafolder = new Folder(activeDocument.path+"/../koma/")
	if(komafolder.exists){
		//コマフォルダがあった
		for(var n = 0; n < activeDocument.layerSets.length; n++){
			 layerset = activeDocument.layerSets[n];
			 if(layerset.name.match("コマ") != null){
			 	var komafilepath = komafolder.absoluteURI + "/" + layerset.name.replace("コマ", "") + ".png"
			 	hideall()
			 	loadimg(komafilepath)
			 	色域赤()
			 	activeDocument.activeLayer.remove()
			 	showall()
			 	activeDocument.activeLayer = layerset
			 	マスク作製()
			 	選択解除()
			 }
		}
	}
}
































function makefolder(folder,name){
	folderObj = folder.layerSets.add();
	folderObj.name = name;
	folders.push(folderObj);
	return folderObj;
}

function getfolderobj(name){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		var folder = activeDocument.layerSets[n];
		if(folder.name == name){return folder}
	}

//	for(var n = 0; n < folders.length; n++){
//		folder = folders[n];
//		if(folder.name.match(name) != null){
//			return folder;
//		}
//	}

	return null;
}


function レベル補正白(){
			//レベル補正　真っ白に（下地用）
			// =======================================================
			var idMk = charIDToTypeID( "Mk  " );
			    var desc45 = new ActionDescriptor();
			    var idnull = charIDToTypeID( "null" );
			        var ref40 = new ActionReference();
			        var idAdjL = charIDToTypeID( "AdjL" );
			        ref40.putClass( idAdjL );
			    desc45.putReference( idnull, ref40 );
			    var idUsng = charIDToTypeID( "Usng" );
			        var desc46 = new ActionDescriptor();
			        var idType = charIDToTypeID( "Type" );
			            var desc47 = new ActionDescriptor();
			            var idpresetKind = stringIDToTypeID( "presetKind" );
			            var idpresetKindType = stringIDToTypeID( "presetKindType" );
			            var idpresetKindDefault = stringIDToTypeID( "presetKindDefault" );
			            desc47.putEnumerated( idpresetKind, idpresetKindType, idpresetKindDefault );
			        var idLvls = charIDToTypeID( "Lvls" );
			        desc46.putObject( idType, idLvls, desc47 );
			    var idAdjL = charIDToTypeID( "AdjL" );
			    desc45.putObject( idUsng, idAdjL, desc46 );
			executeAction( idMk, desc45, DialogModes.NO );
			
			// =======================================================
			var idsetd = charIDToTypeID( "setd" );
			    var desc48 = new ActionDescriptor();
			    var idnull = charIDToTypeID( "null" );
			        var ref41 = new ActionReference();
			        var idAdjL = charIDToTypeID( "AdjL" );
			        var idOrdn = charIDToTypeID( "Ordn" );
			        var idTrgt = charIDToTypeID( "Trgt" );
			        ref41.putEnumerated( idAdjL, idOrdn, idTrgt );
			    desc48.putReference( idnull, ref41 );
			    var idT = charIDToTypeID( "T   " );
			        var desc49 = new ActionDescriptor();
			        var idpresetKind = stringIDToTypeID( "presetKind" );
			        var idpresetKindType = stringIDToTypeID( "presetKindType" );
			        var idpresetKindCustom = stringIDToTypeID( "presetKindCustom" );
			        desc49.putEnumerated( idpresetKind, idpresetKindType, idpresetKindCustom );
			        var idAdjs = charIDToTypeID( "Adjs" );
			            var list16 = new ActionList();
			                var desc50 = new ActionDescriptor();
			                var idChnl = charIDToTypeID( "Chnl" );
			                    var ref42 = new ActionReference();
			                    var idChnl = charIDToTypeID( "Chnl" );
			                    var idChnl = charIDToTypeID( "Chnl" );
			                    var idCmps = charIDToTypeID( "Cmps" );
			                    ref42.putEnumerated( idChnl, idChnl, idCmps );
			                desc50.putReference( idChnl, ref42 );
			                var idInpt = charIDToTypeID( "Inpt" );
			                    var list17 = new ActionList();
			                    list17.putInteger( 253 );
			                    list17.putInteger( 255 );
			                desc50.putList( idInpt, list17 );
			                var idOtpt = charIDToTypeID( "Otpt" );
			                    var list18 = new ActionList();
			                    list18.putInteger( 255 );
			                    list18.putInteger( 255 );
			                desc50.putList( idOtpt, list18 );
			            var idLvlA = charIDToTypeID( "LvlA" );
			            list16.putObject( idLvlA, desc50 );
			        desc49.putList( idAdjs, list16 );
			    var idLvls = charIDToTypeID( "Lvls" );
			    desc48.putObject( idT, idLvls, desc49 );
			executeAction( idsetd, desc48, DialogModes.NO );

}

function マージ(){
			//マージ
			// =======================================================
			var idMrgtwo = charIDToTypeID( "Mrg2" );
			    var desc31 = new ActionDescriptor();
			executeAction( idMrgtwo, desc31, DialogModes.NO );

}

function 二値化(level){
	var idMk = charIDToTypeID( "Mk  " );
	    var desc81 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref71 = new ActionReference();
	        var idAdjL = charIDToTypeID( "AdjL" );
	        ref71.putClass( idAdjL );
	    desc81.putReference( idnull, ref71 );
	    var idUsng = charIDToTypeID( "Usng" );
	        var desc82 = new ActionDescriptor();
	        var idType = charIDToTypeID( "Type" );
	            var desc83 = new ActionDescriptor();
	            var idLvl = charIDToTypeID( "Lvl " );
	            desc83.putInteger( idLvl, level );
	        var idThrs = charIDToTypeID( "Thrs" );
	        desc82.putObject( idType, idThrs, desc83 );
	    var idAdjL = charIDToTypeID( "AdjL" );
	    desc81.putObject( idUsng, idAdjL, desc82 );
	executeAction( idMk, desc81, DialogModes.NO );
}

function クリッピングマスク(){
	var idGrpL = charIDToTypeID( "GrpL" );
	    var desc84 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref72 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref72.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc84.putReference( idnull, ref72 );
	executeAction( idGrpL, desc84, DialogModes.NO );
}


//https://forums.adobe.com/thread/925247
function moveLayerSet( fromLayer, toLayer ){// layerSet objects  
    var desc = new ActionDescriptor();  
        var sourceRef = new ActionReference();  
        sourceRef.putName( charIDToTypeID( "Lyr " ), fromLayer.name );  
    desc.putReference( charIDToTypeID( "null" ), sourceRef );  
            var indexRef = new ActionReference();  
            indexRef.putName( charIDToTypeID("Lyr "), toLayer.name );  
            var layerIndex = executeActionGet(indexRef).getInteger(stringIDToTypeID('itemIndex'));  
        var destinationRef = new ActionReference();  
        destinationRef.putIndex( charIDToTypeID( "Lyr " ), layerIndex-1 );  
    desc.putReference( charIDToTypeID( "T   " ), destinationRef );  
    desc.putBoolean( charIDToTypeID( "Adjs" ), false );  
    desc.putInteger( charIDToTypeID( "Vrsn" ), 5 );  
    executeAction( charIDToTypeID( "move" ), desc, DialogModes.NO );  
}  


function 乗算(){
	// =======================================================
	var idsetd = charIDToTypeID( "setd" );
	    var desc2 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref1 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref1.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc2.putReference( idnull, ref1 );
	    var idT = charIDToTypeID( "T   " );
	        var desc3 = new ActionDescriptor();
	        var idMd = charIDToTypeID( "Md  " );
	        var idBlnM = charIDToTypeID( "BlnM" );
	        var idMltp = charIDToTypeID( "Mltp" );
	        desc3.putEnumerated( idMd, idBlnM, idMltp );
	    var idLyr = charIDToTypeID( "Lyr " );
	    desc2.putObject( idT, idLyr, desc3 );
	executeAction( idsetd, desc2, DialogModes.NO );
}

function ラスタライズ(){
// =======================================================
var idrasterizeLayer = stringIDToTypeID( "rasterizeLayer" );
    var desc17 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref6 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref6.putEnumerated( idLyr, idOrdn, idTrgt );
    desc17.putReference( idnull, ref6 );
executeAction( idrasterizeLayer, desc17, DialogModes.NO );
}

function マスク適用(){
	// =======================================================
	var idDlt = charIDToTypeID( "Dlt " );
	    var desc18 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref7 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idMsk = charIDToTypeID( "Msk " );
	        ref7.putEnumerated( idChnl, idChnl, idMsk );
	    desc18.putReference( idnull, ref7 );
	    var idAply = charIDToTypeID( "Aply" );
	    desc18.putBoolean( idAply, true );
	executeAction( idDlt, desc18, DialogModes.NO );
}

function ベタ塗り(layername){
	// =======================================================
	var idMk = charIDToTypeID( "Mk  " );
	    var desc6 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref2 = new ActionReference();
	        var idcontentLayer = stringIDToTypeID( "contentLayer" );
	        ref2.putClass( idcontentLayer );
	    desc6.putReference( idnull, ref2 );
	    var idUsng = charIDToTypeID( "Usng" );
	        var desc7 = new ActionDescriptor();
	        var idNm = charIDToTypeID( "Nm  " );
	        desc7.putString( idNm, layername );
	        var idType = charIDToTypeID( "Type" );
	            var desc8 = new ActionDescriptor();
	            var idClr = charIDToTypeID( "Clr " );
	                var desc9 = new ActionDescriptor();
	                var idRd = charIDToTypeID( "Rd  " );
	                desc9.putDouble( idRd, 255.000000 );
	                var idGrn = charIDToTypeID( "Grn " );
	                desc9.putDouble( idGrn, 255.000000 );
	                var idBl = charIDToTypeID( "Bl  " );
	                desc9.putDouble( idBl, 255.000000 );
	            var idRGBC = charIDToTypeID( "RGBC" );
	            desc8.putObject( idClr, idRGBC, desc9 );
	        var idsolidColorLayer = stringIDToTypeID( "solidColorLayer" );
	        desc7.putObject( idType, idsolidColorLayer, desc8 );
	    var idcontentLayer = stringIDToTypeID( "contentLayer" );
	    desc6.putObject( idUsng, idcontentLayer, desc7 );
	executeAction( idMk, desc6, DialogModes.NO );

	return activeDocument.activeLayer;

}


function 不透明度(percentage){
// =======================================================
var idsetd = charIDToTypeID( "setd" );
    var desc20 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref19 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref19.putEnumerated( idLyr, idOrdn, idTrgt );
    desc20.putReference( idnull, ref19 );
    var idT = charIDToTypeID( "T   " );
        var desc21 = new ActionDescriptor();
        var idOpct = charIDToTypeID( "Opct" );
        var idPrc = charIDToTypeID( "#Prc" );
        desc21.putUnitDouble( idOpct, idPrc, percentage);
    var idLyr = charIDToTypeID( "Lyr " );
    desc20.putObject( idT, idLyr, desc21 );
executeAction( idsetd, desc20, DialogModes.NO );
}
/*
ファイルをレイヤーに読み込み
*/

function loadimg(filename){
	var basedoc = activeDocument
	fileObj = new File(filename);
	if(filename == null){return false;}
	if(fileObj.exists == false){return false}
	//パスを開く。
	app.open(fileObj);
	
	//空のレイヤーはスキップ
	if(
		(activeDocument.activeLayer.bounds[0].value == 0)&&
		(activeDocument.activeLayer.bounds[1].value == 0)&&
		(activeDocument.activeLayer.bounds[2].value == 0)&&
		(activeDocument.activeLayer.bounds[3].value == 0)
	){
		activeDocument.close(SaveOptions.DONOTSAVECHANGES);
		return true;
	}
	
	//サイズ取得
	targetwidth = app.activeDocument.width
	targetheight = app.activeDocument.height

	layername = activeDocument.name;
	//activeDocument.artLayers[0].name = activeDocument.name;
	
	//処理
	activeDocument.activeLayer.duplicate(basedoc)
	//閉じる
	// =======================================================
	activeDocument.close(SaveOptions.DONOTSAVECHANGES);
	activeDocument.activeLayer.name = layername;

	//サイズが違ったら合わせる
	if((activeDocument.width != targetwidth)||(activeDocument.height != targetheight)){
		preferences.rulerUnits = Units.PIXELS;
		activeDocument.resizeCanvas(targetwidth,targetheight,AnchorPosition.MIDDLECENTER);
	}

	//レイヤーを返せば後処理楽？
	return activeDocument.activeLayer;
}


function 最背面(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc11 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref7 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref7.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc11.putReference( idnull, ref7 );
	    var idT = charIDToTypeID( "T   " );
	        var ref8 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idBack = charIDToTypeID( "Back" );
	        ref8.putEnumerated( idLyr, idOrdn, idBack );
	    desc11.putReference( idT, ref8 );
	executeAction( idmove, desc11, DialogModes.NO );
}

function 最前面(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc10 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref5 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref5.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc10.putReference( idnull, ref5 );
	    var idT = charIDToTypeID( "T   " );
	        var ref6 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idFrnt = charIDToTypeID( "Frnt" );
	        ref6.putEnumerated( idLyr, idOrdn, idFrnt );
	    desc10.putReference( idT, ref6 );
	executeAction( idmove, desc10, DialogModes.NO );
	

}

function 前面(){
// =======================================================
var idmove = charIDToTypeID( "move" );
    var desc12 = new ActionDescriptor();
    var idnull = charIDToTypeID( "null" );
        var ref12 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idTrgt = charIDToTypeID( "Trgt" );
        ref12.putEnumerated( idLyr, idOrdn, idTrgt );
    desc12.putReference( idnull, ref12 );
    var idT = charIDToTypeID( "T   " );
        var ref13 = new ActionReference();
        var idLyr = charIDToTypeID( "Lyr " );
        var idOrdn = charIDToTypeID( "Ordn" );
        var idNxt = charIDToTypeID( "Nxt " );
        ref13.putEnumerated( idLyr, idOrdn, idNxt );
    desc12.putReference( idT, ref13 );
executeAction( idmove, desc12, DialogModes.NO );

}


function 背面(){
	// =======================================================
	var idmove = charIDToTypeID( "move" );
	    var desc8 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref4 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idTrgt = charIDToTypeID( "Trgt" );
	        ref4.putEnumerated( idLyr, idOrdn, idTrgt );
	    desc8.putReference( idnull, ref4 );
	    var idT = charIDToTypeID( "T   " );
	        var ref5 = new ActionReference();
	        var idLyr = charIDToTypeID( "Lyr " );
	        var idOrdn = charIDToTypeID( "Ordn" );
	        var idPrvs = charIDToTypeID( "Prvs" );
	        ref5.putEnumerated( idLyr, idOrdn, idPrvs );
	    desc8.putReference( idT, ref5 );
	executeAction( idmove, desc8, DialogModes.NO );

}


////レイヤーidからレイヤーオブジェクトを取得する
//function lid(layerid){}

function movebyname(fromobj, toobj){
	fromname = fromobj.name
	toname = toobj.name
//	getfolderobj(fromname).move(getfolderobj(toname), ElementPlacement.INSIDE)
	getfolderobj(fromname).moveAfter(getfolderobj(toname))
	activeDocument.activeLayer = getfolderobj(fromname)
	前面()
}

function setActiveLayer(layername){
	layer = activeDocument.artLayers.getByName(layername)
	if(layer != undefined){
		activeDocument.activeLayer = layer
	}else{}
}


function 色域赤(){
	// =======================================================
	var idClrR = charIDToTypeID( "ClrR" );
	    var desc15 = new ActionDescriptor();
	    var idFzns = charIDToTypeID( "Fzns" );
	    desc15.putInteger( idFzns, 200 );
	    var idMnm = charIDToTypeID( "Mnm " );
	        var desc16 = new ActionDescriptor();
	        var idLmnc = charIDToTypeID( "Lmnc" );
	        desc16.putDouble( idLmnc, 54.290000 );
	        var idA = charIDToTypeID( "A   " );
	        desc16.putDouble( idA, 80.800000 );
	        var idB = charIDToTypeID( "B   " );
	        desc16.putDouble( idB, 69.900000 );
	    var idLbCl = charIDToTypeID( "LbCl" );
	    desc15.putObject( idMnm, idLbCl, desc16 );
	    var idMxm = charIDToTypeID( "Mxm " );
	        var desc17 = new ActionDescriptor();
	        var idLmnc = charIDToTypeID( "Lmnc" );
	        desc17.putDouble( idLmnc, 54.290000 );
	        var idA = charIDToTypeID( "A   " );
	        desc17.putDouble( idA, 80.800000 );
	        var idB = charIDToTypeID( "B   " );
	        desc17.putDouble( idB, 69.900000 );
	    var idLbCl = charIDToTypeID( "LbCl" );
	    desc15.putObject( idMxm, idLbCl, desc17 );
	    var idcolorModel = stringIDToTypeID( "colorModel" );
	    desc15.putInteger( idcolorModel, 0 );
	executeAction( idClrR, desc15, DialogModes.NO );

}

function マスク作製(){
	// =======================================================
	var idMk = charIDToTypeID( "Mk  " );
	    var desc24 = new ActionDescriptor();
	    var idNw = charIDToTypeID( "Nw  " );
	    var idChnl = charIDToTypeID( "Chnl" );
	    desc24.putClass( idNw, idChnl );
	    var idAt = charIDToTypeID( "At  " );
	        var ref10 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idMsk = charIDToTypeID( "Msk " );
	        ref10.putEnumerated( idChnl, idChnl, idMsk );
	    desc24.putReference( idAt, ref10 );
	    var idUsng = charIDToTypeID( "Usng" );
	    var idUsrM = charIDToTypeID( "UsrM" );
	    var idRvlS = charIDToTypeID( "RvlS" );
	    desc24.putEnumerated( idUsng, idUsrM, idRvlS );
	executeAction( idMk, desc24, DialogModes.NO );
	

}

function 選択解除(){
	// =======================================================
	var idsetd = charIDToTypeID( "setd" );
	    var desc26 = new ActionDescriptor();
	    var idnull = charIDToTypeID( "null" );
	        var ref12 = new ActionReference();
	        var idChnl = charIDToTypeID( "Chnl" );
	        var idfsel = charIDToTypeID( "fsel" );
	        ref12.putProperty( idChnl, idfsel );
	    desc26.putReference( idnull, ref12 );
	    var idT = charIDToTypeID( "T   " );
	    var idOrdn = charIDToTypeID( "Ordn" );
	    var idNone = charIDToTypeID( "None" );
	    desc26.putEnumerated( idT, idOrdn, idNone );
	executeAction( idsetd, desc26, DialogModes.NO );


}



function showall(){
 	//他のレイヤーの表示
	for(var i = 0; i < activeDocument.layers.length; i++){
		var layer = activeDocument.layers[i];
		layer.visible = true
	}
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerset = activeDocument.layerSets[i];
		layerset.visible = true
	}
}

function hideall(){
	 	//他のレイヤーの非表示
	for(var i = 0; i < activeDocument.layers.length; i++){
		var layer = activeDocument.layers[i];
		layer.visible = false
	}
	for(var i = 0; i < activeDocument.layerSets.length; i++){
		var layerset = activeDocument.layerSets[i];
		layerset.visible = false
	}

}






function 後付カスタム処理(){

/*	いらなくなったかも。
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		var lset = activeDocument.layerSets[n];
		黄緑でフォルダマスク(lset)
	}
*/

}

function 黄緑でフォルダマスク(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 黄緑でフォルダマスク(tmplset)
	}
	
	for(var m = 0; m < layerset.layers.length; m++){
		 layer = layerset.layers[m];
		 if(layer.name.match(/flatcolor/i) != null){
		 	
		 	activeDocument.activeLayer = layer
		 	レイヤーを全て非表示()
		 	layer.visible = true
		 	黄緑を選択()
		 	//選択範囲があれば。
		 	//http://www.openspc2.org/book/PhotoshopCC/easy/selection/012/index.html
		 	if(checkSelection()){
		 		選択範囲の拡張()
		 		//親フォルダにマスクかける
		 		if(layer.parent != null){
		 			activeDocument.activeLayer = layer.parent
		 			選択反転()
		 			マスク作製()
		 		}
		 	}
		}
	}
	
	レイヤーを全て表示()
}

function 選択範囲の拡張(){
    // ==============================================   =========
    var idExpn = charIDToTypeID( "Expn" );
        var desc34 = new ActionDescriptor();
        var idBy = charIDToTypeID( "By  " );
        var idPxl = charIDToTypeID( "#Pxl" );
        desc34.putUnitDouble( idBy, idPxl, 2.000000 );
        var idselectionModifyEffectAtCanvasBounds = stringIDToTypeID( "selectionModif   yEffectAtCanvasBounds" );
        desc34.putBoolean( idselectionModifyEffectAtCanvasBounds, false );
    executeAction( idExpn, desc34, DialogModes.NO );
    

}

function 黄緑を選択(){
    // ==============================================   =========
    var idClrR = charIDToTypeID( "ClrR" );
        var desc42 = new ActionDescriptor();
        var idFzns = charIDToTypeID( "Fzns" );
        desc42.putInteger( idFzns, 24 );
        var idMnm = charIDToTypeID( "Mnm " );
            var desc43 = new ActionDescriptor();
            var idLmnc = charIDToTypeID( "Lmnc" );
            desc43.putDouble( idLmnc, 87.820000 );
            var idA = charIDToTypeID( "A   " );
            desc43.putDouble( idA, -79.270000 );
            var idB = charIDToTypeID( "B   " );
            desc43.putDouble( idB, 81.000000 );
        var idLbCl = charIDToTypeID( "LbCl" );
        desc42.putObject( idMnm, idLbCl, desc43 );
        var idMxm = charIDToTypeID( "Mxm " );
            var desc44 = new ActionDescriptor();
            var idLmnc = charIDToTypeID( "Lmnc" );
            desc44.putDouble( idLmnc, 87.820000 );
            var idA = charIDToTypeID( "A   " );
            desc44.putDouble( idA, -79.270000 );
            var idB = charIDToTypeID( "B   " );
            desc44.putDouble( idB, 81.000000 );
        var idLbCl = charIDToTypeID( "LbCl" );
        desc42.putObject( idMxm, idLbCl, desc44 );
        var idcolorModel = stringIDToTypeID( "colorModel" );
        desc42.putInteger( idcolorModel, 0 );
    executeAction( idClrR, desc42, DialogModes.NO );
    
}


function checkSelection()
{
	var flag = true;
	try {
		activeDocument.selection.translate(0,0);
	}catch(e){
		flag = false;
	}
	return flag;
}

function 選択反転(){
	var idInvs = charIDToTypeID( "Invs" );
	executeAction( idInvs, undefined, DialogModes.NO );
}


function 子を非表示(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 子を非表示(tmplset)
	}
	for(var i = 0; i < layerset.artLayers.length; i++){
		 var layer = layerset.artLayers[i];
		 layer.visible = false
	}
}
function レイヤーを全て非表示(){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 layerset = activeDocument.layerSets[n];
		 子を非表示(layerset)
	}
}


function 子を表示(layerset){
	for(var n = 0; n < layerset.layerSets.length; n++){
		 var tmplset = layerset.layerSets[n];
		 子を表示(tmplset)
	}
	for(var i = 0; i < layerset.artLayers.length; i++){
		 var layer = layerset.artLayers[i];
		 layer.visible = true
	}
}
function レイヤーを全て表示(){
	for(var n = 0; n < activeDocument.layerSets.length; n++){
		 layerset = activeDocument.layerSets[n];
		 子を表示(layerset)
	}
}