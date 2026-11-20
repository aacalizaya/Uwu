import json
import uuid

import pandas as pd
import streamlit as st

st.set_page_config(page_title="EcoImpacto", page_icon="🌿", layout="wide")

NOM = {"agua": "Agua", "aire": "Aire", "suelo": "Suelo"}
SUG = {
    "agua": ["Vertimiento de aguas residuales", "Consumo de agua", "Escorrentía con sedimentos",
             "Derrame de combustibles o aceites", "Lavado de equipos y vehículos"],
    "aire": ["Emisión de material particulado", "Emisión de gases de combustión", "Generación de ruido",
             "Emisión de olores", "Emisión de gases de efecto invernadero"],
    "suelo": ["Generación de residuos sólidos", "Remoción de cobertura vegetal", "Compactación del suelo",
              "Derrame de hidrocarburos", "Generación de residuos peligrosos"],
}

if "S" not in st.session_state:
    st.session_state.S = {"proj": "", "acts": [], "imps": []}
S = st.session_state.S


def score(i):
    return round((3 * i["i"] + 2 * i["e"] + i["d"] + i["r"]) * i["p"] / 5, 1)


def level(i):
    if i["sign"] > 0:
        return "Positivo"
    v = score(i)
    return "Crítico" if v >= 28 else "Severo" if v >= 20 else "Moderado" if v >= 10 else "Bajo"


def act_name(aid):
    return next((a["name"] for a in S["acts"] if a["id"] == aid), "(eliminada)")


st.title("🌿 EcoImpacto")
st.caption("Registra actividades, identifica aspectos ambientales y evalúa impactos sobre agua, aire y suelo.")

# ---------- Barra lateral: proyecto, guardar y cargar ----------
with st.sidebar:
    S["proj"] = st.text_input("Nombre del proyecto", S["proj"])
    st.download_button("Guardar proyecto (JSON)", json.dumps(S, ensure_ascii=False, indent=2),
                       file_name="ecoimpacto.json", mime="application/json")
    up = st.file_uploader("Cargar proyecto (JSON)", type="json")
    if up and st.button("Cargar archivo"):
        try:
            d = json.load(up)
            assert "acts" in d and "imps" in d
            st.session_state.S = d
            st.rerun()
        except Exception:
            st.error("El archivo no es un JSON válido de EcoImpacto.")
    st.info("Los datos viven en tu sesión. Descarga el JSON para no perderlos.")

t1, t2, t3 = st.tabs(["1. Actividades", "2. Aspectos e impactos", "3. Resultados"])

# ---------- 1. Actividades ----------
with t1:
    c1, c2, c3 = st.columns([3, 1.5, 1])
    name = c1.text_input("Actividad", placeholder="Ej.: Excavación y movimiento de tierras")
    phase = c2.selectbox("Etapa", ["Construcción", "Operación", "Mantenimiento", "Cierre"])
    c3.write("")
    c3.write("")
    if c3.button("Agregar actividad", use_container_width=True):
        if name.strip():
            S["acts"].append({"id": uuid.uuid4().hex[:8], "name": name.strip(), "phase": phase})
            st.rerun()
        else:
            st.warning("Escribe el nombre de la actividad.")
    if S["acts"]:
        st.dataframe(pd.DataFrame([{"Actividad": a["name"], "Etapa": a["phase"],
                                    "Impactos": sum(i["act"] == a["id"] for i in S["imps"])}
                                   for a in S["acts"]]), use_container_width=True, hide_index=True)
        dele = st.multiselect("Eliminar actividades (y sus impactos)", [a["id"] for a in S["acts"]],
                              format_func=act_name)
        if dele and st.button("Eliminar seleccionadas"):
            S["acts"] = [a for a in S["acts"] if a["id"] not in dele]
            S["imps"] = [i for i in S["imps"] if i["act"] not in dele]
            st.rerun()
    else:
        st.write("Aún no hay actividades. Agrega la primera arriba.")

# ---------- 2. Impactos ----------
with t2:
    if not S["acts"]:
        st.write("Primero agrega una actividad en la pestaña 1.")
    else:
        a1, a2, a3 = st.columns(3)
        act = a1.selectbox("Actividad", [a["id"] for a in S["acts"]], format_func=act_name)
        comp = a2.selectbox("Componente afectado", list(NOM), format_func=NOM.get)
        sign = a3.selectbox("Tipo de impacto", [-1, 1], format_func=lambda v: "Negativo" if v < 0 else "Positivo")
        b1, b2 = st.columns(2)
        sug = b1.selectbox("Aspecto frecuente", ["(escribir otro)"] + SUG[comp])
        asp = b1.text_input("Aspecto ambiental", value="" if sug == "(escribir otro)" else sug,
                            key=f"asp_{comp}_{sug}")
        imp = b2.text_input("Impacto", placeholder="Ej.: Deterioro de la calidad del aire")
        s1, s2, s3, s4, s5 = st.columns(5)
        vi = s1.slider("Intensidad", 1, 5, 3)
        ve = s2.slider("Extensión", 1, 5, 3)
        vd = s3.slider("Duración", 1, 5, 3)
        vr = s4.slider("Persistencia", 1, 5, 3)
        vp = s5.slider("Probabilidad", 1, 5, 3)
        nuevo = {"id": uuid.uuid4().hex[:8], "act": act, "comp": comp, "aspect": asp, "impact": imp,
                 "sign": sign, "i": vi, "e": ve, "d": vd, "r": vr, "p": vp}
        st.write(f"Significancia estimada: **{score(nuevo)}** – {level(nuevo)}")
        if st.button("Agregar impacto"):
            if asp.strip() and imp.strip():
                S["imps"].append(nuevo)
                st.rerun()
            else:
                st.warning("Completa el aspecto ambiental y el impacto.")
    st.caption("Significancia = (3×Intensidad + 2×Extensión + Duración + Persistencia) × Probabilidad ÷ 5. "
               "Bajo < 10, Moderado 10–19, Severo 20–27, Crítico ≥ 28. Metodología simplificada.")

# ---------- 3. Resultados ----------
with t3:
    cols = st.columns(3)
    for col, c in zip(cols, NOM):
        L = [i for i in S["imps"] if i["comp"] == c]
        neg = [score(i) for i in L if i["sign"] < 0]
        col.metric(NOM[c], f"{len(L)} impactos", f"máx. {max(neg)}" if neg else "sin impactos negativos",
                   delta_color="off")

    if S["imps"]:
        st.subheader("Matriz actividad × componente")
        rows = []
        for a in S["acts"]:
            r = {"Actividad": a["name"]}
            for c in NOM:
                L = [i for i in S["imps"] if i["act"] == a["id"] and i["comp"] == c]
                neg = [i for i in L if i["sign"] < 0]
                if neg:
                    w = max(neg, key=score)
                    r[NOM[c]] = f"{score(w)} · {level(w)}"
                else:
                    r[NOM[c]] = "+" if L else "–"
            rows.append(r)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.subheader("Registro de impactos")
        df = pd.DataFrame([{
            "Proyecto": S["proj"], "Actividad": act_name(i["act"]), "Aspecto ambiental": i["aspect"],
            "Impacto": i["impact"], "Componente": NOM[i["comp"]],
            "Signo": "Positivo" if i["sign"] > 0 else "Negativo", "Intensidad": i["i"], "Extensión": i["e"],
            "Duración": i["d"], "Persistencia": i["r"], "Probabilidad": i["p"],
            "Significancia": score(i), "Nivel": level(i)} for i in S["imps"]])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Exportar CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name="impactos-ambientales.csv", mime="text/csv")
        dele = st.multiselect("Eliminar impactos", [i["id"] for i in S["imps"]],
                              format_func=lambda x: next(f"{act_name(i['act'])} – {i['aspect']}"
                                                         for i in S["imps"] if i["id"] == x))
        if dele and st.button("Eliminar impactos seleccionados"):
            S["imps"] = [i for i in S["imps"] if i["id"] not in dele]
            st.rerun()
    else:
        st.write("Los resultados aparecerán cuando registres impactos.")
