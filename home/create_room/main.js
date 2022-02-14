function cleartelluser(){
    setTimeout(() => {
      document.getElementById('telluser').innerText = '';
    }, 5000)
  }

function submitForm(){
    document.getElementById("mainform").submit()
}

function ispublicchange(){
    ispubbutton = document.querySelector('#ispublic');
    if(ispubbutton.value == "Yes"){
        ispubbutton.value = "No"; // select the radio button
        document.getElementById("nopublic").checked = true;
        document.getElementById("yespublic").checked = false;
        document.getElementById('notpublic').classList.remove("hiddentext");

    } else {
        ispubbutton.value = "Yes"; // select the other radio button
        document.getElementById("yespublic").checked = true;
        document.getElementById("nopublic").checked = false;
        document.getElementById('notpublic').classList.add("hiddentext");
    }}

function adduser(){
    // console.log(1234)
    addusertext = document.querySelector('#addusers');

    user = addusertext.value;
    listofppl = document.getElementById("listofppl")
    addusertext.value = "";
    usernames = listofppl.innerText.split("\n")
    run=true
    for (let index = 0; index < usernames.length; ++index) {
        if(usernames[index] == user){
            run=false
        }
    }
    if(run === false) {
        document.getElementById("telluser").innerText = "User is already added.";
        cleartelluser();
        return;
    }
    if(run === true){
    document.querySelector('#usersubmit').value=user;
    document.querySelector('#checkuser').submit();
    }
}

// setInterval(() => {
//     console.log(pressedKeys[16])
// }, 100);

setTimeout(() => {
document.getElementById("yespublic").checked = true;

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
var failreason = urlParams.get('fail');
document.getElementById("telluser").innerText = failreason;

document.getElementById('notpublic').classList.add("hiddentext");

var myIframe = document.getElementById('submitframe');
myIframe.addEventListener("load", function() {
    document.querySelector('#usersubmit').value="";
    var frameObj = document.getElementById("submitframe");
    var frameContent = frameObj.contentWindow.document.body.innerHTML;
    if(frameContent == "True"){
        usersinchat = document.getElementById("usersinchat");
        usersinchat.value = usersinchat.value + user + ";";
        listofppl.innerText = listofppl.innerText + "\n" + user
    } else if(frameContent == "Not logged in"){
        window.location="/index.html?fail=You are not logged in. Please log in to continue";
    } else {
        // console.log(frameConent)
        document.getElementById("telluser").innerText = "User was not found";
        cleartelluser()
    }

});
if(failreason == "User was not found"){ document.getElementById("telluser").innerText = ""; }
}, 0)

