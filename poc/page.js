function controlStation(stationId,signal) {
	window.location=('./req?stationId='+stationId+'&signal='+signal);
}

function addAsset(relation, type, src) {
  var asset = document.createElement("link");
  asset.setAttribute("rel", relation);
  asset.setAttribute("type", type);
  asset.setAttribute("href", src);
  document.getElementsByTagName("head")[0].appendChild(asset);
}

function writePage() {
  document.write('<html><div id=\'stations\'><h3 id="header">Cloudwater</h3><ul id =\'list\'>');
  var i;
  for(i = 0; i < numStations; i++) {
    if(stations[i]) {
      document.write('<li id=\'on\' onclick=controlStation('+i+',0)>Disable Station ' + (i+1%10) + '</li>');
    } else {
      document.write('<li id=\'off\' onclick=controlStation('+i+',1)>Enable Station ' + (i+1%10) + '</li>');
    }
  }
  document.write('</ul></div></html>');
}

addAsset("stylesheet", "text/css", "styles.css");
addAsset("icon", "image/x-icon", "data:;base64,iVBORw0KGgo=");
writePage();
