import hashlib

class HashingService:
    @staticmethod
    def generate_hash(file_path):
        """Genera un hash SHA-256 de un archivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_integrity(file_path, original_hash):
        """Compara el hash actual con el original."""
        current_hash = HashingService.generate_hash(file_path)
        return current_hash == original_hash