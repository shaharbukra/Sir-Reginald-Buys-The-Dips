#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from api_gateway import ResilientAlpacaGateway

async def main():
    gateway = ResilientAlpacaGateway()
    try:
        await gateway.initialize()
        positions = await gateway.get_all_positions()
        
        active_positions = [pos for pos in positions if float(pos.qty) != 0]
        print(f"Active positions: {len(active_positions)}")
        
        for pos in active_positions:
            qty = float(pos.qty)
            avg_price = float(pos.avg_entry_price)
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_pct = float(pos.unrealized_plpc) * 100
            
            print(f"\n{pos.symbol}:")
            print(f"  Quantity: {qty} shares")
            print(f"  Avg Entry: ${avg_price:.2f}")
            print(f"  Market Value: ${market_value:.2f}")
            print(f"  P&L: ${unrealized_pl:.2f} ({unrealized_pct:.1f}%)")
            
        # Also check account
        account = await gateway.get_account_safe()
        if account:
            print(f"\nAccount Value: ${float(account.equity):.2f}")
            print(f"Cash: ${float(account.cash):.2f}")
            
    finally:
        await gateway.shutdown()

if __name__ == "__main__":
    asyncio.run(main())