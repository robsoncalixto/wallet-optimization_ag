import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def add_suffix(ticker):
    """Adiciona sufixo .SA aos tickers brasileiros."""
    return ticker + ".SA"

def create_tickers_array(tickers):
    """Converte lista de tickers adicionando sufixo .SA."""
    return [add_suffix(ticker) for ticker in tickers]

@st.cache_data
def _baixar_dados_cached(tickers, benchmark, start, end):
    """Função cached para download de dados do yfinance.
    
    Args:
        tickers (tuple): Tupla com códigos dos ativos
        benchmark (str): Código do benchmark
        start (datetime): Data de início
        end (datetime): Data de fim
        
    Returns:
        pd.DataFrame: DataFrame com retornos percentuais dos ativos e benchmark
        
    Raises:
        Exception: Erro ao baixar dados do yfinance ou processar dados
    """
    try:
        # Prepara lista de tickers com sufixo .SA se necessário
        tickers_com_sufixo = []
        for ticker in tickers:
            if not ticker.endswith('.SA') and ticker != benchmark:
                tickers_com_sufixo.append(add_suffix(ticker))
            else:
                tickers_com_sufixo.append(ticker)
        
        # Adiciona benchmark à lista
        todos_tickers = tickers_com_sufixo + [benchmark]
        
        # Download dos dados
        data = yf.download(todos_tickers, start=start, end=end, group_by="ticker", auto_adjust=True)
        adj_close = pd.DataFrame()

        # Extrai coluna Close para cada ticker
        for ticker in todos_tickers:
            try:
                if len(todos_tickers) == 1:
                    # yfinance retorna estrutura diferente para um único ticker
                    adj_close[ticker] = data['Close']
                else:
                    adj_close[ticker] = data[ticker]['Close']
            except (KeyError, TypeError) as e:
                print(f"Erro ao processar ticker {ticker}: {e}")
                continue
        
        # Remove colunas com muitos NaNs e retorna variações percentuais
        adj_close.dropna(axis=1, inplace=True)
        return adj_close.pct_change().dropna()
        
    except Exception as e:
        raise Exception(f"Erro ao baixar dados históricos: {str(e)}")

class ColetorDados:
    """Classe que coleta os dados dos ativos e do benchmark."""
    def __init__(self, tickers, benchmark="^BVSP", start=datetime.today() - timedelta(days=180), end=datetime.today(), cache=True):
        self.tickers = tickers
        self.benchmark = benchmark
        self.start = start
        self.end = end
        self.cache = cache
        # Configuração do cache para evitar downloads repetidos
        if cache:
            yf.set_tz_cache_location("./data/cache")
    
    def baixar_dados(self):
        """Faz o download dos preços ajustados dos ativos e do benchmark.
        
        Returns:
            pd.DataFrame: DataFrame com retornos percentuais dos ativos e benchmark
            
        Raises:
            Exception: Erro ao baixar dados do yfinance ou processar dados
        """
        return _baixar_dados_cached(tuple(self.tickers), self.benchmark, self.start, self.end)
    
    
   