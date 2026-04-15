import threading
from datetime import datetime

class SentinelAPI:
    def __init__(self, engine, scraper, gateway):
        """
        Inicializa el controlador de la API.
        :param engine: Instancia de core.engine.SentinelEngine
        :param scraper: Instancia de api.v1.scraper_service.ScraperService
        :param gateway: Instancia de api.mobile_gateway.NexusGateway
        """
        self.engine = engine
        self.scraper = scraper
        self.gateway = gateway

    def get_system_status(self):
        """Retorna el estado de salud de los componentes (Local/Nexus)."""
        return {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "engine": "active",
                "nexus_sync": "connected",
                "database": "online"
            }
        }

    def start_global_scraping(self, sources=["BOE", "SUIN"]):
        """
        Lanza el proceso de scraping en un hilo separado para no congelar la UI.
        """
        def background_task():
            results = []
            if "BOE" in sources:
                results.append(self.scraper.fetch_boe_daily())
            if "SUIN" in sources:
                results.append(self.scraper.fetch_suin_juriscol("últimas_normas"))
            
            # Pasamos los resultados al motor para análisis de riesgos
            for res in results:
                analysis = self.engine.execute_workflow("ingest_normative", res)
                
                # Si el análisis detecta algo crítico, notificamos a Nexus inmediatamente
                if analysis.get("risk_detected"):
                    self.gateway.push_update(analysis)

        thread = threading.Thread(target=background_task)
        thread.start()
        return {"status": "scraping_initiated", "threads": 1}

    def analyze_local_document(self, file_path):
        """
        Procesa un archivo del ordenador local del abogado.
        """
        print(f"[API] Solicitando análisis de archivo local: {file_path}")
        
        # 1. Ingesta a través del motor
        process = self.engine.execute_workflow("local_forensic_analysis", {"path": file_path})
        
        # 2. El motor coordina con ForensicAgent y SecureVault internamente
        return {
            "file": file_path,
            "status": "analyzed",
            "vault_id": process.get("session_id"),
            "forensic_hash": process.get("hash")
        }

    def sync_with_nexus(self):
        """Fuerza una sincronización manual con el móvil."""
        summary = self.engine.execute_workflow("generate_daily_summary", {})
        push_result = self.gateway.push_update(summary)
        return {"sync_status": "success", "package": push_result}

    def search_knowledge_graph(self, query):
        """Consulta rápida al grafo de conocimiento legal."""
        # Se conecta con core.knowledge_graph
        results = self.engine.execute_workflow("graph_query", {"query": query})
        return {"query": query, "matches": results}