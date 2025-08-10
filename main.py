from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

# Usando Webdriver manager para gerenciar e instalar a versão correta do webdriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from pandas import read_csv, read_excel, DataFrame

from time import sleep
from random import uniform
import re
from argparse import ArgumentParser
from sys import exit


URL = "https://radixeng.com.br/contato"

def init_args_parser() -> ArgumentParser:
    cli_parser = ArgumentParser(
        prog="formautofiller",
        description="""
            Preenche o formulário localizado em https://radixeng.com.br/contato de forma 
            semi-automática dado um arquivo (.csv ou .xlsx) [FILE]. 

            Caso o caminho da arquivo contenha espaços em branco use "" ou '' em volta 
            do caminho.
        """
    )
    cli_parser.add_argument("filename", help="Caminho do arquivo (.csv ou .xlsx) com os dados")
    #cli_parser.add_argument("-h", "--help", action="store_true")

    return cli_parser

def handle_cli_args() -> DataFrame:
    cli_parser = init_args_parser()
    args = cli_parser.parse_args()
    
    try: 
        if args.filename.endswith(".csv"):
            data = read_csv(args.filename)
        elif args.filename.endswith(".xlsx"):
            data = read_excel(args.filename, engine="openpyxl")
        else: 
            raise Exception(f"Arquivo {args.filename} informado não era .csv ou .xlsx")
    except Exception as e:
        print(f"Erro enquanto abria e lia o arquivo {args.filename} informado: {e}")
        exit(1)
    
    return data

def valid_phonenumber(number: str) -> bool:
    """
        Valida um determinado número de acordo com a validação do formulário alvo. 
        Validação: 
        Deve ter 7 ou mais números (dígitos) E Ser constituída apenas de números, +, -, (, ), (espaço) 
    """
    numbersonly = re.sub(r"\D", "", number)

    return number and len(numbersonly) >= 7 and re.match(r"[0-9+\-() ]+", number) is not None

def set_select_input_option(
        driver: WebDriver, 
        select_elem: WebElement, 
        option: str, 
) -> None: 
    """
        Dado um [WebElement] do tipo select: 
            - Capta as opções contidas no input select.
            - Válida se a opção [option] informada está presente nas opções do input e seleciona ela.

        [params]: 
            - [driver]: Driver em uso.
            - [select_elem]: WebElement do tipo input select.
            - [option]: Opção à ser validada e clicada.

        [raise]:
            - [Exception]: Se opção não encontrada.
    """
    _ = driver
    options = select_elem.find_elements(By.TAG_NAME, "option")
    options = [ op for op in options if not op.get_attribute("disabled") ] # Remove Opção Default Desabilitada

    opts_str = ""
    for opt in options:
        opts_str += opt.text + ", " # Monta uma string com todas as opções que foram tentadas
        if opt.text.strip().lower() == option.strip().lower():
            opt.click()
            return
    
    raise Exception(f"Opção {option} não encontrada dentre as opções {opts_str}.")

def disable_form(driver: WebDriver) -> None:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form.hs-form-private"))
    )

    driver.execute_script(
        """
            let form = document.querySelector("form.hs-form-private");

            if (!form) 
            {
                console.log(`form não encontrado! ${form}`);
            }

            form.setAttribute("id", "");
            form.setAttribute("class", "");
            form.setAttribute("action", "");

            form.addEventListener("submit", (e) => {
                e.preventDefault();

                console.log("Fake Form enviado!");
            }, true);

            // Sobrescreve o comportamento de envio do form HubSpot
            window.addEventListener('message', function(event) {
                if (event.data.type === 'hsFormCallback' && event.data.eventName === 'onFormSubmit') {
                    console.log("HubSpot está enviando o form... Bloqueado!");
                    event.stopImmediatePropagation();
                    
                    event.preventDefault = true;
                }
            });
        """
    )

def scroll_until_visible_viewport(driver: WebDriver, target: WebElement, x: int, y: int) -> bool:
    """
        Scrolla para pos [x], [y] se [target] não está presente na viewport. 
        Use com [WebDriverWait] para tratar operações em elementos mesmo 
        quando a janela pode ser repetidamente fechada. 

        Params: 
            - [driver]: [WebDriver]
            - [target]: Elemento para ser verificado
        Returns: 
            - [bool]: Se o elemento está presente na viewport ou não
    """
    in_viewport: bool = driver.execute_script("""
        const rect = arguments[0].getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    """, target)

    if not in_viewport:
        driver.execute_script(f"window.scrollTo({x}, {y});")

    return in_viewport

def main() -> None:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    ua = UserAgent()

    data = handle_cli_args()

    options.add_argument(f"user-agent={ua.chrome}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Suprime os logs do browser no terminal
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options, service=service)

    sleep(uniform(0.8, 1.8))
    driver.get(URL)

    main_window = driver.current_window_handle

    for i in range(len(data)):
        row = data.iloc[i]

        try:
            # Espera carregamento do Form
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.hs-form-iframe"))
            )
            # Seleciona e entra no contexto do iframe form
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe.hs-form-iframe")
            driver.switch_to.frame(iframe)

            # Desabilita o formulário! Comente ou apague a linha para enviar os dados de verdade.
            disable_form(driver)

            sleep(uniform(0.8, 1.5))
            field_boxes = driver.find_elements(By.CLASS_NAME, "field")
            field_boxes = [ box for box in field_boxes if "hs-form-field" in box.get_attribute("class").split() ]
            field_boxes.pop() # Remove campo reCaptcha
            field_boxes = list(filter(
                lambda f: "hs_country__drop_down_" not in f.get_attribute("class").split(), 
                field_boxes
            )) # Remove campo de país escondido
            field_boxes = list(filter(
                lambda f: "hs_hs_language" not in f.get_attribute("class").split(), 
                field_boxes
            )) # Remove campo de língua escondido
            
            # Separa e remove checkbox de consentimento dos outros inputs
            consent_checkbox = field_boxes[-1].find_element(By.CSS_SELECTOR, "input.hs-input")
            field_boxes.pop()
            # Garante que a Checkbox é cliquavél e clica
            driver.switch_to.window(main_window)
            driver.execute_script("window.scrollTo(0, 1400);")  # Scroll down 1400px
            sleep(2.8)
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(consent_checkbox)
            )
            consent_checkbox.click()

            sleep(uniform(1.7, 2.2))
            input_nome = field_boxes[0].find_element(By.TAG_NAME, "input")
            nome = row["nome"]
            input_nome.send_keys(nome)

            sleep(uniform(0.8, 1.4))
            input_sobrenome = field_boxes[1].find_element(By.TAG_NAME, "input")
            sobrenome = row["sobrenome"]
            input_sobrenome.send_keys(sobrenome)

            sleep(uniform(0.8, 1.4))
            input_email = field_boxes[2].find_element(By.TAG_NAME, "input")
            email = row["email"]
            input_email.send_keys(email)

            sleep(uniform(0.8, 1.4))
            input_telefone = field_boxes[3].find_element(By.TAG_NAME, "input")
            telefone = row["telefone"]
            # Válida o número de telefone e preenche o campo caso seja válido
            if valid_phonenumber(telefone):
                input_telefone.send_keys(telefone)
            else: 
                print(f"""
                    Número de telefone {telefone} informado na linha {i} é inválido para o formulário! 
                    Sendo este campo opcional, o formulário irá continuar o preenchimento automático!
                """)

            sleep(uniform(0.8, 1.4))
            input_empresa = field_boxes[4].find_element(By.TAG_NAME, "input")
            empresa = row["empresa"]
            input_empresa.send_keys(empresa)

            sleep(uniform(0.8, 1.4))
            cargo_select = field_boxes[5].find_element(By.TAG_NAME, "select")
            cargo = row["cargo"]
            try: 
                set_select_input_option(driver, cargo_select, cargo)
            except Exception as e:
                print(f"""
                    Opção {cargo} para o campo de Cargo não foi encontrada ou não existe. 
                    Mensagem de erro ao tentar selecionar: {e}\n
                    Linha da tabela não executada: {i}
                """)
                continue

            sleep(uniform(0.8, 1.4))
            segmento_select = field_boxes[6].find_element(By.TAG_NAME, "select")
            segmento = row["segmento"]
            try: 
                set_select_input_option(driver, segmento_select, segmento)
            except Exception as e:
                print(f"""
                    Opção {segmento} para o campo de Segmento não foi encontrada ou não existe. 
                    Mensagem de erro ao tentar selecionar: {e}\n 
                    Linha da tabela não executada: {i}
                """)
                continue

            sleep(uniform(0.8, 1.4))
            assunto_select = field_boxes[7].find_element(By.TAG_NAME, "select")
            assunto = row["assunto"]
            try: 
                set_select_input_option(driver, assunto_select, assunto)
            except Exception as e:
                print(f"""
                    Opção {assunto} para o campo de Assunto não foi encontrada ou não existe. 
                    Mensagem de erro ao tentar selecionar: {e}\n 
                    Linha da tabela não executada: {i}
                """)
                continue

            sleep(uniform(1, 1.8))
            input_msg = field_boxes[8].find_element(By.TAG_NAME, "textarea")
            msg = row["mensagem"]
            input_msg.send_keys(msg)

            sleep(uniform(0.4, 1))
            botao_submit = driver.find_element(By.CSS_SELECTOR, "input.hs-button")
            driver.switch_to.window(main_window)
            driver.execute_script("window.scrollTo(0, 1400);")  # Scroll down 1400px
            sleep(2.8)
            driver.switch_to.frame(iframe)
            botao_submit.click()

            while True:
                input("Resolva o captcha manualmente caso haja um, quando terminar pressione Enter no terminal e confirme...")
                print("Ou invalide a linha digitando 'i'.")
                res = input("Você resolveu o captcha? (s/n/i)").strip().lower()

                if res == "s" or res == "sim":
                    break
                
                if res == "i":
                    raise Exception(f"Linha nº{i} invalidada pelo usuário.")

        except Exception as e:
            print(f"Unexpected error occured: {e}\n")
            print(f"Não pôde gravar os dados da linha {i}.")
        
        driver.switch_to.window(main_window)
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.staleness_of(iframe)
        )
        
    sleep(7)
    driver.quit()


if __name__ == "__main__":
    main()
