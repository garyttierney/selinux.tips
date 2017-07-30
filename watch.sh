inotifywait -e close_write,moved_to,create -r -m source/ |
while read -r directory events filename; do
	make "$1"
done

