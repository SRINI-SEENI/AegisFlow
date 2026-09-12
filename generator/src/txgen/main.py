import typer
from rich import print
from txgen.population import PopulationGenerator

app = typer.Typer(help="AegisFlow Synthetic Transaction & Typology Generator")

@app.command()
def seed(
    accounts: int = typer.Option(100, help="Number of accounts to generate"),
    devices: int = typer.Option(30, help="Number of shared devices to generate"),
    merchants: int = typer.Option(20, help="Number of merchants to generate")
):
    """Seed synthetic entities into population universe"""
    pop = PopulationGenerator()
    accts = pop.generate_accounts(accounts)
    devs = pop.generate_devices(devices)
    merchs = pop.generate_merchants(merchants)
    
    print(f"[bold green][+] Successfully generated universe:[/bold green]")
    print(f"  - Accounts:  {len(accts)}")
    print(f"  - Devices:   {len(devs)}")
    print(f"  - Merchants: {len(merchs)}")

@app.command()
def stream(
    rate: int = typer.Option(10, help="Transactions per second to stream")
):
    """Stream synthetic transactions with injected typologies"""
    print(f"[bold blue]Streaming transactions at {rate} TPS...[/bold blue]")

if __name__ == "__main__":
    app()
