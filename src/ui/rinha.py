# src/ui/rinha.py

import time

import streamlit as st
from calango.core import CalangoEngine
from calango.database import InteractionManager, PersonaManager

engine = CalangoEngine()
db = InteractionManager()
persona_mgr = PersonaManager()

st.title("🥊 A Rinha (The Arena)")
st.caption("Coloque os modelos no ringue. Veja quem sobrevive.")

with st.expander("⚙️ Configuração do Combate", expanded=True):
    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        num_contenders = st.slider("Número de Lutadores", min_value=2, max_value=4, value=2)
    with col_cfg2:
        # Adicionado: Seleção global de Persona para o desafio
        all_personas = [p["name"] for p in persona_mgr.get_all_personas()]
        selected_persona = st.selectbox("Persona (Soul)", all_personas if all_personas else ["Default"])

st.divider()

contenders = []
cols = st.columns(num_contenders)

for i, col in enumerate(cols):
    with col:
        st.subheader(f"Lutador #{i + 1}")

        providers = engine.get_configured_providers()
        if not providers:
            st.error("Nenhum provedor.")
            continue

        prov = st.selectbox("Provedor", providers, key=f"p_{i}")
        models = engine.get_models_for_provider(prov)
        mod = st.selectbox("Modelo", models, key=f"m_{i}")

        contenders.append({"provider": prov, "model": mod})

st.divider()

if prompt := st.chat_input("Lance um desafio no ringue..."):
    st.chat_message("user").write(prompt)

    # Colunas para as respostas
    out_cols = st.columns(num_contenders)

    # Sanitização: O core.py já faz isso, mas enviamos apenas o essencial
    messages = [{"role": "user", "content": prompt}]

    for i, contender in enumerate(contenders):
        with out_cols[i]:
            st.markdown(f"**{contender['model']}**")

            with st.chat_message("assistant"):
                with st.spinner("Lutando..."):
                    # O core.py agora lida com o erro e faz o yield de uma string amigável
                    gen = engine.run_chat(
                        provider_name=contender["provider"],
                        model_name=contender["model"],
                        messages=messages,
                        session_id="rinha-mode",
                        persona_name=selected_persona,  # Parâmetro obrigatório adicionado
                        is_new_session=False,
                    )

                    # O write_stream exibirá o erro como texto se o core.py falhar
                    st.write_stream(gen)

                    # Busca Estatísticas (Aguardando levemente o commit do TinyDB)
                    time.sleep(0.2)
                    try:
                        # Pegamos o último log específico deste modelo na rinha
                        history = db.history_table.all()
                        last_log = next(
                            (
                                rev
                                for rev in reversed(history)
                                if rev["model"] == contender["model"] and rev["session_id"] == "rinha-mode"
                            ),
                            None,
                        )

                        if last_log:
                            cost = last_log.get("cost_usd", 0.0)
                            # Usando .get() para evitar erros se o usage estiver vazio por falha
                            tokens = last_log.get("usage", {}).get("total_tokens", 0)
                            st.success(f"💰 ${cost:.5f} | ⚡ {tokens} tok")
                    except Exception:
                        st.caption("⚠️ Erro ao ler stats.")
