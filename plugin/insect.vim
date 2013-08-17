if !has('python')
  echo "Error: Required vim compiled with +python"
  finish
endif

function! LoadScripts()

python << EOF
import sys
sys.path.append("/Users/karenin/.vim/bundle/insect/plugin")
import insect, urlparse
bug = insect.Insect()
sources = bug.get_sources()
bug.cleanup()

print "received %d sources" % len(sources)
buf_start = len(vim.buffers) + 1

for i, source in enumerate(sources):
  oorl = urlparse.urlparse(source["url"])
  buf_name = oorl.path.split("/")[-1]
  vim.command(":badd "+buf_name)
  vim.command(":b! "+str(buf_start+i))
  vim.command(":set buftype=nofile")
  vim.command(":set bufhidden=hide")
  vim.command(":setlocal noswapfile")
  vim.command(":set syntax=javascript")
  buf = vim.buffers[buf_start + i]
  buf.name = buf_name
  buf[:] = source["source"].split("\n")
  vim.command(":set nomodified")
  # for line in source["source"].split("\n"):
  #  buf.append(""+line)
  # print file_name, " -> ", source["source"][:40]
EOF

endfunction

function! LoadSheets()
python << EOF
import sys
sys.path.append("/Users/karenin/.vim/bundle/insect/plugin")

import insect, urlparse

bug = insect.Insect()
sheets = bug.get_sheets()
bug.cleanup()

for i, sheet in enumerate(sheets):
  oorl = urlparse.urlparse(sheet["href"])
  buf_name = oorl.path.split("/")[-1]
  vim.command(":badd "+buf_name)
  vim.command(":b! "+buf_name)
  vim.command(":set buftype=acwrite")
  vim.command(":set syntax=css")
  vim.command(":autocmd BufWriteCmd "+buf_name+" :call UpdateSheets(\""+buf_name+"\")")
  buf = vim.current.buffer
  buf.name = buf_name
  buf[:] = sheet["source"].split("\n")
  vim.command(":set nomodified")

  # vim.command(":autocmd FileWriteCmd *.css :call UpdateSheets()")
EOF

endfunction

function! UpdateSheets(buf_name)
python << EOF
import sys
sys.path.append("/Users/karenin/.vim/bundle/insect/plugin")

import insect, urlparse
bug = insect.Insect()
sheets = bug.get_sheets()
mod_buf_name = vim.eval("a:buf_name")
newSheets = []
for i, sheet in enumerate(sheets):
  oorl = urlparse.urlparse(sheet["href"])
  buf_name = oorl.path.split("/")[-1]
  if buf_name != mod_buf_name:
    continue
  vim.command(":b! "+buf_name)
  vim.command(":set nomodified")
  buf = vim.current.buffer
  source = ""
  for line in buf:
    source += line + "\n"
  newSheets.append({"href": sheet["href"], "source": source})
bug.update_sheets(newSheets)

bug.cleanup()
EOF

endfunction
