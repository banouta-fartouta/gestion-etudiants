"""Generate local demo credentials; never overwrite an existing .env."""
from pathlib import Path
import secrets
root = Path(__file__).resolve().parents[1]
password = secrets.token_hex(24)
key = secrets.token_hex(32)
with (root / '.env').open('x', encoding='utf-8') as f:
    f.write(f'POSTGRES_PASSWORD={password}\nSECRET_KEY={key}\nDATABASE_URL=postgresql+psycopg://etudiant:{password}@postgres-service:5432/etudiantsdb\n')
print('.env created locally. Do not publish it.')
