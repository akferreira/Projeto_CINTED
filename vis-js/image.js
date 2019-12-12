var page = require('webpage').create();
page.open('file:///home/arthur/projects/vis-js/test.html', function() {
 window.setTimeout(function () {
            page.render('canvas.png');
  phantom.exit();
        }, 4000);
  
});
