# Sobre
Este projeto é uma demonstração de um script de automação web que é capaz de preencher formulários de forma automática. O objetivo é facilitar o processo de preenchimento de dados repetitivos em sites que exigem informações pessoais. 

## Alvo
O formulário alvo deste script é o formulário de contato da empresa Radix Engenharia e Tecnologia, localizado em: [https://radixeng.com.br/contato/](https://radixeng.com.br/contato/). 

Este formulário possui uma proteção de reCaptcha v2 do tipo desafio de imagem, que é acionando automaticamente antes do formulário ser de fato enviado. O script é capaz de preencher os campos do formulário, mas não resolve o reCaptcha, que deve ser resolvido manualmente pelo usuário. 

Fazendo com que o funcionamento deste script seja híbrido. 

## Funcionalidades
### Versões
Atualmente, o script possui apenas uma versão que funciona requisitando os dados do usuário via terminal.

#### Versão CLI:
**Funcionalidades**: 
- Preenchimento automático dos campos do formulário de contato.
- Funcionamento híbrido com reCaptcha v2, onde o usuário deve resolver o desafio de imagem manualmente.

## Como usar
1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd form-autofiller
   ```  
3. Instale as dependências necessárias:
   ```bash
   python -m pip install -r requirements.txt
   ```  
4. Execute o script:
   ```bash
   python main.py
   ```
5. Siga as instruções no terminal para preencher os dados do formulário.