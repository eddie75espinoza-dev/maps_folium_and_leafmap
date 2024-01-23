# Por terminar

from PIL import Image, ImageDraw
import geopandas as gpd
from shapely.geometry import Polygon

# Ruta de la imagen de entrada y salida
imagen_entrada = "./public/meshblock_map/020010911.png"
imagen_salida = "./public/meshblock_map/imagen_recortada.png"
imagen_salida2 = "./public/meshblock_map/imagen_con_poligono.png"

# Cargar el polígono desde el archivo shapefile con geopandas
poligono_gdf = gpd.read_file('../radios_censales/RADIOS_2010_v2021.shp')

# Obtener las coordenadas del polígono
poligono = poligono_gdf[poligono_gdf.COD_2010 == '020010911']

# Crear una máscara poligonal con Pillow
mascara = Image.new("L", (200, 200), 0)  # Ajusta el tamaño según tu imagen
draw = ImageDraw.Draw(mascara)

# Convertir el polígono a coordenadas para la máscara
coordenadas_poligono = [(x, y) for x, y in poligono_gdf.geometry.iloc[0].exterior.coords]

# Dibujar el polígono en la máscara
draw.polygon(coordenadas_poligono, fill=255)

# Abrir la imagen
imagen = Image.open(imagen_entrada)

# Asegurar que ambas imágenes tengan el mismo modo y tamaño
mascara = mascara.resize(imagen.size)

# Recortar la imagen con la máscara
imagen_recortada = Image.alpha_composite(Image.new("RGBA", imagen.size, (0, 0, 0, 0)), Image.merge("RGBA", imagen.split()[:3] + (mascara,)))

# Guardar la imagen recortada
# imagen_recortada.save(imagen_salida)


# Crear un objeto de polígono Shapely
poligono_shapely = Polygon(coordenadas_poligono)

# Obtener límites del polígono para normalizar las coordenadas
min_x, min_y, max_x, max_y = poligono_shapely.bounds

# Normalizar las coordenadas del polígono
coordenadas_normalizadas = [
    ((x - min_x) / (max_x - min_x), (y - min_y) / (max_y - min_y))
    for x, y in coordenadas_poligono
]

# Escalar las coordenadas al tamaño de la imagen
tamaño_imagen = 500
coordenadas_pixel = [
    (int(x * tamaño_imagen), int(y * tamaño_imagen))
    for x, y in coordenadas_normalizadas
]

# Crear una nueva imagen
imagen2 = Image.new("RGB", (tamaño_imagen, tamaño_imagen), color="white")
draw2 = ImageDraw.Draw(imagen2)

# Dibujar el polígono en la imagen
draw2.polygon(coordenadas_pixel, fill="blue", outline="black")

# Guardar la imagen
imagen2.save(imagen_salida2)