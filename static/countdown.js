var countDownDate = document.querySelector('#wakeup').value;
var konec = new Date(countDownDate).getTime();

var x = setInterval(function() {
  var now = new Date().getTime();
  var distance = konec - now;
    
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  
  if (hours.toString().length == 1){
      hours = "0" + hours;
  }
  if (minutes.toString().length == 1){
    minutes = "0" + minutes;
  }
  if (seconds.toString().length == 1){
    seconds = "0" + seconds;
  }
    
  document.getElementById("countdown").innerHTML = hours + ":"
  + minutes + ":" + seconds;
  
  if (distance <= 0 || isNaN(distance)) {
    window.location.replace("/stop-pin");
  }
}, 1000);