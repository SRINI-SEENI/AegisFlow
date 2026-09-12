import typer
import random
from rich import print
from txgen.population import PopulationGenerator
from txgen.behavior import BehaviorModel
from txgen.fraud_rings import FraudRingGenerator
from txgen.typologies import TypologyGenerator
from txgen.labels import LabelSink

app = typer.Typer(help="AegisFlow Synthetic Transaction & Typology Generator")

@app.command()
def seed(
    accounts: int = typer.Option(100, help="Number of accounts to generate"),
    devices: int = typer.Option(30, help="Number of shared devices to generate"),
    merchants: int = typer.Option(20, help="Number of merchants to generate"),
    rings: int = typer.Option(3, help="Number of fraud rings to create")
):
    """Seed synthetic entities and fraud networks into population universe"""
    pop = PopulationGenerator()
    accts = pop.generate_accounts(accounts)
    devs = pop.generate_devices(devices)
    ips = pop.generate_ips(devices)
    merchs = pop.generate_merchants(merchants)
    
    ring_gen = FraudRingGenerator()
    generated_rings = []
    for _ in range(rings):
        ring = ring_gen.generate_ring(accts, devs, ips)
        generated_rings.append(ring)

    print(f"[bold green][+] Successfully generated universe:[/bold green]")
    print(f"  - Accounts:    {len(accts)}")
    print(f"  - Devices:     {len(devs)}")
    print(f"  - IPs:         {len(ips)}")
    print(f"  - Merchants:   {len(merchs)}")
    print(f"  - Fraud Rings: {len(generated_rings)}")

@app.command()
def stream(
    count: int = typer.Option(100, help="Total transactions to generate"),
    inject_typologies: bool = typer.Option(True, help="Inject smurfing, layering, and round-tripping patterns")
):
    """Generate synthetic transaction stream with injected typologies"""
    pop = PopulationGenerator()
    accts = pop.generate_accounts(50)
    merchs = pop.generate_merchants(10)
    behavior = BehaviorModel()
    typo_gen = TypologyGenerator()
    sink = LabelSink()

    txns = []

    # Inject typologies if requested
    if inject_typologies and len(accts) >= 6:
        # Smurfing
        smurf_txns = typo_gen.generate_smurfing(
            target_account_id=accts[0]["id"],
            smurf_account_ids=[a["id"] for a in accts[1:5]]
        )
        for t in smurf_txns:
            txns.append(t)
            sink.record_label(t["id"], True, "smurfing")

        # Layering
        layer_txns = typo_gen.generate_layering(
            chain_account_ids=[a["id"] for a in accts[5:9]]
        )
        for t in layer_txns:
            txns.append(t)
            sink.record_label(t["id"], True, "layering")

        # Round Tripping
        rt_txns = typo_gen.generate_round_tripping(
            origin_account_id=accts[9]["id"],
            intermediary_account_ids=[a["id"] for a in accts[10:13]]
        )
        for t in rt_txns:
            txns.append(t)
            sink.record_label(t["id"], True, "round_tripping")

    # Fill remaining count with clean transactions
    acct_ids = [a["id"] for a in accts]
    merch_ids = [m["id"] for m in merchs]

    while len(txns) < count:
        acct = random.choice(accts)
        amount = behavior.sample_amount(acct["risk_tier"])
        channel = behavior.sample_channel()
        t_id = f"tx_{random.randint(100000, 999999)}"

        txns.append({
            "id": t_id,
            "account_id": acct["id"],
            "counterparty_id": random.choice(acct_ids),
            "merchant_id": random.choice(merch_ids) if channel == "card" else None,
            "amount": amount,
            "channel": channel,
            "status": "completed",
            "is_fraud": False
        })
        sink.record_label(t_id, False)

    summary = sink.get_summary()
    print(f"[bold blue][+] Generated {len(txns)} transactions:[/bold blue]")
    print(f"  - Clean:           {summary['clean_count']}")
    print(f"  - Fraud/Injected:  {summary['fraud_count']}")
    print(f"    * Smurfing:       {summary['smurfing_count']}")
    print(f"    * Layering:       {summary['layering_count']}")
    print(f"    * Round-Tripping: {summary['round_tripping_count']}")

if __name__ == "__main__":
    app()
