# Ciclos de la economía argentina

Visor interactivo de los ciclos económicos de la Argentina a partir de tres series:

| Serie | Papel | Frecuencia | Período | Fuente |
|---|---|---|---|---|
| PIB a precios de 2004, desestacionalizado | Referencia | Trimestral | 1993 T1 – último dato | INDEC (bases 1993 y 2004, empalmadas) |
| EMAE, desestacionalizado | Coincidente | Mensual | ene 2004 – último dato | INDEC |
| Índice Líder | Líder | Mensual | ene 1993 – jul 2021 | CIF, Universidad Torcuato Di Tella |

La página permite:

- **elegir una ventana de datos** (cotas inferior y superior), que define la muestra con la que se estiman la tendencia y los puntos de giro;
- **elegir el método de tendencia**: Hodrick–Prescott (λ seleccionable), filtro de Hamilton, tendencia log-lineal, log-cuadrática o media móvil centrada, y **mostrar u ocultar su gráfica**;
- **elegir el tipo de ciclo**: clásico (nivel), de crecimiento (desvío respecto de la tendencia) o de tasas (variación interanual);
- **ver los puntos de giro** de las tres series, fechados con el algoritmo de Bry y Boschan, con las contracciones sombreadas;
- **comparar** los giros del EMAE y del Índice Líder con los del PIB (adelanto o rezago en meses);
- **contrastar las fechas de los giros de cada serie entre los tres tipos de ciclo** (tasa, crecimiento y nivel), con el desfase en meses respecto del ciclo de crecimiento;
- **cambiar el fondo** entre claro y oscuro.

Toda la aplicación está en **un único archivo HTML autocontenido** (`index.html`), que incluye los estilos, el código, la biblioteca de gráficos y los datos. Funciona abierto directamente desde el disco, sin conexión ni servidor, y se publica tal cual con GitHub Pages.

---

## Estructura del repositorio

```
.
├── index.html                    # Página autocontenida: estilos, código, ECharts y datos incluidos
├── data/
│   ├── series.json               # Copia de los datos en JSON (el script la genera junto con index.html)
│   └── raw/                      # Series crudas en CSV
│       ├── pib_base2004_trim.csv
│       ├── pib_base1993_trim.csv
│       ├── emae_desest_mensual.csv
│       └── indice_lider_utdt.csv
├── scripts/
│   └── actualizar_datos.py       # Descarga, empalme, exportación e incrustación de los datos
├── requirements.txt
├── .github/workflows/
│   └── actualizar-datos.yml      # Actualización mensual automática
├── LICENSE
└── README.md
```

## Ver la página en la computadora

Basta con abrir `index.html` con doble clic: los datos van incrustados en un bloque `<script type="application/json" id="datos-series">` y la biblioteca de gráficos está embebida, de modo que no hace falta servidor ni conexión a internet (solo las tipografías IBM Plex se descargan de Google Fonts; sin conexión se usan las del sistema). El archivo también puede enviarse por correo o subirse al aula virtual.

## Actualizar los datos

### PIB y EMAE (automático)

El script descarga las series del INDEC desde la [API de Series de Tiempo de Argentina](https://datos.gob.ar/series), empalma el PIB, regenera `data/series.json` y **reemplaza el bloque de datos dentro de `index.html`** (el resto de la página no se modifica):

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/actualizar_datos.py
```

Con `--offline` el script no descarga nada y reconstruye el JSON a partir de `data/raw/`.

El *workflow* `.github/workflows/actualizar-datos.yml` ejecuta el script el día 25 de cada mes y hace *commit* de `data/` e `index.html` si cambiaron. También se puede lanzar a mano desde la pestaña **Actions**. Para que pueda escribir en el repositorio: **Settings → Actions → General → Workflow permissions → Read and write permissions**.

Identificadores usados (verificarlos si la descarga falla, porque la API puede cambiarlos):

| Serie | Identificador |
|---|---|
| PIB desestacionalizado, base 2004, trimestral | `3.2_OGP_D_2004_T_17` |
| PIB desestacionalizado, base 1993, trimestral | `1.2_OGP_D_1993_T_17` |
| EMAE desestacionalizado, base 2004, mensual | `143.3_NO_PR_2004_A_31` |

Para buscar otros identificadores: `https://apis.datos.gob.ar/series/api/search/?q=<términos>`.

### Índice Líder (manual)

El Índice Líder no está en la API. Para actualizarlo, descargar la serie histórica desde el sitio del Centro de Investigación en Finanzas de la UTDT, reemplazar `data/raw/indice_lider_utdt.csv` respetando sus dos columnas (`indice_tiempo` en formato `AAAA-MM-DD` e `indice_lider`) y volver a ejecutar el script. La versión incluida corresponde a la planilla publicada en 2021 (último dato: julio de 2021). El CIF revisa la serie hacia atrás, de modo que los valores de una versión nueva pueden diferir de los actuales.

## Metodología

### Datos

- **PIB.** El INDEC publica el PIB desestacionalizado en base 1993 (1993–2013) y en base 2004 (desde 2004). La serie larga toma la base 2004 desde 2004 T1 y, hacia atrás, aplica las tasas de variación de la base 1993:

  $$Y_t = Y_{t_0}^{2004}\,\frac{Y_t^{1993}}{Y_{t_0}^{1993}}, \qquad t < t_0 = 2004\text{ T1}.$$

  El script verifica que el empalme conserve exactamente las tasas de la base 1993.
- **EMAE.** Serie desestacionalizada, índice 2004 = 100.
- **Advertencia.** Las series de actividad del período 2007–2015 fueron revisadas por el INDEC tras la emergencia estadística de 2016.

### Tendencias

Todas se estiman sobre el logaritmo de la serie y **solo con los datos de la ventana elegida**:

| Método | Definición | Parámetros |
|---|---|---|
| Hodrick–Prescott | $\min_\tau \sum_t (\ln y_t - \tau_t)^2 + \lambda \sum_t (\Delta^2 \tau_t)^2$ | λ trimestral seleccionable; para series mensuales se multiplica por $3^4$ (Ravn y Uhlig, 2002) |
| Filtro de Hamilton (2018) | $\tau_{t+h}$ = valor ajustado de regresar $\ln y_{t+h}$ sobre $1, \ln y_t, \dots, \ln y_{t-p+1}$ | $h$ = 2 años, $p$ = 1 año |
| Log-lineal / log-cuadrática | Mínimos cuadrados de $\ln y_t$ sobre un polinomio en $t$ | Grado 1 o 2 |
| Media móvil centrada | Media de $2 \times m$ términos | $m$ = 2, 3, 5 u 8 años |

### Tipos de ciclo

| Ciclo | Serie graficada | Tendencia mostrada |
|---|---|---|
| Clásico | Nivel $y_t$ | $e^{\tau_t}$ |
| De crecimiento | $c_t = 100\,(\ln y_t - \tau_t)$ | Línea en cero |
| De tasas | $100\,(y_t / y_{t-s} - 1)$, $s$ = 4 o 12 | Tasa interanual de la tendencia |

### Puntos de giro

Versión simplificada del algoritmo de Bry y Boschan (1971), aplicada a la serie que se grafica:

1. candidatos: extremos locales en una ventana de ±5 meses (±2 trimestres para el PIB);
2. alternancia estricta de picos y valles (entre dos del mismo tipo se conserva el más extremo);
3. censura: fase mínima de 6 meses (2 trimestres), ciclo mínimo de 15 meses (5 trimestres) y ningún giro a menos de 6 meses (2 trimestres) de los extremos de la ventana.

Para el PIB trimestral las reglas siguen a Harding y Pagan (2002). El algoritmo omite el suavizado previo del original.

### Concordancia

Para cada giro del PIB se busca el giro del mismo tipo más cercano en el EMAE y en el Índice Líder, entre 24 meses antes y 12 meses después, sin reutilizar giros. El desfase se mide en meses contra el mes central del trimestre; un valor negativo indica que la serie se adelanta al PIB.

### Contraste entre tipos de ciclo

Para cada serie se fechan los giros sobre la tasa interanual, el desvío respecto de la tendencia y el nivel, con la misma ventana y el mismo método de tendencia. Los giros del mismo tipo (pico o valle) separados por hasta 18 meses se agrupan en una fila, tomando como ancla el ciclo de crecimiento (o el clásico si aquel no tiene giros). Las columnas finales informan el desfase en meses de la tasa y del nivel respecto del desvío; la teoría anticipa que, en los picos, la tasa gira antes que el desvío y este antes que el nivel.

### Verificación

Las implementaciones en JavaScript del filtro HP, el filtro de Hamilton, las tendencias polinómicas, la media móvil y el fechado se contrastaron con `statsmodels`, `numpy` y una implementación de referencia en Python: las diferencias son del orden de 1e-10 o menores y los puntos de giro coinciden.

## Tecnología

- [Apache ECharts](https://echarts.apache.org/) 5.4.3, embebido en `index.html` (licencia Apache 2.0).
- Tipografías IBM Plex (Google Fonts).
- Python ≥ 3.10 con `pandas` y `requests` para el script de datos.

## Referencias

- Bry, G. y Boschan, C. (1971). *Cyclical Analysis of Time Series: Selected Procedures and Computer Programs*. NBER.
- Hamilton, J. D. (2018). Why you should never use the Hodrick-Prescott filter. *Review of Economics and Statistics*, 100(5), 831–843.
- Harding, D. y Pagan, A. (2002). Dissecting the cycle: A methodological investigation. *Journal of Monetary Economics*, 49(2), 365–381.
- Hodrick, R. J. y Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, 29(1), 1–16.
- Ravn, M. O. y Uhlig, H. (2002). On adjusting the Hodrick-Prescott filter for the frequency of observations. *Review of Economics and Statistics*, 84(2), 371–376.

## Licencia

Código bajo licencia MIT (ver `LICENSE`); Apache ECharts, incluido en `index.html`, se distribuye bajo licencia Apache 2.0. Los datos pertenecen a sus fuentes (INDEC y CIF-UTDT) y se redistribuyen con fines académicos y citando su origen.
