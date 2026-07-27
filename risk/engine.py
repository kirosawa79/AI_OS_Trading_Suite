from core.models import PositionPlan
from config.settings import SETTINGS

def build_position_plan(capital: float, risk_pct: float, ask_price: float) -> PositionPlan:
    capital=max(float(capital),0.0)
    risk_pct=max(0.0,min(float(risk_pct),SETTINGS.max_risk_pct))
    unit_cost=max(float(ask_price),0.0)*100
    budget=capital*risk_pct
    quantity=int(budget//unit_cost) if unit_cost>0 else 0
    total=quantity*unit_cost
    valid=quantity>0 and total<=budget
    reason="Posición dentro del presupuesto de riesgo." if valid else "El contrato excede el presupuesto de riesgo permitido."
    return PositionPlan(capital,risk_pct,budget,unit_cost,quantity,total,valid,reason)
