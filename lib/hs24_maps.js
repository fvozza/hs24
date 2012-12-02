var map;

function initialize() {

  navigator.geolocation.getCurrentPosition(function(position) {
    var mapOptions = {
      zoom: 14,
      center: new google.maps.LatLng(position.coords.latitude, position.coords.longitude),
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      disableDefaultUI: true,
      streetViewControl: true,
      zoomControl: true,
      mapTypeControl: true,
    };
  
    map = new google.maps.Map(document.getElementById('map_canvas'),
        mapOptions);

    google.maps.event.addListener(map, "dragend", test);

/*
    var marker_pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude)
    var marker = new google.maps.Marker({
      position: marker_pos,
      visible: true,
      animation: google.maps.Animation.DROP,
      map: map
    })
*/
  },
  null,
  { enableHighAccuracy: true,
    timeout: 10,
    maximumAge: 10
  })
}

function test() {

}

google.maps.event.addDomListener(window, 'load', initialize);
