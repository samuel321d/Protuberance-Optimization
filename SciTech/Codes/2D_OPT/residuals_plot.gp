set terminal wxt 1 persist
set title "Residuals"
set xlabel "Iteraton"
set ylabel "logscale"
set grid
set datafile separator ","
set logscale y

# Asumiendo que la columna 1 es Iteración y la 12 o 13 es el residuo (ajusta según tu CSV)
# Puedes mapear múltiples columnas separándolas con comas
plot "history.csv" using 3:4 title "rms" with lines

pause 5  # Pausa de 5 segundos
reread   # Hace que gnuplot vuelva a ejecutar el script desde el inicio
