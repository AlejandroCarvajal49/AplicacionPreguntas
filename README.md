📊 Analítica de Resultados Saber 11 - Proyecto 1
Curso: Analítica Computacional para la Toma de Decisiones

Universidad: Universidad de los Andes

Profesor: Juan F. Pérez

Fecha: Febrero 2026

📝 Descripción del Proyecto
Este proyecto desarrolla un producto de analítica de datos (Dashboard Interactivo) basado en los resultados de las pruebas de estado Saber 11 para **ANTIOQUIA** 

El producto está diseñado específicamente para el Ministerio de Educación Nacional, con el objetivo de identificar brechas críticas en la calidad educativa y apoyar la toma de decisiones basada en evidencia para la asignación de recursos, infraestructura tecnológica y capacitación docente.

🎯 Usuario Objetivo
Funcionarios del Ministerio de Educación (Nivel Directivo y Técnico): Requieren una herramienta visual y centralizada para monitorear indicadores de equidad (Rural vs Urbano), calidad (Público vs Privado) y competitividad (Bilingüismo) a nivel departamental.

💼 Preguntas de Negocio Resueltas
El tablero responde a tres preguntas estratégicas, cada una abordada en un módulo independiente:

Equidad Regional (Rural vs. Urbano):

¿Existe una brecha significativa en el desempeño global entre estudiantes de zonas rurales y urbanas que justifique una intervención diferenciada?

Calidad Educativa (Público vs. Privado):

¿En qué áreas del conocimiento presentan los colegios oficiales el mayor rezago respecto a los colegios no oficiales, controlando por el nivel socioeconómico?

Competitividad (Bilingüismo y TIC):

¿Cómo se distribuye el nivel de inglés en el país y qué correlación existe con el acceso a herramientas tecnológicas (Internet/Computador) en el hogar?

⚙️ Arquitectura de la Solución
El flujo de datos sigue una arquitectura moderna en la nube utilizando servicios de AWS para el procesamiento (ETL) y Python para la visualización.

Ingesta y Procesamiento (ETL):

Fuente: Datos Abiertos Colombia (Saber 11).

Herramientas: AWS Glue (Crawler & Jobs) para limpieza y AWS Athena para consultas SQL.

Almacenamiento: S3 (Buckets Raw y Curated).

Visualización (Frontend & Backend):

Framework: Plotly Dash (Python).

Diseño: Dash Bootstrap Components (DBC) con un diseño de tarjetas (Card Layout) para la navegación.

Estructura: Aplicación multipágina (Dash Pages) para modularidad.

Despliegue (Infraestructura):

Servidor: AWS EC2 (t2.micro / Ubuntu).

Accesibilidad: IP Pública configurada en el puerto 8050.
