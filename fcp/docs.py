# Documentation generator
# Generate HTML from json
import os
from jinja2 import Template

from .docs_css import css

signals_template = Template("""
<html>
<head>
<style>
#searchbar {
  background-image: url('css/searchicon.png'); /* Add a search icon to input */
  background-position: 10px 12px; /* Position the search icon */
  background-repeat: no-repeat; /* Do not repeat the icon image */
  width: 100%; /* Full-width */
  font-size: 14px; /* Increase font-size */
  padding: 12px 20px 12px 40px; /* Add some padding */
  border: 1px solid #ddd; /* Add a grey border */
  margin-bottom: 12px; /* Add some space below the input */
}

#signals {
  border-collapse: collapse; /* Collapse borders */
  width: 100%; /* Full-width */
  border: 1px solid #ddd; /* Add a grey border */
  font-size: 14px; /* Increase font-size */
}

#signals th, #signals td {
  text-align: left; /* Left-align text */
  padding: 12px; /* Add padding */
}

#signals tr {
  /* Add a bottom border to all table rows */
  border-bottom: 1px solid #ddd;
}

#signals tr.header, #signals tr:hover {
  /* Add a grey background color to the table header and on hover */
  background-color: #ffdd11;
}
</style>
<script>
function search_function() {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("searchbar");
  filter = input.value.toUpperCase();
  table = document.getElementById("signals");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td0 = tr[i].getElementsByTagName("td")[0];
    td1 = tr[i].getElementsByTagName("td")[1];
    if (td0 || td1) {
      txtValue = td0.textContent || td0.innerText;
      txtValue += td1.textContent || td1.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}
</script>
</head>
<body>
<br>
<input type="text" id="searchbar" onkeyup="search_function()" placeholder="Search">
<title>Signals</title>
<ul>
<table id="signals">
<tr class="header">
<th style="width:10%;">Name</th>
<th style="width:70%;">Description</th>
</tr>
{% for sig in signals %}
<tr>
<td>{{sig.name}}</td>
<td>{{sig.comment}}</td>
</tr>
{% endfor %}
</table>
</ul>
</body>
</html>
""")

def markdown(spec, root):
    main = "% FCP Docs\n"
    # markdown += "# FCP Docs\n"
    main += "## Signal list\n"
    main += "[Signals list](signals.html)\n\n"

    main += f"## Logs\n"
    for log in sorted(spec.logs.values(), key=lambda x: x.id):
        main += f"* {log.id}: [{log.name}]({root}/log.md#{log.name})\n"

    main += "\n"

    main += f"## Devices\n"
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f"* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n"
        for msg in sorted(dev.msgs.values(), key=lambda x: x.id):
            main += f"  + [{msg.id}: {msg.name}]({root}/{dev.name.lower()}.md#{msg.name.lower()})\n"
    main += "\n"

    main += f"## Configs\n"
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f"* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n"
        for cfg in sorted(dev.cfgs.values(), key=lambda x: x.id):
            main += f"  + [{cfg.id}: {cfg.name}]({root}/{dev.name.lower()}.md#{cfg.name.lower()})\n"
    main += "\n"

    main += f"## Commands\n"
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f"* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n"
        for cmd in sorted(dev.cmds.values(), key=lambda x: x.id):
            main += f"  + [{cmd.id}: {cmd.name}]({root}/{dev.name.lower()}.md#{cmd.name.lower()})\n"
    main += "\n"

    devices = []
    for dev in spec.devices.values():
        device = f"% {dev.name} \n"
        device += f"[index]({root}/index.md)\n\n"
        device += "## Messages\n"
        for msg in sorted(dev.msgs.values(), key=lambda x: x.id):
            device += f"### {msg.id}. {msg.name}\n"
            device += f"* dlc: {msg.dlc}\n"
            device += f"* frequency: {msg.frequency}\n\n"
            for sig in sorted(msg.signals.values(), key=lambda x: x.start):
                device += f"#### {sig.name}\n"
                if sig.comment != "":
                    device += f"_{sig.comment}_\n\n"
                device += f"* start: {sig.start}\n"
                device += f"* length: {sig.length}\n"

                if sig.byte_order != "little_endian":
                    device += f"* byte_order: {sig.byte_order}\n"

                if not (sig.scale == 1 and sig.offset == 0):
                    device += f"* scale: {sig.scale}\n"
                    device += f"* offset: {sig.offset}\n"

                device += f"* type: {sig.type}\n"
                if sig.unit != "":
                    device += f"* unit: {sig.unit}\n\n"

                if not (sig.min_value == 0 and sig.max_value == 0):
                    device += f"* min_value: {sig.min_value}\n"
                    device += f"* max_value: {sig.max_value}\n"

                if not (sig.mux_count == 1 and sig.mux == ""):
                    device += f"* mux: {sig.mux}\n"
                    device += f"* mux_count: {sig.mux_count}\n"
                device += "\n"

        device += f"## Configs \n"
        for cfg in sorted(dev.cfgs.values(), key=lambda x: x.id):
            device += f"### {cfg.name} ({cfg.id}) : {cfg.type}\n"
            if not cfg.comment == "":
                device += f"_{cfg.comment}_\n"
            device += "\n"

        device += f"## Commands \n"
        for cmd in sorted(dev.cmds.values(), key=lambda x: x.id):
            device += f"### {cmd.id}. {cmd.name}\n"
            if not cmd.comment == "":
                device += f"_{cmd.comment}_\n"

            if len(cmd.args) > 0:
                device += "\n#### Arguments\n"
                for arg in cmd.args.values():
                    device += f" * {arg.name} ({arg.id}): {arg.type}\n"

            if len(cmd.rets) > 0:
                device += "\n#### Returns\n"
                for ret in cmd.rets.values():
                    device += f" * {ret.name} ({arg.id}): {arg.type}\n"

            device += "\n"

        devices.append(device)

    log_md = "% Logs\n"
    log_md += f"[index]({root}/index.md)\n\n"
    for log in sorted(spec.logs.values(), key=lambda x: x.id):
        log_md += f"## {log.name}\n"
        if log.comment != "":
            log_md += f"_{log.comment}_\n\n"

        log_md += f"* {log.string}\n"
        log_md += f"* {log.id}\n"
        log_md += f"* {log.n_args}\n"
        log_md += "\n"

    signals = spec.get_signals()
    signals = [sig.compile() for sig in signals]
    signals_txt = signals_template.render({"signals": signals})
    return main, log_md, devices, signals_txt


def check_out_dir(out):
    """Create output directory.

    :out: output directory path.
    :return: Failure and error message.
    """

    if not os.path.isdir(out):
        try:
            os.makedirs(out)
        except Exception as e:
            return False, str(e)

    return True, ""


def generate_docs(spec, out, link_location, logger):

    r, msg = check_out_dir(out)
    if not r:
        logger.error(msg)
        return

    root = link_location
    logger.info("Generate docs")

    build_sh = """
    for file in *.md; do
            pandoc -s --css=pandoc.css -f markdown --to=html5 "$file" -o "$(basename "$file" .md).html" --lua-filter=links-to-html.lua; 
    done
    """

    links_to_html = """
-- links-to-html.lua
function Link(el)
  el.target = string.gsub(el.target, "%.md", ".html")
  return el
end
"""

    main, log_md, devices, signals = markdown(spec, link_location)

    with open(os.path.join(out, "signals.html"), "w") as f:
        f.write(signals)

    with open(os.path.join(out, "index.md"), "w") as _f:
        _f.write(main)

    for device, name in zip(devices, spec.devices.keys()):
        with open(os.path.join(out, name + ".md"), "w") as _f:
            _f.write(device)

    with open(os.path.join(out, "log.md"), "w") as _f:
        _f.write(log_md)

    with open(os.path.join(out, "build.sh"), "w") as _f:
        _f.write(build_sh)

    os.chmod(os.path.join(out, "build.sh"), 0o755)

    with open(os.path.join(out, "pandoc.css"), "w") as _f:
        _f.write(css)

    with open(os.path.join(out, "links-to-html.lua"), "w") as _f:
        _f.write(links_to_html)

    os.system(f"cd {out}; ./build.sh")

    logger.info("Done")
