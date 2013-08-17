Insect
======
Insect is a proof-of-concept joint Firefox and Vim plugin which
enables remote editing of document style sheets using the Remote
Debugging Protocol.

Demo
----
<a href="http://www.youtube.com/watch?feature=player_embedded&v=CUAcDvmtICA"
   target="_blank">
   <img src="http://img.youtube.com/vi/CUAcDvmtICA/0.jpg"
        alt="Insect Demo" width="240" height="180" border="10"/>
</a>

Requirements
------------
* Vim 7.3+ with Python support
* Firefox Nightly (may work with normal Firefox, untested)

Installing and Running the Firefox Plugin
-----------------------------------------
The firefox plugin is in the `ff-plugin` directory, and can be
installed by zipping its contents into a `.xpi` file. In terminal,
this can be done using `cd ff-plugin; zip -r insect.xpi ./*`. Next,
drag the `insect.xpi` file into your Firefox window and accept the
installation prompt.

Once installed, start the server by selecting *Activate Insect*
from the *Tools* menu.

Vim Usage
---------
`insect.vim` has three lines in it which must be modified to
refer to the directory containing `insect.py`. It should be
`~/.vim/bundle/insect/plugin`. Fixing this is on the to-do list.

After starting the firefox plugin, run `:call LoadSheets()` to load
in the style sheets of the currently selected Firefox tab. Upon
writing the files they will automatically update in Firefox.

Barely-implemented Functionality
--------------------------------
Run :call LoadScripts() to load in the currently selected tab's
JavaScript sources.
