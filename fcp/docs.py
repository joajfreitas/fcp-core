# Documentation generator
# Generate HTML from json
import os
from ww import f

from .docs_css import css


def markdown(spec, root):
    main = "% FCP Docs\n"
    # markdown += "# FCP Docs\n"
    main += f("## Logs\n")
    for log in sorted(spec.logs.values(), key=lambda x: x.id):
        main += f("* {log.id}: [{log.name}]({root}/log.md#{log.name})\n")

    main += "\n"

    main += f("## Devices\n")
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f("* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n")
        for msg in sorted(dev.msgs.values(), key=lambda x: x.id):
            main += f("  + [{msg.id}: {msg.name}]({root}/{dev.name.lower()}.md#{msg.name.lower()})\n")
    main += "\n"

    main += f("## Configs\n")
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f("* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n")
        for cfg in sorted(dev.cfgs.values(), key=lambda x: x.id):
            main += f("  + [{cfg.id}: {cfg.name}]({root}/{dev.name.lower()}.md#{cfg.name.lower()})\n")
    main += "\n"

    main += f("## Commands\n")
    for dev in sorted(spec.devices.values(), key=lambda x: x.id):
        main += f("* [{dev.id}: {dev.name}]({root}/{dev.name.lower()}.md)\n")
        for cmd in sorted(dev.cmds.values(), key=lambda x: x.id):
            main += f("  + [{cmd.id}: {cmd.name}]({root}/{dev.name.lower()}.md#{cmd.name.lower()})\n")
    main += "\n"

    devices = []
    for dev in spec.devices.values():
        device = f("% {dev.name} \n")
        device += f("[index]({root}/index.md)\n\n")
        device += "## Messages\n"
        for msg in sorted(dev.msgs.values(), key=lambda x: x.id):
            device += f("### {msg.id}. {msg.name}\n")
            device += f("* dlc: {msg.dlc}\n")
            device += f("* frequency: {msg.frequency}\n\n")
            for sig in sorted(msg.signals.values(), key=lambda x: x.start):
                device += f("#### {sig.name}\n")
                if sig.comment != "":
                    device += f("_{sig.comment}_\n\n")
                device += f("* start: {sig.start}\n")
                device += f("* length: {sig.length}\n")

                if sig.byte_order != "little_endian":
                    device += f("* byte_order: {sig.byte_order}\n")

                if not (sig.scale == 1 and sig.offset == 0):
                    device += f("* scale: {sig.scale}\n")
                    device += f("* offset: {sig.offset}\n")

                device += f("* type: {sig.type}\n")
                if sig.unit != "":
                    device += f("* unit: {sig.unit}\n\n")

                if not (sig.min_value == 0 and sig.max_value == 0):
                    device += f("* min_value: {sig.min_value}\n")
                    device += f("* max_value: {sig.max_value}\n")

                if not (sig.mux_count == 1 and sig.mux == ""):
                    device += f("* mux: {sig.mux}\n")
                    device += f("* mux_count: {sig.mux_count}\n")
                device += "\n"

        device += f("## Configs \n")
        for cfg in sorted(dev.cfgs.values(), key=lambda x: x.id):
            device += f("### {cfg.id}. {cfg.name}\n")
            if not cfg.comment == "":
                device += f("_{cfg.comment}_\n")
            device += "\n"

        device += f("## Commands \n")
        for cmd in sorted(dev.cmds.values(), key=lambda x: x.id):
            device += f("### {cmd.id}. {cmd.name}\n")
            if not cmd.comment == "":
                device += f("_{cmd.comment}_\n")
            device += "\n"

        devices.append(device)

    log_md = "% Logs\n"
    log_md += f("[index]({root}/index.md)\n\n")
    for log in sorted(spec.logs.values(), key=lambda x: x.id):
        log_md += f("## {log.name}\n")
        if log.comment != "":
            log_md += f("_{log.comment}_\n\n")

        log_md += f("* {log.string}\n")
        log_md += f("* {log.id}\n")
        log_md += f("* {log.n_args}\n")
        log_md += "\n"

    return main, log_md, devices


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

    main, log_md, devices = markdown(spec, link_location)

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
    
    os.system(f("cd {out}; ./build.sh"))

    logger.info("Done")
