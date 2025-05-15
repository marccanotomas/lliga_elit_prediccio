import streamlit as st
import pandas as pd
from predictor.data_loader import DataLoader
from predictor.simulator import MonteCarloSimulator
from predictor.league_rules import LeagueRules
import plotly.express as px
import io
import os

# --- Rutes imatges ---
ESCUT_VALLS = "img/escut_valls.png"
ESTADI_VILAR = "img/vilar.jpg"
LOGO_RADIO = "img/radiociutat.png"

# --- Colors corporatius UE Valls ---
VALLS_RED = "#D90429"
VALLS_WHITE = "#FFF"
SUCCESS_COLOR = VALLS_RED

# --- Header amb escut i logo radio ---
def load_logo():
    cols = st.columns([1,3,1])
    with cols[0]:
        st.image(ESCUT_VALLS, width=120)
    with cols[1]:
        st.markdown(
            "<h1 style='color:#D90429; font-size:2.8em; margin-bottom: 0;'>"
            "Predicció Final Lliga Èlit"
            "</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='font-size:1.5em; color:#222; margin-bottom:0.5em;'>"
            "Especial <b>UE Valls</b> per a <b>Ràdio Ciutat de Valls</b>"
            "</div>",
            unsafe_allow_html=True
        )
    with cols[2]:
        st.image(LOGO_RADIO, width=120)
    st.caption("Analitzem, amb IA, totes les opcions del nostre equip! ⚽❤️🤍")

# --- Sidebar ---
def sidebar(config):
    st.sidebar.image(ESTADI_VILAR, use_container_width=True, caption="Estadi del Vilar")
    st.sidebar.header("Configuració de la simulació")
    n_sim = st.sidebar.slider("Núm. simulacions", 500, 25000, config.N_SIMULACIONS, step=500)
    st.sidebar.markdown("---")
    ascens_catalans = st.sidebar.radio(
        "Hi ha algun equip català que ha ascendit a 2a RFEF via playoff?",
        ["No", "Sí"], horizontal=True, index=0
    )
    # Missatge informatiu sobre l’efecte d’aquesta opció
    if ascens_catalans == "Sí":
        st.sidebar.info(
            "Si un equip català aconsegueix l’ascens a 2a RFEF a través del playoff, "
            "aquesta plaça allibera una salvació extra a la Lliga Èlit. "
            "**Només baixarien 4 equips** en comptes de 5!"
        )
    else:
        st.sidebar.warning(
            "Si cap català no puja a 2a RFEF via playoff, "
            "**baixen els 5 darrers classificats**."
        )
    st.sidebar.markdown("---")
    st.sidebar.write("App creada per Marc Cano Tomàs")
    return n_sim, ascens_catalans


def highlight_valls(row):
    color = VALLS_RED if row["Equip"].strip().upper() == "VALLS" else "#222"
    background = "#FFEAEA" if row["Equip"].strip().upper() == "VALLS" else ""
    style = f'color: {color}; background-color: {background}; font-weight: bold;' if row["Equip"].strip().upper() == "VALLS" else ""
    return [style for _ in row]

def main():
    # --- Configuració inicial ---
    st.set_page_config(page_title="Final Lliga Èlit - Especial UE Valls", page_icon="⚽", layout="wide")
    from config import N_SIMULACIONS as DEFAULT_N_SIM

    # --- Branding i header ---
    load_logo()

    # --- Carrega dades ---
    data_loader = DataLoader()
    classificacio, historic, partits = data_loader.load_all()

    # --- Sidebar ---
    import config as config_mod
    n_sim, ascens_catalans = sidebar(config_mod)
    config_mod.N_SIMULACIONS = n_sim

    # --- Decideix quants baixen ---
    if ascens_catalans == "Sí":
        n_baixen = 4
    else:
        n_baixen = 5

    rules = LeagueRules(n_ascens=2, n_playoff=4, n_descens=n_baixen)
    simulator = MonteCarloSimulator(config_mod, rules)

    # --- Simulació només en clicar botó ---
    simular = st.button("Simula escenaris per la UE Valls ⚡")
    if simular:
        with st.spinner("Simulant temporada..."):
            summary = simulator.simulate_season(classificacio, historic, partits)
            st.session_state["sim_summary"] = summary
            st.success("Simulació completada!")

    # --- Mostra resultats només si s'ha simulat ---
    if "sim_summary" in st.session_state and st.session_state["sim_summary"] is not None:
        summary = st.session_state["sim_summary"]

        # Missatge informatiu de l'escenari de descens
        if ascens_catalans == "Sí":
            st.info("⚠️ Amb ascens d’un català a 2a RFEF: només baixen 4 equips!")
        else:
            st.warning("Baixen els 5 darrers classificats (escenari habitual).")

        df_summary = pd.DataFrame([
            {
                "Equip": equip,
                "Ascens (%)": val["ascens"],
                "Playoff (%)": val["playoff"],
                "Mantenen (%)": val["mantenen"],
                "Descens (%)": val["descens"],
                "Posicions": val["posicions"]
            }
            for equip, val in summary.items()
        ])

        # Percentatges a dos decimals!
        for col in ["Ascens (%)", "Playoff (%)", "Mantenen (%)", "Descens (%)"]:
            df_summary[col] = df_summary[col].round(2)

        # --- Taula amb Valls destacat ---
        df_display = df_summary.drop(columns=["Posicions"])
        st.markdown("### 📊 Probabilitats finals de cada equip")
        st.dataframe(
            df_display.style.apply(highlight_valls, axis=1),
            height=620
        )

        # --- Gràfic només per la Valls i missatge motivador ---
        st.markdown(f"### 🎯 Focus en la <span style='color:{VALLS_RED}'>UE Valls</span>", unsafe_allow_html=True)
        equip_detall = "VALLS"
        posicions = summary[equip_detall]["posicions"]
        posicions_x = list(map(int, posicions.keys()))
        freq = list(posicions.values())

        ascens = summary[equip_detall]["ascens"]
        playoff = summary[equip_detall]["playoff"]
        descens = summary[equip_detall]["descens"]

        if ascens >= 50:
            st.success(f"La UE Valls té un **{ascens}%** de probabilitat d'ascens directe! 🏆")
        elif descens >= 20:
            st.error(f"Atenció! La UE Valls encara té un **{descens}%** de risc de descens. Toca patir fins al final!")
        else:
            st.info(f"La UE Valls té un **{ascens}%** d'ascens, **{playoff}%** de playoff, **{descens}%** de descens.")

        fig2 = px.bar(
            x=posicions_x, y=freq,
            labels={"x": "Posició final", "y": "Freqüència"}, height=330,
            title="Distribució de posicions finals de la UE Valls"
        )
        fig2.update_traces(marker_color=VALLS_RED)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Nombre de vegades que la UE Valls ha acabat en cada posició (simulació Monte Carlo)")

        # --- Exportació Excel ---
        buf = io.BytesIO()
        df_display.to_excel(buf, index=False)
        st.download_button("Descarrega la taula (Excel)", data=buf.getvalue(),
                          file_name="resultats_lliga_elit_valls.xlsx", mime="application/vnd.ms-excel")

    st.write("---")
    st.markdown(
        f"<div style='text-align: center; color: #888; font-size: 15px;'>"
        "App feta per <b>Marc Cano Tomàs</b> per a <b>Ràdio Ciutat de Valls</b> · Maig, 2025 "
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()