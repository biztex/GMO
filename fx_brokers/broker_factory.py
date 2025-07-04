from fx_brokers.gmo_click_fx import GMOClickFX

def BrokerFactory(name: str, config: dict):
    name = name.lower()
    if name == "gmo":
        return GMOClickFX(config)
    else:
        raise ValueError(f"業者 '{name}' は未対応です。")
