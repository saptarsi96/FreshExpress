var timer = 0,
    timeTotal = 20000,
    timeCount = 20,
    timeStart = 0,
    cFlag;

function updateProgress(percentage) {
    var x = (percentage/timeTotal)*100,
        y = x.toFixed(3);
    $('#pbar_innerdiv').css("width", x + "%");
    $('#pbar_innertext').css("left", x + "%").text(x.toFixed(2) + '%');
}

function animateUpdate() {
    var perc = new Date().getTime() - timeStart;
    if(perc < timeTotal) {
        updateProgress(perc);
        timer = setTimeout(animateUpdate, timeCount);
    } else {
    	  updateProgress(timeTotal);
    }
}

$(document).ready(function() {
    $('#pbar_outerdiv').click(function() {
        if (cFlag == undefined) {
            clearTimeout(timer);
            cFlag = true;
            timeStart = new Date().getTime();
            animateUpdate();
        }
        else if (!cFlag) {
            cFlag = true;
            animateUpdate();
        }
        else {
            clearTimeout(timer);
            cFlag = false;
        }
    });
}); 