# Mundial 2026 — Resultados automáticos

Esto actualiza solo los resultados del Mundial cada 15 minutos y los muestra
en una página web. Tú no tienes que tocar nada después de configurarlo.

## Cómo queda armado

```
GitHub (cada 15 min)  →  actualizar_resultados.py  →  resultados.json
                                                            ↓
                                            Tu página (Netlify) lo lee
```

## Paso 1 — Sácate tu API key gratis

1. Ve a https://www.football-data.org/client/register
2. Pon tu nombre y correo, envía el formulario.
3. Te llega la "API Token" (o "X-Auth-Token") al correo. Cópiala, la vas a
   necesitar en el Paso 3.

## Paso 2 — Sube este proyecto a GitHub

1. Crea tu cuenta en https://github.com/signup (si no la tienes).
2. Crea un repositorio nuevo (botón verde "New repository"). Le puedes poner
   `mundial2026`. Puede ser público o privado, los dos funcionan igual aquí.
3. Sube estos 4 archivos sueltos a ese repositorio (botón "Add file" →
   "Upload files", arrastrándolos):
   - `actualizar_resultados.py`
   - `resultados.json`
   - `index.html`
   - `README.md`
   Y dale "Commit changes".
4. Ahora sube la carpeta `img` con las dos imágenes del encabezado
   (`img/logo-lazaro.png` y `img/cartel-fiesta-futbol.jpg`). Otra vez
   "Add file" → "Upload files", y arrastra esos 2 archivos — GitHub
   normalmente respeta la carpeta `img/` si arrastras la carpeta completa;
   si solo te deja arrastrar archivos sueltos, escribe `img/` antes del
   nombre del archivo en el cuadro de texto que aparece antes de subir,
   igual que harás con la carpeta `.github` en el siguiente paso.
5. Por último sube el archivo del robot, respetando su ruta exacta:
   "Add file" → "Upload files", arrastra `actualizar.yml`, y en el campo de
   nombre escribe la ruta completa:
   ```
   .github/workflows/actualizar.yml
   ```
   GitHub crea las carpetas solas con solo escribir esa ruta.
   Click en "Commit changes".

## Paso 3 — Guarda tu API key como "Secret" (privado y seguro)

1. En tu repositorio de GitHub: Settings → Secrets and variables → Actions.
2. Click en "New repository secret".
3. Name: `FOOTBALL_DATA_API_KEY`
4. Value: pega la clave que te llegó por correo en el Paso 1.
5. Guardar.

Esto es importante: la clave NUNCA queda visible en tu código ni en tu
página. Solo el robot de GitHub la puede leer al momento de correr el script.

## Paso 4 — Activa el robot (GitHub Actions)

1. Ve a la pestaña "Actions" de tu repositorio.
2. Si GitHub pregunta si quieres habilitar workflows, dile que sí.
3. Busca el workflow "Actualizar resultados Mundial 2026".
4. Click en "Run workflow" para probarlo manualmente la primera vez.
5. Espera 1-2 minutos y revisa que `resultados.json` se haya actualizado
   (vas a ver un nuevo commit en el repo hecho por "github-actions[bot]").

Después de esta primera prueba manual, el robot corre solo cada 15 minutos,
para siempre, sin que hagas nada.

## Paso 5 — Conecta tu página con el archivo de resultados

Dentro de `index.html` hay esta línea:

```js
const URL_RESULTADOS = "resultados.json";
```

Tienes dos opciones:

**Opción A (recomendada): subir resultados.json junto con index.html a Netlify**
Si subes ambos archivos juntos a Netlify, deja la línea como está
(`"resultados.json"`) — pero ojo: Netlify NO se actualiza solo cuando
GitHub cambia el archivo. Esta opción solo sirve si conectas tu sitio de
Netlify directo a tu repo de GitHub (Netlify → "Import from Git"), porque
así Netlify sí vuelve a publicar cada vez que el robot actualiza el JSON.

**Opción B (más simple, recomendada si subes los archivos a mano a Netlify):**
Cambia esa línea para que apunte directo al archivo en GitHub (no necesitas
volver a subir nada a Netlify nunca, el archivo siempre se lee fresco):

```js
const URL_RESULTADOS = "https://raw.githubusercontent.com/TU-USUARIO/TU-REPO/main/resultados.json";
```

Sustituye `TU-USUARIO` y `TU-REPO` por los tuyos. Esta es la opción que te
recomiendo porque es la más sencilla de mantener: subes `index.html` una
sola vez a Netlify (arrastrándolo a netlify.com/drop, como ya sabes hacerlo)
y nunca lo vuelves a tocar.

## ¿Y si quiero que sea aún más rápido?

El workflow ya está configurado para correr cada 5 minutos:

```yaml
- cron: "*/5 * * * *"
```

Con tu volumen de tráfico (bajo) y el límite de la API (10 llamadas/minuto,
y el script solo hace 1 llamada por corrida) esto no representa ningún
riesgo de saturación.

Nota: GitHub Actions no garantiza el minuto exacto cuando hay mucha carga
en su infraestructura global — a veces una corrida programada para cada
5 minutos tarda 6-8 minutos en disparar. Para tu caso (revisas resultados
hasta 30 minutos después del partido) esto no importa en absoluto.

Si quisieras bajarlo más (ej. cada 2-3 minutos) técnicamente se puede, pero
no aporta nada real ya que GitHub no lo va a disparar con esa precisión de
todas formas — 5 minutos es el punto dulce.

## Nota sobre el tier gratis de football-data.org

- Incluye el Mundial FIFA sin costo.
- 10 llamadas por minuto (nosotros usamos 1 por corrida, sobra margen).
- Los datos pueden tener algunos minutos de retraso respecto al marcador
  real en el estadio — para tu caso (revisas tú mismo hasta 30 min después
  del partido) esto no representa ningún problema.
