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

from time import sleep
from random import uniform
import re


URL = "https://radixeng.com.br/contato"

def valid_phonenumber(number: str) -> bool:
    """
        Valida um determinado número de acordo com a validação do formulário alvo. 
        Validação: 
        Deve ter 7 ou mais números (dígitos) E Ser constituída apenas de números, +, -, (, ), (espaço) 
    """
    numbersonly = re.sub(r"\D", "", number)

    return len(numbersonly) >= 7 and re.match(r"[0-9+\-() ]+", number) is not None

def get_valid_phonenumber() -> str:
    """
        Recebe o número de telefone do usuário, tentanto novamente sempre que o número é inválido
    """
    num = input("Número de Celular: ").strip()

    while not valid_phonenumber(num):
        print("""
              ----- Número de Celular Inválido - Deve conter 7 ou mais números e deve se 
              constituir apenas de números e caracteres especiais (+, -, (, ), ) -----
        """)
        num = input("Número de Celular: ").strip()
    
    return num

def get_selection_field_input(driver: WebDriver, select_elem: WebElement, label: str = "Opções: ") -> None: 
    """
        Dado um [WebElement] do tipo select: 
            - Capta as opções contidas no input select
            - Mostra as opções para o usuário
            - permite que o usuário escolha uma das opções através de um índice númerico

        [params]: 
            - [select_elem]: WebElement do tipo input select
            - [label]: Label opcional para a escolha das opções
    """
    _ = driver
    options = select_elem.find_elements(By.TAG_NAME, "option")
    options = [ op for op in options if not op.get_attribute("disabled") ] # Remove Opção Default Desabilitada

    # Monta o prompt de pergunta
    prompt = f"{label}\n"
    for i, opt in enumerate(options):
        prompt += f"\t{i+1}) {opt.text}\n"

    # Verifica se user_opt está no range da lista (options)
    in_list_range = lambda n, l: n <= len(l) and n > 0
    # Pega a opção do usuário
    user_opt = ""
    while True:
        user_opt = input(prompt+"\n").strip()
        if user_opt.isdigit() and in_list_range(int(user_opt), options):
            break
    
    # Seleciona a opção
    options[int(user_opt) - 1].click()

def main() -> None:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.chrome}")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options, service=service)

    sleep(uniform(0.8, 1.8))
    driver.get(URL)

    main_window = driver.current_window_handle

    # Espera carregamento do Form
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.hbspt-form"))
    )
    # Seleciona e entra no contexto do iframe form
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe.hs-form-iframe")
    driver.switch_to.frame(iframe)

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
    nome = input("Nome: ").strip()
    input_nome.send_keys(nome)

    sleep(uniform(0.8, 1.4))
    input_sobrenome = field_boxes[1].find_element(By.TAG_NAME, "input")
    sobrenome = input("Sobrenome: ").strip()
    input_sobrenome.send_keys(sobrenome)

    sleep(uniform(0.8, 1.4))
    input_email = field_boxes[2].find_element(By.TAG_NAME, "input")
    email = input("E-mail corporativo: ").strip()
    input_email.send_keys(email)

    sleep(uniform(0.8, 1.4))
    input_telefone = field_boxes[3].find_element(By.TAG_NAME, "input")
    telefone = get_valid_phonenumber()
    input_telefone.send_keys(telefone)

    sleep(uniform(0.8, 1.4))
    input_empresa = field_boxes[4].find_element(By.TAG_NAME, "input")
    empresa = input("Nome da empresa: ").strip()
    input_empresa.send_keys(empresa)

    sleep(uniform(0.8, 1.4))
    cargo_select = field_boxes[5].find_element(By.TAG_NAME, "select")
    get_selection_field_input(driver, cargo_select, label="Selecione seu Cargo: ")

    sleep(uniform(0.8, 1.4))
    segmento_select = field_boxes[6].find_element(By.TAG_NAME, "select")
    get_selection_field_input(driver, segmento_select, label="Selecione seu Segmento: ")

    sleep(uniform(0.8, 1.4))
    assunto_select = field_boxes[7].find_element(By.TAG_NAME, "select")
    get_selection_field_input(driver, assunto_select, label="Selecione o Assunto: ") 

    sleep(uniform(1, 1.8))
    input_msg = field_boxes[8].find_element(By.TAG_NAME, "textarea")
    msg = input("Mensagem: ").strip()
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
        res = input("Você resolveu o captcha? (s/n) ").strip().lower()

        if res == "s" or res == "sim":
            break

    
    driver.switch_to.window(main_window)
    sleep(4.5)
    driver.quit()


if __name__ == "__main__":
    main()
