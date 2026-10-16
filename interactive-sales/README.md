# KONIG Interactive Sales — guia de uso

Biblioteca independente de componentes comerciais interativos, sem dependências e sem chamadas de IA. Não modifica ONIX, Waves, SOPs ou squads existentes.

## Começar
Abra `interactive-sales/demo.html` no navegador. Funciona localmente, sem servidor. Altere os controles e observe as estimativas em tempo real.

## Integrar a um site
Copie o bloco HTML do componente desejado e o script correspondente de `demo.html` para sua página. Os cálculos usam JavaScript nativo e podem ser migrados para React/Vue posteriormente.

## Componentes
1. **Stone Configurator:** material, dimensões, acabamento e recorte; gera briefing comercial.
2. **Industrial ROI:** capacidade, jornada, ganho, margem e investimento; calcula peças adicionais, contribuição incremental e payback simplificado.
3. **Mineral Economics:** preço, frete e rendimento; calcula custo por tonelada útil e diferença para referência.

## Uso comercial
1. Substitua os valores de exemplo por uma tabela de preços autorizada.
2. Valide as regras com o setor técnico e comercial do cliente.
3. Adicione identificação e consentimento do lead antes de integrar CRM/WhatsApp.
4. Registre versão de tabela, premissas e data de cada orçamento.
5. Trate resultados como **estimativas**, não ofertas vinculantes; frete, tributos, instalação e perdas podem alterar valores.

## Limites e segurança
Não há autenticação, banco de dados, pagamentos, CRM ou persistência nesta demonstração. Nunca coloque segredos de API no JavaScript do navegador. Cálculos críticos e preços finais devem ser validados no backend. A estimativa de ROI pressupõe venda integral da produção adicional e não inclui custos operacionais extras. O cálculo mineral usa rendimento uniforme e exige ensaios reais.

## Próximos passos
Criar pacote versionado de componentes, testes automatizados de fórmulas, integração com catálogo de produtos e geração de propostas com aprovação humana.
