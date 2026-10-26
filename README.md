# Ciclos de la economía argentina — Tendencia, tipos de ciclo y puntos de giro

Visor interactivo, autocontenido y sin dependencias de compilación, para estimar la tendencia, extraer el ciclo y fechar los puntos de giro del PIB trimestral del INDEC, del Estimador Mensual de Actividad Económica (EMAE) como serie coincidente y del Índice Líder de la Universidad Torcuato Di Tella, según las tres nociones de ciclo de la literatura: clásico, de crecimiento y de tasas (Harding y Pagan, 2002; Zarnowitz y Ozyildirim, 2006).

**[▶ Abrir el visor](https://fcontiggiani.github.io/ciclo-argentina/ciclos.html)**

![Captura del visor de ciclos de la economía argentina, mostrando el panel de controles (series, ventana de datos, método de tendencia y tipo de ciclo) y los paneles del PIB y del EMAE en el ciclo de crecimiento, con los picos y valles fechados y las contracciones sombreadas](screenshot-visor.png)

---

## Descripción

La herramienta reúne en un mismo eje temporal tres series de la economía argentina:

| Serie | Papel | Frecuencia | Período | Fuente |
|---|---|---|---|---|
| PIB a precios de 2004, desestacionalizado | Referencia | Trimestral | 1993 T1 – último dato | INDEC (bases 1993 y 2004, empalmadas) |
| EMAE, desestacionalizado | Coincidente | Mensual | ene 2004 – último dato | INDEC |
| Índice Líder | Líder | Mensual | ene 1993 – jul 2021 | CIF, Universidad Torcuato Di Tella |

Sobre una **ventana de datos** elegida por quien la usa, la herramienta estima la tendencia de cada serie y construye el ciclo según una de tres definiciones:

```
Clásico:        y(t)
Crecimiento:    c(t) = 100 · [ln y(t) − τ(t)]
Tasas:          g(t) = 100 · [y(t) / y(t − s) − 1],   s = 4 trimestres o 12 meses
```

Sobre la serie que se muestra, fecha los **picos y valles** con una versión simplificada del algoritmo de Bry y Boschan (1971). Luego compara los giros del EMAE y del Índice Líder con los del PIB (adelanto o rezago) y contrasta, para cada serie, las fechas que surgen de los tres tipos de ciclo.

El objetivo didáctico es hacer visible que **los puntos de giro dependen de la definición de ciclo**. En torno a un pico, la tasa interanual gira antes que el desvío respecto de la tendencia, y este antes que el nivel. Además, el ciclo de crecimiento hereda las propiedades —y los problemas en los extremos de la muestra— del método de tendencia elegido. Como cada estimación usa solo los datos de la ventana, desplazar las cotas permite apreciar la sensibilidad de las fechas a la muestra disponible en tiempo real.

## Características principales

| Panel / control | Descripción |
|---|---|
| **Series** | Casillas para mostrar u ocultar el PIB (referencia), el EMAE (coincidente) y el Índice Líder UTDT (líder); cada serie se dibuja en su propio panel con eje vertical independiente y eje temporal compartido. |
| **Ventana de datos** | Cotas inferior y superior con resolución mensual y atajos (toda la muestra, 1993–2003, 2004–hoy, período con Índice Líder). La ventana define la muestra con la que se estiman la tendencia y los giros. |
| **Tendencia** | Hodrick–Prescott (λ trimestral seleccionable, reescalado para series mensuales), filtro de Hamilton, tendencia log-lineal, log-cuadrática y media móvil centrada; casilla para mostrar u ocultar su gráfica. |
| **Tipo de ciclo** | Clásico (nivel, con escala logarítmica opcional), de crecimiento (desvío porcentual respecto de la tendencia) o de tasas (variación interanual, con la tasa de la tendencia como referencia). |
| **Puntos de giro** | Picos (▼) y valles (△) fechados con reglas de Bry–Boschan sobre la serie que se muestra; sombreado opcional de las fases de contracción (de cada pico al valle siguiente). |
| **Resumen por serie** | Tarjetas con el número de picos y valles, la duración media de las expansiones y contracciones, y la tabla de giros con su valor. |
| **Concordancia con el PIB** | Para cada giro del PIB, giro del mismo tipo más cercano en el EMAE y en el Índice Líder, con el desfase en meses (negativo = adelanto) y su mediana. |
| **Contraste entre tipos de ciclo** | Tabla por serie con las fechas de cada giro según el ciclo de tasas, de crecimiento y clásico, el desfase en meses respecto del ciclo de crecimiento y su mediana para picos y valles; la columna del ciclo que muestra el gráfico aparece resaltada. |
| **Tema claro / oscuro** | Conmutador persistido por navegador; recolorea los paneles de ECharts en vivo. |

## Fundamento teórico

### Tres nociones de ciclo

1. **Ciclo clásico** (Burns y Mitchell, 1946): alternancia de expansiones y contracciones en el **nivel** de la actividad. Un pico es un máximo local de *y(t)* y marca el inicio de una caída absoluta.
2. **Ciclo de crecimiento**: fluctuaciones del **desvío respecto de la tendencia**, *c(t) = 100 · [ln y(t) − τ(t)]*. Un pico marca el momento en que la economía deja de crecer por encima de su tendencia, aunque siga creciendo en nivel. Es la noción que emplea el sistema de indicadores líderes compuestos de la OCDE.
3. **Ciclo de tasas**: fluctuaciones de la **tasa de variación interanual**. Un pico marca el máximo de la velocidad de crecimiento.

Como la tasa aproxima la derivada del nivel y el desvío resta al nivel una tendencia suave, en torno a un pico se espera la secuencia **tasas → crecimiento → clásico**. Por eso el ciclo de crecimiento ocupa una posición intermedia y sirve de referencia en la tabla de contraste.

### Métodos de tendencia

Todos se estiman sobre el logaritmo de la serie y **solo con los datos de la ventana elegida**:

| Método | Definición | Parámetros |
|---|---|---|
| Hodrick–Prescott (1997) | min Σ [ln y(t) − τ(t)]² + λ Σ [Δ²τ(t)]² | λ trimestral seleccionable; para series mensuales se multiplica por 3⁴ (Ravn y Uhlig, 2002): 1600 → 129 600 |
| Filtro de Hamilton (2018) | τ(t + h) = valor ajustado de regresar ln y(t + h) sobre 1, ln y(t), …, ln y(t − p + 1) | h = 2 años, p = 1 año |
| Log-lineal / log-cuadrática | Mínimos cuadrados de ln y(t) sobre un polinomio en *t* | Grado 1 o 2 |
| Media móvil centrada | Media de 2 × m términos | m = 2, 3, 5 u 8 años |

### Fechado de los puntos de giro

Versión simplificada del algoritmo de Bry y Boschan (1971), aplicada a la serie que se grafica:

1. **Candidatos**: extremos locales en una ventana de ±5 meses (±2 trimestres para el PIB).
2. **Alternancia**: entre dos giros consecutivos del mismo tipo se conserva el más extremo.
3. **Censura**: fase mínima de 6 meses (2 trimestres), ciclo mínimo de 15 meses (5 trimestres) y ningún giro a menos de 6 meses (2 trimestres) de los extremos de la ventana.

Para el PIB trimestral las reglas siguen a Harding y Pagan (2002). El algoritmo omite el suavizado previo (curva de Spencer y medias móviles) del procedimiento original.

### Concordancia y contraste

- **Concordancia con el PIB.** Para cada giro del PIB se busca el giro del mismo tipo más cercano en el EMAE y en el Índice Líder, entre 24 meses antes y 12 meses después, sin reutilizar giros. El desfase se mide en meses contra el mes central del trimestre.
- **Contraste entre tipos de ciclo.** Para cada serie se fechan los giros sobre la tasa, el desvío y el nivel, con la misma ventana y el mismo método de tendencia. Los giros del mismo tipo separados por hasta 18 meses se agrupan en una fila, con el ciclo de crecimiento como ancla (o el clásico, si aquel no registra giros).

## Estructura del repositorio

```
.
├── index.html                    # Visor completo (HTML + CSS + JavaScript + ECharts + datos)
├── screenshot-visor.png          # Captura usada en este documento
├── data/
│   ├── series.json               # Copia de los datos en JSON (generada por el script)
│   └── raw/                      # Series crudas en CSV
│       ├── pib_base2004_trim.csv
│       ├── pib_base1993_trim.csv
│       ├── emae_desest_mensual.csv
│       └── indice_lider_utdt.csv
├── scripts/
│   └── actualizar_datos.py       # Descarga, empalme, exportación e incrustación de los datos
├── requirements.txt              # Dependencias del script (pandas, requests)
├── .github/workflows/
│   └── actualizar-datos.yml      # Actualización mensual automática
├── README.md                     # Este documento
└── LICENSE                       # Licencia MIT
```

`index.html` es un **único archivo autocontenido**. Las tres series van incrustadas en un bloque `<script type="application/json" id="datos-series">` y la biblioteca de gráficos está embebida. Por eso funciona abierto con doble clic, sin servidor ni conexión, y puede distribuirse por correo o subirse al aula virtual. Solo las tipografías se descargan de Google Fonts; sin conexión se usan las del sistema.

### Actualización de los datos

**PIB y EMAE (automática).** El script descarga las series del INDEC desde la [API de Series de Tiempo de Argentina](https://datos.gob.ar/series) y empalma el PIB. Luego regenera `data/series.json` y reemplaza el bloque de datos dentro de `index.html`, sin modificar el resto de la página:

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/actualizar_datos.py             # Con descarga
python scripts/actualizar_datos.py --offline   # Solo reconstruye a partir de data/raw/
```

El *workflow* `.github/workflows/actualizar-datos.yml` ejecuta el script el día 25 de cada mes y hace *commit* de `data/` e `index.html` si hubo cambios. También puede lanzarse a mano desde la pestaña **Actions**. Para que pueda escribir en el repositorio, hay que habilitar **Settings → Actions → General → Workflow permissions → Read and write permissions**.

Identificadores de la API utilizados (deben verificarse si la descarga falla, porque pueden cambiar):

| Serie | Identificador |
|---|---|
| PIB desestacionalizado, base 2004, trimestral | `3.2_OGP_D_2004_T_17` |
| PIB desestacionalizado, base 1993, trimestral | `1.2_OGP_D_1993_T_17` |
| EMAE desestacionalizado, base 2004, mensual | `143.3_NO_PR_2004_A_31` |

**Índice Líder (manual).** El Índice Líder no está disponible en la API. Para actualizarlo hay que descargar la serie histórica del sitio del Centro de Investigación en Finanzas (CIF) de la UTDT. Con ella se reemplaza `data/raw/indice_lider_utdt.csv`, conservando sus columnas `indice_tiempo` (`AAAA-MM-DD`) e `indice_lider`, y se vuelve a ejecutar el script.

## Stack técnico

- **JavaScript vanilla** (sin frameworks ni transpilación). Se usa para:
  - el filtro de Hodrick–Prescott, resuelto con una factorización LDLᵀ de banda, de costo lineal en *n*;
  - el filtro de Hamilton y las tendencias polinómicas, por mínimos cuadrados con eliminación gaussiana y pivoteo parcial;
  - la media móvil centrada 2 × m;
  - el fechado de Bry–Boschan.
- **[Apache ECharts](https://echarts.apache.org/) 5.4.3**, embebido en `index.html`, para los paneles apilados con eje temporal compartido, el sombreado de contracciones y los marcadores de giro.
- **Google Fonts**: IBM Plex Sans Condensed (títulos), IBM Plex Sans (interfaz), IBM Plex Mono (valores numéricos).
- **Python ≥ 3.10** con `pandas` y `requests` para el script de datos; **GitHub Actions** para la actualización programada.
- Sin dependencias de servidor: todo el cálculo se ejecuta en el navegador del usuario.

## Notas metodológicas y limitaciones conocidas

- **Empalme del PIB.** La serie larga toma la base 2004 desde 2004 T1 y, hacia atrás, aplica las tasas de variación de la base 1993: *Y(t) = Y₂₀₀₄(t₀) · Y₁₉₉₃(t) / Y₁₉₉₃(t₀)*, con *t₀* = 2004 T1. Conserva exactamente las tasas de la base 1993, pero no corrige las diferencias de estructura de precios relativos entre ambas bases.
- **Emergencia estadística.** Las series de actividad del período 2007–2015 fueron revisadas por el INDEC tras la emergencia estadística de 2016; los giros de ese período deben leerse con esa salvedad.
- **Índice Líder.** La versión incluida corresponde a la planilla publicada por el CIF-UTDT en 2021 (último dato: julio de 2021). El CIF revisa la serie hacia atrás, de modo que una versión nueva puede alterar las fechas de los giros.
- **Problema de los extremos.** Hodrick–Prescott, las tendencias polinómicas y la media móvil son filtros bilaterales. Cerca del final de la ventana, la tendencia —y con ella el ciclo de crecimiento— se revisa al incorporar datos nuevos. El filtro de Hamilton es unilateral, pero pierde los primeros tres años de la ventana.
- **Fechado simplificado.** El algoritmo omite el suavizado previo de Bry–Boschan y aplica reglas de censura uniformes; las fechas no sustituyen a una cronología oficial de ciclos.
- **Frecuencias mixtas.** Los desfases entre series mensuales y el PIB trimestral se miden contra el mes central del trimestre, por lo que tienen una imprecisión de ±1 mes.
- **Verificación.** Las implementaciones en JavaScript se contrastaron con `statsmodels`, `numpy` y una implementación de referencia en Python: las diferencias son del orden de 1e-10 o menores y los puntos de giro coinciden.

## Referencias

Bry, G., & Boschan, C. (1971). *Cyclical analysis of time series: Selected procedures and computer programs*. National Bureau of Economic Research.

Burns, A. F., & Mitchell, W. C. (1946). *Measuring business cycles*. National Bureau of Economic Research.

Hamilton, J. D. (2018). Why you should never use the Hodrick-Prescott filter. *Review of Economics and Statistics*, *100*(5), 831–843.

Harding, D., & Pagan, A. (2002). Dissecting the cycle: A methodological investigation. *Journal of Monetary Economics*, *49*(2), 365–381.

Hodrick, R. J., & Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, *29*(1), 1–16.

Ravn, M. O., & Uhlig, H. (2002). On adjusting the Hodrick-Prescott filter for the frequency of observations. *Review of Economics and Statistics*, *84*(2), 371–376.

Zarnowitz, V., & Ozyildirim, A. (2006). Time series decomposition and measurement of business cycles, trends and growth cycles. *Journal of Monetary Economics*, *53*(7), 1717–1739.

## Autoría

Federico Contiggiani — Universidad Nacional de Río Negro (UNRN)

## Licencia

El código se distribuye bajo licencia [MIT](https://opensource.org/licenses/MIT) (véase `LICENSE`). Apache ECharts, incluido en `index.html`, se distribuye bajo licencia [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Los datos pertenecen a sus fuentes (INDEC y CIF-UTDT) y se redistribuyen con fines académicos, citando su origen.
