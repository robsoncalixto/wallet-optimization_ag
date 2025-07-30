import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Configuração para evitar warnings de emojis em matplotlib
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Configuração adicional do matplotlib para fontes
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
from datetime import datetime, timedelta
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
from dados import ColetorDados, _baixar_dados_cached
from portfolio import Portfolio
from geneticAlgorithm import GeneticAlgorithm

st.set_page_config(page_title="Otimizador de Portfolio", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def _baixar_dados_ibovespa_cached(start_date, end_date):
    """Função cached para download de dados do Ibovespa.
    
    Args:
        start_date (datetime): Data de início
        end_date (datetime): Data de fim
        
    Returns:
        pd.DataFrame: DataFrame com preços de fechamento do Ibovespa
        
    Raises:
        Exception: Erro ao baixar dados do yfinance
    """
    try:
        import yfinance as yf
        data = yf.download("^BVSP", start=start_date, end=end_date, auto_adjust=True)
        return data
    except Exception as e:
        raise Exception(f"Erro ao baixar dados do Ibovespa: {str(e)}")

@st.cache_data
def carregar_empresas():
    """Carrega dados das empresas do arquivo CSV.
    
    Returns:
        list: Lista de dicionários com dados das empresas (código, nome, setor, preço)
        
    Raises:
        FileNotFoundError: Arquivo CSV não encontrado
        pd.errors.EmptyDataError: Arquivo CSV vazio ou corrompido
    """
    try:
        stocks_df = pd.read_csv("data/empresas_br_bovespa.csv")
        
        if stocks_df.empty:
            raise pd.errors.EmptyDataError("Arquivo CSV está vazio")
            

        empresas = []
        for _, row in stocks_df.iterrows():
            empresas.append({
                'codigo': row['Ticker'],
                'nome': row['Nome'],
                'setor': row['Setor'],
                'preco': row['Preço']
            })
        return empresas
        
    except FileNotFoundError:
        st.error("❌ Arquivo 'data/empresas_br_bovespa.csv' não encontrado. Verifique se o arquivo existe.")
        return []
    except pd.errors.EmptyDataError:
        st.error("❌ Arquivo CSV está vazio ou corrompido.")
        return []
    except KeyError as e:
        st.error(f"❌ Coluna obrigatória não encontrada no CSV: {e}")
        return []
    except Exception as e:
        st.error(f"❌ Erro inesperado ao carregar dados das empresas: {str(e)}")
        return []


if "etapa_atual" not in st.session_state:
    st.session_state.etapa_atual = 1
if "acoes_selecionadas" not in st.session_state:
    st.session_state.acoes_selecionadas = []
if "configuracao_investimento" not in st.session_state:
    st.session_state.configuracao_investimento = None
if "parametros_otimizacao" not in st.session_state:
    st.session_state.parametros_otimizacao = None
if "resultado_otimizacao" not in st.session_state:
    st.session_state.resultado_otimizacao = None



def mostrar_selecao_acoes():
    """Interface para seleção de ações e configuração do investimento.
    
    Permite ao usuário selecionar ações da Bovespa, definir valor do aporte
    e taxa livre de risco. Valida seleções e navega para próxima etapa.
    
    Raises:
        FileNotFoundError: Arquivo de empresas não encontrado
    """
    st.title("📈 Seleção das Ações")
    
    empresas = carregar_empresas()
    
    if not empresas:
        st.error("Não foi possível carregar os dados das empresas.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configuração do Investimento")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            valor_aporte = st.number_input("💰 Valor do Aporte (R$)", min_value=1000, value=10000, step=1000)
        
        with col_config2:
            risk_free_rate = st.slider("📊 Taxa Livre de Risco", 0.01, 0.10, 0.05, 0.01, 
                                     help="Taxa de referência para cálculo do fitness (Selic anual)")
        
        st.subheader("Filtros e Seleção de Ações")
        
        # Filtro por setor (remove valores NaN/None)
        setores_unicos = sorted(list(set(emp['setor'] for emp in empresas if emp['setor'] and not pd.isna(emp['setor']))))
        setores_disponiveis = ['Todos os Setores'] + setores_unicos
        setor_selecionado = st.selectbox("🏢 Filtrar por Setor", setores_disponiveis)
        
        # Aplicar filtro por setor
        if setor_selecionado == 'Todos os Setores':
            empresas_filtradas = empresas
        else:
            empresas_filtradas = [emp for emp in empresas if emp['setor'] == setor_selecionado and emp['setor'] and not pd.isna(emp['setor'])]
        
        # Converter para DataFrame para exibição
        df_empresas = pd.DataFrame(empresas_filtradas)
        df_empresas.columns = ['Código', 'Nome', 'Setor', 'Preço (R$)']
        
        # Checkbox para selecionar todas
        selecionar_todas = st.checkbox("Selecionar todas as ações disponíveis")
        
        if selecionar_todas:
            acoes_selecionadas = [emp['codigo'] for emp in empresas_filtradas]
        else:
            # Limite para performance
            st.info("💡 Recomendamos selecionar entre 5-20 ações para otimização eficiente")
            acoes_selecionadas = st.multiselect(
                "Escolha as ações para otimização:",
                [emp['codigo'] for emp in empresas_filtradas],
                default=[codigo for codigo in st.session_state.acoes_selecionadas if codigo in [emp['codigo'] for emp in empresas_filtradas]][:20],
                format_func=lambda x: f"{x} - {next((emp['nome'] for emp in empresas_filtradas if emp['codigo'] == x), x)} ({next((emp['setor'] for emp in empresas_filtradas if emp['codigo'] == x and emp['setor'] and not pd.isna(emp['setor'])), 'Sem Setor')})"
            )
        
        # Mostrar tabela das ações filtradas
        if setor_selecionado != 'Todos os Setores':
            st.subheader(f"Ações do Setor: {setor_selecionado}")
        else:
            st.subheader("Ações Disponíveis (Amostra)")
            
        if not df_empresas.empty:
            # Mostra todas as ações filtradas ou apenas uma amostra se for muitas
            df_exibir = df_empresas.head(20) if len(df_empresas) > 20 else df_empresas
            
            st.dataframe(
                df_exibir.style.format({
                    'Preço (R$)': 'R$ {:.2f}'
                }),
                use_container_width=True
            )
            
            if len(df_empresas) > 20:
                st.info(f"Mostrando 20 de {len(df_empresas)} ações do filtro selecionado. Use a seleção acima para escolher.")
            else:
                st.info(f"Exibindo todas as {len(df_empresas)} ações do filtro selecionado.")
    
    with col2:
        st.subheader("Resumo da Seleção")
        
        st.metric("Total de Ações", len(acoes_selecionadas) if acoes_selecionadas else 0)
        st.metric("Valor do Aporte", f"R$ {valor_aporte:,.2f}")
        st.metric("Taxa Livre de Risco", f"{risk_free_rate:.1%}")
        
        if empresas_filtradas and setor_selecionado != 'Todos os Setores':
            st.metric("Ações no Setor", len(empresas_filtradas))
        
        if acoes_selecionadas:
            st.write(f"**Primeiras 10 Ações Selecionadas:**")
            for codigo in acoes_selecionadas[:10]:
                empresa = next((emp for emp in empresas if emp['codigo'] == codigo), None)
                if empresa:
                    setor_display = empresa['setor'] if empresa['setor'] and not pd.isna(empresa['setor']) else 'Sem Setor'
                    st.write(f"• {codigo} - {empresa['nome']} ({setor_display})")
            
            if len(acoes_selecionadas) > 10:
                st.write(f"... e mais {len(acoes_selecionadas) - 10} ações")
                
            # Distribuição por setor das ações selecionadas
            if len(acoes_selecionadas) > 1:
                setores_selecionados = [next((emp['setor'] for emp in empresas if emp['codigo'] == codigo and emp['setor'] and not pd.isna(emp['setor'])), 'Sem Setor') for codigo in acoes_selecionadas]
                distribuicao_setores = pd.Series(setores_selecionados).value_counts()
                
                with st.expander("📊 Distribuição por Setor"):
                    for setor, count in distribuicao_setores.items():
                        st.write(f"• {setor}: {count} ação(ões)")
            
            # Validação
            if len(acoes_selecionadas) < 2:
                st.warning("⚠️ Selecione pelo menos 2 ações para diversificação")
                st.button("➡️ Configurar Otimização", disabled=True, help="Selecione pelo menos 2 ações")
            elif len(acoes_selecionadas) > 20:
                st.warning("⚠️ Muitas ações podem afetar a performance. Recomendamos no máximo 20.")
                if st.button("➡️ Configurar Otimização", type="secondary"):
                    st.session_state.acoes_selecionadas = acoes_selecionadas[:20]  # Limita a 20
                    st.session_state.configuracao_investimento = {
                        'capital_inicial': valor_aporte,
                        'risk_free_rate': risk_free_rate
                    }
                    st.session_state.etapa_atual = 2
                    st.rerun()
            else:
                st.success("✅ Seleção válida!")
                if st.button("➡️ Configurar Otimização", type="primary"):
                    st.session_state.acoes_selecionadas = acoes_selecionadas
                    st.session_state.configuracao_investimento = {
                        'capital_inicial': valor_aporte,
                        'risk_free_rate': risk_free_rate
                    }
                    st.session_state.etapa_atual = 2
                    st.rerun()
        else:
            st.info("📝 Selecione pelo menos uma ação para continuar")
            st.button("➡️ Configurar Otimização", disabled=True, help="Nenhuma ação selecionada")

def mostrar_parametros_algoritmo():
    """Interface para configuração dos parâmetros do algoritmo genético.
    
    Permite configurar tamanho da população, número máximo de gerações,
    taxas de crossover e mutação. Exibe resumo das configurações atuais.
    
    Raises:
        ValueError: Configuração de investimento não encontrada
    """
    st.title("⚙️ Configuração dos Parâmetros")
    
    if st.session_state.configuracao_investimento is None:
        st.error("Configuração de investimento não encontrada. Volte à etapa anterior.")
        return
    
    config = st.session_state.configuracao_investimento
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Parâmetros do Algoritmo Genético")
        
        st.info("⚙️ **Configuração Atual do Sistema:** Os parâmetros abaixo refletem a implementação real do algoritmo.")
        
        col_param1, col_param2 = st.columns(2)
        
        with col_param1:
            st.write("**Parâmetros da População**")
            # Valores fixos baseados na implementação atual
            tamanho_populacao = st.number_input("👥 Tamanho da População", 
                                               min_value=5, max_value=50, value=10, step=5,
                                               help="Valor padrão da implementação: 10")
            max_geracoes = st.number_input("🔄 Máximo de Gerações", 
                                         min_value=10, max_value=200, value=50, step=10,
                                         help="Valor padrão da implementação: 50")
            # Threshold fixo (valor realista para otimização de portfólio)
            threshold_fitness = 0.01  # Valor fixo mais apropriado
        
        with col_param2:
            st.write("**Operadores Genéticos**")
            taxa_crossover = st.slider("🧬 Taxa de Crossover", 0.3, 0.9, 0.5, 0.1,
                                      help="Valor padrão da implementação: 0.5 (50%)")
            taxa_mutacao = st.slider("🎲 Taxa de Mutação", 0.1, 0.5, 0.2, 0.05,
                                    help="Valor padrão da implementação: 0.2 (20%)")
            
            st.write("**Configurações Fixas:**")
            st.write("• **Seleção:** Tournament (3 competidores)")
            st.write("• **Crossover:** Single-point") 
            st.write("• **Elitismo:** Ativo (10% melhores)")
            st.write("• **Critério Parada:** Número máximo de gerações")
        

    
    with col2:
        st.subheader("Resumo da Configuração")
        
        st.metric("Ações Selecionadas", len(st.session_state.acoes_selecionadas))
        st.metric("Valor do Aporte", f"R$ {config['capital_inicial']:,.2f}")
        st.metric("Taxa Livre de Risco", f"{config['risk_free_rate']:.1%}")
        
        st.divider()
        
        st.write("**Parâmetros do Algoritmo:**")
        st.write(f"• População: {tamanho_populacao}")
        st.write(f"• Gerações Máx: {max_geracoes}")
        st.write(f"• Crossover: {taxa_crossover:.0%}")
        st.write(f"• Mutação: {taxa_mutacao:.0%}")
        

        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⬅️ Voltar"):
                st.session_state.etapa_atual = 2
                st.rerun()
        
        with col_btn2:
            if st.button("🚀 Executar Otimização", type="primary"):

                st.session_state.parametros_otimizacao = {
                    'population_size': tamanho_populacao,
                    'max_generations': max_geracoes,
                    'threshold': threshold_fitness,
                    'crossover_rate': taxa_crossover,
                    'mutation_rate': taxa_mutacao,
                    'risk_free_rate': config['risk_free_rate']
                }
                st.session_state.etapa_atual = 3
                st.rerun()

@st.cache_data
def calcular_benchmarks(returns_data_hash, capital_inicial, dias, acoes_selecionadas):
    """Calcula benchmark do Índice Bovespa usando dados reais do yfinance.
    
    Args:
        returns_data_hash (str): Hash dos dados de retorno para cache
        capital_inicial (float): Valor inicial do investimento
        dias (int): Número de dias para simulação
        acoes_selecionadas (list): Lista de ações selecionadas
        
    Returns:
        dict: Dicionário com valores do benchmark Bovespa
        
    Raises:
        ValueError: Erro nos parâmetros de entrada
    """
    try:
        if capital_inicial <= 0:
            raise ValueError("Capital inicial deve ser positivo")
        if dias <= 0:
            raise ValueError("Número de dias deve ser positivo")
            
        # Baixa dados reais do Ibovespa usando função cached
        end_date = datetime.now()
        start_date = end_date - timedelta(days=dias + 60)  # Margem maior para garantir dados suficientes
        

        bovespa_data = _baixar_dados_ibovespa_cached(start_date, end_date)
        
        if bovespa_data is None or bovespa_data.empty:
            raise ValueError("Não foi possível baixar dados do Ibovespa")
            
        # Extrai preços de fechamento (lida com MultiIndex)
        if 'Close' in bovespa_data.columns:
            close_prices = bovespa_data['Close']

            if hasattr(close_prices, 'squeeze'):
                close_prices = close_prices.squeeze()
        elif hasattr(bovespa_data.columns, 'levels') and 'Close' in bovespa_data.columns.get_level_values(0):
            # MultiIndex - pega a coluna Close
            close_prices = bovespa_data.xs('Close', axis=1, level=0)
            if hasattr(close_prices, 'squeeze'):
                close_prices = close_prices.squeeze()
        else:

            close_cols = [col for col in bovespa_data.columns if 'Close' in str(col)]
            if close_cols:
                close_prices = bovespa_data[close_cols[0]]
                if hasattr(close_prices, 'squeeze'):
                    close_prices = close_prices.squeeze()
            else:
                raise ValueError("Coluna 'Close' não encontrada nos dados do Ibovespa")
            

        bovespa_returns = close_prices.pct_change().dropna()
        
        if len(bovespa_returns) == 0:
            raise ValueError("Não foi possível calcular retornos do Ibovespa")
        

        if len(bovespa_returns) < dias:
            st.warning(f"⚠️ Apenas {len(bovespa_returns)} dias de dados disponíveis para o Ibovespa. Usando todos os dados disponíveis.")
            retornos_utilizados = bovespa_returns
        else:
            retornos_utilizados = bovespa_returns.tail(dias)
        
        # Converte para array numpy 1D de forma segura
        retornos_array = np.asarray(retornos_utilizados).flatten()
        

        retornos_array = retornos_array[~np.isnan(retornos_array)]
        
        if len(retornos_array) == 0:
            raise ValueError("Nenhum retorno válido encontrado")
            

        valor_cumulativo = capital_inicial * np.cumprod(1 + retornos_array)
        valor_bovespa = pd.Series(valor_cumulativo)
        

        valor_bovespa.reset_index(drop=True, inplace=True)
        
        return {
            'bovespa': valor_bovespa
        }

    except ValueError as e:
        st.error(f"❌ Erro nos parâmetros do benchmark: {str(e)}")

        return {
            'bovespa': pd.Series([capital_inicial] * max(1, dias))
        }
    except Exception as e:
        st.warning(f"⚠️ Erro ao baixar dados do Ibovespa, usando benchmark neutro: {str(e)}")

        return {
            'bovespa': pd.Series([capital_inicial] * max(1, dias))
        }

def executar_otimizacao_real():
    """Executa otimização usando a implementação real do algoritmo genético.
    
    Baixa dados históricos reais do Yahoo Finance, executa o algoritmo genético
    para otimizar a carteira e calcula métricas de performance.
    
    Returns:
        dict: Dicionário com resultados da otimização incluindo pesos, fitness,
              métricas de risco/retorno e histórico de evolução
              
    Raises:
        Exception: Erro ao baixar dados ou executar otimização
    """
    acoes = st.session_state.acoes_selecionadas
    params = st.session_state.parametros_otimizacao
    config = st.session_state.configuracao_investimento
    
    try:
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📊 Carregando dados históricos das ações...")
        progress_bar.progress(20)
        
        # Carrega dados históricos reais
        coletor = ColetorDados(acoes)
        returns_data = coletor.baixar_dados()
        
        # Filtra apenas as colunas que correspondem às ações selecionadas (com sufixo .SA)
        acoes_com_sufixo = [ticker + ".SA" if not ticker.endswith('.SA') else ticker for ticker in acoes]
        acoes_disponiveis = [col for col in returns_data.columns if col in acoes_com_sufixo or col in acoes]
        
        if len(acoes_disponiveis) < 2:
            raise ValueError(f"Dados insuficientes. Apenas {len(acoes_disponiveis)} ações disponíveis de {len(acoes)} selecionadas.")
        

        returns_data = returns_data[acoes_disponiveis]
        

        ticker_mapping = {}
        for ticker in acoes:
            ticker_sa = ticker + ".SA" if not ticker.endswith('.SA') else ticker
            if ticker_sa in acoes_disponiveis:
                ticker_mapping[ticker] = ticker_sa
            elif ticker in acoes_disponiveis:
                ticker_mapping[ticker] = ticker
        

        acoes_com_dados = list(ticker_mapping.keys())
        

        acoes_nao_carregadas = [ticker for ticker in acoes if ticker not in acoes_com_dados]
        if acoes_nao_carregadas:
            st.warning(f"⚠️ {len(acoes_nao_carregadas)} ação(ões) não puderam ser carregadas: {', '.join(acoes_nao_carregadas[:5])}{'...' if len(acoes_nao_carregadas) > 5 else ''}. Continuando com {len(acoes_com_dados)} ações.")
        
        status_text.text("🧬 Inicializando população do algoritmo genético...")
        progress_bar.progress(40)
        

        n_acoes = len(acoes_com_dados)
        initial_weights = {ticker: 1/n_acoes for ticker in acoes_com_dados}
        

        population = []
        for _ in range(params['population_size']):

            weights_for_portfolio = {}
            for ticker_orig in acoes_com_dados:
                ticker_data = ticker_mapping[ticker_orig]
                weights_for_portfolio[ticker_data] = 1/n_acoes
            
            portfolio = Portfolio.random_instance(
                weights=weights_for_portfolio,
                returns=returns_data,
                risk_free_rate=params['risk_free_rate']
            )
            population.append(portfolio)
        
        status_text.text("🔄 Executando evolução do algoritmo genético...")
        progress_bar.progress(60)
        

        ga = GeneticAlgorithm(
            population=population,
            fitness_key=lambda p: p.fitness(),
            max_generations=params['max_generations'],
            mutation_rate=params['mutation_rate'],
            crossover_rate=params['crossover_rate'],
            selection_type=GeneticAlgorithm.SelectionType.TOURNAMENT,
            threshold=params['threshold']
        )
        

        best_portfolio = ga.run()
        
        status_text.text("📈 Calculando métricas finais...")
        progress_bar.progress(90)
        

        pesos_otimos_raw = best_portfolio.weights
        fitness_final = best_portfolio.fitness()
        retorno_esperado = best_portfolio.ExpReturn
        cvar_final = best_portfolio.cvar
        

        pesos_otimos_display = {}
        for ticker_orig, ticker_data in ticker_mapping.items():
            if ticker_data in pesos_otimos_raw:
                pesos_otimos_display[ticker_orig] = pesos_otimos_raw[ticker_data]
        
        pesos_otimos = pd.Series(pesos_otimos_display)
        
        # Métricas adicionais - usa os pesos corretos alinhados com os dados
        pesos_para_calculo = pd.Series(pesos_otimos_raw)
        portfolio_returns = returns_data.dot(pesos_para_calculo)
        volatilidade = portfolio_returns.std() * np.sqrt(252)
        
        progress_bar.progress(100)
        status_text.text("✅ Otimização concluída!")
        

        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Simula dados de evolução se disponível
        if hasattr(ga, 'results') and ga.results is not None:
            fitness_hist = {
                'melhor': ga.results['best_fitness'].tolist(),
                'media': ga.results['mean_fitness'].tolist()
            }
            geracoes_executadas = len(ga.results['best_fitness'])
        else:

            geracoes_executadas = params['max_generations']
            fitness_hist = {
                'melhor': [fitness_final] * geracoes_executadas,
                'media': [fitness_final * 0.8] * geracoes_executadas
            }
        

        dias = 120
        valor_portfolio = pd.Series(config['capital_inicial'] * np.cumprod(1 + portfolio_returns.tail(dias)))
        

        returns_data_hash = str(hash(str(returns_data.values.tobytes())))
        benchmarks = calcular_benchmarks(returns_data_hash, config['capital_inicial'], dias, acoes_com_dados)
        
        progress_bar.empty()
        status_text.empty()
        
        return {
            'pesos': pesos_otimos,
            'fitness': fitness_final,
            'retorno_esperado': retorno_esperado,
            'volatilidade': volatilidade,
            'cvar': cvar_final,
            'fitness_hist': fitness_hist,
            'valor_portfolio': valor_portfolio,
            'valor_bovespa': benchmarks['bovespa'],
            'datas': pd.date_range(end=datetime.now(), periods=len(valor_portfolio)),
            'geracoes_executadas': geracoes_executadas,
            'convergiu': fitness_final >= params['threshold']
        }
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Erro na otimização: {str(e)}")
        
        # Fallback para dados simulados em caso de erro
        st.warning("Usando dados simulados devido ao erro. Verifique conectividade para dados reais.")
        return executar_otimizacao_simulada()

def executar_otimizacao_simulada():
    """Fallback com dados simulados para demonstração.
    
    Utilizada quando a otimização real falha ou para testes.
    Simula um algoritmo genético com parâmetros realísticos.
    
    Returns:
        dict: Dicionário com resultados simulados da otimização
        
    Raises:
        Exception: Erro durante simulação (raro)
    """
    acoes = st.session_state.acoes_selecionadas
    params = st.session_state.parametros_otimizacao
    config = st.session_state.configuracao_investimento
    
    n_acoes = len(acoes)
    

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(101):
        progress_bar.progress(i)
        if i < 30:
            status_text.text("🧬 Simulando população inicial...")
        elif i < 80:
            status_text.text(f"🔄 Evolução: Geração {int(i/80 * params['max_generations'])}")
        else:
            status_text.text("📊 Finalizando cálculos...")
        time.sleep(0.01)
    
    progress_bar.empty()
    status_text.empty()
    

    np.random.seed(42)
    pesos_raw = np.random.dirichlet(np.ones(n_acoes))
    pesos = pd.Series(pesos_raw, index=acoes)
    

    fitness_final = np.random.uniform(8.0, 15.0)
    retorno_esperado = np.random.uniform(0.08, 0.15)
    volatilidade = np.random.uniform(0.12, 0.25)
    cvar_simulado = -np.random.uniform(0.03, 0.08)
    

    geracoes = params['max_generations']
    fitness_inicial = fitness_final * 0.6
    fitness_melhor = []
    fitness_media = []
    
    for g in range(geracoes):
        progresso = 1 - np.exp(-g/20)
        fitness_ger = fitness_inicial + (fitness_final - fitness_inicial) * progresso
        fitness_melhor.append(fitness_ger + np.random.normal(0, 0.1))
        fitness_media.append(fitness_ger * 0.8 + np.random.normal(0, 0.05))
    
    # Simula valor do portfolio
    dias = 120
    retornos_simulados = np.random.normal(retorno_esperado/252, volatilidade/np.sqrt(252), dias)
    valor_portfolio = pd.Series(config['capital_inicial'] * np.cumprod(1 + retornos_simulados))
    

    returns_data_hash = "simulacao_" + str(hash(str(acoes)))
    benchmarks = calcular_benchmarks(returns_data_hash, config['capital_inicial'], dias, acoes)
    valor_bovespa = benchmarks['bovespa']
    
    # Limpa indicadores de progresso
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    return {
        'pesos': pesos,
        'fitness': fitness_final,
        'retorno_esperado': retorno_esperado,
        'volatilidade': volatilidade,
        'cvar': cvar_simulado,
        'fitness_hist': {
            'melhor': fitness_melhor,
            'media': fitness_media
        },
        'valor_portfolio': valor_portfolio,
        'valor_bovespa': valor_bovespa,
        'datas': pd.date_range(end=datetime.now(), periods=dias),
        'geracoes_executadas': geracoes,
        'convergiu': fitness_final >= params['threshold']
    }

def mostrar_resultados():
    """Exibe os resultados da otimização com visualizações interativas.
    
    Apresenta métricas de performance, gráficos de alocação, comparação
    com benchmarks e evolução do algoritmo genético em abas organizadas.
    
    Raises:
        Exception: Erro ao executar otimização ou gerar visualizações
    """
    st.title("Resultados da Otimização")
    

    if (st.session_state.resultado_otimizacao is None or 
        'valor_bovespa' not in st.session_state.resultado_otimizacao):
        st.session_state.resultado_otimizacao = executar_otimizacao_real()
    
    resultado = st.session_state.resultado_otimizacao
    config = st.session_state.configuracao_investimento
    

    col1, col2, col3, col4, col5 = st.columns(5)
    

    def get_last_value(data):
        """Obtém o último valor de um array ou Series de forma segura"""
        if hasattr(data, 'iloc'):
            return data.iloc[-1]
        else:
            return data[-1]
    
    valor_final_otimizado = get_last_value(resultado['valor_portfolio']) if len(resultado['valor_portfolio']) > 0 else config['capital_inicial']
    

    if 'valor_bovespa' in resultado and len(resultado['valor_bovespa']) > 0:
        valor_final_bovespa = get_last_value(resultado['valor_bovespa'])
    else:
        # Simula benchmark se não disponível
        valor_final_bovespa = config['capital_inicial'] * 1.05
    
    ganho_otimizado = valor_final_otimizado - config['capital_inicial']
    ganho_bovespa = valor_final_bovespa - config['capital_inicial']
    
    with col1:
        st.metric("Fitness Final", f"{resultado['fitness']:.3f}")
    with col2:
        st.metric("Retorno Esperado", f"{resultado['retorno_esperado']:.1%}")
    with col3:
        st.metric("CVaR (Risco)", f"{resultado['cvar']:.3f}")
    with col4:
        st.metric("Carteira Otimizada", f"R$ {valor_final_otimizado:,.2f}", f"R$ {ganho_otimizado:,.2f}")
    with col5:
    
        if ganho_otimizado > ganho_bovespa:
            delta_bovespa = f"+R$ {ganho_otimizado - ganho_bovespa:,.0f} vs Bovespa"
        else:
            delta_bovespa = f"-R$ {ganho_bovespa - ganho_otimizado:,.0f} vs Bovespa"
        st.metric("vs Benchmark", f"{((valor_final_otimizado/config['capital_inicial'])-1):.1%}", delta_bovespa)
    

    tab1, tab2, tab3 = st.tabs(["🥧 Alocação", "📈 Performance", "🧬 Evolução AG"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Composição da Carteira")
            df_pesos = pd.DataFrame({
                'Ação': resultado['pesos'].index,
                'Peso (%)': (resultado['pesos'] * 100).round(2),
                'Valor (R$)': (resultado['pesos'] * config['capital_inicial']).round(2)
            })
            st.dataframe(df_pesos, use_container_width=True)
            

            csv = df_pesos.to_csv(index=False)
            st.download_button(
                label="📥 Exportar Alocação (CSV)",
                data=csv,
                file_name=f"alocacao_otima_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.subheader("Distribuição por Ativo")
            try:

                pesos_plot = resultado['pesos'].sort_values(ascending=True)
                if len(pesos_plot) > 15:
                    outros = pesos_plot[:-15].sum()
                    pesos_plot = pesos_plot[-15:]
                    if outros > 0:
                        pesos_plot = pd.concat([pd.Series({'Outros': outros}), pesos_plot])
                
                fig, ax = plt.subplots(figsize=(8, max(6, len(pesos_plot) * 0.4)))
                

                colors = plt.cm.viridis(np.linspace(0, 1, len(pesos_plot)))
                bars = ax.barh(range(len(pesos_plot)), pesos_plot.values, color=colors)
                

                ax.set_yticks(range(len(pesos_plot)))
                ax.set_yticklabels(pesos_plot.index, fontsize=9)
                ax.set_xlabel("Alocação (%)")
                ax.set_title("Alocação Ótima da Carteira", fontsize=12, fontweight='bold')
                

                for i, (bar, valor) in enumerate(zip(bars, pesos_plot.values)):
                    ax.text(valor + max(pesos_plot.values) * 0.01, i, f'{valor:.1%}', 
                           va='center', fontsize=8, fontweight='bold')
                

                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
                

                ax.grid(axis='x', alpha=0.3, linestyle='--')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)  # Clean up memory
                
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de barras: {e}")
                st.write("**Distribuição por Peso:**")
                for ativo, peso in resultado['pesos'].sort_values(ascending=False).head(15).items():
                    st.write(f"• {ativo}: {peso:.1%}")
    
    with tab2:
        st.subheader("Comparação de Performance")
        
        # Aviso se benchmarks são simulados
        if ('valor_bovespa' not in resultado or 'valor_aleatorio' not in resultado):
            st.info("💡 **Nota:** Alguns benchmarks estão sendo simulados para demonstração. Execute uma nova otimização para obter dados reais.")
        
        if len(resultado['valor_portfolio']) > 1:
            # Gráfico principal de comparação
            fig, ax = plt.subplots(figsize=(14, 8))
            
            ax.plot(resultado['datas'], resultado['valor_portfolio'], 
                   label="Carteira Otimizada (AG)", linewidth=3, color='#2E8B57')
            
            # Verifica se benchmarks estão disponíveis para o gráfico
            if 'valor_bovespa' in resultado and len(resultado['valor_bovespa']) > 0:
                ax.plot(resultado['datas'], resultado['valor_bovespa'], 
                       label="Índice Bovespa", linewidth=2, linestyle='--', color='#1f77b4', alpha=0.8)
            else:
                # Simula benchmark se não disponível
                dias = len(resultado['datas'])
                retornos_bovespa_sim = np.random.normal(0.0003, 0.02, dias)
                valor_bovespa_sim = config['capital_inicial'] * np.cumprod(1 + retornos_bovespa_sim)
                ax.plot(resultado['datas'], valor_bovespa_sim, 
                       label="Bovespa (Simulado)", linewidth=2, linestyle='--', color='#1f77b4', alpha=0.8)
            
            # Linha de referência do capital inicial
            ax.axhline(y=config['capital_inicial'], color='gray', linestyle='-', alpha=0.5, label='Capital Inicial')
            
            ax.set_title("Evolução Comparativa dos Investimentos", fontsize=14, fontweight='bold')
            ax.set_xlabel("Data")
            ax.set_ylabel("Valor do Investimento (R$)")
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')
            

            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
    with tab3:
        st.subheader("Evolução do Algoritmo Genético")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        geracoes = range(1, len(resultado['fitness_hist']['melhor']) + 1)
        ax.plot(geracoes, resultado['fitness_hist']['melhor'], 
               label="Melhor Fitness", color="blue", linewidth=2)
        ax.plot(geracoes, resultado['fitness_hist']['media'], 
               label="Fitness Médio", color="orange", linestyle="--", alpha=0.7)
        ax.set_title("Evolução do Fitness por Geração")
        ax.set_xlabel("Geração")
        ax.set_ylabel("Fitness")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)  # Clean up memory
        

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Melhor Fitness", f"{max(resultado['fitness_hist']['melhor']):.3f}")
        with col2:
            st.metric("Gerações Executadas", f"{resultado['geracoes_executadas']}")
        with col3:
            convergencia = "✅ Sim" if resultado['convergiu'] else "❌ Não"
            st.metric("Convergiu", convergencia)
    

    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Voltar aos Parâmetros"):
            st.session_state.etapa_atual = 3
            st.rerun()
    
    with col2:
        if st.button("🔄 Nova Otimização"):

            st.session_state.etapa_atual = 1
            st.session_state.resultado_otimizacao = None
            st.session_state.acoes_selecionadas = []
            st.session_state.configuracao_investimento = None
            st.session_state.parametros_otimizacao = None
            st.rerun()
    
    with col3:
        if st.button("🔧 Ajustar Parâmetros"):
            st.session_state.resultado_otimizacao = None
            st.session_state.etapa_atual = 2
            st.rerun()




with st.sidebar:
    st.title("Navegação")
    

    etapas = ["Seleção", "Parâmetros", "Resultados"]
    etapa_atual = st.session_state.etapa_atual
    
    for i, etapa in enumerate(etapas, 1):
        if i < etapa_atual:
            st.success(f"✅ {i}. {etapa}")
        elif i == etapa_atual:
            st.info(f"▶️ {i}. {etapa}")
        else:
            st.write(f"⏳ {i}. {etapa}")
    
    st.divider()
    

    if etapa_atual > 1 and st.session_state.acoes_selecionadas:
        st.write("**Resumo:**")
        st.write(f"• {len(st.session_state.acoes_selecionadas)} ações")
        if st.session_state.configuracao_investimento:
            st.write(f"• R$ {st.session_state.configuracao_investimento['capital_inicial']:,.2f}")
    
    if etapa_atual > 2 and st.session_state.parametros_otimizacao:
        st.write(f"• {st.session_state.parametros_otimizacao['max_generations']} gerações")


if st.session_state.etapa_atual == 1:
    mostrar_selecao_acoes()
elif st.session_state.etapa_atual == 2:
    mostrar_parametros_algoritmo()
elif st.session_state.etapa_atual == 3:
    mostrar_resultados()


st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    🧬 Grupo 89 - Otimização de Carteira de Investimentos Utilizando Algoritmo Genético
</div>
""", unsafe_allow_html=True)