import glob

ls = glob.glob("*.html")

print("<h1> Index </h1>")

for l in ls:
    print(f"<a href={l}> {l}</a><br>")
