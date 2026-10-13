"""Editable English / Spanish copy. Keys are stable across language changes."""
TEXT = {
"title": ("Regenerative Car Simulator", "Simulador de coche regenerativo"),
"intro": ("Compare turbine electricity with added drag, total aerodynamic losses and propulsion demand on one shared drive.", "Compara la electricidad de la turbina con su resistencia añadida, las pérdidas aerodinámicas totales y la demanda de propulsión en un mismo recorrido."),
"inputs": ("Set up your analysis", "Configura tu análisis"),
"vehicle": ("Vehicle", "Vehículo"),
"mass": ("Vehicle mass (kg)", "Masa del vehículo (kg)"),
"preset": ("Illustrative aerodynamic shape", "Forma aerodinámica ilustrativa"),
"ld": ("L/D ratio — model proxy", "Relación L/D — aproximación del modelo"),
"ld_help": ("This model uses Cd = 1 / L/D. This slider is not a measured physical lift-to-drag ratio. Presets set it once; you can then adjust it.", "Este modelo usa Cx = 1 / L/D. El deslizador no representa una relación física medida de sustentación/resistencia. Los preajustes fijan su valor y después puedes modificarlo."),
"preset_note": ("Presets are conceptual starting points, not standard values. Only the aerodynamic proxy changes: mass and turbine diameter stay as entered. Every shape uses the same 2.2 m² reference frontal area, even trucks and imaginary airfoil bodies.", "Los preajustes son puntos de partida conceptuales, no valores estándar. Solo cambia la aproximación aerodinámica: se mantienen la masa y el diámetro introducidos. Todas las formas usan el mismo área frontal de referencia de 2,2 m², incluidos camiones y carrocerías imaginarias de perfil alar."),
"preset_sources": ("Preset values and references", "Valores de los preajustes y referencias"),
"f1_note": ("F1 downforce/drag is not 1/Cd. The F1 preset is conceptual; the sports-car preset uses a 2015 Porsche 911 Cd reference. Airfoil and fuselage presets are invented installed-body proxies, not published NACA or aircraft coefficients.", "La relación carga aerodinámica/resistencia de F1 no es 1/Cx. El preajuste F1 es conceptual; el deportivo usa una referencia de Cx de un Porsche 911 de 2015. Los preajustes alar y fuselaje son aproximaciones conceptuales de carrocerías instaladas, no coeficientes publicados de NACA o aviones."),
"cd": ("Equivalent model Cd", "Cx equivalente del modelo"),
"diameter": ("Turbine diameter (m)", "Diámetro de la turbina (m)"),
"eff_mode": ("Efficiency model", "Modelo de eficiencia"),
"realistic": ("Realistic", "Realista"),
"ideal": ("Idealised slider", "Deslizador idealizado"),
"eff": ("Wind-to-electric energy transfer (%)", "Transferencia de energía del aire a electricidad (%)"),
"ideal_note": ("The idealised slider changes electrical generation only. Turbine drag keeps its fixed coefficient. High settings may exceed the model's aerodynamic extraction limit and must be read as hypothetical sensitivity cases.", "El deslizador idealizado solo cambia la generación eléctrica. La resistencia de la turbina conserva su coeficiente fijo. Los valores altos pueden superar el límite de extracción aerodinámica del modelo y deben interpretarse como casos hipotéticos de sensibilidad."),
"drive": ("Driving event", "Evento de conducción"),
"drive_source": ("Choose how to define vehicle speed", "Elige cómo definir la velocidad del vehículo"),
"manual": ("Manual vehicle speed", "Velocidad manual del vehículo"),
"cycle": ("Predefined driving scenario", "Escenario de conducción predefinido"),
"speed": ("Vehicle speed (km/h)", "Velocidad del vehículo (km/h)"),
"scenario": ("Driving scenario", "Escenario de conducción"),
"dirt": ("Dirt Road", "Camino de tierra"),
"city": ("City", "Ciudad"),
"highway": ("Highway", "Carretera"),
"motorway": ("Motorway", "Autopista"),
"condition": ("Driving condition", "Condición de conducción"),
"acceleration": ("Acceleration", "Aceleración"),
"cruise": ("Cruise", "Circulación"),
"braking": ("Analyse braking / deceleration", "Analizar frenada / desaceleración"),
"grade": ("Road gradient (%)", "Pendiente de la carretera (%)"),
"distance": ("Distance travelled (km)", "Distancia recorrida (km)"),
"distance_note": ("Distance stretches one selected event. Duration follows from its average speed; it does not repeat accelerations or stops. Manual mode is constant speed, or a linear stop from the entered speed when braking is selected.", "La distancia alarga un único evento seleccionado. La duración se obtiene de su velocidad media; no repite aceleraciones ni paradas. El modo manual mantiene velocidad constante, o frena linealmente hasta detenerse desde la velocidad introducida si se selecciona frenada."),
"gate": ("Vehicle speed at which gates open (km/h)", "Velocidad del vehículo a la que se abren las compuertas (km/h)"),
"gate_help": ("Gates are open at or above this vehicle speed and closed below it. This is not their mechanical opening speed.", "Las compuertas están abiertas a partir de esta velocidad del vehículo y cerradas por debajo. No es la velocidad mecánica de apertura."),
"closed": ("Keep Version 2 gates closed throughout", "Mantener cerradas las compuertas de la versión 2 durante todo el recorrido"),
"extra": ("Include alternative energy methods (separate tab only)", "Incluir métodos energéticos alternativos (solo en su pestaña)"),
"sun": ("Solar light available (%)", "Luz solar disponible (%)"),
"sun_help": ("Scales the reference solar irradiance from no usable sunlight to 1000 W/m² peak/STC-style irradiance.", "Escala la irradiancia solar de referencia desde ausencia de luz útil hasta 1000 W/m², valor de pico tipo STC."),
"extra_note": (
    "Solar and traction-motor regeneration are credited only in the "
    "alternative-methods tab. Select braking/deceleration to include braking recovery.",
    "La energía solar y la regeneración del motor de tracción solo se contabilizan "
    "en la pestaña de métodos alternativos. Selecciona frenada/desaceleración "
    "para incluir recuperación de frenada.",
),
"run": ("Run Analysis", "Ejecutar análisis"),
"pending": ("Inputs have changed. These results still describe your last submitted analysis. Press Run Analysis to update them.", "Los datos han cambiado. Estos resultados siguen describiendo el último análisis ejecutado. Pulsa Ejecutar análisis para actualizarlos."),
"ready": ("Choose your inputs above and press Run Analysis to display results.", "Elige los datos arriba y pulsa Ejecutar análisis para ver los resultados."),
"invalid": ("A positive distance requires a non-zero vehicle speed. Check the driving inputs.", "Una distancia positiva requiere una velocidad del vehículo distinta de cero. Revisa los datos de conducción."),
"v1": ("Version 1 — Always Open", "Versión 1 — Siempre abierta"),
"v2": ("Version 2 — Smart Gates", "Versión 2 — Compuertas"),
"comparison": ("Direct Comparison", "Comparación directa"),
"alternatives": ("Alternative Energy Methods", "Métodos energéticos alternativos"),
"limitations": ("Model Limitations", "Limitaciones del modelo"),
"snapshot": ("Analysed drive", "Recorrido analizado"),
"duration": ("Duration", "Duración"),
"time": ("Time (s)", "Tiempo (s)"),
"power": ("Power (W)", "Potencia (W)"),
"energy": ("Energy (Wh)", "Energía (Wh)"),
"g1": ("1. Turbine electricity versus added drag", "1. Electricidad de la turbina frente a resistencia añadida"),
"g1_note": ("This is the turbine's own aerodynamic balance, not the whole vehicle's energy balance.", "Este es el balance aerodinámico de la propia turbina, no el balance energético del vehículo completo."),
"generation": ("Turbine electricity generated", "Electricidad generada por la turbina"),
"penalty": ("Energy lost to added turbine drag", "Energía perdida por la resistencia añadida de la turbina"),
"net_turbine": ("Net turbine energy effect", "Efecto energético neto de la turbina"),
"net_toggle": ("Show net turbine effect", "Mostrar efecto neto de la turbina"),
"g2": ("2. Where total aerodynamic losses come from", "2. Origen de las pérdidas aerodinámicas totales"),
"baseline": ("Vehicle aerodynamic loss without turbine", "Pérdida aerodinámica del vehículo sin turbina"),
"aero": ("Total aerodynamic loss including turbine", "Pérdida aerodinámica total incluida la turbina"),
"drag_share": ("Turbine share of total aerodynamic loss", "Proporción de pérdida aerodinámica debida a la turbina"),
"g3": ("3. Turbine recovery versus propulsion demand", "3. Recuperación de la turbina frente a demanda de propulsión"),
"spent": ("Total modelled propulsion energy required", "Energía total de propulsión requerida por el modelo"),
"remaining": ("Energy required after turbine electricity", "Energía requerida tras descontar la electricidad de la turbina"),
"net_drive": ("Net drive balance (return − demand)", "Balance neto del recorrido (retorno − demanda)"),
"net_drive_toggle": ("Show net drive balance", "Mostrar balance neto del recorrido"),
"g3_note": ("Propulsion demand includes aerodynamic drag, acceleration and gradient. It excludes rolling resistance, powertrain losses and auxiliary loads. Negative demand is plotted below zero; electrical returns above zero.", "La demanda de propulsión incluye resistencia aerodinámica, aceleración y pendiente. Excluye rodadura, pérdidas del sistema de propulsión y consumos auxiliares. La demanda se representa bajo cero; los retornos eléctricos, sobre cero."),
"results": ("Results for this drive", "Resultados de este recorrido"),
"quantity": ("Quantity", "Magnitud"),
"value": ("Value", "Valor"),
"offset_penalty": ("Added turbine drag offset by turbine electricity", "Resistencia añadida de la turbina compensada por su electricidad"),
"offset_aero": ("Total aerodynamic loss offset by turbine electricity", "Pérdida aerodinámica total compensada por la electricidad de la turbina"),
"offset_spent": ("Propulsion energy offset by turbine electricity", "Energía de propulsión compensada por la electricidad de la turbina"),
"yield": ("Turbine electricity per kilometre (Wh/km)", "Electricidad de la turbina por kilómetro (Wh/km)"),
"open_time": ("Time with turbine exposed (s)", "Tiempo con la turbina expuesta (s)"),
"selected": ("User-selected gates", "Compuertas elegidas por el usuario"),
"recommended": ("Generation-concentration gates", "Compuertas según concentración de generación"),
"guide": ("Why do some results change much more than others?", "¿Por qué algunos resultados cambian mucho más que otros?"),
"scan_title": ("4. Explore the vehicle speed at which gates open", "4. Explora la velocidad del vehículo a la que abrir las compuertas"),
"scan_x": ("Vehicle speed at which gates open (km/h)", "Velocidad del vehículo a la que abrir las compuertas (km/h)"),
"retained": ("Always-open electricity retained (%)", "Electricidad conservada respecto a siempre abierta (%)"),
"exposure": ("Drive time with gates open (%)", "Tiempo del recorrido con compuertas abiertas (%)"),
"score": ("Generation concentration (percentage points)", "Concentración de generación (puntos porcentuales)"),
"scan_note": ("The recommendation maximizes electricity retained as a fraction of always-open generation minus time exposed as a fraction of the drive. It selects above-average-output portions without a wattage target. This is a declared screening trade-off, not a turbine efficiency optimum. Generation and drag decrease together, so their ratio does not improve.", "La recomendación maximiza la fracción de electricidad conservada respecto a siempre abierta menos la fracción de tiempo expuesto. Selecciona los tramos de producción superior a la media sin fijar un objetivo en vatios. Es un criterio explícito de estudio, no un óptimo de eficiencia de la turbina. La generación y la resistencia disminuyen juntas, por lo que su cociente no mejora."),
"scan_formula": ("For the linear event, the threshold is the cube root of mean speed cubed. Diameter changes the watts and Wh, but cancels from this relative threshold. No cut-in behaviour or rated output is modelled.", "Para el evento lineal, el umbral es la raíz cúbica de la media de la velocidad al cubo. El diámetro cambia los vatios y Wh, pero se cancela en este umbral relativo. No se modelan el arranque de la turbina ni una potencia nominal."),
"no_threshold": ("No distinct generation-concentration threshold exists: speed is constant or electrical output is zero. At constant speed, all thresholds at or below that speed are equivalent to always open; thresholds above it are equivalent to closed.", "No existe un umbral diferenciado de concentración de generación: la velocidad es constante o la generación eléctrica es cero. A velocidad constante, todos los umbrales iguales o inferiores equivalen a siempre abierta; los superiores equivalen a cerrada."),
"threshold_result": ("Generation-concentration threshold: {speed:.2f} km/h. Retains {retained:.1f}% of always-open electricity with gates open for {exposure:.1f}% of the drive.", "Umbral de concentración de generación: {speed:.2f} km/h. Conserva el {retained:.1f}% de la electricidad de siempre abierta con las compuertas abiertas durante el {exposure:.1f}% del recorrido."),
"closed_reference": ("Always-closed reference: 0 Wh turbine electricity, 0 Wh turbine drag; propulsion demand {spent:.2f} Wh. This reference is not the default recommendation.", "Referencia siempre cerrada: 0 Wh de electricidad y 0 Wh de resistencia de turbina; demanda de propulsión de {spent:.2f} Wh. Esta referencia no es la recomendación predeterminada."),
"chosen_gate": ("Selected vehicle opening speed", "Velocidad de apertura elegida"),
"compare_note": (
    "Both versions use the same submitted drive. Version 2 uses the "
    "scanned generation-concentration threshold in this comparison.",
    "Ambas versiones usan el mismo recorrido ejecutado. La versión 2 usa "
    "el umbral de concentración de generación del barrido en esta comparación.",
),
"equal_note": ("These results match because your gate policy exposes the turbine for the same portions of the drive, or generation/drag is negligible.", "Los resultados coinciden porque la política de compuertas expone la turbina durante los mismos tramos, o la generación/resistencia es despreciable."),
"compare_lines": ("Cumulative net energy balance on the same drive", "Balance energético neto acumulado en el mismo recorrido"),
"best_note": ("Turbine source: {version}, selected for the lower net event energy requirement among your two submitted configurations. Scan results are not substituted. Ties use Version 1.", "Origen de la turbina: {version}, elegido por su menor requerimiento energético neto entre las dos configuraciones ejecutadas. No se sustituyen por resultados del barrido. Los empates usan la versión 1."),
"methods": ("Electrical energy by method", "Energía eléctrica por método"),
"regen": ("Regenerative braking", "Frenada regenerativa"),
"solar": ("Roof solar", "Solar en el techo"),
"standalone_note": ("The braking bar is the standalone no-turbine benchmark on the same event. The combined balance below instead uses braking energy left after turbine drag; it does not recover the same braking energy twice.", "La barra de frenada es la referencia independiente sin turbina para el mismo evento. El balance combinado inferior usa la energía de frenada restante tras la resistencia de la turbina; no recupera dos veces la misma energía."),
"combined": ("Cumulative energy: demand and electrical returns", "Energía acumulada: demanda y retornos eléctricos"),
"combined_toggle": ("Show combined balance after all returns", "Mostrar balance combinado tras todos los retornos"),
"regen_combined": ("Braking electricity remaining with turbine", "Electricidad de frenada restante con la turbina"),
"total_returns": ("Total electrical returns in combined case", "Retornos eléctricos totales del caso combinado"),
"combined_net": ("Combined net balance", "Balance neto combinado"),
"charge_note": ("A positive combined balance means net electrical charging during this event, not creation of energy. Sunlight, downhill gravitational energy and/or initial kinetic energy can supply it; an isolated stop does not include the energy used to accelerate before the stop.", "Un balance combinado positivo significa carga eléctrica neta durante este evento, no creación de energía. Pueden aportarla la luz solar, la energía gravitatoria de una bajada o la energía cinética inicial; una frenada aislada no incluye la energía usada para acelerar antes de frenar."),
"solar_note": ("Solar: {sun:.0f}% of {irr:.0f} W/m² reference irradiance; {area:.1f} m² roof PV, {panel:.0f}% panel and {charge:.0f}% charging efficiency → {power:.1f} W for this drive.", "Solar: {sun:.0f}% de {irr:.0f} W/m² de irradiancia de referencia; {area:.1f} m² de panel en el techo, {panel:.0f}% de eficiencia del panel y {charge:.0f}% de carga → {power:.1f} W durante el recorrido."),
"regen_note": ("Regenerative braking uses {eff:.1f}% wheel-to-battery screening efficiency. It is zero when no braking demand remains.", "La frenada regenerativa usa una eficiencia aproximada rueda-batería del {eff:.1f}%. Es cero si no queda demanda de frenada."),
"method_table": ("Method totals and combined balance", "Totales por método y balance combinado"),
"standalone_regen": ("Standalone braking electricity (no turbine)", "Electricidad de frenada independiente (sin turbina)"),
"na": ("N/A", "No aplicable"),
"sign_note": ("Green: returned energy. Red: energy spent/lost. Net lines use return minus demand: positive is a return, negative is consumption. Colours accompany explicit signs and labels.", "Verde: energía retornada. Rojo: energía gastada/perdida. Las líneas netas usan retorno menos demanda: positivo es retorno y negativo es consumo. Los colores acompañan signos y etiquetas explícitos."),
"gate_range": (
    "This scenario uses {low:.1f}–{high:.1f} km/h. "
    "The opening threshold is restricted to that range.",
    "Este escenario usa {low:.1f}–{high:.1f} km/h. "
    "El umbral de apertura se limita a ese intervalo.",
),

"normalize_braking": (
    "Use a normalized braking event for the alternative-methods comparison",
    "Usar una frenada normalizada en la comparación de métodos alternativos",
),

"normalize_braking_help": (
    "Uses the same initial/final speeds over 20 seconds. "
    "Turbine, braking and solar are recalculated together in that tab only.",
    "Usa las mismas velocidades inicial y final durante 20 segundos. "
    "Turbina, frenada y solar se recalculan juntas solo en esa pestaña.",
),

"normalized_reference": (
    "Alternative-methods reference: {duration:.0f} seconds, "
    "{distance:.3f} km. Other tabs retain your entered distance.",
    "Referencia de métodos alternativos: {duration:.0f} segundos, "
    "{distance:.3f} km. Las otras pestañas conservan la distancia introducida.",
),

"enable_braking_note": (
    "Select 'Analyse braking / deceleration' to include regenerative braking.",
    "Selecciona 'Analizar frenada / desaceleración' para incluir "
    "la frenada regenerativa.",
),

"comparison_threshold": (
    "Version 2 opening threshold used here: {speed:.2f} km/h.",
    "Umbral de apertura de la versión 2 usado aquí: {speed:.2f} km/h.",
),

"comparison_no_threshold": (
    "No distinct concentration threshold exists for this event. "
    "The comparison uses always-open operation as its reference.",
    "No existe un umbral diferenciado de concentración para este evento. "
    "La comparación usa funcionamiento siempre abierto como referencia.",
)
}

GUIDE = (
"""- **Speed and diameter strongly affect absolute output.** Turbine generation and added drag scale with speed cubed and diameter squared.
- **Electricity / turbine drag stays nearly fixed.** With constant efficiency and thrust coefficient, speed and swept area cancel from the ratio.
- **Mass changes acceleration, hill and braking energy**, not the air power crossing a fixed-size rotor.
- **The L/D proxy changes baseline vehicle drag**, not the turbine's own output.
- **Distance stretches this single event.** Aerodynamic and solar energy increase with duration; its total kinetic-energy change stays fixed for the same endpoints.
- **The concentration scan selects higher-output portions**, not a speed where drag becomes free. At constant speed there is no special opening threshold.
- The actuator-disk thrust coefficient is **{ct:.3f}**. Fractions with a zero denominator are **N/A**.""",
"""- **La velocidad y el diámetro afectan mucho a la producción absoluta.** La generación y la resistencia añadida escalan con la velocidad al cubo y el diámetro al cuadrado.
- **Electricidad / resistencia de turbina permanece casi constante.** Con eficiencia y coeficiente de empuje constantes, la velocidad y el área se cancelan en el cociente.
- **La masa cambia la energía de aceleración, pendiente y frenada**, no la potencia del aire que atraviesa un rotor de tamaño fijo.
- **La aproximación L/D cambia la resistencia del vehículo**, no la producción de la turbina.
- **La distancia alarga este único evento.** La energía aerodinámica y solar aumenta con la duración; el cambio total de energía cinética sigue siendo el mismo si no cambian las velocidades inicial y final.
- **El barrido de concentración selecciona los tramos de mayor producción**, no una velocidad donde desaparezca la resistencia. A velocidad constante no hay un umbral especial.
- El coeficiente de empuje del disco actuador es **{ct:.3f}**. Los cocientes con denominador cero son **No aplicables**.""")

LIMITATIONS = (
"""- **Vehicle geometry is simplified.** All presets keep a fixed 2.2 m² frontal area. `Cd = 1 / L/D` is a model proxy, not a physical identity. Presets are illustrative; named vehicles vary by year and configuration. Mass and turbine size never set frontal area. NACA/fuselage presets are conceptual installed bodies, not published wing-area drag coefficients.
- **Turbine aerodynamics use a fixed actuator disk.** Cp = 0.40 determines Ct through one-dimensional momentum theory. Drag is turbine thrust × vehicle speed. Duct blockage, blades, wakes, installation losses and speed-dependent coefficient maps are absent.
- **Efficiency is constant.** Realistic wind-to-electric efficiency is 0.40 × 0.90 × 0.90 = 0.324. Cut-in torque/speed, bearing losses, controller thresholds and power limits are absent. The idealised slider varies generation while Ct remains fixed; settings above aerodynamic Cp are hypothetical, and settings above Ct may imply a nonphysical positive turbine balance.
- **The gate recommendation is a declared relative trade-off.** It maximizes retained generation fraction minus exposed-time fraction. It does not optimize energy consumption, improve generation/drag, or predict physical cut-in speed. Diameter cancels from this relative threshold, although output scales with diameter squared. Constant-speed and zero-output cases have no distinct threshold. Always-closed is an explicit reference and selectable policy.
- **Gate motion is instantaneous and free.** Actuator energy, opening time, movement drag, seals and latency are ignored.
- **Driving events are synthetic, not certification cycles.** Each selected acceleration/cruise/deceleration event has a linear speed-time trace. Entered distance stretches that one event; duration = distance / average speed. It does not repeat accelerations or stops. Long acceleration or stopping distances imply correspondingly gentle acceleration or braking. Manual speed means constant speed, or speed-to-zero braking. Predefined braking reverses the selected event endpoints consistently in both versions. Positive-distance zero-speed events are invalid; parking is not modelled.
- **Propulsion and braking are separated at every time interval.** Positive wheel demand is accumulated as propulsion; negative wheel demand is available braking energy. They are not cancelled before integration. Kinetic change and gradient work are included. Values are numerical midpoint integrals; the scan uses the same integration grid and an analytical concentration threshold.
- **Rolling resistance is omitted.** Tyres, road texture, tyre pressure and bearing friction are absent.
- **Propulsion-system losses are omitted.** Traction motor, inverter, gearbox, discharge efficiency, battery temperature/state of charge and auxiliary loads are absent. Wheel-side demand minus electrical generation is a screening balance, not calibrated battery consumption. Percentages can exceed 100% for downhill/braking or hypothetical coefficient cases; zero denominators are undefined, not 0%.
- **Braking regeneration only appears in the alternative-methods tab.** A fixed motor-generator × inverter × charging efficiency is applied to remaining wheel braking demand, including downhill braking. No power, charge, adhesion, blending, temperature or low-speed limits are present. The standalone benchmark has no turbine. The combined case uses braking left after turbine drag to avoid double counting.
- **Solar only appears in the alternative-methods tab and is external energy.** The model assumes 2.0 m² roof PV, fixed panel and charge efficiencies, and constant irradiance scaled from 1000 W/m² by the light percentage. Shading, curvature, sun angle, temperature, orientation and seasonal yield are absent. Duration follows the entered distance and speed.
- **Ambient wind is omitted.** Airflow equals vehicle speed; wind, gusts and traffic wakes are absent.
- **Air properties are fixed.** Density = 1.225 kg/m³; altitude and weather effects are absent.
- **Road gradient is constant** over the event. Distance is road-path distance, using grade angle = atan(grade/100).
- **Vehicle attitude and downforce are omitted.** Pitch, ride height, suspension, cornering and turbine-body coupling are absent. F1 downforce-to-drag is not the slider's inverse-Cd proxy.
- **One turbine and no flow coupling.** Multiple rotors, duct networks, recirculation, pressure recovery and body interference are absent.
- **An event is not a complete energy lifecycle.** Initial kinetic energy or downhill potential energy may charge the battery; an isolated stop excludes preceding acceleration. Net electrical charging is not energy creation. The method comparison chooses the lower net event requirement of the two user-selected configurations, not a scanned replacement.""",
"""- **La geometría del vehículo está simplificada.** Todos los preajustes conservan un área frontal de 2,2 m². `Cx = 1 / L/D` es una aproximación del modelo, no una identidad física. Los preajustes son ilustrativos; los vehículos reales varían según año y configuración. La masa y la turbina no determinan el área frontal. Los preajustes NACA/fuselaje son carrocerías conceptuales, no coeficientes publicados referidos al área alar.
- **La turbina usa un disco actuador fijo.** Cp = 0,40 determina Ct mediante teoría unidimensional de cantidad de movimiento. La resistencia equivale a empuje de turbina × velocidad del vehículo. No se incluyen bloqueo del conducto, álabes, estelas, pérdidas de instalación ni mapas de coeficientes según velocidad.
- **La eficiencia es constante.** La eficiencia realista aire-electricidad es 0,40 × 0,90 × 0,90 = 0,324. No se incluyen par/velocidad de arranque, pérdidas de rodamientos, umbrales de control ni límites de potencia. El deslizador idealizado cambia la generación manteniendo Ct fijo; superar el Cp aerodinámico es hipotético, y superar Ct puede implicar un balance positivo no físico de la turbina.
- **La recomendación de compuertas es un compromiso relativo explícito.** Maximiza la fracción de generación conservada menos la fracción de tiempo expuesto. No optimiza el consumo, no mejora generación/resistencia ni predice el arranque físico. El diámetro se cancela en este umbral relativo, aunque la producción escala con su cuadrado. A velocidad constante o producción cero no hay umbral diferenciado. Siempre cerrada es una referencia y una política seleccionable.
- **Las compuertas se mueven instantáneamente y sin coste.** No se incluyen energía del actuador, tiempo de apertura, resistencia del movimiento, sellado ni latencia.
- **Los eventos son sintéticos, no ciclos de homologación.** Cada evento de aceleración/circulación/desaceleración tiene velocidad lineal en el tiempo. La distancia introducida alarga ese único evento; duración = distancia / velocidad media. No repite aceleraciones ni paradas. Distancias largas de aceleración o frenada implican aceleraciones o frenadas suaves. La velocidad manual es constante, o una frenada hasta cero. La frenada predefinida invierte los extremos del evento de igual forma en ambas versiones. No es válida una distancia positiva a velocidad cero; no se modela el estacionamiento.
- **La propulsión y la frenada se separan en cada intervalo.** La demanda positiva en rueda se acumula como propulsión; la negativa es energía disponible para frenar. No se cancelan antes de integrar. Se incluyen cambio cinético y trabajo de la pendiente. Los resultados son integrales numéricas por puntos medios; el barrido usa la misma malla y un umbral analítico de concentración.
- **Se omite la resistencia a la rodadura.** No se incluyen neumáticos, textura del firme, presión ni fricción de rodamientos.
- **Se omiten las pérdidas de propulsión.** No se incluyen motor de tracción, inversor, caja de cambios, eficiencia de descarga, temperatura/carga de batería ni consumos auxiliares. Demanda en rueda menos electricidad es un balance aproximado, no un consumo de batería calibrado. Los porcentajes pueden superar el 100% en bajadas/frenadas o con coeficientes hipotéticos; un denominador cero no está definido, no equivale al 0%.
- **La regeneración de frenada solo aparece en su pestaña alternativa.** Se aplica una eficiencia fija motor-generador × inversor × carga a la demanda de frenada restante, incluida la frenada en bajada. No hay límites de potencia, carga, adherencia, reparto de frenada, temperatura ni baja velocidad. La referencia independiente no lleva turbina. El caso combinado usa la frenada restante tras la resistencia de turbina para evitar doble contabilización.
- **La energía solar solo aparece en la pestaña alternativa y es energía externa.** Se suponen 2,0 m² de panel, eficiencias fijas e irradiancia constante escalada desde 1000 W/m² según el porcentaje de luz. No se incluyen sombra, curvatura, ángulo solar, temperatura, orientación ni rendimiento estacional. La duración depende de distancia y velocidad.
- **Se omite el viento ambiental.** El flujo de aire equivale a la velocidad del vehículo; no hay viento, ráfagas ni estelas del tráfico.
- **Las propiedades del aire son fijas.** Densidad = 1,225 kg/m³; se omiten altitud y meteorología.
- **La pendiente es constante** durante el evento. La distancia se mide sobre la carretera, con ángulo = atan(pendiente/100).
- **Se omiten la actitud y la carga aerodinámica.** No hay cabeceo, altura, suspensión, curvas ni interacción turbina-carrocería. La relación carga/resistencia de F1 no es la aproximación inversa de Cx del deslizador.
- **Una turbina y sin acoplamiento de flujo.** No se incluyen varios rotores, redes de conductos, recirculación, recuperación de presión ni interferencia con la carrocería.
- **Un evento no es un ciclo energético completo.** La energía cinética inicial o potencial de una bajada puede cargar la batería; una frenada aislada excluye la aceleración previa. Carga eléctrica neta no es creación de energía. La comparación elige el menor requerimiento energético neto de las dos configuraciones del usuario, no una sustitución del barrido.""")


def translate(key, language="en", **kwargs):
    return TEXT[key][language == "es"].format(**kwargs)
