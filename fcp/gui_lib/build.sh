for i in $(ls | grep "\.ui"); do
	echo "building" $i "$(basename "$i" .ui).py"
	pyside2-uic $i > "$(basename "$i" .ui).py";
done
