var casper = require('casper').create();

url = phantom.args[phantom.args.length - 1]

casper.start(url, function() {
    this.debugHTML();
    casper.exit();
})
casper.run(function () {
})
