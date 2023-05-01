function geoFindMe() {
    var todayDate = new Date();
    var datetime = todayDate.getFullYear() + "-" + (todayDate.getMonth()+1) + "-" + todayDate.getDate()
+ " " + todayDate.getHours() + ":" + todayDate.getMinutes() + ":" + todayDate.getSeconds();
    document.getElementById("today").value = datetime;

    const status = document.querySelector('#status');
    const lng = document.querySelector('#lon').value;
    const lat = document.querySelector('#lat').value;

    function success(position) {
        const latitude  = position.coords.latitude;
        const longitude = position.coords.longitude;

        status.textContent = '';
        document.getElementById("lat").value = latitude;
        document.getElementById("lon").value = longitude;
    }

    function error() {
        status.textContent = 'Nebylo možné nalézt Vaši lokaci';
    }

    if (!navigator.geolocation) {
        status.textContent = 'Vyhledání geolokace není možné v tomhle prohlížeči, zkuste jiný';
    } else {
        status.textContent = 'Lokalizování';
        navigator.geolocation.getCurrentPosition(success, error);
    }

}
window.onload = geoFindMe();

