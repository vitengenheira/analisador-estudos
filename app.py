# 📦 Importando bibliotecas necessárias
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import os
import unicodedata

# 🧠 Função para remover acentos (compatível com fpdf)
def remover_acentos(txt):
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

# 📊 Função que gera o gráfico interativo com Plotly (cacheado)
@st.cache_data
def gerar_grafico(dias, horas):
    fig = go.Figure(data=[go.Bar(x=dias, y=horas, marker_color='skyblue')])
    fig.update_layout(
        title='Estudos da Semana',
        xaxis_title='Dias da Semana',
        yaxis_title='Horas Estudadas',
        yaxis=dict(range=[0, 12]),
        template='plotly_white'
    )
    return fig

# 📄 Função que gera o PDF com dados convertidos em ASCII e inclui o gráfico
def gerar_pdf(nome_aluno, dias_semana, horas_estudo, media, maximo, minimo, avaliacao, nome_pdf, img_grafico):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    nome_ascii = remover_acentos(nome_aluno)
    avaliacao_ascii = remover_acentos(avaliacao)

    pdf.cell(200, 10, txt=f"Relatorio de Estudos - {nome_ascii}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Horas de estudo por dia:", ln=True)

    for dia, horas in zip(dias_semana, horas_estudo):
        dia_ascii = remover_acentos(dia)
        pdf.cell(200, 10, txt=f"{dia_ascii}: {horas:.1f} horas", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Media diaria: {media:.2f} horas", ln=True)
    pdf.cell(200, 10, txt=f"Maximo: {maximo:.2f} horas", ln=True)
    pdf.cell(200, 10, txt=f"Minimo: {minimo:.2f} horas", ln=True)
    pdf.cell(200, 10, txt=f"Avaliacao: {avaliacao_ascii}", ln=True)

    pdf.ln(10)  # Espaço antes da imagem

    # Insere a imagem do gráfico no PDF
    pdf.image(img_grafico, x=10, w=pdf.w - 20)  # Largura do gráfico = largura da página menos margens

    pdf.output(nome_pdf)

# Configuração do app
st.set_page_config(page_title="Analisador de Estudos", layout="centered")
st.title("📊 Analisador de Estudos Semanais")
st.write("Informe quantas horas você estudou em cada dia da semana. Veja o gráfico e baixe seu relatório em PDF.")

# Entrada do nome do aluno
nome_aluno = st.text_input("Digite seu nome:")

# Dias da semana e coleta de horas
dias_semana = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
horas_estudo = []

# Formulário com sliders
with st.form("form_estudos"):
    for dia in dias_semana:
        horas = st.slider(f"{dia}:", 0.0, 12.0, step=0.5, key=dia)
        horas_estudo.append(horas)
    submitted = st.form_submit_button("Gerar Análise")

# Processamento após submit
if submitted:
    if nome_aluno.strip() == "":
        st.warning("Por favor, digite seu nome para gerar o relatório.")
    else:
        st.write("🔄 Processando dados...")

        media = np.mean(horas_estudo)
        maximo = np.max(horas_estudo)
        minimo = np.min(horas_estudo)

        # Função de avaliação com mensagens detalhadas
        def avaliar_semana(media):
            if media >= 6:
                return "Excelente ritmo de estudos! Continue assim e voce estara cada vez mais perto dos seus objetivos."
            elif media >= 4:
                return "Bom trabalho, mas voce pode melhorar! Tente organizar melhor sua rotina para ganhar mais consistencia."
            else:
                return "Voce estudou pouco essa semana. Procure estabelecer metas diarias e focar no seu objetivo. Voce consegue!"
        
        avaliacao = avaliar_semana(media)

        # Exibe avaliação antes do gráfico
        st.subheader("📋 Avaliação da Semana")
        st.markdown(f"""
**Média de estudo por dia:** {media:.2f} horas  
**Resumo:** {avaliacao}
""")

        st.write("📊 Gerando gráfico...")
        fig = gerar_grafico(dias_semana, horas_estudo)
        st.subheader("📈 Gráfico de Estudo")
        st.plotly_chart(fig, use_container_width=True)

        # Salvar gráfico como imagem PNG para inserir no PDF
        img_path = "grafico_estudos.png"
        fig.write_image(img_path, format="png")

        # Preparar nome do PDF com timestamp
        data = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nome_pdf = f"Relatorio_Estudos_{nome_aluno.replace(' ', '_')}_{data}.pdf"

        st.write("📄 Gerando PDF...")
        gerar_pdf(nome_aluno, dias_semana, horas_estudo, media, maximo, minimo, avaliacao, nome_pdf, img_path)

        with open(nome_pdf, "rb") as file:
            st.success("✅ Relatório gerado com sucesso!")
            st.download_button("📥 Baixar PDF", data=file, file_name=os.path.basename(nome_pdf), mime="application/pdf")

  



  
