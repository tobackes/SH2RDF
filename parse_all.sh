for file in input/*.csv; do
    filename="${file##*/}";
    echo $filename;
    python csv2json.py input/${filename} output/"${filename%.*}".json;
done
