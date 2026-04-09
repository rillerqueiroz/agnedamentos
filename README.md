# Sistema de Gestão de RH

API completa para RH com:

- Cadastro de colaboradores.
- Registro de horas extras.
- Registro de faltas.
- Registro de atestados médicos.
- Dashboard individual do colaborador (situação atual na empresa).
- Batida de ponto pelo portal interno.
- Batida de ponto por integração com localização enviada via WhatsApp (Evolution API).
- Validação de geolocalização (geofence da empresa).

## Stack

- FastAPI
- SQLAlchemy
- SQLite (padrão)
- Pytest

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`.

## Variáveis de ambiente

- `COMPANY_LAT`: latitude da empresa (padrão `-23.55052`)
- `COMPANY_LON`: longitude da empresa (padrão `-46.633308`)
- `GEOFENCE_RADIUS_M`: raio permitido em metros para validar ponto (padrão `300`)

Exemplo:

```bash
export COMPANY_LAT=-23.55052
export COMPANY_LON=-46.633308
export GEOFENCE_RADIUS_M=250
```

## Principais endpoints

### Colaboradores

- `POST /collaborators`
- `GET /collaborators/{id}`
- `GET /collaborators/{id}/dashboard`

### RH administrativo

- `POST /overtime`
- `POST /absences`
- `POST /medical-certificates`

### Ponto

- `POST /time-punches/portal` (ponto pelo módulo do colaborador)
- `POST /integrations/evolution/time-punch` (ponto via WhatsApp + Evolution)

## Fluxo da integração WhatsApp (Evolution)

1. O colaborador envia sua localização atual no WhatsApp.
2. A Evolution encaminha evento para `POST /integrations/evolution/time-punch`.
3. O backend registra latitude/longitude e valida se está dentro do raio geográfico permitido.
4. O RH pode auditar pelo campo `within_geofence`.

Payload sugerido:

```json
{
  "collaborator_id": 1,
  "latitude": -23.5506,
  "longitude": -46.6332,
  "event_id": "msg_123",
  "raw_payload": {
    "source": "evolution",
    "chat": "5511999999999@c.us"
  }
}
```

## Observações de produção

- Adicionar autenticação (JWT + perfis RH/colaborador).
- Adicionar armazenamento de documentos de atestado (S3, GCS etc).
- Configurar banco robusto (PostgreSQL).
- Adicionar trilha de auditoria e LGPD.
