/*jshint moz:true */
var Insect = {
  start: function() {
    console.log("insect");
    Cu.import('resource://gre/modules/devtools/dbg-server.jsm');
    if (!DebuggerServer.initialized) {
      DebuggerServer.init(() => true);
      DebuggerServer.addBrowserActors();

      try {
        DebuggerServer.openListener(6000);
      } catch (e) {
        dump('Unable to start debugger server: ' + e + '\n');
      }
      console.dir(DebuggerServer);
    }
  }
};
