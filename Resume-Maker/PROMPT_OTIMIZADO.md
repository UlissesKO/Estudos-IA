# Prompt padrão para otimização de currículo

## Objetivo

Otimizar o currículo geral para a vaga descrita em `Resume-Maker/Fontes de conteúdo/descricao-vaga.md`, produzindo uma versão adequada para leitura de um tech recruiter humano e para sistemas ATS.

## Fontes obrigatórias

Use exclusivamente estas fontes locais:

- `Resume-Maker/Fontes de conteúdo/descricao-vaga.md`: descrição da vaga e requisitos do empregador.
- `Resume-Maker/Fontes de conteúdo/conhecimentos.md`: única fonte autorizada para competências, experiências, cursos, certificações, projetos, formação e idiomas.
- `Resume-Maker/Fontes de conteúdo/Currículo Geral.html`: modelo visual e estrutural a ser otimizado.

Não use informações externas sobre o candidato. Pesquisas externas podem ajudar a interpretar termos da vaga, mas nunca podem fornecer uma nova afirmação sobre o candidato.

## Procedimento obrigatório

1. Use `get_server_status` para confirmar que os arquivos de entrada existem.
2. Use `get_resume_optimization_context` para ler a vaga, a base factual e o currículo geral.
3. Se a descrição da vaga estiver vazia ou contiver apenas o modelo, pare e solicite que o usuário cole a vaga.
4. Use `analyze_vacancy_match` para separar requisitos, palavras-chave, competências transferíveis e lacunas.
5. Compare cada requisito da vaga com `conhecimentos.md`:
   - inclua somente competências sustentadas pelo arquivo;
   - preserve qualificadores como “apoio”, “estudo”, “noções”, “introdutório” e “POC”;
   - não transforme curso em experiência profissional;
   - não transforme estudo ou POC em administração plena;
   - não crie resultados, métricas, cargos, datas, ferramentas ou certificações;
   - não declare certificações relacionadas que não estejam registradas como obtidas.
6. Reescreva o HTML para destacar primeiro as experiências e competências mais relevantes para a vaga.
7. Preserve a estrutura visual do currículo geral:
   - mantenha o formato HTML completo;
   - mantenha o CSS, o padrão A4, as margens, a tipografia e o estilo dos títulos;
   - não remova contatos, formação ou certificações verdadeiras;
   - não altere os links Credly existentes;
   - não inclua tabelas, colunas ou elementos que prejudiquem ATS sem necessidade.
8. Mantenha o currículo resumido, de forma que não fique extenso e de leitura díficil. Deverá ter idealmente 1 página PDF 
8. Use `save_optimized_resume` para salvar o resultado em `Resume-Maker/Curriculos Finalizados` com nome `.html` descritivo.
9. Use `evaluate_resume` passando o HTML salvo.
10. Apresente ao usuário:
    - resumo das adaptações realizadas;
    - requisitos atendidos e evidência usada em `conhecimentos.md`;
    - requisitos não atendidos ou não comprovados;
    - nota de 0 a 10 para um tech recruiter humano;
    - nota de 0 a 10 para compatibilidade ATS;
    - limitações e recomendações sem inventar informações.

## Critérios de avaliação

### Tech recruiter humano

Avalie clareza, coerência da trajetória, relevância das experiências, credibilidade do nível de domínio, legibilidade, priorização das informações e aderência ao contexto da vaga.

### ATS

Avalie presença contextual de palavras-chave sustentadas, títulos de seção claros, HTML legível, ausência de conteúdo essencial apenas em imagens, consistência de nomenclaturas e cobertura dos requisitos comprovados.

As notas devem refletir o currículo produzido para a vaga atual, não uma avaliação abstrata do candidato. Nunca aumente uma nota para compensar uma lacuna não comprovada.
