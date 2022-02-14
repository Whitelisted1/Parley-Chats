function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

function toggleGradient(self, setgradient=""){
    if(setgradient != "") self.innerText = setgradient;
    if(self.innerText == "Active"){
        self.innerText = "Inactive"
        document.cookie = "chatcolor=default; path=/;";
    } else {
        self.innerText = "Active";
        document.cookie = "chatcolor=gradient; path=/;";
    }
}

window.onload = function(){
    gtoggle = document.getElementById("gradientToggle");
    // console.log(getCookie("chatcolor"));
    if(getCookie("chatcolor") == "default" || getCookie("chatcolor") == undefined){
        gtoggle.innerText = "Inactive";
    }

    startup = document.getElementById("startuptime");
    startup.innerText = new Date(parseFloat(startup.innerText)*1000).toLocaleString()
}
