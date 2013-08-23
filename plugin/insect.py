import socket, json, urlparse

class Communicator:
  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.connect(("localhost", 6000))
    self.s.settimeout(0.5)
    self.buf_size = 1024
    self.leftovers = ""

  def recv(self, debug=False):
    data = self.leftovers
    while data.find(":") < 0:
      try:
        data = self.s.recv(self.buf_size)
      except socket.timeout:
        self.leftovers = data
        return None

    length = int(data.split(":")[0])
    data = data.split(":", 1)[1]
    while len(data) < length:
      try:
        data += self.s.recv(self.buf_size)
      except socket.timeout:
        self.leftovers = data
        return None
    self.leftovers = data[length:]
    data = data[:length]
    if debug:
      print data
    return json.loads(data)

  def send(self, data):
    data = json.dumps(data)
    self.s.send(str(len(data))+":"+data)
  def command(self, actor, type, **kwargs):
    data = {"to":actor, "type":type}
    for key in kwargs.keys():
      data[key] = kwargs[key]
    self.send(data)

class Insect():
  def __init__(self):
    self.comms = Communicator()
  def startup(self):
    self.comms.recv()
    self.comms.command("root", "listTabs")
    return self.comms.recv()
  def attach(self, actor):
    self.comms.command(actor, "attach")
    tabAttach = self.comms.recv()
    return tabAttach, "error" not in tabAttach

  def attachThread(self, threadActor):
    self.comms.command(threadActor, "attach")
    threadAttach = self.comms.recv()
    return threadAttach, threadAttach["type"] == "paused"

  def interrupt(self, thread):
    self.comms.command(thread, "interrupt")
    threadInterrupt = None
    while threadInterrupt is None:
      threadInterrupt = self.comms.recv()

    return threadInterrupt["type"] == "paused"

  def get_sources(self):
    tab = self.get_selected_tab()

    tabAttach, ok = self.attach(tab["actor"])
    if not ok:
      print "Error attaching to: "+tab
      return []

    threadActor = tabAttach["threadActor"]
    threadAttach, ok = self.attachThread(threadActor)
    if not ok:
      print "Error attaching to thread"
      return []

    ok = self.interrupt(threadActor)
    if not ok:
      return []

    self.comms.command(threadActor, "sources")
    sources = []
    while True:
      threadSources = self.comms.recv()
      # print threadSources
      if threadSources is None:
        break
      if "type" in threadSources and threadSources["type"] == "newSource":
        # currently undocumented, so not using it
        continue
      if "sources" not in threadSources:
        continue
      for source in threadSources["sources"]:
        sources.append(source)

    for source in sources:
      self.comms.command(source["actor"], "source")
      sourceReply = self.comms.recv()
      while sourceReply is None:
        sourceReply = self.comms.recv()
      source["source"] = sourceReply["source"]
    for source in sources:
      if type(source["source"]) != dict:
        continue
      grip = source["source"]
      # print type(grip)
      self.comms.command(grip["actor"], "substring", start=0, end=grip["length"])
      subs = self.comms.recv()
      if "substring" not in subs:
        print "error in grip reply"
        continue
      source["source"] = subs["substring"]
    return sources

  def resume(self, thread):
    self.comms.command(thread, "resume")
    self.comms.recv()

  def detach(self, tab):
    self.comms.command(tab["actor"], "detach")
    self.comms.recv()
    self.comms.s.close()

  def get_selected_tab(self):
    tabsList = self.startup()
    if "tabs" not in tabsList:
      print tabsList
    return tabsList["tabs"][tabsList["selected"]]

  def get_sheets(self):
    sheets = []
    tab = self.get_selected_tab()
    styleEditor = tab["styleEditorActor"]
    self.comms.command(styleEditor, "getStyleSheets")
    styleSheets = self.comms.recv()
    for sheet in styleSheets["styleSheets"]:
      actor = sheet["actor"]
      self.comms.command(actor, "fetchSource")
      source = self.comms.recv()
      while True:
        if source is None:
          break
        if "source" in source:
          break
        source = self.comms.recv()
      if source is not None:
        name = sheet["href"]
        if name is None:
          name = "inline"+str(sheet["styleSheetIndex"])
        sheets.append({
          "href": name,
          "source": source["source"]
        })
        if sheet["href"] is None:
          print sheet
    return sheets

  def update_sheets(self, newSheets):
    tab = self.get_selected_tab()
    styleEditor = tab["styleEditorActor"]
    self.comms.command(styleEditor, "getStyleSheets")
    styleSheets = self.comms.recv()
    for sheet in styleSheets["styleSheets"]:
      actor = sheet["actor"]
      if sheet["href"] is None:
        sheet["href"] = "inline"+str(sheet["styleSheetIndex"])
      for newSheet in newSheets:
        if not newSheet["href"] == sheet["href"]:
          continue
        self.comms.command(actor, "update", text=newSheet["source"], transition=True)
        break

  def cleanup(self):
    while self.comms.recv() is not None:
      pass
    self.comms.s.close()

