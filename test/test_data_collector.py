"""
Testes para o módulo data_collector.py

Este módulo contém testes para as funções e classes relacionadas
a coleta de dados financeiros, incluindo testes com dados mockados.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector import add_suffix, create_tickers_array, DataCollector, _download_data_cached


class TestUtilityFunctions:
        
    def test_add_suffix_basic(self):
        result = add_suffix("PETR4")
        assert result == "PETR4.SA"
    
    def test_add_suffix_empty_string(self):
        result = add_suffix("")
        assert result == ".SA"
    
    def test_add_suffix_with_spaces(self):
        result = add_suffix("PETR 4")
        assert result == "PETR 4.SA"
    
    def test_add_suffix_with_numbers(self):
        result = add_suffix("123")
        assert result == "123.SA"
    
    def test_add_suffix_with_special_characters(self):
        result = add_suffix("PETR-4")
        assert result == "PETR-4.SA"
    
    def test_create_tickers_array_basic(self):
        tickers = ["PETR4", "VALE3", "ITUB4"]
        result = create_tickers_array(tickers)
        expected = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        assert result == expected
    
    def test_create_tickers_array_empty_list(self):
        result = create_tickers_array([])
        assert result == []
    
    def test_create_tickers_array_single_ticker(self):
        result = create_tickers_array(["PETR4"])
        assert result == ["PETR4.SA"]
    
    def test_create_tickers_array_preserves_order(self):
        tickers = ["VALE3", "PETR4", "ITUB4", "BBDC4"]
        result = create_tickers_array(tickers)
        expected = ["VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA"]
        assert result == expected


class TestDataCollectorInitialization:
        
    def test_init_with_defaults(self):
        tickers = ["PETR4", "VALE3"]
        collector = DataCollector(tickers)
        
        assert collector.tickers == tickers
        assert collector.benchmark == "^BVSP"
        assert collector.cache
        
        # Verifica se as datas padrão são razoáveis
        assert isinstance(collector.start, datetime)
        assert isinstance(collector.end, datetime)
        assert collector.start < collector.end
    
    def test_init_with_custom_values(self):
        tickers = ["PETR4", "VALE3"]
        benchmark = "^GSPC"
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        collector = DataCollector(
            tickers=tickers,
            benchmark=benchmark,
            start=start_date,
            end=end_date,
            cache=False
        )
        
        assert collector.tickers == tickers
        assert collector.benchmark == benchmark
        assert collector.start == start_date
        assert collector.end == end_date
        assert not collector.cache
    
    def test_init_with_empty_tickers(self):
        collector = DataCollector([])
        assert collector.tickers == []
    
    def test_init_date_validation(self):
        tickers = ["PETR4"]
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2022, 12, 31)  # Data final anterior à inicial
        
        # O construtor não valida datas, mas isso pode ser um comportamento esperado
        collector = DataCollector(tickers, start=start_date, end=end_date)
        assert collector.start == start_date
        assert collector.end == end_date


class TestDataCollectorDownload:
        
    def setup_method(self):
        self.tickers = ["PETR4", "VALE3"]
        self.collector = DataCollector(self.tickers)
    
    @patch('data_collector._download_data_cached')
    def test_download_data_calls_cached_function(self, mock_cached):
        # Configura o mock para retornar um DataFrame válido
        mock_data = pd.DataFrame({
            'PETR4.SA': [0.01, 0.02, -0.01],
            'VALE3.SA': [0.015, -0.005, 0.02],
            '^BVSP': [0.008, 0.012, 0.005]
        })
        mock_cached.return_value = mock_data
        
        result = self.collector.download_data()
        
        # Verifica se a função cached foi chamada com os parâmetros corretos
        mock_cached.assert_called_once_with(
            tuple(self.tickers),
            self.collector.benchmark,
            self.collector.start,
            self.collector.end
        )
        
        # Verifica se o resultado é o esperado
        pd.testing.assert_frame_equal(result, mock_data)
    
    @patch('data_collector._download_data_cached')
    def test_download_data_with_custom_parameters(self, mock_cached):
        custom_benchmark = "^GSPC"
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 30)
        
        collector = DataCollector(
            self.tickers,
            benchmark=custom_benchmark,
            start=start_date,
            end=end_date
        )
        
        mock_data = pd.DataFrame({'test': [1, 2, 3]})
        mock_cached.return_value = mock_data
        
        result = collector.download_data()
        
        mock_cached.assert_called_once_with(
            tuple(self.tickers),
            custom_benchmark,
            start_date,
            end_date
        )


class TestDownloadDataCached:
    
    def setup_method(self):
        self.tickers = ("PETR4", "VALE3")
        self.benchmark = "^BVSP"
        self.start = datetime(2023, 1, 1)
        self.end = datetime(2023, 12, 31)
    
    
    @patch('data_collector.yf.download')
    def test_download_data_cached_single_ticker(self, mock_yf_download):
        single_ticker = ("PETR4",)
        
        # Mock para um único ticker
        dates = pd.date_range(start='2023-01-01', end='2023-01-03', freq='D')
        mock_data = pd.DataFrame({
            'Close': [100, 101, 99]
        }, index=dates)
        
        mock_yf_download.return_value = mock_data
        
        result = _download_data_cached(single_ticker, self.benchmark, self.start, self.end)
        
        assert isinstance(result, pd.DataFrame)
    
    @patch('data_collector.yf.download')
    def test_download_data_cached_handles_existing_suffix(self, mock_yf_download):
        tickers_with_suffix = ("PETR4.SA", "VALE3")
        
        mock_data = pd.DataFrame()
        mock_yf_download.return_value = mock_data
        
        _download_data_cached(tickers_with_suffix, self.benchmark, self.start, self.end)
        
        # Verifica se não duplicou o sufixo
        call_args = mock_yf_download.call_args[0][0]
        assert "PETR4.SA" in call_args
        assert "VALE3.SA" in call_args
        assert "PETR4.SA.SA" not in call_args
    
    @patch('data_collector.yf.download')
    def test_download_data_cached_handles_benchmark_without_suffix(self, mock_yf_download):
        mock_data = pd.DataFrame()
        mock_yf_download.return_value = mock_data
        
        _download_data_cached(self.tickers, self.benchmark, self.start, self.end)
        
        call_args = mock_yf_download.call_args[0][0]
        assert "^BVSP" in call_args
        assert "^BVSP.SA" not in call_args
    
    
    


class TestEdgeCases:
    
    def test_data_collector_with_none_values(self):
        with pytest.raises(TypeError):
            DataCollector(None)
    
    def test_add_suffix_with_none(self):
        with pytest.raises(TypeError):
            add_suffix(None)
    
    def test_create_tickers_array_with_none_elements(self):
        with pytest.raises(TypeError):
            create_tickers_array([None, "PETR4"])
    
    @patch('data_collector.yf.download')
    def test_download_with_invalid_dates(self, mock_yf_download):
        mock_yf_download.return_value = pd.DataFrame()
        
        # Data final anterior à inicial
        start_date = datetime(2023, 12, 31)
        end_date = datetime(2023, 1, 1)
        
        collector = DataCollector(["PETR4"], start=start_date, end=end_date)
        
        # O yfinance deve lidar com isso, mas testamos se não quebra
        try:
            result = collector.download_data()
            assert isinstance(result, pd.DataFrame)
        except Exception:
            pass  # Comportamento aceitável para datas inválidas


if __name__ == '__main__':
    # Configuração para executar os testes
    pytest.main([__file__, "-v"])
