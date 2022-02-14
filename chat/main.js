function checkOutput() {
  var frameObj = document.getElementById("formsubmit");
  var frameContent = frameObj.contentWindow.document.body.innerHTML;
  return frameContent
}

function copytext(self){
  //if(pressedKeys[keycodes["shift"]]){
    // console.log(self.innerText)
    navigator.clipboard.writeText(self.innerText);
    // if(!document.getElementById("userclickable").matches(':hover'))
    alert("Copied text to clipboard\n\n" + self.innerText)
  //}
}
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// function convertHMS(value) {
//   const sec = parseInt(value, 10); // convert value to number if it's string
//   let hours   = Math.floor(sec / 3600); // get hours
//   let minutes = Math.floor((sec - (hours * 3600)) / 60); // get minutes
//   let seconds = sec - (hours * 3600) - (minutes * 60); //  get seconds
//   // add 0 if value < 10; Example: 2 => 02
//   if (hours   < 10) {hours   = "0"+hours;}
//   if (minutes < 10) {minutes = "0"+minutes;}
//   if (seconds < 10) {seconds = "0"+seconds;}
//   return hours+':'+minutes+':'+seconds; // Return is HH : MM : SS
// }

function onFileChange(myFile){
  var file = myFile.files[0];  
  var filename = file.name;
  document.getElementById('uploadlabel').innerText = filename;
  document.getElementById('percent').innerText = ""
}

function resetfields(){
  setTimeout(() => {
  document.getElementById('sendfile').reset();
  document.getElementById('uploadlabel').innerText = "Upload a file";
  }, 0);
}

function cleartelluser(){
  setTimeout(() => {
    document.getElementById('updatemessage').innerHTML = '';
  }, 5000)
}

function telluser(text){
  document.getElementById('telluser').innerText = text;
}

timestampts = [];
lasttimestamp = 0;
lengthofchat = 0;
mentioned = [];
try{ username = getCookie("username").toLowerCase() }
catch { username = getCookie("username") }

firsttime = false;
checkMessage = true;
starttime = new Date()
setInterval(function() {
  // console.log(checkMessage == false);
  if(checkMessage == false) return;
  if((new Date() - starttime) < 1000) return;
  checkMessage = false;
  starttime = new Date()
  
  jQuery(function($){
    $.get("/api/chat/{roomuuid}?length=" + lengthofchat + " &timestamp=" + lasttimestamp, function(txt) {
      checkMessage = true;
      if(txt == "<b style=\"text-align:center\">You have to sign in to view this channel!<b>"){ document.getElementById('chat').innerHTML = txt; return; }
      if(txt == "<b style=\"text-align:center\">You don't have access to this room!<b>"){ document.getElementById('chat').innerHTML = txt; return; }
      try {
      if(txt.split(":")[0] == "0"){
        console.log("Contents are the same: ", txt.split(":")[1]);
        lasttimestamp = parseFloat(txt.split(":")[1]);  
        return;
      } else {
          lasttimestamp = parseFloat(txt.split("%")[1].split("%")[0])
          txt = txt.split("%")[0]
        } // Now I just need to implement this to the "newer" messages system
      } catch { document.getElementById('chat').innerHTML = txt; }
        lengthofchat = txt.length;
      var chat = $('#chat');

      console.log(((chat[0].scrollHeight - chat.height()) - chat[0].scrollTop));
    if(Math.round(((chat[0].scrollHeight - chat.height()) - chat[0].scrollTop)) < 135){ // If the scroll bar is on the bottom of the screen, scroll to the bottom in case a new message is sent
        scrolltobottom = true;
    } else scrolltobottom = false; // If not, user has scrolled so don't scroll to the bottom of the chat box

    finishedtxt = []
    searchtxt = txt.split("\n")
    for (var element of searchtxt) {
      if(element.search("<Image:") != -1){
        split = element.split(":");

        finishedtxt.push(split[1] + " uploaded an image. <a download href=\"" + split[2] + "/download\">Click here to download</a>\n<img style=\"width:200px;\" src=\"" + split[2] + "\">");
      } else if(element.search("<File:") != -1){
        split = element.split(":");
        finishedtxt.push(split[1] + " uploaded a file called '" + split[2] + "' <a download href=\"" + split[3] + "\">Click Here to Download</a>");
    } else {
      split = element.split("::")
      if(split.length > 1){

        secondsSinceSent =  Math.floor(Date.now() / 1000)-split[0] // Get time in seconds from when the message was sent
        readableDate = new Date(split[0] * 1000).toLocaleString()
        // time = convertHMS(secondsSinceSent)
        splitmessage = split[1].split(":")
        // timestampts.push(split[0])


        // finishedtxt.push(element = '<pre id="chattext" class="chattext">' + split[1] + " <b class=\"hiddentimestamp\">" + time[0] + " hours, " + time[1] + " minutes and " + time[2] + " seconds ago" + "</b></pre>");
        text = '<pre id="chattext" class="chattext'; // onclick="copytext(this)" 
        if(element.toLowerCase().indexOf("@" + username) != -1){
          if(!mentioned.includes(split[0])){
            if(firsttime){
            document.getElementById('notificationsound').play();
            }
          }
          text = text + " mention";
          mentioned.push(split[0]);
        }
        text = text + "\">";
        finishedtxt.push(text + split[1] + "<b id=\"hiddentimestamp\"class=\"hiddentimestamp\">" + readableDate + "</b>" + "</pre>");
      } else finishedtxt.push(element)
    }
  }

  txt = ""
  for(const element of finishedtxt){
    txt = txt + element + "\n"
  }
  document.getElementById('chat').innerHTML = txt;

    if(scrolltobottom || firsttime == false){ // scroll to the bottom of the chat
      chat.scrollTop(
      chat[0].scrollHeight - chat.height())}

      firsttime = true;
    }).fail(checkMessage = true);
  })
}, 20); // Get text from chat text file and display it on the screen


function ClearFields(){
  setTimeout(() => {
    document.getElementById("messaging").reset();

    setTimeout(() => {
      var output = checkOutput()
      if(output == "Sent message.") telluser("")
      if(output == "Not in queue"){
        telluser("Unable to send message. You are not in the game queue!");
      } else if(output == "No message"){
        telluser("No content in your message; it was not sent");
      } else if(output == "No username") {
      window.location="/index.html?fail=You are not signed in, please sign in";
      }
    }, 100);
  }, 0);
  
}

isshiftpressed = true;
var keycodes = {"shift": 16};
var pressedKeys = {};
window.onkeyup = function(e) { pressedKeys[e.keyCode] = false; }
window.onkeydown = function(e) { pressedKeys[e.keyCode] = true; }

setInterval(function() {
  const textlimit = document.getElementById("textlimit");
  const textbox = document.getElementById("message");
  textlimit.innerText = textbox.value.length + "/200"
}, 100);

window.onload=function(){
$(function() {
  var percent = $('.percent');

  $('form').ajaxForm({
      beforeSend: function() {
          var percentVal = '0%';
          percent.html(percentVal);
      },
      uploadProgress: function(event, position, total, percentComplete) {
          var percentVal = percentComplete + '%';
          percent.html(percentVal);
      },
  });
});

var chat = $('#chat');
chat.scrollTop(
chat[0].scrollHeight - chat.height())
// window.innerWidth;
// chatbox = document.getElementById("chat")
// chatbox.style.width = window.innerWidth;

}
