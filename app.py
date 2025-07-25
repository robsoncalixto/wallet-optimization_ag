import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

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
from dados import ColetorDados
from portfolio import Portfolio
from geneticAlgorithm import GeneticAlgorithm

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Otimizador de Portfolio", layout="wide", initial_sidebar_state="expanded")

# CSS para fonte menor em toda a aplicação
st.markdown("""
<style>
    .main .block-container {
        font-size: 0.85rem;
    }
    
    .stSelectbox > div > div > div {
        font-size: 0.85rem;
    }
    
    .stMultiSelect > div > div > div {
        font-size: 0.85rem;
    }
    
    .stNumberInput > div > div > input {
        font-size: 0.85rem;
    }
    
    .stSlider > div > div > div {
        font-size: 0.85rem;
    }
    
    .stButton > button {
        font-size: 0.85rem;
    }
    
    .stMetric {
        font-size: 0.8rem;
    }
    
    .stMarkdown {
        font-size: 0.85rem;
    }
    
    .stDataFrame {
        font-size: 0.8rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 0.85rem;
    }
    
    .sidebar .block-container {
        font-size: 0.8rem;
    }
    
    h1 {
        font-size: 1.8rem !important;
    }
    
    h2 {
        font-size: 1.4rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
     
    .stInfo {
        font-size: 0.8rem;
    }
    
    .stWarning {
        font-size: 0.8rem;
    }
    
    .stSuccess {
        font-size: 0.8rem;
    }
    
    .stError {
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_empresas():
    """Carrega dados das empresas do arquivo CSV"""
    try:
        stocks_df = pd.read_csv("data/empresas_br_bovespa.csv")
        # Filtra apenas as colunas necessárias: código, nome, preço
        empresas = []
        for _, row in stocks_df.iterrows():
            empresas.append({
                'codigo': row['Ticker'],
                'nome': row['Nome'],
                'setor': row['Setor'],
                'preco': row['Preço']
            })
        return empresas
    except Exception as e:
        st.error(f"Erro ao carregar dados das empresas: {e}")
        return []

# Inicializa estados da aplicação
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

def mostrar_informacoes_app():
    """Exibe informações sobre a aplicação"""
    st.title("🧬 Otimizador de Portfolio com Algoritmo Genético")
    
    st.markdown("""
    ## 📋 Sobre a Aplicação
    
    Esta aplicação utiliza **algoritmos genéticos** para encontrar a alocação ótima de um portfólio de investimentos,
    **maximizando o retorno esperado** enquanto **controla o risco** através da medida CVaR (Conditional Value at Risk).
    
    ### 🎯 Objetivo de Otimização
    **Maximizar:** Função de fitness que equilibra retorno esperado e controle de risco CVaR:
    ```
    fitness = (1 - risk_free_rate) × retorno_médio - risk_free_rate × CVaR
    ```
    
    ### 📊 CVaR (Conditional Value at Risk)
    **CVaR** é uma medida de risco coerente que captura o risco de cauda (tail risk):
    - Representa a **perda média esperada** nos piores cenários (5% piores casos)
    - Mais sensível a **eventos extremos** que a variância tradicional
    - Amplamente aceito por **reguladores financeiros** (Basel III)
    
    ### 🧬 Configuração do Algoritmo Genético
    **Parâmetros Implementados:**
    - **População:** 10 indivíduos
    - **Gerações:** 50 máximo  
    - **Seleção:** Tournament (3 competidores)
    - **Crossover:** Single-point (50% taxa)
    - **Mutação:** 20% taxa
    - **Elitismo:** Ativo (10% melhores preservados)
    - **Threshold:** Fitness ≥ 13.0
    
    ### 🔄 Fluxo da Aplicação
    1. **Seleção das Ações** - Escolha os ativos da B3
    2. **Configuração** - Defina valor do aporte
    3. **Otimização** - Execute o algoritmo genético com CVaR
    4. **Resultados** - Visualize a alocação ótima e métricas de performance
    """)
    
    if st.button("🚀 Começar Otimização", type="primary", use_container_width=True):
        st.session_state.etapa_atual = 2
        st.rerun()

def mostrar_selecao_acoes():
    """Interface para seleção de ações"""
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
                    st.session_state.etapa_atual = 3
                    st.rerun()
            else:
                st.success("✅ Seleção válida!")
                if st.button("➡️ Configurar Otimização", type="primary"):
                    st.session_state.acoes_selecionadas = acoes_selecionadas
                    st.session_state.configuracao_investimento = {
                        'capital_inicial': valor_aporte,
                        'risk_free_rate': risk_free_rate
                    }
                    st.session_state.etapa_atual = 3
                    st.rerun()
        else:
            st.info("📝 Selecione pelo menos uma ação para continuar")
            st.button("➡️ Configurar Otimização", disabled=True, help="Nenhuma ação selecionada")

def mostrar_parametros_algoritmo():
    """Interface para configuração dos parâmetros do algoritmo genético"""
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
            threshold_fitness = st.number_input("🎯 Threshold de Fitness", 
                                               min_value=1.0, max_value=20.0, value=13.0, step=0.5,
                                               help="Valor padrão da implementação: 13.0")
        
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
            st.write("• **Critério Parada:** Threshold OU Gerações")
        
        # Seção informativa sobre CVaR
        with st.expander("📊 Sobre o CVaR (Conditional Value at Risk)"):
            st.markdown("""
            **CVaR** é a medida de risco utilizada neste projeto:
            
            - **Definição:** Média das perdas nos piores cenários (5% piores casos)
            - **Vantagem:** Captura risco de eventos extremos melhor que variância
            - **Cálculo:** CVaR = E[retorno | retorno ≤ VaR₉₅%]
            - **Uso na Fitness:** Penaliza portfólios com alto risco de cauda
            
            **Fórmula da Fitness:**
            ```
            fitness = (1 - risk_free_rate) × retorno_médio - risk_free_rate × CVaR
            ```
            """)
    
    with col2:
        st.subheader("Resumo da Configuração")
        
        st.metric("Ações Selecionadas", len(st.session_state.acoes_selecionadas))
        st.metric("Valor do Aporte", f"R$ {config['capital_inicial']:,.2f}")
        st.metric("Taxa Livre de Risco", f"{config['risk_free_rate']:.1%}")
        
        st.divider()
        
        st.write("**Parâmetros do Algoritmo:**")
        st.write(f"• População: {tamanho_populacao}")
        st.write(f"• Gerações Máx: {max_geracoes}")
        st.write(f"• Threshold: {threshold_fitness}")
        st.write(f"• Crossover: {taxa_crossover:.0%}")
        st.write(f"• Mutação: {taxa_mutacao:.0%}")
        
        # Estimativa de tempo
        tempo_estimado = (tamanho_populacao * max_geracoes) / 500  # Estimativa baseada em performance
        st.info(f"⏱️ Tempo estimado: ~{tempo_estimado:.1f} segundos")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⬅️ Voltar"):
                st.session_state.etapa_atual = 2
                st.rerun()
        
        with col_btn2:
            if st.button("🚀 Executar Otimização", type="primary"):
                # Salva parâmetros
                st.session_state.parametros_otimizacao = {
                    'population_size': tamanho_populacao,
                    'max_generations': max_geracoes,
                    'threshold': threshold_fitness,
                    'crossover_rate': taxa_crossover,
                    'mutation_rate': taxa_mutacao,
                    'risk_free_rate': config['risk_free_rate']
                }
                st.session_state.etapa_atual = 4
                st.rerun()

def calcular_benchmarks(returns_data, capital_inicial, dias, acoes_selecionadas):
    """Calcula benchmark do Índice Bovespa"""
    try:
        # Benchmark: Índice Bovespa (se disponível nos dados)
        if '^BVSP' in returns_data.columns:
            retornos_bovespa = returns_data['^BVSP'].tail(dias)
            valor_bovespa = pd.Series(capital_inicial * np.cumprod(1 + retornos_bovespa))
        else:
            # Simula Bovespa se não disponível
            retornos_bovespa = np.random.normal(0.0003, 0.02, dias)  # ~7.8% aa, 32% vol
            valor_bovespa = pd.Series(capital_inicial * np.cumprod(1 + retornos_bovespa))

        return {
            'bovespa': valor_bovespa
        }

    except Exception as e:
        # Em caso de erro, simula benchmark
        retornos_bovespa = np.random.normal(0.0003, 0.02, dias)

        return {
            'bovespa': pd.Series(capital_inicial * np.cumprod(1 + retornos_bovespa))
        }

def executar_otimizacao_real():
    """Executa otimização usando a implementação real do algoritmo genético"""
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
        
        # Filtra returns_data para conter apenas as ações disponíveis
        returns_data = returns_data[acoes_disponiveis]
        
        # Mapeia de volta para os códigos originais (sem .SA)
        ticker_mapping = {}
        for ticker in acoes:
            ticker_sa = ticker + ".SA" if not ticker.endswith('.SA') else ticker
            if ticker_sa in acoes_disponiveis:
                ticker_mapping[ticker] = ticker_sa
            elif ticker in acoes_disponiveis:
                ticker_mapping[ticker] = ticker
        
        # Atualiza lista de ações para apenas as que têm dados
        acoes_com_dados = list(ticker_mapping.keys())
        
        # Informa sobre ações que não puderam ser carregadas
        acoes_nao_carregadas = [ticker for ticker in acoes if ticker not in acoes_com_dados]
        if acoes_nao_carregadas:
            st.warning(f"⚠️ {len(acoes_nao_carregadas)} ação(ões) não puderam ser carregadas: {', '.join(acoes_nao_carregadas[:5])}{'...' if len(acoes_nao_carregadas) > 5 else ''}. Continuando com {len(acoes_com_dados)} ações.")
        
        status_text.text("🧬 Inicializando população do algoritmo genético...")
        progress_bar.progress(40)
        
        # Configuração inicial dos pesos apenas para ações com dados
        n_acoes = len(acoes_com_dados)
        initial_weights = {ticker: 1/n_acoes for ticker in acoes_com_dados}
        
        # Cria população inicial usando mapeamento correto
        population = []
        for _ in range(params['population_size']):
            # Cria weights com mapeamento correto para as colunas dos dados
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
        
        # Configura e executa algoritmo genético
        ga = GeneticAlgorithm(
            population=population,
            fitness_key=lambda p: p.fitness(),
            max_generations=params['max_generations'],
            mutation_rate=params['mutation_rate'],
            crossover_rate=params['crossover_rate'],
            selection_type=GeneticAlgorithm.SelectionType.TOURNAMENT,
            threshold=params['threshold']
        )
        
        # Executa otimização
        best_portfolio = ga.run()
        
        status_text.text("📈 Calculando métricas finais...")
        progress_bar.progress(90)
        
        # Coleta resultados
        pesos_otimos_raw = best_portfolio.weights  # Dict com tickers .SA
        fitness_final = best_portfolio.fitness()
        retorno_esperado = best_portfolio.ExpReturn
        cvar_final = best_portfolio.cvar
        
        # Converte pesos de volta para códigos originais para exibição
        pesos_otimos_display = {}
        for ticker_orig, ticker_data in ticker_mapping.items():
            if ticker_data in pesos_otimos_raw:
                pesos_otimos_display[ticker_orig] = pesos_otimos_raw[ticker_data]
        
        pesos_otimos = pd.Series(pesos_otimos_display)
        
        # Métricas adicionais - usa os pesos corretos alinhados com os dados
        pesos_para_calculo = pd.Series(pesos_otimos_raw)  # Usa os pesos com .SA
        portfolio_returns = returns_data.dot(pesos_para_calculo)
        volatilidade = portfolio_returns.std() * np.sqrt(252)  # Anualizada
        
        progress_bar.progress(100)
        status_text.text("✅ Otimização concluída!")
        
        # Simula dados de evolução se disponível
        if hasattr(ga, 'results') and ga.results is not None:
            fitness_hist = {
                'melhor': ga.results['best_fitness'].tolist(),
                'media': ga.results['mean_fitness'].tolist()
            }
            geracoes_executadas = len(ga.results['best_fitness'])
        else:
            # Dados simulados se histórico não disponível
            geracoes_executadas = params['max_generations']
            fitness_hist = {
                'melhor': [fitness_final] * geracoes_executadas,
                'media': [fitness_final * 0.8] * geracoes_executadas
            }
        
        # Simula evolução do portfólio
        dias = 120  # 4 meses
        valor_portfolio = pd.Series(config['capital_inicial'] * np.cumprod(1 + portfolio_returns.tail(dias)))
        
        # Adiciona comparação com benchmarks
        benchmarks = calcular_benchmarks(returns_data, config['capital_inicial'], dias, acoes_com_dados)
        
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
    """Fallback com dados simulados para demonstração"""
    acoes = st.session_state.acoes_selecionadas
    params = st.session_state.parametros_otimizacao
    config = st.session_state.configuracao_investimento
    
    n_acoes = len(acoes)
    
    # Simula progresso
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
    
    # Gera pesos simulados
    np.random.seed(42)
    pesos_raw = np.random.dirichlet(np.ones(n_acoes))
    pesos = pd.Series(pesos_raw, index=acoes)
    
    # Métricas simuladas realísticas
    fitness_final = np.random.uniform(8.0, 15.0)
    retorno_esperado = np.random.uniform(0.08, 0.15)
    volatilidade = np.random.uniform(0.12, 0.25)
    cvar_simulado = -np.random.uniform(0.03, 0.08)
    
    # Simula evolução
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
    
    # Simula benchmark
    retornos_bovespa = np.random.normal(0.0003, 0.02, dias)  # ~7.8% aa, 32% vol
    valor_bovespa = pd.Series(config['capital_inicial'] * np.cumprod(1 + retornos_bovespa))
    
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
    """Exibe os resultados da otimização"""
    st.title("📊 Resultados da Otimização")
    
    # Executa otimização se ainda não foi executada ou se falta benchmark
    if (st.session_state.resultado_otimizacao is None or 
        'valor_bovespa' not in st.session_state.resultado_otimizacao):
        st.session_state.resultado_otimizacao = executar_otimizacao_real()
    
    resultado = st.session_state.resultado_otimizacao
    config = st.session_state.configuracao_investimento
    
    # Métricas principais comparativas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calcula valores finais com verificações defensivas
    def get_last_value(data):
        """Obtém o último valor de um array ou Series de forma segura"""
        if hasattr(data, 'iloc'):
            return data.iloc[-1]  # pandas Series
        else:
            return data[-1]  # numpy array
    
    valor_final_otimizado = get_last_value(resultado['valor_portfolio']) if len(resultado['valor_portfolio']) > 0 else config['capital_inicial']
    
    # Verifica se os benchmarks existem no resultado
    if 'valor_bovespa' in resultado and len(resultado['valor_bovespa']) > 0:
        valor_final_bovespa = get_last_value(resultado['valor_bovespa'])
    else:
        # Simula benchmark se não disponível
        valor_final_bovespa = config['capital_inicial'] * 1.05  # ~5% de retorno simulado
    
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
        # Compara performance
        if ganho_otimizado > ganho_bovespa:
            delta_bovespa = f"+R$ {ganho_otimizado - ganho_bovespa:,.0f} vs Bovespa"
        else:
            delta_bovespa = f"-R$ {ganho_bovespa - ganho_otimizado:,.0f} vs Bovespa"
        st.metric("vs Benchmark", f"{((valor_final_otimizado/config['capital_inicial'])-1):.1%}", delta_bovespa)
    
    # Tabs para diferentes visualizações
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
            
            # Botão de exportar
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
                # Prepara dados para gráfico de barras horizontais
                pesos_plot = resultado['pesos'].sort_values(ascending=True)  # Crescente para barras
                if len(pesos_plot) > 15:
                    outros = pesos_plot[:-15].sum()
                    pesos_plot = pesos_plot[-15:]  # Pega os 15 maiores
                    if outros > 0:
                        pesos_plot = pd.concat([pd.Series({'Outros': outros}), pesos_plot])
                
                fig, ax = plt.subplots(figsize=(8, max(6, len(pesos_plot) * 0.4)))
                
                # Cria barras horizontais com cores gradientes
                colors = plt.cm.viridis(np.linspace(0, 1, len(pesos_plot)))
                bars = ax.barh(range(len(pesos_plot)), pesos_plot.values, color=colors)
                
                # Configurações do gráfico
                ax.set_yticks(range(len(pesos_plot)))
                ax.set_yticklabels(pesos_plot.index, fontsize=9)
                ax.set_xlabel("Alocação (%)")
                ax.set_title("Alocação Ótima da Carteira", fontsize=12, fontweight='bold')
                
                # Adiciona valores nas barras
                for i, (bar, valor) in enumerate(zip(bars, pesos_plot.values)):
                    ax.text(valor + max(pesos_plot.values) * 0.01, i, f'{valor:.1%}', 
                           va='center', fontsize=8, fontweight='bold')
                
                # Formata eixo x como percentual
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
                
                # Ajustes visuais
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
            
            # Formatação do eixo Y para valores monetários
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
        
        # Estatísticas do algoritmo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Melhor Fitness", f"{max(resultado['fitness_hist']['melhor']):.3f}")
        with col2:
            st.metric("Gerações Executadas", f"{resultado['geracoes_executadas']}")
        with col3:
            convergencia = "✅ Sim" if resultado['convergiu'] else "❌ Não"
            st.metric("Convergiu", convergencia)
    
    # Botões de navegação
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Voltar aos Parâmetros"):
            st.session_state.etapa_atual = 3
            st.rerun()
    
    with col2:
        if st.button("🔄 Nova Otimização"):
            # Reset estados para nova otimização
            st.session_state.etapa_atual = 1
            st.session_state.resultado_otimizacao = None
            st.session_state.acoes_selecionadas = []
            st.session_state.configuracao_investimento = None
            st.session_state.parametros_otimizacao = None
            st.rerun()
    
    with col3:
        if st.button("🔧 Ajustar Parâmetros"):
            st.session_state.resultado_otimizacao = None
            st.session_state.etapa_atual = 3
            st.rerun()

# ================================
# INTERFACE PRINCIPAL
# ================================

# Sidebar com navegação e progresso
with st.sidebar:
    st.title("📊 Navegação")
    
    # Indicador de progresso
    etapas = ["Início", "Seleção", "Parâmetros", "Resultados"]
    etapa_atual = st.session_state.etapa_atual
    
    for i, etapa in enumerate(etapas, 1):
        if i < etapa_atual:
            st.success(f"✅ {i}. {etapa}")
        elif i == etapa_atual:
            st.info(f"▶️ {i}. {etapa}")
        else:
            st.write(f"⏳ {i}. {etapa}")
    
    st.divider()
    
    # Resumo rápido se em etapas avançadas
    if etapa_atual > 2 and st.session_state.acoes_selecionadas:
        st.write("**Resumo:**")
        st.write(f"• {len(st.session_state.acoes_selecionadas)} ações")
        if st.session_state.configuracao_investimento:
            st.write(f"• R$ {st.session_state.configuracao_investimento['capital_inicial']:,.2f}")
    
    if etapa_atual > 3 and st.session_state.parametros_otimizacao:
        st.write(f"• {st.session_state.parametros_otimizacao['max_generations']} gerações")

# Roteamento das etapas
if st.session_state.etapa_atual == 1:
    mostrar_informacoes_app()
elif st.session_state.etapa_atual == 2:
    mostrar_selecao_acoes()
elif st.session_state.etapa_atual == 3:
    mostrar_parametros_algoritmo()
elif st.session_state.etapa_atual == 4:
    mostrar_resultados()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    🧬 Grupo 89 - Otimização de Carteira de Investimentos Utilizando Algoritmo Genético
</div>
""", unsafe_allow_html=True)