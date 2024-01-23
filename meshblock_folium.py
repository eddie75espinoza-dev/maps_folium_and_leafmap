import os
import geopandas
import folium
from pathlib import Path
import matplotlib.pyplot as plt
import contextily as ctx


PORT = 5975
HOST = 'localhost'
# Descarga de radios censales: https://www.indec.gob.ar/indec/web/Nivel4-Tema-1-39-120
mbs_shp_path = '../radios_censales/RADIOS_2010_v2021.shp'

geo_meshblock = geopandas.read_file(mbs_shp_path)

# Add custom base maps to folium
basemaps = {
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    )
}


def create_static_folder_if_not_exists():
    # Specific path to create static folder for the maps
    file_path = './public/meshblock_map/'
    if not os.path.exists(file_path):
        # Create the folder if it does not exist
        os.makedirs(file_path)


def check_file_existance(file_name:str, ext:str) -> bool:
    try:
        fileObj = Path(f"./public/meshblock_map/{file_name}.{ext}")
        return fileObj.exists()
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False


def get_meshblock_data(meshblock_id:str) -> geopandas.GeoSeries:
    meshblock_data = geo_meshblock[geo_meshblock.COD_2010 == meshblock_id]
    return meshblock_data


def get_center_bounds(data:geopandas.GeoSeries) -> list:
    bounds = data.geometry.bounds
    lon_min = bounds['minx']
    lat_min = bounds['miny']
    lon_max = bounds['maxx']
    lat_max = bounds['maxy']
    
    center_bound = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
        
    return center_bound


def generate_meshblock_map_html(meshblock_id:str, zoom_start:float=17):
    """
    Generates a map based on the given coordinates (latitude and longitude) 
    and the census meshblock identifier from to RADIOS_2010_v2021.shp.

    - meshblock_id: str = Identifier of the census meshblock to visualize.
    - zoom_start: float(optional) = Initial zoom level of the map.

    Returns:
    - meshblock_map: folium.Map = Generated map object with the highlighted meshblock.

    """
    try:
        meshblock_filtered = get_meshblock_data(meshblock_id)
        
        center_bound = get_center_bounds(meshblock_filtered)
        
        meshblock_map = folium.Map(
            location=center_bound, 
            zoom_start=zoom_start,
            zoom_control=False,
            titles=None
        )
        
        gdf_mbs_data = geopandas.GeoDataFrame(
            data=meshblock_filtered, geometry='geometry'
        )

        popup = folium.GeoJsonPopup(fields=["COD_2010"])
        
        folium.GeoJson(
            data=gdf_mbs_data,
            style_function=lambda feature:{
                "color": "red",
                "opacity": 0.8,
                "fillColor": "blue",
                "fillOpacity": 0.3
            },
            popup=popup
        ).add_to(meshblock_map)
        
        basemaps['Google Satellite Hybrid'].add_to(meshblock_map)
    
        return meshblock_map
    
    except Exception as exc:
        
        print(f'meshblock: {meshblock_id} does not exist, verify. Exc: {exc}') # TODO cambiar por logger
        return None

def generate_meshblock_img_by_id(meshblock_id:str):
    """
    Generate an image from the meshblock ID.

    - meshblock_id: str = Identifier of the meshblock.

    Returns:
    - meshblock_img: .png = Image of the map with the polygon generated from 
    the meshblock.

    """
    try:
        img_path = f'./public/meshblock_map/{meshblock_id}.png'
        
        meshblockimgexist = check_file_existance(meshblock_id, 'png')
        if meshblockimgexist:
            return True
        
        meshblock_filtered = get_meshblock_data(meshblock_id)
        
        # Crear una figura y un eje
        fig, ax = plt.subplots(figsize=(8, 8), frameon=False)
        meshblock_filtered.plot(ax=ax, color='none')

        # Agregar el fondo del mapa (usando Google Satellite como ejemplo)
        ctx.add_basemap(
            ax, 
            source='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
            crs=4326, 
            zoom=18
        )

        # Agregar el polígono seleccionado al eje
        meshblock_filtered.boundary.plot(
            ax=ax,
            linewidth=2, 
            linestyle="-", 
            edgecolor="red"
        )
        
        # Oculta los valores de los ejes x e y y cualquier otra información
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_axis_off()

        # Guardar la imagen resultante
        plt.savefig(
            img_path,
            dpi=100, 
            bbox_inches='tight'
        )
        
        return True
    except:
        return None


def get_meshblock_map_by_id(meshblock_id:str) -> dict:
    """
    Get the meshblock map using meshblock_id from the public folder; 
    otherwise generate the map.

    - meshblock_id: str = ID to the meshblock. Ex: 020010914

    Returns:
    - meshblock_id: meshblock map url: dict[str, str] = url to meshblock map.
    """
    html_path = f"http://{HOST}:{PORT}/public/meshblock_map/{meshblock_id}.html"

    if check_file_existance(meshblock_id, 'html'):
        return {meshblock_id: html_path}

    meshblock_map = generate_meshblock_map_html(meshblock_id)

    if meshblock_map:
        meshblock_map.save(f'./public/meshblock_map/{meshblock_id}.html')
        return {meshblock_id: html_path}




if __name__ == '__main__':
    import typer
    
    app = typer.Typer()
            
    @app.command()
    def get_map(meshblock_id:str):
        meshblock_map = generate_meshblock_map_html(meshblock_id) # No existe: 069051306; Existe: 068610402
        if meshblock_map is not None:
            create_static_folder_if_not_exists()
            meshblock_map.save(f'./public/meshblock_map/{meshblock_id}.html')
        
        return meshblock_map
    
    
    typer.run(get_map)
    