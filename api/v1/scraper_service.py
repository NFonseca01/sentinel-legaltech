import httpx
from bs4 import BeautifulSoup
import asyncio
import os

class ScraperService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Sentinel-LegalTech/1.0 (Professional Legal Tool; contact@sentinel.local)"
        }
        # Timeouts extendidos para portales gubernamentales que suelen ser lentos
        self.timeout = httpx.Timeout(20.0, read=30.0)

    async def fetch_boe_daily(self):
        """
        Extrae el sumario del Boletín Oficial del Estado (España).
        Utiliza el endpoint XML para obtener datos estructurados y fiables.
        """
        url = "https://www.boe.es/diario_boe/xml.php"
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parseo básico del XML del BOE
                soup = BeautifulSoup(response.content, "xml")
                items = []
                for diario in soup.find_all("diario"):
                    items.append({
                        "fecha": diario.get("fecha"),
                        "sumario": "Sumario diario capturado"
                    })
                return {"source": "BOE", "status": "success", "data": items}
            except Exception as e:
                return {"source": "BOE", "status": "error", "message": str(e)}

    async def fetch_suin_juriscol(self, law_id=""):
        """
        Extrae normativa del Sistema Único de Información Normativa (Colombia).
        """
        # Ejemplo de URL de búsqueda o documento específico
        url = f"https://www.suin-juriscol.gov.co/viewDocument.asp?id={law_id}"
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                # Intentamos extraer el título de la norma o el cuerpo principal
                title = soup.title.string if soup.title else "Documento SUIN"
                
                return {
                    "source": "SUIN-Juriscol",
                    "status": "success",
                    "title": title,
                    "url": url
                }
            except Exception as e:
                return {"source": "SUIN", "status": "error", "message": str(e)}

    def scan_local_normative(self, directory):
        """
        Escanea el disco local del abogado buscando normativa interna.
        Método síncrono para facilitar la integración con el explorador de archivos.
        """
        if not os.path.exists(directory):
            return {"status": "error", "message": "Directorio no encontrado"}

        found_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.pdf', '.docx', '.txt')):
                    found_files.append({
                        "name": file,
                        "path": os.path.join(root, file),
                        "size": os.path.getsize(os.path.join(root, file))
                    })
        
        return {"source": "Local-System", "status": "success", "count": len(found_files), "files": found_files}

    async def run_full_sync(self):
        """Ejecuta una sincronización completa de todas las fuentes externas."""
        results = await asyncio.gather(
            self.fetch_boe_daily(),
            self.fetch_suin_juriscol("30046030") # Ejemplo de ID normativo
        )
        return results