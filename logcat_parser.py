import sys
import os
import re
import json

def parse_file(f, out_dir):
  """Parse logcat file and put separate JSON requests/responses into separate files."""
  buffer = ''
  method_name = ''
  count = 0
  for line in f:
    # Init write_flag and method_name
    write_flag = False
    try:
      method_search = re.search('"method":"(.+?)"', line)
      method_search.groups()[0]
    except Exception:
      True
    else:
      method_name = method_search.groups()[0]

    # Extract JSON from the line.
    index = line.find("Sent to server")
    if (index > -1):
      line = line[index + 17:]
      write_flag = True
    index = line.find("Server response")
    if (index > -1):
      if (line.find("chunk") == -1):
        line = line[index + 18:]
        write_flag = True
      else:
        # Match current chunk number and total number of chunks.
        chunks = re.search('chunk (\d+) of (\d+):', line)
        chunks = chunks.groups()
        current_chunk = chunks[0]
        end_chunk = chunks[1]
        # Handle buffer/chunks
        skip = 29 + len(str(current_chunk)) + len(str(end_chunk))
        buffer += line[index + skip:].rstrip("\n")
        if (current_chunk == end_chunk):
          line = buffer
          buffer = ''
          write_flag = True

    # Write to file if allowed.
    if (write_flag):
      file_path = out_dir + "/" + str(count) + "-" + method_name + ".json"
      out_file = open(file_path, 'w')
      line = json.loads(line)
      line = json.dumps(line, sort_keys=True, indent=2, separators=(',', ': '))
      out_file.write(line)
      count += 1
  return

def create_output_dir( file_name ):
  """Create output directory"""
  base_dir_name = "output_" + file_name
  dir_name = base_dir_name
  suffix = 2
  while (os.path.exists(dir_name)):
    dir_name = base_dir_name + "_" + str(suffix)
    suffix += 1
  os.makedirs(dir_name, 0755)
  return dir_name

# === MAIN PROGRAM === #

# Check that file parameter is passed.
if (len(sys.argv) < 2):
  print "Usage: python log_parser.py FILE_NAME"
  sys.exit()

for file_name in sys.argv[1:]:
  try:
    f = open(file_name, 'r')
    out_dir = create_output_dir(file_name)
    parse_file(f, out_dir)
  except IOError:
    print "Can't open file " + file_name + ". Skipping..."
  except Exception as inst:
    print inst
  else:
    print "Successfully parsed file " + file_name + ". Output files located in " + out_dir + "."
