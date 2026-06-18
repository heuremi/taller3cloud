# Drive Clone

Clon de drive para el taller de Cloud Computing. 
Permite subir archivos con drag and drop y guardarlos en un bucket S3 levantado con LocalStack. 
El bucket se crea con Terraform y todo corre en Docker.

## Herramientas necesarias

- Docker y Docker Compose
- Terraform

## Cómo levantarlo

1. Levantar LocalStack y el backend:

```
docker compose up -d --build
```

2. Crear el bucket con Terraform:

```
cd terraform
terraform init
terraform apply -auto-approve
cd ..
```

3. Abrir http://localhost:8000 en el navegador.

## Variables de entorno

El backend usa estas variables, ya configuradas en el docker-compose:

- S3_ENDPOINT: endpoint de LocalStack (http://localstack:4566 dentro de Docker)
- S3_BUCKET: nombre del bucket (drive-clone-bucket)
- AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY: credenciales test / test
- AWS_DEFAULT_REGION: region us-east-1

Si corre el backend fuera de Docker, usar S3_ENDPOINT=http://localhost:4566.

## Estructura

- backend/: API en FastAPI (subida, listado y descarga)
- frontend/: interfaz con drag and drop
- terraform/: definicion del bucket S3
- docker-compose.yml: LocalStack y backend

## Detener

```
docker compose down
```

*Para volver a levantar hay que correr de nuevo terraform apply para recrear el bucket.