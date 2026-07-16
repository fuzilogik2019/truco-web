# Web del mod Truco Argentino

Sitio **estático y serverless** (un solo `index.html` + assets pixel art) para
desplegar en **Amazon S3** con static website hosting. Sin build, sin
dependencias, sin backend.

## Qué versiona este repo

Solo lo necesario para publicar el sitio. Las herramientas de desarrollo, las
fuentes de arte (`.aseprite`) y los assets sin usar quedan en local, fuera del
repo (ver [`.gitignore`](.gitignore)).

```
truco-web/
├── index.html          # todo el sitio: HTML + CSS + JS embebidos
├── assets/
│   ├── header_logo.png # wordmark del hero y la barra
│   ├── mate.png
│   ├── cards/          # los 40 sprites de la baraja española + back.png
│   └── mc/
│       ├── mesa_iso.png    # la Mesa de Truco en isométrico (resultado del crafteo)
│       └── icons/          # íconos de Minecraft (McIcons, MIT)
├── deploy.ps1          # deploy a S3 (crea el bucket con -Create)
├── .gitignore
└── README.md
```

## Probar en local

```powershell
python -m http.server 8735 --directory .
# → http://localhost:8735
```

## Deploy a S3

Necesitás el [AWS CLI](https://aws.amazon.com/cli/) configurado (`aws configure`).

**Primera vez** — crea el bucket, habilita website hosting y aplica la policy pública:

```powershell
.\deploy.ps1 -Bucket truco-argentino-web -Region us-east-1 -Create
```

**Deploys siguientes** — solo sincroniza los archivos (incremental, con `--delete`):

```powershell
.\deploy.ps1 -Bucket truco-argentino-web
```

El script sube **solo lo necesario** (mismos filtros que `.gitignore`): assets con
cache largo e `index.html` con cache corto para que se actualice enseguida.

URL resultante: `http://<bucket>.s3-website-<region>.amazonaws.com`

### HTTPS / dominio propio (opcional)

S3 website hosting es HTTP-only. Para HTTPS o dominio propio, poné **CloudFront**
adelante (origin = el endpoint *website* del bucket) con un certificado de ACM en
`us-east-1`, e invalidá `/index.html` en cada deploy:

```powershell
aws cloudfront create-invalidation --distribution-id XXXX --paths "/index.html"
```

## Editar el contenido

Todo vive en `index.html` (features, comandos, roadmap). Si el mod suma o cambia
sprites, re-copiá desde
`truco-fabric/src/main/resources/assets/truco/textures/gui/cards/`.

## Créditos

- Baraja española pixel art por [J. Canabal](https://jcanabal.itch.io/spanish-deck-pixel-art).
- Íconos de Minecraft por [McIcons](https://github.com/themuhamed/mcicons) (MIT).
- Mod [Truco Argentino](https://github.com/fuzilogik2019/truco-minecraft) — © Fuzilogik (MIT).
