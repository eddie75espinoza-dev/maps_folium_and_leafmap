import uvicorn
import webbrowser

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import meshblock_folium



app = FastAPI()

PORT = 5975
HOST = 'localhost'

meshblock_folium.create_static_folder_if_not_exists()
app.mount("/public/meshblock_map", StaticFiles(directory="public/meshblock_map"), name="static")


@app.get("/meshblock_map_url/{meshblock_id}")
def get_meshblock_map_url(meshblock_id:str):
    """Genera la ruta del mapa con el radio censal."""
    meshblock_map_url = meshblock_folium.get_meshblock_map_by_id(meshblock_id)
    
    if meshblock_map_url: 
        return JSONResponse(content=meshblock_map_url, status_code=200)
    else:
        message_error = {'message_error': f'meshblock_id {meshblock_id} not found.'}        
        return JSONResponse(content=message_error, status_code=404)



@app.get(
    "/meshblock_map_img/{meshblock_id}",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Return an image with the meshblock polygon.",
        }
    },
)
async def get_meshblock_map_img(meshblock_id:str):
    meshblockimgexist = meshblock_folium.check_file_existance(meshblock_id, 'png')
    if meshblockimgexist:
        return FileResponse(f"./public/meshblock_map/{meshblock_id}.png", media_type="image/png")
    else:
        img_response = meshblock_folium.generate_meshblock_img_by_id(meshblock_id)
        if img_response:
            return FileResponse(f"./public/meshblock_map/{meshblock_id}.png", media_type="image/png")
        else:
            return JSONResponse(status_code=404, content={"message": "meshblock_id not found"})


@app.get("/show_meshblock_map/{meshblock_id}")
def get_meshblock_map(meshblock_id:str):
    """Genera la ruta y muestra en una nueva pestaña el mapa con el radio censal."""
    meshblockmapexist = meshblock_folium.check_file_existance(meshblock_id, 'html')
    html_path = f"http://{HOST}:{PORT}/public/meshblock_map/{meshblock_id}.html"
    url_response = {'meshblock_map_url': html_path}
    
    if meshblockmapexist:
        webbrowser.open(html_path, new=2)
        
        return JSONResponse(content=url_response, status_code=200)
    else:
        meshblock_map = meshblock_folium.generate_meshblock_map_html(meshblock_id)
        
        if meshblock_map:
            meshblock_map.save(f'./public/meshblock_map/{meshblock_id}.html')
            webbrowser.open(html_path, new=2)
            
            return JSONResponse(content=url_response, status_code=200)
        
        else:
            message_error = {'message_error': f'meshblock_id {meshblock_id} not found.'}
            
            return JSONResponse(content=message_error, status_code=404)
        
 
@app.get("/meshblock_map_html/{meshblock_id}")
def get_meshblock_map_html(meshblock_id:str):
    """Genera y guarda el mapa con el radio censal, en version HTML."""
    meshblock_map = meshblock_folium.generate_meshblock_map_html(meshblock_id)
    
    if meshblock_map:
        html_content = meshblock_map.save(f'./public/meshblock_map/{meshblock_id}.html')

        return HTMLResponse(content=html_content, status_code=200)
    else:
        message_error = {'message_error': f'meshblock_id {meshblock_id} not found.'}
        
        return JSONResponse(content=message_error, status_code=404)


if __name__ == "__main__":
    config = uvicorn.Config("fast_main:app", port=PORT, reload=True)
    server = uvicorn.Server(config)
    server.run()