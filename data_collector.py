"""
Módulo para coleta e processamento de dados financeiros.

Este módulo contém classes e funções para baixar dados históricos
de ações do Yahoo Finance e processá-los para uso no algoritmo genético.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def add_suffix(ticker: str) -> str:
    """Adiciona sufixo .SA aos tickers brasileiros."""
    if ticker is None:
        raise TypeError("ticker cannot be None")
    return ticker + ".SA"

def create_tickers_array(tickers: list) -> list:
    """Converte lista de tickers adicionando sufixo .SA."""
    return [add_suffix(ticker) for ticker in tickers]

@st.cache_data
def _download_data_cached(tickers: tuple, benchmark: str, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Função cached para download de dados do yfinance.
    
    Args:
        tickers: Tupla com códigos dos ativos
        benchmark: Código do benchmark
        start: Data de início
        end: Data de fim
        
    Returns:
        pd.DataFrame: DataFrame com retornos percentuais dos ativos e benchmark
        
    Raises:
        Exception: Erro ao baixar dados do yfinance ou processar dados
    """
    try:
        tickers_with_suffix = []
        for ticker in tickers:
            if not ticker.endswith('.SA') and ticker != benchmark:
                tickers_with_suffix.append(add_suffix(ticker))
            else:
                tickers_with_suffix.append(ticker)
        
        all_tickers = tickers_with_suffix + [benchmark]
        data = yf.download(all_tickers, start=start, end=end, group_by="ticker", auto_adjust=True)
        adj_close = pd.DataFrame()
        
        for ticker in all_tickers:
            try:
                if len(all_tickers) == 1:
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

class DataCollector:
    """
    Classe responsável por coletar dados históricos de ativos financeiros.
    
    Esta classe utiliza o Yahoo Finance para baixar dados históricos
    de ações e benchmarks, processando-os para uso em algoritmos de otimização.
    """
    
    def __init__(
        self, 
        tickers: list, 
        benchmark: str = "^BVSP", 
        start: datetime = datetime.today() - timedelta(days=180), 
        end: datetime = datetime.today(), 
        cache: bool = True
    ):
        """
        Inicializa o coletor de dados.
        
        Args:
            tickers: Lista de códigos dos ativos
            benchmark: Código do benchmark (padrão: Ibovespa)
            start: Data de início dos dados
            end: Data de fim dos dados
            cache: Se deve usar cache para evitar downloads repetidos
        """
        if tickers is None:
            raise TypeError("tickers cannot be None")
        self.tickers = tickers
        self.benchmark = benchmark
        self.start = start
        self.end = end
        self.cache = cache
        
        # Configuração do cache para evitar downloads repetidos
        if cache:
            yf.set_tz_cache_location("./data/cache")
    
    def download_data(self) -> pd.DataFrame:
        """
        Faz o download dos preços ajustados dos ativos e do benchmark.
        
        Returns:
            pd.DataFrame: DataFrame com retornos percentuais dos ativos e benchmark
            
        Raises:
            Exception: Erro ao baixar dados do yfinance ou processar dados
        """
        return _download_data_cached(tuple(self.tickers), self.benchmark, self.start, self.end)
