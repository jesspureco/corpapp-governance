import streamlit as st
import pandas as pd
from governance_engine import load_initiatives, process_portfolio, evaluate_governance

# Configuración inicial de la página web
st.set_page_config(page_title="CorpApp Gatekeeper", layout="wide")

st.title("🛡️ CorpApp Gatekeeper: Gobernanza de Aplicaciones HQ")
st.caption("Motor de evaluación de demandas de IT para Finanzas, HSE, People y Compliance")

# Carga y procesamiento del portfolio de datos
df_raw = load_initiatives()
df = process_portfolio(df_raw)

# 📊 1. Indicadores Ejecutivos (KPIs)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Iniciativas", len(df))
c2.metric("Fast-Track (Pase Directo)", len(df[df["status"] == "Fast-Track (Pase Directo)"]))
c3.metric("Requiere Comité HQ", len(df[df["status"] == "Requiere Comité HQ"]))
c4.metric("Bloqueado por QA/Seguridad", len(df[df["status"].str.contains("BLOQUEADO")]))

st.divider()

# 📋 2. Tabla Interactiva del Portfolio
st.subheader("📋 Portfolio Global de Iniciativas Corporativas")

domains = ["Todos"] + list(df["domain"].unique())
selected_domain = st.selectbox("Filtrar por Dominio Funcional:", domains)

df_display = df if selected_domain == "Todos" else df[df["domain"] == selected_domain]

st.dataframe(
    df_display[["id", "name", "domain", "risk_score", "status", "action"]],
    use_container_width=True
)

st.divider()

# ➕ 3. Formulario para Evaluar Nuevas Demandas
st.subheader("➕ Simular Nueva Demanda Corporativa")

with st.form("new_initiative_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("Nombre de la Aplicación", value="App de Reporte Operativo")
        domain = st.selectbox("Área de Negocio", ["HSE", "Finance", "People", "Compliance"])
        strategic_value = st.slider("Valor Estratégico (1-5)", 1, 5, 4)
    with col_b:
        tech_complexity = st.slider("Complejidad Técnica (1-5)", 1, 5, 3)
        requires_erp = st.checkbox("¿Requiere Integración con ERP Corporativo?")
        sensitive_data = st.checkbox("¿Maneja Datos Sensibles?")
        has_qa_plan = st.checkbox("¿Cuenta con Plan de QA / UAT Validado?")

    submitted = st.form_submit_button("Evaluar Gobernanza de la Demanda")

    if submitted:
        new_data = pd.Series({
            "id": f"INIT-00{len(df)+1}",
            "name": name,
            "domain": domain,
            "strategic_value": strategic_value,
            "tech_complexity": tech_complexity,
            "requires_erp_integration": requires_erp,
            "sensitive_data": sensitive_data,
            "has_qa_plan": has_qa_plan
        })
        result = evaluate_governance(new_data)
        
        if "BLOQUEADO" in result["status"]:
            st.error(f"🚨 **Estado:** {result['status']}")
        elif "Comité" in result["status"]:
            st.warning(f"⚠️ **Estado:** {result['status']}")
        else:
            st.success(f"✅ **Estado:** {result['status']}")
            
        st.info(f"💡 **Acción recomendada:** {result['action']}")

        st.divider()

# 📈 4. Matriz Ejecutiva de Riesgo vs Complejidad
st.subheader("📈 Matriz de Decisión Estratégica (Comité HQ)")

import plotly.express as px

fig = px.scatter(
    df,
    x="tech_complexity",
    y="strategic_value",
    color="status",
    size="risk_score",
    hover_name="name",
    text="id",
    labels={
        "tech_complexity": "Complejidad Técnica (1-5)",
        "strategic_value": "Valor Estratégico (1-5)",
        "status": "Estado de Gobernanza"
    },
    title="Evaluación de Portfolio: Impacto vs Complejidad"
)

# Ajustes visuales de la gráfica
fig.update_traces(textposition='top center', marker=dict(sizeref=2))
fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)