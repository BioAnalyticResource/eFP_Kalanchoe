function datasetSelected(dataset, selectedTissue, selectedTissue2) {
	var tlist = tissues[dataset];
	var selectElem = document.getElementById('tissue');
	var selectElem_cmp = document.getElementById('tissue2');
	selectElem.options.length = 0;
	if(selectElem_cmp != null) {
		selectElem_cmp.options.length = 0;
	}
	selectElem.style.backgroundColor = tissue_colors[dataset][0];
	selectElem.style.color = suitColor(tissue_colors[dataset][0]);
	var arLen=tlist.length;
	var new_opt;
	for ( var i=0; i<arLen; ++i ){
		sel = false;
		if(selectedTissue == tlist[i]) {
			sel = true;
			selectElem.style.backgroundColor=tissue_colors[dataset][i];
			selectElem.style.color=suitColor(tissue_colors[dataset][i]);
		}
		new_opt = new Option(tlist[i], tlist[i], false, sel);
		new_opt.title= tlist[i]
		new_opt.style.backgroundColor=tissue_colors[dataset][i];
		new_opt.style.color=suitColor(tissue_colors[dataset][i]);
		new_opt.style.width="auto";
		try {
			selectElem.add(new_opt, null); // standards compliant; doesn't work in IE
		}
		catch(ex) {
			selectElem.add(new_opt, 0); // IE only
		}
		if(selectElem_cmp != null) {
			sel = false;
			if(selectedTissue2 == tlist[i]) {
				sel = true;
				selectElem_cmp.style.backgroundColor=tissue_colors[dataset][i];
                        	selectElem_cmp.style.color=suitColor(tissue_colors[dataset][i]);
                	}
			new_opt = new Option(tlist[i], tlist[i], false, sel);
			new_opt.title= tlist[i]
			new_opt.style.backgroundColor=tissue_colors[dataset][i];
			new_opt.style.color=suitColor(tissue_colors[dataset][i]);
			new_opt.style.width="auto";
			try {
				selectElem_cmp.add(new_opt, null); // standards compliant; doesn't work in IE
			}
			catch(ex) {
				selectElem_cmp.add(new_opt, 0); // IE only
			}
		}
	}
}	

function suitColor(backgroundcolor) {
	var gray = 0;
	if (backgroundcolor.substr(0,4) == "rgb(") {
		bgcolor = backgroundcolor.replace(/rgb\(|\)/g, "").split(",");
		gray = bgcolor[0]*0.299 + bgcolor[1]*0.587 + bgcolor[2]*0.114;
	} else {
		gray = parseInt(backgroundcolor.substr(1,2))*0.299 + parseInt(backgroundcolor.substr(3,2))*0.587 + parseInt(backgroundcolor.substr(5,2))*0.114;
	}
	if(gray < 186) { return "#FFFFFF"; }	// return white for dark background
	else { return "#000000"; }				// return white for light background
}

function toggleElementDisplay(id, disp) {
    var elem = document.getElementById(id)
    if(elem) {
    	if(disp == true) {
    		elem.style.visibility="visible";
    	} else {
    		elem.style.visibility="hidden";
    	}
    }
}
