import streamlit as st
import asyncio
import json
from fx_brokers.broker_factory import BrokerFactory

st.title("GMOクリック証券 UIテスト（ログイン・レート・発注）")

with open("config.json") as f:
    config = json.load(f)

if "broker" not in st.session_state:
    st.session_state.broker = BrokerFactory("gmo", config)
    st.session_state.loop = asyncio.new_event_loop()
    st.session_state["show_input"] = False
    # asyncio.set_event_loop(st.session_state.loop)
    

async def run_async(fn, *args, **kwargs):
    try:
        result = await fn(*args, **kwargs)
        st.success(f"完了: {result}")
    except Exception as e:
        st.error(f"エラー: {e}")

if st.button("① ログイン"):
    st.session_state.loop.run_until_complete(run_async(st.session_state.broker.login))

if st.button("② レート取得"):
    st.session_state.loop.run_until_complete(run_async(st.session_state.broker.fetch_rate))

if st.button("③ 発注（USD/JPY 成行・買）", key="order_button"):
    st.session_state.show_input = True

if st.session_state.show_input:
    amount = st.number_input("注文数量を入力してください", min_value=0.01, value=1.0, step=0.01, key="amount_input")
    if st.button("注文を確定", key="confirm_button"):
        order_data = {"pair": "USD/JPY", "amount": amount, "type": "buy"}
        st.session_state.loop.run_until_complete(
            run_async(st.session_state.broker.place_order, order_data)
        )
