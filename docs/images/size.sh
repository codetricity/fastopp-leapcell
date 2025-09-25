for file in *.png; do
    magick "$file" -resize 800x "${file%.*}.webp"
done

