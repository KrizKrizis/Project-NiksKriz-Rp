# auction/keyboards/auction.py
from vkbottle import Keyboard, Callback, KeyboardButtonColor

def get_auction_list_keyboard(businesses: list) -> str:
    keyboard = Keyboard(inline=True)
    for biz in businesses:
        label = f"{biz['name']} | {biz['status_text']}"
        if biz["is_on_auction"] and biz["owner_id"] is None:
            current_bid = biz["current_bid_amount"] or (2000000 if biz["type"] == "auction_casino" else 500000)
            label += f" | Текущая ставка: {current_bid} NK"
            keyboard.add(Callback(label, payload={"cmd": "auction_info", "business_id": biz["business_id"]}), color=KeyboardButtonColor.PRIMARY)
        else:
            keyboard.add(Callback(label, payload={"cmd": "auction_noop"}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "shop_businesses"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()

def get_auction_info_keyboard(business_id: str) -> str:
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("💰 Сделать ставку", payload={"cmd": "auction_bid", "business_id": business_id}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("🔙 Назад", payload={"cmd": "auction_list"}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()