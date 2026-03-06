---
name: plan_arquitectura
description: Prompt para planificar estructura de arquitectura de software. Ejecuta subagentes para mantener el contexto de la conversación. 
agent: Plan
argument-hint: Pregunta al usuario sobre el proyecto a desarrollar, sus requerimientos y objetivos. Luego, planifica la estructura de la arquitectura de software, sobretodo las tecnologías a utilizar, los módulos o componentes principales, y cómo se comunicarán entre sí.
tools: [read/readFile, agent, edit/createFile, edit/editFiles, todo] 
---


# <Goal>

La meta de este prompt es planificar la estructura de proyectos enteros de software, incluyendo las tecnologías a utilizar, los módulos o componentes principales, y cómo se comunicarán entre sí. Para ello sigue los siguientes pasos:
</Goal>

# <plan_guide>

#tool:todo
- Pregunta al usuario sobre el proyecto a desarrollar, sus requerimientos y objetivos.

- Define cuales van a ser las tenologías a utilizar, los frameworks, lenguajes de programación, bases de datos, etc. (Ej.)

- Por cada framework (de test, desarrollo, etc), lenguaje de programación o tecnología que hayas definido, lanza el subagente #tool:agent/runSubagent `<.github/agents/Generador_SI.agent.md>` e indicale el framework, lenguaje de programación o tecnología, como output de cada subagente recivirás el path de todas las skills e instructions que ha generado el subagente. Deberas editar el fichero  proyecto/.github/copilot-instructions.md con #tool:edit/editFiles, añadiendo toda la información que te ha dado cada subagente, que sera la ruta de los archivos generados. Sigue las pautas de la template #tool:read/readFile `<.github/templates/copilot-instructions.template.md>` para saber como añadirlo añadirlo. (En el apartado Skill para Skills e Instructions para las instrucciones)

- Puando termine el último subagente, deberas lanzar el subagente #tool:agent/runSubagent `<.github/agents/Analizador.agent.md>`. Se encargará de analizar todas las skills e instructions generados. En el output recibiras cuales skills o instructions no han pasado el analisis. Deberas regenerar esos archivos con el subagente #tool:agent/runSubagent `<.github/agents/Generador_SI.agent.md>` indicandole que solo genere las skills o instructions que no han pasado el analisis. Cuando te entregue los nuevos archivos, editas de nuevo el fichero copilot-instructions.md añadiendo la nueva información siguiendo las pautas de la template #tool:read/readFile `<.github/templates/copilot-instructions.template.md>` hasta que todas las skills e instructions hayan pasado el analisis.

- Por último, lanza un subagente #tool:agent/runSubagent `<.github/agents/Arquitecto.agent.md>` para que se encargue de finalizar el documento copilot-instructions.md, añadiendo toda la información de la arquitectura de software planificada, y organizandolo de forma clara y estructurada siguiendo la template #tool:read/readFile `<.github/template/copilot-instructions.md>`. También sera el encargado de generar el esqueleto del proyecto (carpetas), y de generar un README.md con la información más relevante del proyecto.
</plan_guide>