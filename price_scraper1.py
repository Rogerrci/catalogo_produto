from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
import time

def format_price(price_text):
    """
    Convert price text from Brazilian format (2.500,00) to float (2500.00)
    """
    # Remove currency symbol and whitespace
    price_text = price_text.replace('R$', '').strip()
    # Remove all dots (thousand separators)
    price_text = price_text.replace('.', '')
    # Replace comma with dot for decimal point
    price_text = price_text.replace(',', '.')
    return float(price_text)

def format_currency(value):
    """
    Format number to Brazilian currency format (R$ 0.000,00)
    """
    if pd.isna(value):
        return ''
    return f'R$ {value:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')

def calculate_discount(value, percentage):
    """
    Calculate discounted price
    """
    if pd.isna(value):
        return None
    return value * (1 - percentage/100)

def buscar_preco(driver, url):
    try:
        driver.get(url)

        # Verifica se o produto existe
        error_message_elements = driver.find_elements(By.XPATH, '/html/body/main/section/div/div/h1')
        if error_message_elements:
            error_message_text = error_message_elements[0].text.strip()
            if "The requested detailed product page was not found." in error_message_text:
                print(f"Produto não encontrado na URL: {url}")
                return None

        # Aguarda carregamento da página
        time.sleep(1)

        # Busca o elemento de preço usando o novo XPath
        preco_element = driver.find_element(
            By.XPATH, '/html/body/main/section/div/div/div/div[1]/div[3]/div[2]/div[1]/div/div/div[1]/span[2]')
        
        if preco_element:
            preco_texto = preco_element.text.strip()
            try:
                preco = format_price(preco_texto)
                #print(f"Preço encontrado: {format_currency(preco)} para URL: {url}")
                return preco
            except ValueError as e:
                print(f"Erro ao converter preço '{preco_texto}': {e}")
                return None

    except TimeoutException:
        print(f"Tempo de espera expirado ao buscar preço para URL: {url}")
        return None
    except Exception as e:
        print(f"Erro ao buscar preço para URL {url}: {e}")
        return None

    return None

def main():
    # Configuração do Selenium com User Agent aleatório
    options = webdriver.ChromeOptions()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
   
    # Caminho do ChromeDriver no drive D:
    service = Service(executable_path="D:\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Lê o arquivo CSV com separador ponto e vírgula
        arquivo_entrada = 'produtos.csv'
        #print(f"Lendo arquivo: {arquivo_entrada}")
        df = pd.read_csv(arquivo_entrada, sep=';')
        
        # Colunas para os resultados
        df['preco'] = None
        df['total'] = None
        df['desconto_35'] = None  # Nova coluna para desconto de 35%
        df['desconto_50'] = None  # Nova coluna para desconto de 50%

        # Processa cada produto
        total_produtos = len(df)
        valor_total_geral = 0.0
        valor_total_35 = 0.0
        valor_total_50 = 0.0
        
        for index, row in df.iterrows():
            codigo = str(row['codigo']).strip()
            quantidade = float(row['quantidade'])
            
            #print(f"\nProcessando produto {index + 1} de {total_produtos}")
            #print(f"Código: {codigo}, Quantidade: {quantidade}")
            
            # Atualizado para usar a URL base br/pt
            url = f"https://www.ifm.com/br/pt/product/{codigo}"
            preco = buscar_preco(driver, url)
            
            if preco is not None:
                # Calcula preço total sem desconto
                total = preco * quantidade
                df.at[index, 'preco'] = preco
                df.at[index, 'total'] = total
                valor_total_geral += total

                # Calcula preços com desconto
                total_35 = calculate_discount(total, 35)
                total_50 = calculate_discount(total, 50)
                
                df.at[index, 'desconto_35'] = total_35
                df.at[index, 'desconto_50'] = total_50
                
                valor_total_35 += total_35
                valor_total_50 += total_50

                #print(f"Preço unitário: {format_currency(preco)}")
                #print(f"Total: {format_currency(total)}")
                #print(f"Total com 35% desconto: {format_currency(total_35)}")
                #print(f"Total com 50% desconto: {format_currency(total_50)}")
            else:
                print(f"Não foi possível obter o preço para o código {codigo}")

        # Formata as colunas monetárias
        df['preco'] = df['preco'].apply(format_currency)
        df['total'] = df['total'].apply(format_currency)
        df['desconto_35'] = df['desconto_35'].apply(format_currency)
        df['desconto_50'] = df['desconto_50'].apply(format_currency)

        # Adiciona linha com totais gerais
        df_total = pd.DataFrame([{
            'codigo': 'TOTAL GERAL',
            'quantidade': '',
            'preco': '',
            'total': format_currency(valor_total_geral),
            'desconto_35': format_currency(valor_total_35),
            'desconto_50': format_currency(valor_total_50)
        }])
        df = pd.concat([df, df_total], ignore_index=True)

        # Salva os resultados usando ponto e vírgula como separador
        arquivo_saida = 'resultado_precos.csv'
        df.to_csv(arquivo_saida, sep=';', index=False)
        
        #print("\n" + "="*50)
        #print(f"RESUMO FINAL:")
        #print(f"Total de produtos processados: {total_produtos}")
        #print(f"Valor total sem desconto: {format_currency(valor_total_geral)}")
        #print(f"Valor total com 35% desconto: {format_currency(valor_total_35)}")
        #print(f"Valor total com 50% desconto: {format_currency(valor_total_50)}")
        #print("="*50)
        #print(f"\nResultados detalhados salvos em: {arquivo_saida}")

    except Exception as e:
        print(f"Erro durante a execução: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
