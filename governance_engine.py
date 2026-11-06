import pandas as pd
import json

def load_initiatives(filepath="initiatives_mock.json") -> pd.DataFrame:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def evaluate_governance(row: pd.Series) -> dict:
    """
    Evalúa la iniciativa bajo criterios de gobernanza técnica,
    calidad (QA) y criticidad de arquitectura.
    """
    # 1. Quality Gate Crítico: Datos sensibles sin plan de QA formal
    if row["sensitive_data"] and not row["has_qa_plan"]:
        return {
            "status": "BLOQUEADO (Quality Gate)",
            "risk_score": 90,
            "action": "Exigir Plan UAT y Matriz de Riesgos antes de revisión en comité."
        }

    # 2. Cálculo ponderado de riesgo técnico/arquitectura
    base_score = (row["strategic_value"] * 10) + (row["tech_complexity"] * 10)
    
    # Penalización por dependencias de integración cruzada (ERP)
    if row["requires_erp_integration"]:
        base_score += 20

    # 3. Determinación de ruta según nivel de riesgo
    if base_score >= 80:
        decision = "Requiere Comité HQ"
        action = "Presentar en Comité de Gobernanza mensual para aprobación de arquitectura."
    elif base_score >= 50:
        decision = "Revisión Funcional Estándar"
        action = "Aprobación delegada a nivel Product Owner / Líder de Dominio."
    else:
        decision = "Fast-Track (Pase Directo)"
        action = "Priorización directa en backlog del sprint técnico."

    return {
        "status": decision,
        "risk_score": min(base_score, 100),
        "action": action
    }

def process_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    evaluations = df.apply(evaluate_governance, axis=1)
    eval_df = pd.DataFrame(evaluations.tolist())
    return pd.concat([df, eval_df], axis=1)

if __name__ == "__main__":
    df = load_initiatives()
    portfolio_evaluated = process_portfolio(df)
    print(portfolio_evaluated[["name", "domain", "status", "risk_score"]])