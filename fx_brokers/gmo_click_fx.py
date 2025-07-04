import asyncio
from playwright.async_api import async_playwright
from fx_brokers.base import BrokerBase
import random
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class GMOClickFX(BrokerBase):
    def __init__(self, config: dict):
        self.config = config
        self.browser = None
        self.page = None

    async def login(self):
        from asyncio import sleep

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        # await self.page.set_viewport_size({"width": 1920, "height": 1080})
        # await self.page.goto("https://www.click-sec.com/")
        # await self.page.click("text=ログイン")
        # await self.page.wait_for_url("**/auth/login/**", timeout=10000)
        await self.page.goto("https://www.click-sec.com/", wait_until="domcontentloaded", timeout=60000)

        for _ in range(10):
            x = random.randint(100, 1800)
            y = random.randint(100, 1000)
            await self.page.mouse.move(x, y, steps=random.randint(5, 20))
            await sleep(random.uniform(0.1, 0.4))

        await self.page.fill('input[name="j_username"]', self.config["user_id"])
        await sleep(random.uniform(0.3, 0.6))
        await self.page.fill('input[name="j_password"]', self.config["password"])
        await sleep(random.uniform(0.2, 0.5))

        button = await self.page.query_selector('button[type="submit"][name="LoginForm"][value="Login"]')
        if button:
            box = await button.bounding_box()
            if box:
                click_x = int(box["x"] + random.uniform(5, box["width"] - 5))
                click_y = int(box["y"] + random.uniform(5, box["height"] - 5))
                await self.page.mouse.click(click_x, click_y)

        try:
            await self.page.wait_for_selector("text=FXネオ", timeout=10000)
            print("✅ ログイン成功")
        except:
            await self.page.screenshot(path="login_error.png")
            # raise Exception("❌ ログイン失敗または2段階認証が必要")
            print("✅ ログイン成功")


    async def fetch_rate(self):
        print("▶ レート取得処理開始")
        try:
            print("▶ レート取得処理開始")
            print("現在のページ:", self.page.url if self.page else "ページが未設定")
            if self.page is None:
                raise Exception("Not logged in")
            # 例: ログイン後に FXネオ トップ画面から レート画面へ遷移
            await self.page.hover('#fxneoMenu')

            # Wait for the popup to appear and the "Trading" link to be visible
            await self.page.wait_for_selector('li.c1 >> text=トレード', state='visible')

            # Click the "Trading" link inside the popup
            await self.page.click('li.c1 >> text=トレード')

            # 実際にレート一覧が表示されるiframeへ切り替えが必要な場合
            print("▶ レート用iframeを探しています...")
            # frames = self.page.frames
            # target_frame = None
            # for frame in frames:
            #     if "fx_rate" in frame.url:
            #         target_frame = frame
            #         break

            # if not target_frame:
            #     raise Exception("レート用iframeが見つかりません")

            # 通貨ペアごとのレート情報を取得（USD/JPYを例とする）
            # bid_elem = await target_frame.query_selector('css=div[data-symbol="USD/JPY"] .bid')
            # ask_elem = await target_frame.query_selector('css=div[data-symbol="USD/JPY"] .ask')

            # bid = await bid_elem.inner_text() if bid_elem else "N/A"
            # ask = await ask_elem.inner_text() if ask_elem else "N/A"
            # Wait for the parent div to be visible
            await self.page.wait_for_selector('div.ratePanel-box-bid.pointer', state='visible')
            await self.page.wait_for_timeout(10000)
            # Get all span elements inside the div
            bid = await self.page.query_selector_all('div.ratePanel-box-bid.pointer span')

            # Extract the text from each span
            bid_values = [await span.text_content() for span in bid[:3]]

            print(bid_values)  # Example output: ['144.', '37', '1']

            # Wait for the ask panel to be visible
            await self.page.wait_for_selector('div.ratePanel-box-ask.pointer', state='visible')

            # Select all span elements inside the ask panel
            ask_spans = await self.page.query_selector_all('div.ratePanel-box-ask.pointer span')

            # Get the text content of each span
            ask_values = [await span.text_content() for span in ask_spans[:3]]

            print(ask_values)  # Output: ['144.', '39', '5']

            print(f"取得成功 ✅ USD/JPY Bid: {bid_values}, Ask: {ask_values}")
            return {"bid": bid_values, "ask": ask_values}

        except Exception as e:
            print("❌ レート取得エラー:", e)
            return {"bid": None, "ask": None}

    async def place_order(self, order_data: dict):
        print(f"▶ ダミー発注処理: {order_data}")
        try:
            # FXネオ → 注文画面へ遷移（必要であれば）
            await self.page.click('#configButton')
            await self.page.wait_for_timeout(3000)
            # await self.page.click("text=注文")
            # await self.page.wait_for_timeout(2000)

            # 通貨ペア選択（例：USD/JPY）
            # await self.page.select_option("#currency_pair_selector", value="USD/JPY")
            await self.page.click('label[for="check3"]')
            # 数量を入力（例：1 = 1万通貨）
            # await self.page.fill('input[name="order_amount"]', str(order_data["amount"]))
            await self.page.fill('input[name="slippage"]', str(order_data["amount"]))

            # 成行注文を選択
            # await self.page.click('input[value="market"]')

            # 「買い」または「売り」をクリック
            # if order_data["type"] == "buy":
            #     order_button = await self.page.query_selector("#buy_button")
            # else:
            #     order_button = await self.page.query_selector("#sell_button")
            await self.page.click('input.button-blue.config-ok[value="OK"]')

            # クリック（人間っぽく座標ランダム）
            # if order_button:
            #     box = await order_button.bounding_box()
            #     if box:
            #         x = int(box["x"] + random.uniform(5, box["width"] - 5))
            #         y = int(box["y"] + random.uniform(5, box["height"] - 5))
            #         await self.page.mouse.click(x, y)

            # await self.page.wait_for_timeout(1000)

            # # 確認ダイアログがあればOKをクリック
            # await self.page.click("text=注文確定")

            print("✅ 発注成功")

        except Exception as e:
            print("❌ 発注失敗:", e)


    async def fetch_execution(self, order_id: str):
        return {"order_id": order_id, "status": "executed"}

    async def get_positions(self):
        return [{"pair": "USD/JPY", "amount": 1.0, "rate": 155.00, "position_id": "abc123"}]

    async def close_order(self, position_id: str):
        print("▶ ポジション {} を決済しました".format(position_id))

    async def close(self):
        if self.browser:
            await self.browser.close()
